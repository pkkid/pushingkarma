// Adding anchor hashtag support is bit wonky
// https://github.com/vuejs/vue-router/issues/1668#issuecomment-443079797
import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from '@/components/home/Home';
import Notes from '@/components/notes/Notes';
import NotFound from '@/components/NotFound';
Vue.use(VueRouter);

export default new VueRouter({
  mode: 'history',
  //scrollBehavior() { return {x:0, y:0}; },
  routes: [
    {path:'/', component:Home},
    {path:'/notes', component:Notes},
    {path: '*', component:NotFound}
  ]
});
