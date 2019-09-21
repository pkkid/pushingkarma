module.exports = {
  lintOnSave: true,
  publicPath: '/static/',
  css: {loaderOptions: {sass: {data: `
    @import "@/assets/css/layout.scss";
    @import "@/assets/css/parallax.scss";
  `}}}
};
