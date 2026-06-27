document.addEventListener('DOMContentLoaded', () => {
  // ─── Scroll-triggered reveal animations ───
  const revealElements = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-up');
  if (revealElements.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    revealElements.forEach(el => observer.observe(el));
  }

  // ─── Parallax hero effect ───
  const hero = document.querySelector('.hero-parallax');
  if (hero) {
    window.addEventListener('scroll', () => {
      const scrolled = window.scrollY;
      const bg = hero.querySelector('.hero-bg');
      const content = hero.querySelector('.hero-content');
      if (bg) bg.style.transform = `translateY(${scrolled * 0.4}px)`;
      if (content) content.style.transform = `translateY(${scrolled * 0.15}px)`;
    });
  }

  // ─── 3D Tilt effect on product cards ───
  const tiltCards = document.querySelectorAll('.card-tilt');
  tiltCards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = (y - centerY) / 12;
      const rotateY = (centerX - x) / 12;
      card.style.transform = `perspective(600px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(600px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
    });
  });

  // ─── Image zoom on mouse move (product detail) ───
  const zoomContainer = document.querySelector('.img-zoom-container');
  const zoomImg = zoomContainer?.querySelector('img');
  if (zoomContainer && zoomImg) {
    zoomContainer.addEventListener('mousemove', (e) => {
      const rect = zoomContainer.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      zoomImg.style.transformOrigin = `${x}% ${y}%`;
      zoomImg.style.transform = 'scale(2)';
    });
    zoomContainer.addEventListener('mouseleave', () => {
      zoomImg.style.transformOrigin = 'center center';
      zoomImg.style.transform = 'scale(1)';
    });
  }

  // ─── Animate cart counter ───
  const cartBadge = document.querySelector('.cart-badge');
  if (cartBadge) {
    const observer = new MutationObserver(() => {
      cartBadge.classList.add('cart-bump');
      setTimeout(() => cartBadge.classList.remove('cart-bump'), 300);
    });
    observer.observe(cartBadge, { childList: true, characterData: true, subtree: true });
  }

  // ─── Quick view modal ───
  document.querySelectorAll('[data-quick-view]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const modal = document.getElementById('quickViewModal');
      const slug = btn.dataset.quickView;
      if (modal) {
        modal.classList.remove('hidden');
        modal.querySelector('.modal-content').classList.remove('scale-95', 'opacity-0');
        document.body.style.overflow = 'hidden';
        fetch(`/product/${slug}/quick`)
          .then(r => r.text())
          .then(html => {
            modal.querySelector('.modal-body').innerHTML = html;
          });
      }
    });
  });

  // ─── Close modals ───
  document.querySelectorAll('.modal-overlay, .modal-close').forEach(el => {
    el.addEventListener('click', (e) => {
      if (e.target === el || el.classList.contains('modal-close') || e.target.classList.contains('modal-overlay')) {
        const modal = el.closest('.modal') || document.getElementById('quickViewModal');
        if (modal) {
          modal.querySelector('.modal-content')?.classList.add('scale-95', 'opacity-0');
          setTimeout(() => { modal.classList.add('hidden'); document.body.style.overflow = ''; }, 200);
        }
      }
    });
  });

  // ─── Color / Size selector ───
  document.querySelectorAll('.swatch-group .swatch').forEach(el => {
    el.addEventListener('click', function() {
      this.closest('.swatch-group')?.querySelectorAll('.swatch').forEach(s => s.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // ─── Mobile menu toggle ───
  const menuToggle = document.getElementById('menuToggle');
  const mobileMenu = document.getElementById('mobileMenu');
  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
      document.body.classList.toggle('overflow-hidden');
    });
  }

  // ─── Floating cart toggle ───
  const cartToggle = document.getElementById('cartToggle');
  const cartDrawer = document.getElementById('cartDrawer');
  const cartOverlay = document.getElementById('cartOverlay');
  if (cartToggle && cartDrawer) {
    cartToggle.addEventListener('click', () => {
      cartDrawer.classList.remove('translate-x-full');
      cartOverlay?.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
    });
  }
  const closeCart = () => {
    const drawer = document.getElementById('cartDrawer');
    const overlay = document.getElementById('cartOverlay');
    if (drawer) drawer.classList.add('translate-x-full');
    if (overlay) setTimeout(() => { overlay.classList.add('hidden'); document.body.style.overflow = ''; }, 300);
  };
  document.querySelectorAll('[data-close-cart]').forEach(el => el.addEventListener('click', closeCart));
  cartOverlay?.addEventListener('click', closeCart);

  // ─── Quantity stepper ───
  document.querySelectorAll('.qty-stepper').forEach(group => {
    const input = group.querySelector('.qty-input');
    const minus = group.querySelector('.qty-minus');
    const plus = group.querySelector('.qty-plus');
    if (minus) minus.addEventListener('click', () => {
      const v = parseInt(input.value) - 1;
      if (v >= parseInt(input.min || 1)) input.value = v;
    });
    if (plus) plus.addEventListener('click', () => {
      const v = parseInt(input.value) + 1;
      if (v <= parseInt(input.max || 999)) input.value = v;
    });
  });

  // ─── Smooth scroll for anchor links ───
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ─── Sticky header shadow on scroll ───
  const header = document.querySelector('.site-header');
  if (header) {
    window.addEventListener('scroll', () => {
      header.classList.toggle('shadow-lg', window.scrollY > 20);
      header.classList.toggle('bg-opacity-95', window.scrollY > 20);
    });
  }

  // ─── Star rating hover (review form) ───
  document.querySelectorAll('.star-rating-input .star').forEach(star => {
    star.addEventListener('mouseenter', function() {
      const val = parseInt(this.dataset.value);
      this.closest('.star-rating-input').querySelectorAll('.star').forEach(s => {
        s.classList.toggle('text-yellow-400', parseInt(s.dataset.value) <= val);
        s.classList.toggle('text-gray-300', parseInt(s.dataset.value) > val);
      });
    });
    star.addEventListener('click', function() {
      const input = this.closest('.star-rating-input').querySelector('input[type="hidden"]');
      if (input) input.value = this.dataset.value;
    });
    star.closest('.star-rating-input')?.addEventListener('mouseleave', function() {
      const val = parseInt(this.querySelector('input[type="hidden"]')?.value || 0);
      this.querySelectorAll('.star').forEach(s => {
        s.classList.toggle('text-yellow-400', parseInt(s.dataset.value) <= val);
        s.classList.toggle('text-gray-300', parseInt(s.dataset.value) > val);
      });
    });
  });

  // ─── Add to cart success animation ───
  document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      const form = this.closest('form');
      if (!form) return;
      e.preventDefault();
      const btnText = this.querySelector('.btn-text');
      const original = btnText ? btnText.textContent : 'Add to Cart';
      if (btnText) btnText.textContent = 'Added ✓';
      this.classList.add('bg-green-500', 'border-green-500');
      setTimeout(() => {
        if (btnText) btnText.textContent = original;
        this.classList.remove('bg-green-500', 'border-green-500');
        form.submit();
      }, 600);
    });
  });
});
