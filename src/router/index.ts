import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../pages/Dashboard.vue'),
  },
  {
    path: '/trends',
    name: 'Trends',
    component: () => import('../pages/Trends.vue'),
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../pages/Users.vue'),
  },
  {
    path: '/content',
    name: 'Content',
    component: () => import('../pages/Content.vue'),
  },
  {
    path: '/data-table',
    name: 'DataTable',
    component: () => import('../pages/DataTable.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
