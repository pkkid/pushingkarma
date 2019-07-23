// Adding anchor hashtag support is bit wonky
// https://github.com/vuejs/vue-router/issues/1668#issuecomment-443079797
import VueRouter from 'vue-router'
import Home from './components/Home.vue'
import Notes from './components/Notes.vue'

export default new VueRouter({
  routes: [
    {path:'/', component:Home},
    {path:'/notes', component:Notes}
  ],
  scrollBehavior() {
    return {x:0, y:0};
  },
});
