import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import userRoutes from './userRoutes';
import facultyRoutes from './facultyRoutes';
import supportRoutes from './supportRoutes';
import { authService } from '@/api/authService'
import useAuthStore from '@/stores/useAuthStore'
import { ROLE } from '@/AppConstants/globalConstants'
import rolePaths from '@/AppConstants/rolePaths'
import LoginView from '../views/LoginView.vue'
import AuthCallback from '../views/AuthCallback.vue'

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
    component: LoginView,
    meta: {
      title: 'Login | Cognitum',
      hideUserNavbar: true
    }
  },
  {
    path: '/auth/callback',
    name: 'auth-callback',
    component: AuthCallback,
    meta: {
      title: 'Authentication | Cognitum',
      hideUserNavbar: true
    }
  },
  {
    path: '/set-password',
    name: 'set-password',
    component: () => import('../views/SetPasswordView.vue'),
    meta: { 
      title: 'Set Password | Cognitum', 
      requiresAuth: true 
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
  // Skip auth check for public routes or the auth callback route
  if (to.path === '/auth/callback' || to.path === '/login' || to.path === '/' || 
      to.path === '/about' || to.path === '/contact' || to.path === '/faq' || 
      to.path === '/privacy-policy' || to.path === '/terms-of-service') {
    next();
    return;
  }

  console.log(`Navigation guard: checking auth for route ${to.fullPath}`);
  
  // Store the intended path if user needs to authenticate
  if (to.meta.requiresAuth || to.path.startsWith('/support') || 
      to.path.startsWith('/user') || to.path.startsWith('/faculty')) {
    localStorage.setItem('loginRedirectPath', to.fullPath);
  }

  try {
    const isAuthenticated = await authService.isAuthenticated();
    console.log(`Auth check: authenticated = ${isAuthenticated}`);
    
    if (!isAuthenticated) {
      // Not authenticated, redirect to login
      console.log('Not authenticated, redirecting to login');
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      });
      return;
    }
    
    // User is authenticated, now check for role-specific paths
    const authStore = useAuthStore();
    const userRole = authStore.userRole;
    
    // Log actual role for debugging
    console.log(`ROUTER GUARD: User Role = "${userRole}", ROLE.FACULTY = "${ROLE.FACULTY}", ROLE.SUPPORT = "${ROLE.SUPPORT}"`);
    console.log(`Role comparison: userRole === ROLE.SUPPORT is ${userRole === ROLE.SUPPORT}`);
    console.log(`Role comparison: userRole === ROLE.FACULTY is ${userRole === ROLE.FACULTY}`);
    
    // Handle role-specific paths
    if (to.path.startsWith('/support') && userRole !== ROLE.SUPPORT) {
      console.log('Attempting to access support route without support role');
      next({ path: rolePaths.STUDENT.dashboard });
      return;
    }
    
    if (to.path.startsWith('/faculty') && userRole !== ROLE.FACULTY) {
      console.log('Attempting to access faculty route without faculty role');
      next({ path: rolePaths.STUDENT.dashboard });
      return;
    }
    
    if (to.path.startsWith('/user') && userRole === ROLE.SUPPORT) {
      console.log('Support user attempting to access student route');
      next({ path: rolePaths.SUPPORT.dashboard });
      return;
    }
    
    if (to.path.startsWith('/user') && userRole === ROLE.FACULTY) {
      console.log('Faculty user attempting to access student route');
      next({ path: rolePaths.FACULTY.dashboard });
      return;
    }
    
    // Check for role requirements if specified in meta
    if (to.meta.role) {
      const hasRequiredRole = authService.hasRole(to.meta.role);
      console.log(`Role check for ${to.meta.role}: ${hasRequiredRole}`);
      
      if (!hasRequiredRole) {
        // Redirect to appropriate dashboard based on actual role
        console.log('User does not have required role, redirecting to dashboard');
        if (userRole === ROLE.SUPPORT) {
          next({ path: rolePaths.SUPPORT.dashboard });
        } else if (userRole === ROLE.FACULTY) {
          next({ path: rolePaths.FACULTY.dashboard });
        } else {
          next({ path: rolePaths.STUDENT.dashboard });
        }
        return;
      }
    }
    
    // User is authenticated and has proper role access
    next();
  } catch (error) {
    console.error('Error in navigation guard:', error);
    next('/login');
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
