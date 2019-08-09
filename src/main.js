import Vue from 'vue'
import store from './store'
import router from './router'
import App from './App.vue'

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
