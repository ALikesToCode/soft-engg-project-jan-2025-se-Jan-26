<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full p-6">
      <div class="text-center">
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

export default {
  name: 'AuthCallback',
  setup() {
    const message = ref('Processing your login...');
    const subMessage = ref('Please wait while we authenticate you');
    const route = useRoute();
    const router = useRouter();
    const authStore = useAuthStore();

    onMounted(async () => {
      try {
        // Get the token from the URL query parameters
        const accessToken = route.query.access_token;
        
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
        
        message.value = 'Authentication successful!';
        subMessage.value = 'Redirecting you to the dashboard...';
        
        // Redirect to the appropriate dashboard based on user role
        setTimeout(() => authStore.navigateToRoleDashboard(), 1500);
      } catch (error) {
        console.error('Error in auth callback:', error);
        message.value = 'Authentication error';
        subMessage.value = 'An error occurred during authentication. Please try again.';
        setTimeout(() => router.push('/login'), 3000);
      }
    });

    return {
      message,
      subMessage
    };
  }
}
</script> 