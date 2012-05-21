var mv = {
  data: {},
  modules: []
};


!function($) {
  mv.main = (function() {
    return new function() {

      var self        = this;

      this.init = function() {
        _.each(mv.modules, function(mod) {
          mod.init();
        })
      }
    }
  })();

  $(document).ready(function() {
    mv.main.init();
  });

}(jQuery);
