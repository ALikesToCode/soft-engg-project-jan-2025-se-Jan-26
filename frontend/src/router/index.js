import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import userRoutes from './userRoutes';
import facultyRoutes from './facultyRoutes';
import supportRoutes from './supportRoutes';
import { authService } from '@/api/authService'
import useAuthStore from '@/stores/useAuthStore'
import { ROLE } from '@/AppConstants/globalConstants'

// Import support routes
import SupportDashboard from '../views/support/SupportDashboard.vue';
import NotificationsView from '../views/support/NotificationsView.vue';
import ProfilePage from '../views/support/ProfilePage.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: {
      title: 'Home | Cognitum',
      hideUserNavbar: true
    }
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('../views/AboutView.vue'),
    meta: {
      title: 'About | Cognitum',
      hideUserNavbar: true
    }
  },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('../views/ContactView.vue'),
    meta: {
      title: 'Contact | Cognitum',
      hideUserNavbar: true
    }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: {
      title: 'Login | Cognitum',
      hideUserNavbar: true
    }
  },
  {
    path: '/auth/callback',
    name: 'auth-callback',
    component: () => import('../views/AuthCallback.vue'),
    meta: {
      title: 'Authentication | Cognitum',
      hideUserNavbar: true
    }
  },
  {
    path: '/faq',
    name: 'faq',
    component: () => import('../views/FAQView.vue'),
    meta: {
      title: 'FAQ | Cognitum',
      hideUserNavbar: true
    }
  },
  {
    path: '/privacy-policy',
    name: 'privacy',
    component: () => import('../views/PrivacyView.vue'),
    meta: {
      title: 'Privacy Policy | Cognitum',
      hideUserNavbar: true
    }
  },
  {
    path: '/terms-of-service',
    name: 'terms',
    component: () => import('../views/TermsView.vue'),
    meta: {
      title: 'Terms of Service | Cognitum',
      hideUserNavbar: true
    }
  },
  { ...userRoutes },
  { ...facultyRoutes },
  { ...supportRoutes },

  // Support routes
  {
    path: '/support',
    name: 'support',
    component: SupportDashboard,
    meta: { requiresAuth: true, role: 'support' }
  },
  {
    path: '/support/notifications',
    name: 'support-notifications',
    component: NotificationsView,
    meta: { requiresAuth: true, role: 'support' }
  },
  {
    path: '/support/profile',
    name: 'support-profile',
    component: ProfilePage,
    meta: { requiresAuth: true, role: 'support' }
  },

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

// Navigation guard to handle role switching based on URL
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isDevelopment = import.meta.env.VITE_NODE_ENV === 'development'

  if (isDevelopment) {
    // Extract role from URL path
    const path = to.path
    if (path.startsWith('/user/')) {
      authStore.switchRole(ROLE.STUDENT)
    } else if (path.startsWith('/faculty/')) {
      authStore.switchRole(ROLE.FACULTY)
    } else if (path.startsWith('/support/')) {
      authStore.switchRole(ROLE.SUPPORT)
    }
  }

  next()
})

export default router
