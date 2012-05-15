var mv = {
  modules: []
};


!function($) {
  mv.main = !function() {
    return new function() {

      var self        = this;

      this.init = function() {
        _.each(mv.modules, function(mod) {
          mod.init();
        })
      }
    }
  }();
}(jQuery);
