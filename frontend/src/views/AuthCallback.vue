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
import useAuthStore from '@/stores/useAuthStore'
import { ROLE } from '@/AppConstants/globalConstants'
import rolePaths from '@/AppConstants/rolePaths'

export default {
  name: 'AuthCallback',
  async mounted() {
    try {
      // Get auth store
      const authStore = useAuthStore();
      
      // Process auth callback
      const urlParams = new URLSearchParams(window.location.search);
      const access_token = urlParams.get('access_token');
      const user_role = urlParams.get('user_role');
      const password_needed = urlParams.get('password_needed') === 'true';
      
      console.log("Received callback params:", { 
        token: access_token ? "provided" : "missing", 
        role: user_role || "not provided",
        password_needed
      });
      
      if (access_token) {
        // Save auth data
        localStorage.setItem('token', access_token);
        
        // Save user role if available
        if (user_role) {
          // Convert role to proper format for our constants
          let formattedRole;
          switch(user_role.toLowerCase()) {
            case 'student':
              formattedRole = ROLE.STUDENT;
              break;
            case 'faculty':
              formattedRole = ROLE.FACULTY;
              break;
            case 'support':
              formattedRole = ROLE.SUPPORT;
              break;
            default:
              formattedRole = ROLE.STUDENT; // Default if unknown
          }
          
          // Save role to localStorage and update store
          authStore.setUserRole(formattedRole);
          console.log(`User role set to: ${formattedRole}`);
        }
        
        // Check for redirect path from localStorage
        const redirectPath = localStorage.getItem('loginRedirectPath');
        
        // Determine where to redirect the user based on role
        let targetPath;
        
        // Handle password_needed first if applicable
        if (password_needed) {
          // Redirect to set password page
          console.log("User needs to set a password, redirecting to password setup");
          targetPath = '/set-password';
        } else if (redirectPath && redirectPath.includes('/monitoring') && user_role === 'support') {
          // If there's a redirect path to monitoring and user has support role, go there
          targetPath = redirectPath;
        } else {
          // Get default dashboard based on role
          const role = authStore.userRole;
          
          // Use rolePaths for consistent redirects
          if (role === ROLE.SUPPORT) {
            targetPath = rolePaths.SUPPORT.dashboard;
          } else if (role === ROLE.FACULTY) {
            targetPath = rolePaths.FACULTY.dashboard;
          } else {
            targetPath = rolePaths.STUDENT.dashboard;
          }
          
          console.log(`Redirecting to ${targetPath} based on role: ${role}`);
        }
        
        // Clear stored redirect path
        localStorage.removeItem('loginRedirectPath');
        
        // Get user info to complete auth process
        await authService.getCurrentUser();
        
        // Redirect user
        this.$router.push(targetPath);
      } else {
        // No token found, go to login
        console.error("No access token provided in callback URL");
        this.$router.push('/login?error=no_token');
      }
    } catch (error) {
      console.error('Auth callback error:', error);
      this.$router.push('/login?error=callback_error');
    }
  }
}
</script> 