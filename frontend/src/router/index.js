import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import userRoutes from './userRoutes';
import facultyRoutes from './facultyRoutes';
import supportRoutes from './supportRoutes';
import { authService } from '@/api/authService'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: {
      title: 'Home | Cognitum'
    }
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('../views/AboutView.vue'),
    meta: {
      title: 'About | Cognitum'
    }
  },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('../views/ContactView.vue'),
    meta: {
      title: 'Contact | Cognitum'
    }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: {
      title: 'Login | Cognitum'
    }
  },
  {
    path: '/faq',
    name: 'faq',
    component: () => import('../views/FAQView.vue'),
    meta: {
      title: 'FAQ | Cognitum'
    }
  },
  {
    path: '/privacy-policy',
    name: 'privacy',
    component: () => import('../views/PrivacyView.vue'),
    meta: {
      title: 'Privacy Policy | Cognitum'
    }
  },
  {
    path: '/terms-of-service',
    name: 'terms',
    component: () => import('../views/TermsView.vue'),
    meta: {
      title: 'Terms of Service | Cognitum'
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
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Update document title based on route meta
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Cognitum'
  next()
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const isAuthenticated = await authService.isAuthenticated()
    if (!isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
