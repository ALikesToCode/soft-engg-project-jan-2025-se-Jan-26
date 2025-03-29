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
        
        // Save user role if available and convert it properly to match ROLE constants
        if (user_role) {
          // Convert backend role format to frontend ROLE constant format
          let formattedRole;
          switch(user_role.toLowerCase()) {
            case 'student':
              formattedRole = ROLE.STUDENT; // STUDENT constant
              break;
            case 'faculty':
              formattedRole = ROLE.FACULTY; // FACULTY constant
              break;
            case 'support':
              formattedRole = ROLE.SUPPORT; // SUPPORT constant
              break;
            case 'admin':
              formattedRole = ROLE.SUPPORT; // Admin users use SUPPORT dashboard
              break;
            default:
              formattedRole = ROLE.STUDENT; // Default if unknown
          }
          
          // Save role to localStorage and update store
          authStore.setUserRole(formattedRole);
          console.log(`User role set to: ${formattedRole} from backend role: ${user_role}`);
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
        } else if (redirectPath && redirectPath.includes('/monitoring') && (user_role === 'support' || user_role === 'admin')) {
          // If there's a redirect path to monitoring and user has support/admin role, go there
          targetPath = redirectPath;
        } else {
          // Get current role from store to ensure we're using the latest value
          const role = authStore.userRole;
          console.log(`Current role in auth store for redirection: ${role}`);
          
          // Use rolePaths for consistent redirects based on role constants
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
        
        status.value = "Getting user information...";
        
        // Validate token by getting user info
        try {
          const userData = await authService.getCurrentUser();
          if (!userData) {
            throw new Error("Failed to get user data");
          }
          
          // Update role from user data if available (most accurate source)
          if (userData.role) {
            // Convert backend role to frontend format
            let updatedRole;
            switch(userData.role.toLowerCase()) {
              case 'faculty':
                updatedRole = ROLE.FACULTY;
                break;
              case 'support':
              case 'admin':
                updatedRole = ROLE.SUPPORT;
                break;
              default: 
                updatedRole = ROLE.STUDENT;
            }
            
            // Update store with the latest role
            authStore.setUserRole(updatedRole);
            
            // Re-determine target path based on updated role
            if (updatedRole === ROLE.SUPPORT) {
              targetPath = rolePaths.SUPPORT.dashboard;
            } else if (updatedRole === ROLE.FACULTY) {
              targetPath = rolePaths.FACULTY.dashboard;
            } else {
              targetPath = rolePaths.STUDENT.dashboard;
            }
            console.log(`Updated redirection to ${targetPath} based on user data role: ${updatedRole}`);
          }
          
          status.value = "Authentication successful! Redirecting...";
          
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