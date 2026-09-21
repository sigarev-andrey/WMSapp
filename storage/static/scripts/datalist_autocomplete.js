function setupDatalistAutocomplete(config) {
  var $input = $(config.inputSelector);
  var $datalist = $(config.datalistSelector);
  var timer = null;
  var request = null;
  var minLength = config.minLength || 2;
  var delay = config.delay || 300;

  function clearOptions() {
    $datalist.empty();
  }

  function renderOptions(results) {
    clearOptions();
    (results || []).forEach(function(item) {
      var $option = $('<option>')
        .attr('value', item.label)
        .attr('data-value', item.id);

      if (item.count !== undefined) {
        $option.attr('data-count', item.count);
      }
      if (item.contract !== undefined) {
        $option.attr('data-contract', item.contract);
      }

      $option.appendTo($datalist);
    });
  }

  function collectParams(query) {
    var params = { q: query };
    if (typeof config.extraParams === 'function') {
      $.extend(params, config.extraParams());
    }
    return params;
  }

  function loadOptions(query) {
    if (request) {
      request.abort();
    }
    request = $.getJSON(config.url, collectParams(query))
      .done(function(data) {
        renderOptions(data.results);
        if (typeof config.onResultsLoaded === 'function') {
          config.onResultsLoaded();
        }
      });
  }

  $input.on('input', function() {
    var query = this.value.trim();
    clearTimeout(timer);
    if (query.length < minLength) {
      clearOptions();
      if (typeof config.onCleared === 'function') {
        config.onCleared();
      }
      return;
    }
    timer = setTimeout(function() {
      loadOptions(query);
    }, delay);
  });

  return {
    clear: clearOptions,
    findSelectedOption: function(value) {
      return $datalist.find('option').filter(function() {
        return this.value === value;
      }).first();
    },
    reload: function() {
      var query = $input.val().trim();
      if (query.length >= minLength) {
        loadOptions(query);
      }
    }
  };
}
