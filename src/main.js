/* global globals */
import Vue from 'vue';
import store from './store';
import router from './router';
import PortalVue from 'portal-vue';
import {fixScroll} from './utils/plugins';
import App from './App.vue';
import './utils/filters';

Vue.use(PortalVue);
Vue.config.productionTip = false;

new Vue({
  mixins: [fixScroll],
  render: h => h(App),
  router: router,
  store: store,
}).$mount('#app');
