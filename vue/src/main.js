import Vue from 'vue'
import App from './App.vue'
import VueRouter from 'vue-router'
import router from './router'

Vue.config.productionTip = false;
Vue.use(VueRouter);

const fixScroll = {
  watch: {
    $route(to, from) {
      const currentRoute = this.$router.currentRoute;
      const idToScrollTo = currentRoute.hash;
      this.$nextTick(() => {
        if (idToScrollTo && document.querySelector(idToScrollTo)) {
          document.querySelector(idToScrollTo).scrollIntoView();
        }
      });
    },
  },
};

new Vue({
  mixins: [fixScroll],
  render: h => h(App),
  router,
}).$mount('#app');
