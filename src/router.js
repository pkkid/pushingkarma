// Adding anchor hashtag support is bit wonky
// https://github.com/vuejs/vue-router/issues/1668#issuecomment-443079797
import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from '@/components/home/Home';
import Notes from '@/components/notes/Notes';
import Budget from '@/components/budget/Budget';
import NewTab from '@/components/newtab/NewTab';
import NotFound from '@/components/site/NotFound';
Vue.use(VueRouter);

export default new VueRouter({
  mode: 'history',
  routes: [
    {path:'/', component:Home},
    {path:'/notes', component:Notes},
    {path:'/budget', component:Budget},
    {path:'/newtab', component:NewTab},
    {path: '*', component:NotFound}
  ]
});
