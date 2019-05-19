module.exports = {
  lintOnSave: true,
  publicPath: '/static/',
  outputDir: 'vue/dist',
  configureWebpack: {
    resolve: {alias: {'@': 'vue/src'}},
    entry: {app: './vue/src/main.js'}
  }
}
