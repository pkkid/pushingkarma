import Vue from 'vue';
import store from './store';
import router from './router';
import axios from 'axios';
import {fixScroll} from '@/utils/plugins';
import App from './App.vue';
import '@/utils/filters';
require('@/assets/css/index.scss');

// Initialize General Vue Components
import vPortal from 'portal-vue'; Vue.use(vPortal);
import vHotkey from 'v-hotkey'; Vue.use(vHotkey);
import vClickOutside from 'v-click-outside'; Vue.use(vClickOutside);

// Initialize Buefy Components
import bButton from 'buefy/dist/components/button'; Vue.use(bButton);
import bDropdown from 'buefy/dist/components/dropdown'; Vue.use(bDropdown);
import bField from 'buefy/dist/components/field'; Vue.use(bField);
import bIcon from 'buefy/dist/components/icon'; Vue.use(bIcon);
import bInput from 'buefy/dist/components/input'; Vue.use(bInput);
import bModal from 'buefy/dist/components/modal'; Vue.use(bModal);
import bTable from 'buefy/dist/components/table'; Vue.use(bTable);

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

// Setup Vue
Vue.config.productionTip = false;
//Vue.config.silent = true;
new Vue({
  mixins: [fixScroll],
  render: h => h(App),
  router: router,
  store: store,
}).$mount('#app');
