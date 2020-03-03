module.exports = {
  lintOnSave: true,
  publicPath: '/static/',
  runtimeCompiler: true,
  css: {loaderOptions: {sass: {data: `
    @import "@/assets/css/__variables.scss";
  `}}},
  chainWebpack: config => {
    config.plugins.delete("hmr");
  },
  configureWebpack: {
    performance: {
      maxEntrypointSize: 1024000,
      maxAssetSize: 1024000
    }
  }
};
