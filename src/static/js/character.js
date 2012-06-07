!function($) {
  mv.character = (function() {
    return new function() {

      var self        = this,
          dom         = {},
          callbacks   = {},
          typeaheadTimer = null;

      this.init = function() {
        mv.data.character.items = {};
      };

      this.initDashboard = function() {
        self.updateTransactions($('#transactions > .content'));
      };

      this.initTransactions = function() {
        self.updateTransactions($('.sell-transactions'), { 'transaction_type': 'sell' });
        self.updateTransactions($('.buy-transactions'), { 'transaction_type': 'buy' });

      };

      this.initAnalysis = function() {
        dom.analysisContainer = $('#analysis-container');
        dom.analysisForm = dom.analysisContainer.find('#form-analysis');
        dom.analysisFormSubmitButton = dom.analysisForm.find('button');
        dom.analysisFormNameInput = dom.analysisForm.find('[name=commodityname]');

        dom.analysisFormSubmitButton.attr('disabled', true);

        dom.analysisForm.on('submit', callbacks.analysisFormSubmit);
        dom.analysisFormSubmitButton.on('click', callbacks.analysisFormSubmit);

        dom.analysisContainer.on('submit', '#form-mean-price', callbacks.analysisMeanFormSubmit).on('click', '#form-mean-price button', callbacks.analysisMeanFormSubmit);

        dom.analysisFormNameInput.on('change', callbacks.commodityNameChange).typeahead({
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
        if(typeaheadTimer) {
          clearTimeout(typeaheadTimer);
        }
        typeaheadTimer = setTimeout(function() {
          typeaheadTimer = null;
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
              mv.data.character.items[c[1]] = c[0];
            })
            process(source);
          });
        }, 250);
      };

      this.updateMeanValues = function(data, $target) {
        var tmplData = {
            mean: data.mean,
            median:  data.median,
            itemName: data.item_name,
            nrOfTransactions: data.prices.length,
            transactionTypeName: data.transaction_type_name
          },
          $output = $($.mustache(mv.templates.itemPriceAnalysisTable, tmplData));

        dom.analysisContainer.find('.mean-content').empty().append($output);
      };

      this.fetchCommodityAnalysis = function() {
        var commodityId = mv.data.character.items[dom.analysisFormNameInput.val()]
            data = {
              'type_id': commodityId,
              'char': mv.data.character.id
            };

        dom.analysisContainer.find('> .progress').show();
        mv.data.currentCommodityId = commodityId;

        $.ajax({
          url: dom.analysisForm.attr('action'),
          type: dom.analysisForm.attr('method'),
          data: data
        }).done(function(response) {
          dom.analysisContainer.find('.content').html(response);
        });
      };

      this.fetchMeanPrices = function($target, transactionType) {
        var $form = $('#form-mean-price'),
            data = {};

        if(mv.data.currentCommodityId) {
          $form.find('.progress').show();

          data.quantity = $form.find('[name=quantity]').val();
          data.transaction_type = transactionType || $form.find('[name=transactiontype]').val();
          data['char'] = mv.data.character.id;
          data.type_id = mv.data.currentCommodityId;

          $.ajax({
            url: $form.attr('action'),
            type: $form.attr('method'),
            data: data,
            dataType: 'JSON'
          }).done(function(response) {
            if(response.prices) {
              self.updateMeanValues(response, $target);
            }
          }).always(function() {
            $form.find('.progress').hide();
          });
        }

      };

      callbacks.commodityNameChange = function(e) {
        var $input = $(this),
            commodity = mv.data.character.items[$input.val()];

        dom.analysisFormSubmitButton.attr('disabled', !(commodity));
      };

      callbacks.analysisFormSubmit = function(e) {
        try {
          self.fetchCommodityAnalysis();
        } catch(err) {

        }
        e.preventDefault();
        e.stopPropagation();
        return false;
      };

      callbacks.analysisMeanFormSubmit = function(e) {
        var transactionType,
            $target;

        try {
          transactionType = parseInt(dom.analysisContainer.find('[name=transactiontype]').val(), 10);
          if(transactionType == 0) {

          }
          else {
            self.fetchMeanPrices(dom.analysisContainer.find('.mean-content'));
          }
        } catch(err) {

        }
        e.preventDefault();
        e.stopPropagation();
        return false;
      };
    }
  })();

  mv.modules.push(mv.character);

}(jQuery);
