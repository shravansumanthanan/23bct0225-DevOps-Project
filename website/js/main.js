document.addEventListener('DOMContentLoaded', () => {
  console.log('ABC Technologies Website Loaded');
  
  // Dynamic Year in Footer
  const yearSpan = document.getElementById('current-year');
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
  }
  
  // Mobile Menu Toggle
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  const nav = document.querySelector('nav');
  
  if (mobileMenuBtn && nav) {
    mobileMenuBtn.addEventListener('click', () => {
      if (nav.style.display === 'block') {
        nav.style.display = 'none';
        mobileMenuBtn.innerHTML = '&#9776;';
      } else {
        nav.style.display = 'block';
        nav.style.position = 'absolute';
        nav.style.top = '100%';
        nav.style.left = '0';
        nav.style.width = '100%';
        nav.style.background = 'rgba(11, 15, 25, 0.95)';
        nav.style.backdropFilter = 'blur(12px)';
        nav.style.padding = '1.5rem 2rem';
        nav.style.borderBottom = '1px solid var(--border-color)';
        
        const navList = nav.querySelector('ul');
        if (navList) {
          navList.style.flexDirection = 'column';
          navList.style.gap = '1.25rem';
          navList.style.alignItems = 'flex-start';
        }
        
        mobileMenuBtn.innerHTML = '&times;';
      }
    });
  }

  // Fade-in animation on scroll for bento cards
  const cards = document.querySelectorAll('.bento-card, .gallery-item, .job-card');
  
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);
  
  cards.forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
    observer.observe(card);
  });
});
