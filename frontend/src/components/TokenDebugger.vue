<template>
  <div class="p-4 bg-gray-100 rounded-lg mb-4">
    <h3 class="text-lg font-semibold mb-2">Token Debugger</h3>
    <div v-if="tokenExists" class="space-y-2">
      <div class="flex items-center">
        <span :class="tokenValid ? 'text-green-500' : 'text-yellow-500'" class="material-icons mr-2">
          {{ tokenValid ? 'check_circle' : 'warning' }}
        </span>
        <span>Token exists in localStorage {{ tokenValid ? '(valid)' : '(may be invalid)' }}</span>
        <button 
          @click="refreshTokenDisplay" 
          class="ml-2 px-2 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-xs"
          title="Refresh token display"
        >
          <span class="material-icons text-sm">refresh</span>
        </button>
      </div>
      
      <!-- Token details -->
      <div v-if="tokenDetails" class="text-sm bg-gray-200 p-2 rounded">
        <div><strong>Subject:</strong> {{ tokenDetails.subject }}</div>
        <div><strong>Expires:</strong> {{ tokenDetails.expiry }}</div>
        <div :class="tokenDetails.isExpired ? 'text-red-600 font-bold' : 'text-green-600'">
          <strong>Status:</strong> {{ tokenDetails.isExpired ? 'EXPIRED' : 'Valid' }}
          <span v-if="!tokenDetails.isExpired"> ({{ tokenDetails.timeRemaining }} remaining)</span>
        </div>
      </div>
      
      <div class="text-sm bg-gray-200 p-2 rounded overflow-auto max-h-20">
        <code>{{ tokenPreview }}</code>
      </div>
      
      <div class="flex flex-wrap gap-2">
        <button 
          @click="checkToken" 
          class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Test Token
        </button>
        <button 
          @click="requestNewToken" 
          class="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Refresh Token
        </button>
        <button 
          @click="clearToken" 
          class="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Clear Token
        </button>
      </div>
      
      <!-- Test results -->
      <div v-if="testResult" class="mt-2">
        <div v-if="testResult.success" class="text-green-600">
          <div class="flex items-center">
            <span class="material-icons mr-2">check_circle</span>
            <span>Token is valid</span>
          </div>
          <div class="text-sm bg-gray-200 p-2 rounded mt-1 overflow-auto max-h-40">
            <pre><code>{{ JSON.stringify(testResult.data, null, 2) }}</code></pre>
          </div>
        </div>
        <div v-else class="text-red-600">
          <div class="flex items-center">
            <span class="material-icons mr-2">error</span>
            <span>Token is invalid: {{ testResult.error }}</span>
          </div>
        </div>
      </div>
      
      <!-- Refresh token results -->
      <div v-if="refreshResult" class="mt-2" :class="refreshResult.success ? 'text-green-600' : 'text-red-600'">
        <div class="flex items-center">
          <span class="material-icons mr-2">{{ refreshResult.success ? 'check_circle' : 'error' }}</span>
          <span>{{ refreshResult.message }}</span>
        </div>
      </div>
    </div>
    
    <!-- No token state -->
    <div v-else class="text-red-600 flex items-center">
      <span class="material-icons mr-2">error</span>
      <span>No token found in localStorage</span>
      <button 
        @click="refreshTokenDisplay" 
        class="ml-2 px-2 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-xs"
      >
        <span class="material-icons text-sm">refresh</span>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { authService } from '@/api/authService';

export default {
  name: 'TokenDebugger',
  setup() {
    const token = ref(null);
    const testResult = ref(null);
    const refreshResult = ref(null);
    const tokenDetails = ref(null);
    const tokenValid = ref(true);
    
    const tokenExists = computed(() => !!token.value);
    const tokenPreview = computed(() => {
      if (!token.value) return '';
      if (token.value.length > 50) {
        return token.value.substring(0, 25) + '...' + token.value.substring(token.value.length - 25);
      }
      return token.value;
    });
    
    onMounted(() => {
      refreshTokenDisplay();
    });
    
    function refreshTokenDisplay() {
      token.value = localStorage.getItem('token');
      try {
        // Check if token is stored as JSON
        const parsed = JSON.parse(token.value);
        if (typeof parsed === 'string') {
          token.value = parsed;
        }
      } catch (e) {
        // Not JSON, use as is
      }
      
      // Extract token details
      extractTokenDetails();
      
      // Also log to console for debugging
      tokenValid.value = authService.debugTokenStatus();
    }
    
    function extractTokenDetails() {
      if (!token.value) {
        tokenDetails.value = null;
        return;
      }
      
      try {
        const tokenParts = token.value.split('.');
        if (tokenParts.length === 3) {
          // Decode the payload (middle part)
          const payload = JSON.parse(atob(tokenParts[1]));
          const expiry = payload.exp ? new Date(payload.exp * 1000) : 'unknown';
          const isExpired = payload.exp ? Date.now() > payload.exp * 1000 : false;
          
          tokenDetails.value = {
            subject: payload.sub || 'unknown',
            expiry: expiry.toString(),
            isExpired,
            timeRemaining: payload.exp ? 
              Math.floor((payload.exp * 1000 - Date.now()) / 1000) + ' seconds' : 
              'unknown'
          };
          
          tokenValid.value = !isExpired;
        } else {
          tokenDetails.value = null;
          tokenValid.value = false;
        }
      } catch (e) {
        console.error('Error extracting token details:', e);
        tokenDetails.value = null;
        tokenValid.value = false;
      }
    }
    
    async function checkToken() {
      testResult.value = null;
      refreshResult.value = null;
      
      try {
        const userData = await authService.getCurrentUser();
        if (userData) {
          testResult.value = {
            success: true,
            data: userData
          };
        } else {
          testResult.value = {
            success: false,
            error: 'No user data returned'
          };
        }
      } catch (error) {
        testResult.value = {
          success: false,
          error: error.message || 'Unknown error'
        };
      }
    }
    
    async function requestNewToken() {
      testResult.value = null;
      refreshResult.value = null;
      
      try {
        const success = await authService.refreshToken();
        if (success) {
          refreshResult.value = {
            success: true,
            message: 'Token refreshed successfully'
          };
          // Update the token display
          refreshTokenDisplay();
        } else {
          refreshResult.value = {
            success: false,
            message: 'Failed to refresh token'
          };
        }
      } catch (error) {
        refreshResult.value = {
          success: false,
          message: `Error refreshing token: ${error.message || 'Unknown error'}`
        };
      }
    }
    
    function clearToken() {
      authService.clearAuthData();
      token.value = null;
      testResult.value = null;
      refreshResult.value = null;
      tokenDetails.value = null;
    }
    
    return {
      tokenExists,
      tokenPreview,
      tokenDetails,
      tokenValid,
      testResult,
      refreshResult,
      checkToken,
      clearToken,
      refreshTokenDisplay,
      requestNewToken
    };
  }
}
</script> 