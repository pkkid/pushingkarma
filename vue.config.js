module.exports = {
  lintOnSave: true,             // Enabled https://cli.vuejs.org/config/#lintonsave
  outputDir: 'pk/_dist',        // Save distribution files to pk dir
  assetsDir: 'pushingkarma',    // Put frontend assets into a pushingkarma dir
  publicPath: '/static/',       // Assets will be served at /static/
  runtimeCompiler: true,        // Enable using templates in javascript files
  css: {loaderOptions: {sass: {data: `@import "@/assets/css/__variables.scss";`}}},   // All components get variables by default
  //chainWebpack: config => { config.plugins.delete("hmr"); },                        // Disable hot-reload plugin
  configureWebpack: {performance: {maxEntrypointSize:1024000, maxAssetSize:1024000}}  // Remove warnings for large js files large
};
