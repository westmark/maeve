!function($) {
  mv.character = (function() {
    return new function() {

      var self        = this;

      this.init = function() {
        self.updateTransactions();
      };

      this.updateTransactions = function() {
        var ajaxOpts = {
          url: '/stat/transactions',
          type: 'GET',
          data: {
            'char': mv.data.character.id
          },
          dataType: 'JSON'
        };

        jQuery.ajax(ajaxOpts).done(function(jsonData) {
          var view = {
                transactions: jsonData
              },
              $output = $($.mustache(mv.templates.transactionTable, view)),
              $target = $('#transactions');

            $target.empty().append($output);
        });
      };
    }
  })();

  mv.modules.push(mv.character);

}(jQuery);
