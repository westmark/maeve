!function($) {
  mv.character = (function() {
    return new function() {

      var self        = this,
          dom         = {},
          callbacks   = {};

      this.init = function() {
        mv.character.items = {};
      };

      this.initDashboard = function() {
        self.updateTransactions($('#transactions > .content'));
      };

      this.initTransactions = function() {
        dom.calculator = $('#calculator');
        dom.averageContainer = dom.calculator.find('#average-container');
        dom.averageForm = dom.calculator.find('#form-average');
        dom.averageFormSubmitButton = dom.averageForm.find('button');
        dom.averageFormNameInput = dom.averageForm.find('[name=commodity_name]');

        self.updateTransactions($('.sell-transactions'), { 'transaction_type': 'sell' });
        self.updateTransactions($('.buy-transactions'), { 'transaction_type': 'buy' });

        dom.averageFormSubmitButton.attr('disabled', true);

        dom.averageForm.on('submit', callbacks.averageFormSubmit);

        dom.averageFormNameInput.on('change', callbacks.commodityNameChange).typeahead({
          source: self.typeaheadCommodityName
        });

      };

      this.updateTransactions = function($target, filterData) {
        var data = {
            'char': mv.data.character.id
          },
          ajaxOpts = {
            url: '/stat/transactions',
            type: 'GET',
            data: data,
            dataType: 'JSON'
          };

        if(filterData) {
          data.filters = JSON.stringify(filterData);
        }

        jQuery.ajax(ajaxOpts).done(function(jsonData) {
          var view = {
                transactions: jsonData
              },
              $output = $($.mustache(mv.templates.transactionTable, view));

            $target.empty().append($output);
        });
      };

      this.typeaheadCommodityName = function(query, process) {
        $.ajax({
          url: '/stat/commodity/search',
          type: 'GET',
          data: {
            query: query
          },
          dataType: 'JSON'
        }).done(function(response) {
          var source = [];
          _.each(response.matches, function(c) {
            source.push(c[1]);
            mv.character.items[c[1]] = c[0];
          })
          process(source);
        })
      };

      callbacks.commodityNameChange = function(e) {
        var $input = $(this),
            commodity = mv.character.items[$input.val()];

        dom.averageFormSubmitButton.attr('disabled', !(commodity));
      };

      callbacks.averageFormSubmit = function(e) {
        var commodity = mv.character.items[dom.averageFormNameInput.val()];

        if(commodity) {
          dom.averageContainer.find('.progress').show();
        }
        e.preventDefault();
        return false;
      };
    }
  })();

  mv.modules.push(mv.character);

}(jQuery);
