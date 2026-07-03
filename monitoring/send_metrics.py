import socket
import time
import subprocess
import os

GRAPHITE_HOST = 'localhost'
GRAPHITE_PORT = 2003

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
    print("Starting metrics collector script...")
    while True:
        cpu = get_cpu_usage()
        mem_pct, mem_used, mem_free = get_memory_usage()
        
        metrics = {
            'system.cpu.usage_percent': cpu,
            'system.memory.usage_percent': mem_pct,
            'system.memory.used_gb': mem_used,
            'system.memory.free_gb': mem_free
        }
        
        send_to_graphite(metrics)
        time.sleep(10)

if __name__ == '__main__':
    main()
