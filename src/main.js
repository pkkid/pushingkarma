import Vue from 'vue';
import store from './store';
import router from './router';
import axios from 'axios';
import vPortal from 'portal-vue';
import vHotkey from 'v-hotkey';
import vClickOutside from 'v-click-outside';
import {fixScroll} from './utils/vue-plugins';
import App from './App.vue';
import './utils/vue-filters';
require('@/assets/css/index.scss');

// Tell Axios we want to treat any non-json responses as errors
// as well as any responses containing the key 'errors'
axios.interceptors.response.use(function(response) {
  if (response.headers['content-type'] != 'application/json') { return Promise.reject(response); }
  else if (response.data.errors !== undefined) { return Promise.reject(response); }
  else { return response; }
});

// Setup Vue plugins and configuration
Vue.use(vPortal);
Vue.use(vHotkey);
Vue.use(vClickOutside);
Vue.config.productionTip = false;

new Vue({
  mixins: [fixScroll],
  render: h => h(App),
  router: router,
  store: store,
}).$mount('#app');
