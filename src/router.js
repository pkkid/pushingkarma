// Adding anchor hashtag support is bit wonky
// https://github.com/vuejs/vue-router/issues/1668#issuecomment-443079797
import Budget from '@/components/budget/Budget';
import Home from '@/components/home/Home';
import NewTab from '@/components/newtab/NewTab';
import Notes from '@/components/notes/Notes';
import NotFound from '@/components/site/NotFound';
import Privacy from '@/components/site/Privacy';
import Vue from 'vue';
import VueRouter from 'vue-router';
Vue.use(VueRouter);

export default new VueRouter({
  mode: 'history',
  routes: [
    {path:'/', component:Home},
    {path:'/notes', component:Notes},
    {path:'/budget', component:Budget},
    {path:'/newtab', component:NewTab},
    {path:'/privacy', component:Privacy},
    {path: '*', component:NotFound}
  ]
});
