import Vue from 'vue';
import axios from 'axios';
import store from './store';
import router from './router';
import PortalVue from 'portal-vue';
import {fixScroll} from './pk/plugins';
import App from './App.vue';
import Cookie from "js-cookie";
import './pk/filters';

Vue.use(PortalVue);
Vue.config.productionTip = false;
axios.defaults.headers.common['X-CSRFToken'] = Cookie.get('csrftoken');

new Vue({
  mixins: [fixScroll],
  render: h => h(App),
  router: router,
  store: store,
}).$mount('#app');
