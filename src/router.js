// Adding anchor hashtag support is bit wonky
// https://github.com/vuejs/vue-router/issues/1668#issuecomment-443079797
import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '@/components/home'
import Notes from '@/components/notes'
Vue.use(VueRouter)

export default new VueRouter({
  routes: [
    {path:'/', component:Home},
    {path:'/notes', component:Notes}
  ],
  scrollBehavior() {
    return {x:0, y:0}
  },
})
