<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full p-6">
      <div v-if="showPasswordForm" class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">Set Your Password</h2>
        <p class="text-gray-600 mb-6">
          You've logged in with Google, but you need to set a password to enable email login in the future.
        </p>
        
        <div v-if="passwordError" class="bg-red-50 text-red-700 p-3 rounded mb-4">
          {{ passwordError }}
        </div>
        
        <form @submit.prevent="setPassword">
          <div class="mb-4">
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">New Password</label>
            <input 
              type="password" 
              id="password" 
              v-model="password"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-maroon-500"
              placeholder="Enter a secure password"
              required
            />
          </div>
          
          <div class="mb-6">
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
            <input 
              type="password" 
              id="confirmPassword" 
              v-model="confirmPassword"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-maroon-500"
              placeholder="Confirm your password"
              required
            />
          </div>
          
          <div class="flex items-center justify-between">
            <button
              type="submit"
              class="w-full bg-maroon-600 text-white py-2 px-4 rounded-md hover:bg-maroon-700 focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:ring-offset-2"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting" class="inline-block animate-spin mr-2">⟳</span>
              {{ isSubmitting ? 'Setting Password...' : 'Set Password' }}
            </button>
          </div>
          
          <div class="mt-4 text-center">
            <button 
              @click="skipPasswordSetup" 
              type="button"
              class="text-sm text-gray-600 hover:text-maroon-600"
            >
              Skip for now (You can set it later in your profile)
            </button>
          </div>
        </form>
      </div>
      
      <div v-else class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-maroon-600 mx-auto mb-4"></div>
        <h2 class="text-xl font-semibold text-gray-800 mb-2">{{ message }}</h2>
        <p class="text-gray-600">{{ subMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import useAuthStore from '@/stores/useAuthStore';
import { useRoute, useRouter } from 'vue-router';
import { onMounted, ref } from 'vue';
import { authService } from '@/api/authService';

export default {
  name: 'AuthCallback',
  setup() {
    const message = ref('Processing your login...');
    const subMessage = ref('Please wait while we authenticate you');
    const route = useRoute();
    const router = useRouter();
    const authStore = useAuthStore();
    
    // Password form state
    const showPasswordForm = ref(false);
    const password = ref('');
    const confirmPassword = ref('');
    const passwordError = ref('');
    const isSubmitting = ref(false);

    const setPassword = async () => {
      // Validate passwords
      if (password.value.length < 8) {
        passwordError.value = 'Password must be at least 8 characters long';
        return;
      }
      
      if (password.value !== confirmPassword.value) {
        passwordError.value = 'Passwords do not match';
        return;
      }
      
      try {
        isSubmitting.value = true;
        passwordError.value = '';
        
        // Call API to set password using the authStore method
        const result = await authStore.setPassword(password.value);
        
        if (result.success) {
          message.value = 'Password set successfully!';
          subMessage.value = 'Redirecting you to the dashboard...';
          showPasswordForm.value = false;
          
          // Redirect to the appropriate dashboard based on user role
          setTimeout(() => authStore.navigateToRoleDashboard(), 1500);
        } else {
          passwordError.value = result.message;
        }
      } catch (error) {
        console.error('Error setting password:', error);
        passwordError.value = 'Failed to set password. Please try again.';
      } finally {
        isSubmitting.value = false;
      }
    };
    
    const skipPasswordSetup = () => {
      showPasswordForm.value = false;
      message.value = 'Continuing to dashboard...';
      subMessage.value = 'You can set your password later in your profile';
      
      // Redirect to the appropriate dashboard based on user role
      setTimeout(() => authStore.navigateToRoleDashboard(), 1500);
    };

    onMounted(async () => {
      try {
        // Get the token from the URL query parameters
        const accessToken = route.query.access_token;
        const passwordNeeded = route.query.password_needed === 'true';
        
        if (!accessToken) {
          message.value = 'Authentication failed';
          subMessage.value = 'No access token received. Please try again.';
          setTimeout(() => router.push('/login'), 3000);
          return;
        }

        // Store the token in localStorage
        localStorage.setItem('token', accessToken);
        
        // Update the auth store
        authStore.token = accessToken;
        
        // Check if password setup is needed
        if (passwordNeeded) {
          showPasswordForm.value = true;
        } else {
          message.value = 'Authentication successful!';
          subMessage.value = 'Redirecting you to the dashboard...';
          
          // Redirect to the appropriate dashboard based on user role
          setTimeout(() => authStore.navigateToRoleDashboard(), 1500);
        }
      } catch (error) {
        console.error('Error in auth callback:', error);
        message.value = 'Authentication error';
        subMessage.value = 'An error occurred during authentication. Please try again.';
        setTimeout(() => router.push('/login'), 3000);
      }
    });

    return {
      message,
      subMessage,
      showPasswordForm,
      password,
      confirmPassword,
      passwordError,
      isSubmitting,
      setPassword,
      skipPasswordSetup
    };
  }
}
</script> 