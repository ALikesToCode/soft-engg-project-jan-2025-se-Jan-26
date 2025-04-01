<template>
  <div v-if="showBanner" class="text-center p-2 bg-amber-100 border-b border-amber-200 text-amber-800 text-sm">
    <span class="font-semibold">Mock Data:</span> You're seeing mock data because you're not logged in with a support account.
    <button @click="login" class="ml-2 underline hover:text-amber-900">Log in</button>
  </div>
</template>

<script>
import monitoringService from '../../../services/monitoring.service';
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'MockDataBanner',
  setup() {
    const showBanner = ref(false);
    const router = useRouter();
    
    onMounted(() => {
      showBanner.value = monitoringService.isUsingMockData();
    });
    
    const login = () => {
      // Save current path to redirect back after login
      localStorage.setItem('loginRedirectPath', window.location.pathname);
      // Redirect to login page
      router.push({ 
        path: '/login', 
        query: { redirect: window.location.pathname } 
      });
    };
    
    return {
      showBanner,
      login
    };
  }
};
</script> 