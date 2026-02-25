$('document').ready(function () {
    //function for automatically hide bootstrap alert messages
    setTimeout(function () {
        $('.alert').alert('close');
    }, 2000);
    //function for clean filter button
    //function for clean filter button
    $('.filter-clear-button').on('click', function(e) {
      console.log('reset button clicked')
      console.log($('#filter-form')[0])
      $('#filter-form')[0].reset();
      //$('.filter-form').submit();
    });
});