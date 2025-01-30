import {createRouter, createWebHistory} from 'vue-router'
import HomeView from '@/views/Home.vue'

const router = createRouter({
  mode: 'history',
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {path:'/', name:'home', component:HomeView},
    {path:'/notes', name:'notes', component: () => import('@/views/Notes.vue')},
    {path:'/budget', name:'budget', component: () => import('@/views/Budget.vue')},
    {path:'/newtab', name:'newtab', component: () => import('@/views/NewTab.vue')},
  ],
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      return {el:to.hash, behavior:'smooth'}
    } else {
      return {top:0}
    }
  },
})

export default router
