$(document).ready(function () {
  $(document).on('click', '.action-button', function (e) {
    e.preventDefault();

    const $btn = $(this);
    const action = $btn.data('action'); // 'add', 'edit', 'delete'
    const url = $btn.data('url');       // ссылка на view

    if (!action || !url) {
      console.warn('Missing data-action, data-url, or data-target on element:', this);
      return;
    }

    $.get(url, function (data) {
      $('body').after(data);
      if (action === 'delete') {
        const name = $btn.data('name') || '';
        $('#' + action + ' .form').attr('action', url);
     }
      $('#'+ action).modal('show');
    });
  });
});