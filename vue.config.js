module.exports = {
  lintOnSave: true,
  mode: 'production',
  publicPath: '/static/',
  runtimeCompiler: true,
  css: {loaderOptions: {sass: {data: `
    @import "@/assets/css/__variables.scss";
  `}}},
  chainWebpack: config => { config.plugins.delete("hmr"); },
};
