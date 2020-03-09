// Adding anchor hashtag support is bit wonky
// https://github.com/vuejs/vue-router/issues/1668#issuecomment-443079797
import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from '@/components/home/Home';
import NewTab from '@/components/newtab/NewTab';
import NotFound from '@/components/site/NotFound';
Vue.use(VueRouter);

// Dynamically importing router modules this way hints to Webpack that we want
// to split the generated JavaScript files by each chunk name specified.
// https://vuedose.tips/tips/dynamic-imports-in-vue-js-for-better-performance/
const Notes = () => import(/* webpackChunkName: "notes" */'@/components/notes/Notes');
const Budget = () => import(/* webpackChunkName: "budget" */'@/components/budget/Budget');


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
