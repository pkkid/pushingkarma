module.exports = {
  lintOnSave: true,
  outputDir: 'vue/dist',
  configureWebpack: {
    resolve: {alias: {'@': 'vue/src'}},
    entry: {app: './vue/src/main.js'}
  }
}
