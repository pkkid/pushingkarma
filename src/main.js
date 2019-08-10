import App from './App.vue'
import Vue from 'vue'
import router from './router'
import store from './store'

Vue.config.productionTip = false

const fixScroll = {
  watch: {
    $route() {
      const currentRoute = this.$router.currentRoute
      const idToScrollTo = currentRoute.hash
      this.$nextTick(() => {
        if (idToScrollTo && document.querySelector(idToScrollTo)) {
          document.querySelector(idToScrollTo).scrollIntoView()
        }
      })
    },
  },
}

new Vue({
  mixins: [fixScroll],
  render: h => h(App),
  router: router,
  store: store,
}).$mount('#app')
