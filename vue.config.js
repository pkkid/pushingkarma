module.exports = {
  lintOnSave: true,
  publicPath: '/static/',
  outputDir: 'vue/dist',
  pages: {
    index: {
      entry: 'vue/src/main.js',
      template: 'vue/public/index.html'
    }
  },
  configureWebpack: {
    resolve: {alias: {'@': 'vue/src'}},
    entry: {app: './vue/src/main.js'}
  }
}
