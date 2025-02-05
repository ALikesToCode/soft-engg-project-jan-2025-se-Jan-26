import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import userRoutes from './userRoutes';
import facultyRoutes from './facultyRoutes';
import supportRoutes from './supportRoutes';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: {
      title: 'SE | IIT Madras'
    }
  },
  {
    path: '/login',
    name: 'about',
    component: () => import('../views/LoginView.vue'),
    meta: {
      title: 'Login'
    }
  },
  { ...userRoutes },
  { ...facultyRoutes },
  { ...supportRoutes },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})
router.beforeEach(async (to, from, next) => {
  document.title = `${to.meta.title}`;
  next();
})
export default router
