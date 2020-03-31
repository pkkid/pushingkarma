var plugins = [];

// Visualize size of output files in treemap
// const {BundleAnalyzerPlugin} = require('webpack-bundle-analyzer');
// plugins.push(new BundleAnalyzerPlugin({
//   analyzerMode: 'server',
//   generateStatsFile: true,
//   statsOptions: {source: false}
// }));

module.exports = {
  lintOnSave: true,             // Enabled https://cli.vuejs.org/config/#lintonsave
  outputDir: 'pk/_dist',        // Save distribution files to pk dir
  assetsDir: 'pushingkarma',    // Put frontend assets into a pushingkarma dir
  publicPath: '/static/',       // Assets will be served at /static/
  runtimeCompiler: true,        // Enable using templates in javascript files
  css: {loaderOptions: {        // All components get variables by default
    sass: {data: `@import "@/assets/css/_variables.scss";`}
  }},    
  configureWebpack: {
    plugins: plugins,           // Plugins defined above
    performance: {              // Remove warnings for large js files large
      maxEntrypointSize: 1024000,
      maxAssetSize: 1024000
    }}
};
