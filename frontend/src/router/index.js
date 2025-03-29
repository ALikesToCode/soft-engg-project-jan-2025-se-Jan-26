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

// Import monitoring components
import SystemHealth from '@/components/support/monitoring/SystemHealth.vue';
import PerformanceMetrics from '@/components/support/monitoring/PerformanceMetrics.vue';
import ErrorReporting from '@/components/support/monitoring/ErrorReporting.vue';

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

  // Explicit monitoring routes
  {
    path: '/monitoring/system-health',
    name: 'monitoring-system-health',
    component: SystemHealth,
    meta: { 
      requiresAuth: true, 
      role: 'support',
      title: 'System Health | Monitoring'
    }
  },
  {
    path: '/monitoring/performance',
    name: 'monitoring-performance',
    component: PerformanceMetrics,
    meta: { 
      requiresAuth: true, 
      role: 'support',
      title: 'Performance Metrics | Monitoring'
    }
  },
  {
    path: '/monitoring/errors',
    name: 'monitoring-errors',
    component: ErrorReporting,
    meta: { 
      requiresAuth: true, 
      role: 'support',
      title: 'Error Reporting | Monitoring'
    }
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
  // Special handling for support paths
  if (to.path.startsWith('/support')) {
    const isAuthenticated = await authService.isAuthenticated()
    const hasSupportRole = authService.hasSupportRole()
    
    if (!isAuthenticated) {
      // Not authenticated, redirect to login
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
    
    if (!hasSupportRole) {
      // Authenticated but not support role
      next({ path: '/dashboard' })
      return
    }
    
    // User is authenticated and has support role
    next()
    return
  }
  
  // Handle other routes with requiresAuth meta
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const isAuthenticated = await authService.isAuthenticated()
    if (!isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      // Check for role requirements if specified in meta
      if (to.meta.role && !authService.hasRole(to.meta.role)) {
        // User is authenticated but doesn't have the required role
        next({ path: '/dashboard' })
      } else {
        next()
      }
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
