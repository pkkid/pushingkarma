module.exports = {
  lintOnSave: true,
  outputDir: 'pk/_vue',
  assetsDir: 'pushingkarma',
  publicPath: '/static/',
  runtimeCompiler: true,
  pluginOptions: {sourceDir: 'vue'},
  css: {loaderOptions: {sass: {data: `@import "@/assets/css/__variables.scss";`}}},
  chainWebpack: config => { config.plugins.delete("hmr"); },
  configureWebpack: {
    performance: {
      maxEntrypointSize: 1024000,
      maxAssetSize: 1024000
    }
  }
};
