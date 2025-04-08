<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-lg max-w-md w-full text-center">
      <span class="material-icons text-5xl text-maroon-600 animate-spin mb-4">refresh</span>
      <h1 class="text-2xl font-bold text-gray-800 mb-2">Authentication in progress...</h1>
      <p class="text-gray-600">{{ status }}</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/api/authService'
import useAuthStore from '@/stores/useAuthStore'
import { ROLE } from '@/AppConstants/globalConstants'
import rolePaths from '@/AppConstants/rolePaths'

export default {
  name: 'AuthCallback',
  setup() {
    const status = ref('Please wait while we complete your login.')
    const router = useRouter()

    // Helper function to convert backend role to frontend role format
    const mapBackendRoleToFrontend = (backendRole) => {
      if (!backendRole) return ROLE.STUDENT;
      
      // Log the original role from backend for debugging
      console.log(`Mapping backend role: ${backendRole}, type: ${typeof backendRole}`);
      
      // Add more debug info
      console.log(`ROLE constants:`, ROLE);
      console.log(`rolePaths:`, rolePaths);
      
      const lowerCaseRole = backendRole.toLowerCase();
      console.log(`Lowercase role: ${lowerCaseRole}`);
      
      let result;
      switch(lowerCaseRole) {
        case 'faculty':
          result = ROLE.FACULTY;
          break;
        case 'support':
        case 'admin':
          result = ROLE.SUPPORT;
          break;
        case 'student':
        default:
          result = ROLE.STUDENT;
          break;
      }
      
      console.log(`Mapped role result: ${result}`);
      return result;
    }

    onMounted(async () => {
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
        
        if (!access_token) {
          console.error("No access token provided in callback URL");
          status.value = "Authentication failed. Redirecting to login...";
          setTimeout(() => router.push('/login?error=no_token'), 2000);
          return;
        }
        
        // Save auth data
        localStorage.setItem('token', access_token);
        status.value = "Token received. Setting up your account...";
        
        // Save user role if available
        if (user_role) {
          const frontendRole = mapBackendRoleToFrontend(user_role);
          authStore.setUserRole(frontendRole);
          console.log(`User role set to: ${frontendRole} from backend role: ${user_role}`);
        }
        
        // Handle password_needed first if applicable
        if (password_needed) {
          console.log("User needs to set a password, redirecting to password setup");
          setTimeout(() => router.push('/set-password'), 1000);
          return;
        }
        
        status.value = "Getting user information...";
        
        // Validate token by getting user info
        try {
          const userData = await authService.getCurrentUser();
          if (!userData) {
            throw new Error("Failed to get user data");
          }
          
          // Detailed logging of user data
          console.log("Complete user data:", JSON.stringify(userData, null, 2));
          
          // Update role from user data (most accurate source)
          if (userData.role) {
            console.log(`Current userRole before mapping: ${authStore.userRole}`);
            const updatedRole = mapBackendRoleToFrontend(userData.role);
            console.log(`Updated role after mapping: ${updatedRole}`);
            authStore.setUserRole(updatedRole);
            console.log(`Role updated in store: ${authStore.userRole}`);
          }
          
          // Check for redirect path from localStorage
          const redirectPath = localStorage.getItem('loginRedirectPath');
          console.log(`Stored redirect path: ${redirectPath}`);
          let targetPath;
          
          console.log(`Current user role for redirection: ${authStore.userRole}`);
          console.log(`Role comparison: authStore.userRole === ROLE.SUPPORT: ${authStore.userRole === ROLE.SUPPORT}`);
          
          if (redirectPath && redirectPath.includes('/monitoring') && authStore.userRole === ROLE.SUPPORT) {
            // If there's a redirect path to monitoring and user has support role, go there
            targetPath = redirectPath;
            console.log(`Using stored redirect path for support user: ${targetPath}`);
          } else {
            // Use rolePaths for consistent redirects based on role
            console.log(`Using rolePaths for redirection based on role: ${authStore.userRole}`);
            
            switch(authStore.userRole) {
              case ROLE.SUPPORT:
                targetPath = rolePaths.SUPPORT.dashboard;
                console.log(`Support user redirecting to: ${targetPath}`);
                break;
              case ROLE.FACULTY:
                targetPath = rolePaths.FACULTY.dashboard;
                console.log(`Faculty user redirecting to: ${targetPath}`);
                break;
              default:
                targetPath = rolePaths.STUDENT.dashboard;
                console.log(`Student/default user redirecting to: ${targetPath}`);
            }
          }
          
          // Clear stored redirect path
          localStorage.removeItem('loginRedirectPath');
          
          status.value = "Authentication successful! Redirecting...";
          console.log(`Redirecting to ${targetPath} based on role: ${authStore.userRole}`);
          
          // Give a small delay to show success message
          setTimeout(() => router.push(targetPath), 1000);
        } catch (userError) {
          console.error("Error getting user data:", userError);
          status.value = "Error loading user data. Redirecting to login...";
          setTimeout(() => router.push('/login?error=user_data_error'), 2000);
        }
      } catch (error) {
        console.error('Auth callback error:', error);
        status.value = "Authentication error. Redirecting to login...";
        setTimeout(() => router.push('/login?error=callback_error'), 2000);
      }
    })

    return {
      status
    }
  }
}
</script> 