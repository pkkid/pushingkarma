import Vue from 'vue';
import store from './store';
import router from './router';
import PortalVue from 'portal-vue';
import VueHotkey from 'v-hotkey';
import {fixScroll} from './utils/plugins';
import App from './App.vue';
import './utils/filters';

Vue.use(PortalVue);
Vue.use(VueHotkey);
Vue.config.productionTip = false;

new Vue({
  mixins: [fixScroll],
  render: h => h(App),
  router: router,
  store: store,
}).$mount('#app');
