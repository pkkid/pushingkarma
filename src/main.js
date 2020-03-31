import Vue from 'vue';
import store from './store';
import router from './router';
import axios from 'axios';
import vPortal from 'portal-vue';
import vHotkey from 'v-hotkey';
import vClickOutside from 'v-click-outside';
import {fixScroll} from '@/utils/plugins';
import App from './App.vue';
import Buefy from 'buefy';
import '@/utils/filters';
require('@/assets/css/index.scss');

// Axios Configuiration - Tell Axios we want to include the csrf token and
// where to get the value. The intercepter is a convenience function to
// globally catch and respond to errors.
var urlparams = new URLSearchParams(window.location.search);
axios.defaults.withCredentials = true;
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';
if (urlparams.get('apikey')) {
  axios.defaults.headers.common.Authorization = `Token ${urlparams.get('apikey')}`;
}
axios.interceptors.response.use(function(response) {
  if (response.headers['content-type'] != 'application/json') { return Promise.reject(response); }
  if (response.data && response.data.errors && response.data.errors.length > 0) { return Promise.reject(response); }
  if (response.data && response.data.detail && response.data.detail.length > 0) { return Promise.reject(response); }
  return response;
});

// Setup Vue plugins and configuration
Vue.use(Buefy);
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
