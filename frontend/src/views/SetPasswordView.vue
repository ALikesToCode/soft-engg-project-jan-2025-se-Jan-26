<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
      <div class="text-center mb-6">
        <h1 class="text-2xl font-bold text-gray-800">Set Your Password</h1>
        <p class="text-gray-600 mt-2">
          Please set a password for your account to continue.
        </p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Password Input -->
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
            Password
          </label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
              <span class="material-icons text-xl">lock</span>
            </span>
            <input
              :type="showPassword ? 'text' : 'password'"
              id="password"
              v-model="form.password"
              class="w-full pl-12 pr-12 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-all duration-300 border-gray-200 hover:border-gray-300 focus:border-maroon-500 focus:ring-maroon-500/30"
              placeholder="Enter a strong password"
              required
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-500 transition-colors"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
            >
              <span class="material-icons text-xl">{{
                showPassword ? 'visibility_off' : 'visibility'
              }}</span>
            </button>
          </div>
          <p v-if="form.password && !passwordValid" class="mt-2 text-sm text-red-600">
            Password must be at least 8 characters and include a letter and a number
          </p>
        </div>

        <!-- Confirm Password Input -->
        <div>
          <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
            Confirm Password
          </label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
              <span class="material-icons text-xl">lock</span>
            </span>
            <input
              :type="showConfirmPassword ? 'text' : 'password'"
              id="confirmPassword"
              v-model="form.confirmPassword"
              class="w-full pl-12 pr-12 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-all duration-300 border-gray-200 hover:border-gray-300 focus:border-maroon-500 focus:ring-maroon-500/30"
              placeholder="Confirm your password"
              required
            />
            <button
              type="button"
              @click="showConfirmPassword = !showConfirmPassword"
              class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-500 transition-colors"
              :aria-label="showConfirmPassword ? 'Hide password' : 'Show password'"
            >
              <span class="material-icons text-xl">{{
                showConfirmPassword ? 'visibility_off' : 'visibility'
              }}</span>
            </button>
          </div>
          <p v-if="form.confirmPassword && !passwordsMatch" class="mt-2 text-sm text-red-600">
            Passwords do not match
          </p>
        </div>

        <!-- Password Strength Indicator -->
        <div v-if="form.password">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Password Strength
          </label>
          <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              class="h-full transition-all duration-300"
              :class="{
                'w-1/4 bg-red-500': passwordStrength === 'weak',
                'w-2/4 bg-yellow-500': passwordStrength === 'medium',
                'w-3/4 bg-blue-500': passwordStrength === 'strong',
                'w-full bg-green-500': passwordStrength === 'very-strong'
              }"
            ></div>
          </div>
          <p class="mt-1 text-xs text-gray-500">
            {{ passwordStrengthText }}
          </p>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="p-3 bg-red-100 border-l-4 border-red-500 text-red-700">
          <p>{{ error }}</p>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="loading || !formValid"
          class="w-full flex justify-center items-center py-3.5 px-6 rounded-xl text-sm font-medium text-white bg-maroon-600 hover:bg-maroon-700 focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:ring-offset-2 transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed"
        >
          <span v-if="loading" class="material-icons animate-spin mr-2">refresh</span>
          {{ loading ? 'Processing...' : 'Set Password & Continue' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import useAuthStore from '@/stores/useAuthStore'
import rolePaths from '@/AppConstants/rolePaths'

export default {
  name: 'SetPasswordView',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)
    const loading = ref(false)
    const error = ref('')
    
    const form = ref({
      password: '',
      confirmPassword: ''
    })
    
    // Password validation
    const passwordValid = computed(() => {
      const password = form.value.password
      if (!password) return false
      return password.length >= 8 && /[A-Za-z]/.test(password) && /[0-9]/.test(password)
    })
    
    const passwordsMatch = computed(() => {
      return form.value.password === form.value.confirmPassword
    })
    
    const formValid = computed(() => {
      return passwordValid.value && passwordsMatch.value && form.value.password.length > 0
    })
    
    // Password strength calculation
    const passwordStrength = computed(() => {
      const password = form.value.password
      if (!password) return ''
      
      // Basic strength check
      if (password.length < 8) return 'weak'
      if (password.length >= 8 && /[A-Za-z]/.test(password) && /[0-9]/.test(password)) {
        if (password.length >= 12 && /[^A-Za-z0-9]/.test(password)) {
          return 'very-strong'
        }
        if (password.length >= 10 && /[^A-Za-z0-9]/.test(password)) {
          return 'strong'
        }
        return 'medium'
      }
      return 'weak'
    })
    
    const passwordStrengthText = computed(() => {
      switch (passwordStrength.value) {
        case 'weak':
          return 'Weak: Use at least 8 characters with letters and numbers'
        case 'medium':
          return 'Medium: Good basic password'
        case 'strong':
          return 'Strong: Good length with special characters'
        case 'very-strong':
          return 'Very Strong: Excellent password!'
        default:
          return ''
      }
    })
    
    // Form submission
    async function handleSubmit() {
      if (!formValid.value) return
      
      loading.value = true
      error.value = ''
      
      try {
        const result = await authStore.setPassword(form.value.password)
        
        if (result.success) {
          // Navigate to appropriate dashboard based on user role
          const role = authStore.userRole
          let targetPath = '/dashboard' // Default fallback
          
          if (role && rolePaths[role]?.dashboard) {
            targetPath = rolePaths[role].dashboard
          }
          
          router.push(targetPath)
        } else {
          error.value = result.message || 'Failed to set password. Please try again.'
        }
      } catch (err) {
        console.error('Password setup error:', err)
        error.value = 'An error occurred. Please try again.'
      } finally {
        loading.value = false
      }
    }
    
    return {
      form,
      showPassword,
      showConfirmPassword,
      loading,
      error,
      passwordValid,
      passwordsMatch,
      formValid,
      passwordStrength,
      passwordStrengthText,
      handleSubmit
    }
  }
}
</script> 