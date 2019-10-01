module.exports = {
  lintOnSave: true,
  publicPath: '/static/',
  runtimeCompiler: true,
  css: {loaderOptions: {sass: {data: `
    @import "@/assets/css/layout.scss";
    @import "@/assets/css/parallax.scss";
  `}}},
  chainWebpack: config => { config.plugins.delete("hmr"); },
};
