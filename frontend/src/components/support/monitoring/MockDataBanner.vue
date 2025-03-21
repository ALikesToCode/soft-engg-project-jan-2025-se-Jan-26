<template>
  <div v-if="showBanner" class="text-center p-2 bg-amber-100 border-b border-amber-200 text-amber-800 text-sm">
    <span class="font-semibold">Mock Data:</span> You're seeing mock data because you're not logged in with a support account.
    <button @click="login" class="ml-2 underline hover:text-amber-900">Log in</button>
  </div>
</template>

<script>
import monitoringService from '../../../services/monitoring.service';
import { ref, onMounted } from 'vue';

export default {
  name: 'MockDataBanner',
  setup() {
    const showBanner = ref(false);
    
    onMounted(() => {
      showBanner.value = monitoringService.isUsingMockData();
    });
    
    const login = () => {
      // Redirect to login page
      window.location.href = '/login';
    };
    
    return {
      showBanner,
      login
    };
  }
};
</script> 