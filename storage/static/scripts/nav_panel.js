    $(document).ready(function(){
      const offcanvasEl = document.getElementById('sidebarOffcanvas');
      const menuToggle = document.getElementById('menuToggle');
      if (!offcanvasEl || !menuToggle) return;

      const bsOffcanvas = new bootstrap.Offcanvas(offcanvasEl);
      let isOpen = false;

      menuToggle.addEventListener('click', function(){
        if (isOpen) { bsOffcanvas.hide(); } else { bsOffcanvas.show(); }
      });

      offcanvasEl.addEventListener('shown.bs.offcanvas', function(){
        isOpen = true;
        menuToggle.classList.add('offcanvas-open','open');
        menuToggle.setAttribute('aria-expanded','true');
      });
      offcanvasEl.addEventListener('hidden.bs.offcanvas', function(){
        isOpen = false;
        menuToggle.classList.remove('offcanvas-open','open');
        menuToggle.setAttribute('aria-expanded','false');
      });

      document.querySelectorAll('.submenu-header').forEach(function(header){
        const targetSelector = header.getAttribute('data-target');
        const btn = header.querySelector('.btn-toggle');
        const icon = btn.querySelector('.fa');
        if (!targetSelector || !btn || !icon) return;
        const target = document.querySelector(targetSelector);
        if (!target) return;

        const collapse = new bootstrap.Collapse(target, { toggle: false });

        const setAria = () => {
          const expanded = target.classList.contains('show');
          header.setAttribute('aria-expanded', expanded ? 'true' : 'false');
          if (expanded) icon.classList.add('rotate-up'); else icon.classList.remove('rotate-up');
        };

        setAria();
        target.addEventListener('shown.bs.collapse', setAria);
        target.addEventListener('hidden.bs.collapse', setAria);

        header.addEventListener('click', function(e){
          if (!e.target.closest('a')) {
            collapse.toggle();
          }
        });
      });

      $(document).on('click', '#report-button', function (e) {
        e.preventDefault();

        const $btn = $(this);
        const url = $btn.data('url'); // view link
        const modal_id = $btn.data('modal-id'); // modal window id

        $.get(url, function (data) {
          $('body').append(data);
          $('#'+ modal_id).modal('show');
        });
      });

    });