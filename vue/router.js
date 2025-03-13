import {createRouter, createWebHistory} from 'vue-router'
import HomeView from '@/views/Home.vue'

const router = createRouter({
  mode: 'history',
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {path:'/', name:'home', component:HomeView},
    {path:'/notes', name:'notes', component: () => import('@/views/notes/Notes.vue')},
    {path:'/budget', name:'budget', component: () => import('@/views/budget/Budget.vue')},
    {path:'/stocks', name:'stocks', component: () => import('@/views/stocks/Stocks.vue')},
    {path:'/newtab', name:'newtab', component: () => import('@/views/NewTab.vue')},
  ],
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      var top = document.getElementById(to.hash.substring(1)).offsetTop
      return {top:top, left:0, behavior:'smooth'}
    } else {
      return {top:0, left:0, behavior:'smooth'}
    }
  },
})

export default router
