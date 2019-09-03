import path from 'path';

module.exports = {
  lintOnSave: true,
  publicPath: '/static/',
  resolve: {
    alias : {
      'icons': path.resolve('@/node_modules/vue-material-design-icons')
    }
  }
};
