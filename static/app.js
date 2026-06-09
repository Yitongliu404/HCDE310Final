document.addEventListener('DOMContentLoaded', () => {

  const btn = document.querySelector('.find-btn');
  if (btn) {
    btn.addEventListener('click', function(e) {
      const rect = btn.getBoundingClientRect();
      const r = document.createElement('span');
      r.className = 'ripple';
      r.style.top  = (e.clientY - rect.top  - 3) + 'px';
      r.style.left = (e.clientX - rect.left - 3) + 'px';
      btn.appendChild(r);
      setTimeout(() => r.remove(), 520);
    });
  }

});