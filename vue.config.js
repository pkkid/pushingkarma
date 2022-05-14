const {BundleAnalyzerPlugin} = require('webpack-bundle-analyzer');

module.exports = {
  lintOnSave: true,             // Enabled https://cli.vuejs.org/config/#lintonsave
  outputDir: 'pk/_dist',        // Save distribution files to pk dir
  assetsDir: 'pushingkarma',    // Put frontend assets into a pushingkarma dir
  publicPath: '/static/',       // Assets will be served at /static/
  runtimeCompiler: true,        // Enable using templates in javascript files
  css: {loaderOptions: {        // All components get variables by default
    sass: {additionalData: `@import "@/assets/css/_variables.scss";`}
  }},    
  configureWebpack: {
    plugins: [
      // Visualize size of output files in treemap
      new BundleAnalyzerPlugin({
        analyzerMode: 'static',
        generateStatsFile: false,
        logLevel: 'silent',
        openAnalyzer: false,
        statsOptions: {source: false}
      }),
    ],
    // Remove warnings for large js files large
    performance: {
      maxEntrypointSize: 5000000,
      maxAssetSize: 5000000
    }
  }
};
