import axios from 'axios';
import Vue from 'vue';
import store from './store';
import router from './router';
import PortalVue from 'portal-vue';
import VueHotkey from 'v-hotkey';
import vClickOutside from 'v-click-outside';
import {fixScroll} from './utils/plugins';
import App from './App.vue';
import './utils/filters';

// Tell Axios we want to treat any non-json responses as errors
// as well as any responses containing the key 'errors'
axios.interceptors.response.use(function(response) {
  if (response.headers['content-type'] != 'application/json') { return Promise.reject(response); }
  else if (response.data.errors !== undefined) { return Promise.reject(response); }
  else { return response; }
});

// Setup Vue plugins and configuration
Vue.use(PortalVue);
Vue.use(VueHotkey);
Vue.use(vClickOutside);
Vue.config.productionTip = false;

new Vue({
  mixins: [fixScroll],
  render: h => h(App),
  router: router,
  store: store,
}).$mount('#app');
