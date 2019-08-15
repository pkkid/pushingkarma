import Vue from 'vue'
import axios from 'axios'
import store from './store'
import router from './router'
import App from './App.vue'
import Cookie from "js-cookie"

Vue.config.productionTip = false
axios.defaults.headers.common['X-CSRFToken'] = Cookie.get('csrftoken')

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
