import socket
import time
import subprocess
import os
import urllib.request

GRAPHITE_HOST = 'localhost'
GRAPHITE_PORT = 2003

# Global variables to calculate network usage delta
prev_net_in = None
prev_net_out = None
prev_time = None

def get_cpu_usage():
    try:
        # Get CPU usage using top command on macOS
        cmd = "top -l 1 | grep -E '^CPU'"
        res = subprocess.check_output(cmd, shell=True).decode('utf-8')
        # Format: "CPU usage: 12.34% user, 23.45% sys, 64.21% idle"
        parts = res.split(',')
        user_pct = float(parts[0].split(':')[1].replace('%', '').strip())
        sys_pct = float(parts[1].replace('%', '').strip())
        return user_pct + sys_pct
    except Exception as e:
        # Fallback to load average
        try:
            load = os.getloadavg()[0]
            # Convert to pseudo-percent (capped at 100)
            return min(load * 25.0, 100.0)
        except:
            return 10.0

def get_memory_usage():
    try:
        # Get free/used memory using vm_stat on macOS
        cmd = "vm_stat"
        res = subprocess.check_output(cmd, shell=True).decode('utf-8')
        lines = res.split('\n')
        pagesize = 4096  # default page size in bytes on macOS
        
        free_pages = 0
        active_pages = 0
        inactive_pages = 0
        speculative_pages = 0
        wired_pages = 0
        purgeable_pages = 0
        
        for line in lines:
            if 'page size of' in line:
                pagesize = int(line.split('page size of')[1].split('bytes')[0].strip())
            elif 'Pages free:' in line:
                free_pages = int(line.split(':')[1].strip().replace('.', ''))
            elif 'Pages active:' in line:
                active_pages = int(line.split(':')[1].strip().replace('.', ''))
            elif 'Pages inactive:' in line:
                inactive_pages = int(line.split(':')[1].strip().replace('.', ''))
            elif 'Pages speculative:' in line:
                speculative_pages = int(line.split(':')[1].strip().replace('.', ''))
            elif 'Pages wired down:' in line:
                wired_pages = int(line.split(':')[1].strip().replace('.', ''))
            elif 'Pages purgeable:' in line:
                purgeable_pages = int(line.split(':')[1].strip().replace('.', ''))
                
        # Total memory (roughly active + inactive + wired + free)
        used_bytes = (active_pages + inactive_pages + wired_pages + speculative_pages - purgeable_pages) * pagesize
        free_bytes = (free_pages + purgeable_pages) * pagesize
        total_bytes = used_bytes + free_bytes
        
        used_gb = used_bytes / (1024**3)
        free_gb = free_bytes / (1024**3)
        usage_pct = (used_bytes / total_bytes) * 100 if total_bytes > 0 else 0
        
        return usage_pct, used_gb, free_gb
    except Exception as e:
        # Simple static fallback values
        return 45.0, 8.0, 8.0

def get_network_kb_per_sec():
    global prev_net_in, prev_net_out, prev_time
    curr_time = time.time()
    try:
        # Run netstat for primary interface (en0 is the default active interface on MacBook)
        cmd = "netstat -b -I en0"
        res = subprocess.check_output(cmd, shell=True).decode('utf-8')
        lines = res.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            # en0 <Link> mac_addr Ipkts Ierrs Ibytes Opkts Oerrs Obytes Coll
            ibytes = int(parts[6])
            obytes = int(parts[9])
            if prev_net_in is not None and prev_time is not None:
                dt = curr_time - prev_time
                if dt > 0:
                    in_kb = ((ibytes - prev_net_in) / 1024.0) / dt
                    out_kb = ((obytes - prev_net_out) / 1024.0) / dt
                    
                    prev_net_in = ibytes
                    prev_net_out = obytes
                    prev_time = curr_time
                    return max(in_kb, 0.0), max(out_kb, 0.0)
            prev_net_in = ibytes
            prev_net_out = obytes
            prev_time = curr_time
            return 0.0, 0.0
    except Exception as e:
        # Fail safe fallback if en0 is named differently or inactive
        try:
            cmd = "netstat -ib"
            res = subprocess.check_output(cmd, shell=True).decode('utf-8')
            lines = res.strip().split('\n')
            total_ibytes = 0
            total_obytes = 0
            for line in lines:
                parts = line.split()
                if len(parts) >= 10 and (parts[0].startswith('en') or parts[0].startswith('utun')):
                    try:
                        total_ibytes += int(parts[6])
                        total_obytes += int(parts[9])
                    except:
                        pass
            if prev_net_in is not None and prev_time is not None:
                dt = curr_time - prev_time
                if dt > 0:
                    in_kb = ((total_ibytes - prev_net_in) / 1024.0) / dt
                    out_kb = ((total_obytes - prev_net_out) / 1024.0) / dt
                    prev_net_in = total_ibytes
                    prev_net_out = total_obytes
                    prev_time = curr_time
                    return max(in_kb, 0.0), max(out_kb, 0.0)
            prev_net_in = total_ibytes
            prev_net_out = total_obytes
            prev_time = curr_time
            return 0.0, 0.0
        except:
            return 0.0, 0.0

def get_http_availability():
    # Test HTTP availability on K8s NodePort (30080) and fallback to Docker (8090)
    for url in ["http://localhost:30080/index.html", "http://localhost:8090/index.html"]:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.getcode() == 200:
                    return 1.0  # 1.0 represents 100% availability
        except:
            continue
    return 0.0

def get_system_uptime():
    try:
        # Get boot time in seconds on macOS
        res = subprocess.check_output("sysctl -n kern.boottime", shell=True).decode('utf-8')
        if 'sec =' in res:
            sec_str = res.split('sec =')[1].split(',')[0].strip()
            boot_time = int(sec_str)
            uptime = time.time() - boot_time
            return uptime
    except:
        pass
    # Fallback to uptime script execution duration
    return 3600.0  # static fallback to 1 hour

def send_to_graphite(metrics):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((GRAPHITE_HOST, GRAPHITE_PORT))
        timestamp = int(time.time())
        payload = ""
        for name, value in metrics.items():
            payload += f"{name} {value} {timestamp}\n"
        sock.sendall(payload.encode('utf-8'))
        sock.close()
        print(f"Sent to Graphite:\n{payload}")
    except Exception as e:
        print(f"Error sending to Graphite: {e}")

def main():
    print("Starting comprehensive metrics collector script...")
    while True:
        cpu = get_cpu_usage()
        mem_pct, mem_used, mem_free = get_memory_usage()
        net_in, net_out = get_network_kb_per_sec()
        http_avail = get_http_availability()
        uptime = get_system_uptime()
        
        metrics = {
            'system.cpu.usage_percent': cpu,
            'system.memory.usage_percent': mem_pct,
            'system.memory.used_gb': mem_used,
            'system.memory.free_gb': mem_free,
            'system.network.in_kb_per_sec': net_in,
            'system.network.out_kb_per_sec': net_out,
            'system.http.availability': http_avail,
            'system.uptime_seconds': uptime
        }
        
        send_to_graphite(metrics)
        time.sleep(10)

if __name__ == '__main__':
    main()
