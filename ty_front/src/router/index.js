import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '../auth'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import SearchView from '../views/SearchView.vue'
import TopologyView from '../views/TopologyView.vue'

const routes = [
  { path: '/', redirect: () => (isAuthenticated() ? '/search' : '/login') },
  { path: '/login', component: LoginView, meta: { guestOnly: true } },
  
  // 具体的路由映射
  { path: '/dashboard', component: DashboardView, meta: { requiresAuth: true } },
  { path: '/search', component: SearchView, meta: { requiresAuth: true } },
  { path: '/topology', component: TopologyView, meta: { requiresAuth: true } }
]

const router = createRouter({
  // 使用 HTML5 的历史记录模式，地址栏不会有难看的 "#" 号
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authed = isAuthenticated()

  if (to.meta.requiresAuth && !authed) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.guestOnly && authed) {
    next('/search')
    return
  }

  next()
})

export default router