import {createRouter, createWebHistory} from 'vue-router'
import HomeView from '@/views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {path:'/', name:'home', component:HomeView},
    {path:'/notes', name:'notes', component: () => import('@/views/Notes.vue')},
    {path:'/budget', name:'budget', component: () => import('@/views/Budget.vue')},
    {path:'/newtab', name:'newtab', component: () => import('@/views/NewTab.vue')},
  ]
})

export default router
