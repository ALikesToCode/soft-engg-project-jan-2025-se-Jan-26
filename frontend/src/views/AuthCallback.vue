<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-lg max-w-md w-full text-center">
      <span class="material-icons text-5xl text-maroon-600 animate-spin mb-4">refresh</span>
      <h1 class="text-2xl font-bold text-gray-800 mb-2">Authentication in progress...</h1>
      <p class="text-gray-600">Please wait while we complete your login.</p>
    </div>
  </div>
</template>

<script>
import { authService } from '@/api/authService'

export default {
  name: 'AuthCallback',
  async mounted() {
    try {
      // Process auth callback
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');
      const userRole = urlParams.get('user_role');
      
      if (token) {
        // Save auth data
        localStorage.setItem('token', token);
        
        // Save user role if available
        if (userRole) {
          localStorage.setItem('userRole', userRole.toUpperCase());
        }
        
        // Check for redirect path from localStorage
        const redirectPath = localStorage.getItem('loginRedirectPath');
        
        // Determine where to redirect the user
        let targetPath;
        
        if (redirectPath && redirectPath.includes('/monitoring') && userRole === 'support') {
          // If there's a redirect path to monitoring and user has support role, go there
          targetPath = redirectPath;
        } else {
          // Otherwise use default route based on role
          targetPath = userRole === 'support' ? '/support/dashboard' : '/dashboard';
        }
        
        // Clear stored redirect path
        localStorage.removeItem('loginRedirectPath');
        
        // Redirect user
        this.$router.push(targetPath);
      } else {
        // No token found, go to login
        this.$router.push('/login');
      }
    } catch (error) {
      console.error('Auth callback error:', error);
      this.$router.push('/login');
    }
  }
}
</script> 