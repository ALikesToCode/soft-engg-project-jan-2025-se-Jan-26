<template>
  <div class="min-h-screen bg-white">
    <!-- Back to Home -->
    <router-link 
      to="/" 
      class="fixed top-6 left-6 z-50 flex items-center p-2 rounded-lg bg-white/90 backdrop-blur-sm shadow-sm text-gray-600 hover:text-maroon-600 hover:bg-white transition-all duration-300"
    >
      <span class="material-icons mr-2">arrow_back</span>
      <span class="font-medium">Back to Home</span>
    </router-link>

    <div class="flex min-h-screen">
      <!-- Left Side - Hero Section -->
      <div class="w-1/2 bg-gradient-to-br from-maroon-600 via-maroon-700 to-maroon-800 p-8 lg:p-12 flex flex-col justify-center relative overflow-hidden">
        <div class="relative z-10 space-y-8">
          <div class="fade-in">
            <div class="mb-6">
              <div class="w-16 h-16 mb-4 bg-white/10 rounded-2xl flex items-center justify-center">
                <span class="material-icons text-3xl text-yellow-400">school</span>
              </div>
              <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight">
                Elevate Your<br>Learning Experience
              </h1>
            </div>
            <p class="text-xl text-gray-200/90 leading-relaxed">
              Your gateway to intelligent academic support at IITM BS
            </p>
          </div>

          <!-- Feature List -->
          <div class="space-y-6 fade-in delay-100">
            <div v-for="(feature, index) in features" :key="index" class="group flex items-start p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-all duration-300 cursor-default">
              <span class="material-icons text-2xl text-yellow-400 mr-4 mt-1 transform group-hover:scale-110 transition-transform">{{ feature.icon }}</span>
              <p class="text-lg text-white/90 leading-snug">{{ feature.text }}</p>
            </div>
          </div>
        </div>

        <!-- Animated Background Elements -->
        <div class="absolute inset-0 opacity-15 mix-blend-overlay">
          <div 
            class="absolute top-1/4 left-1/4 w-32 h-32 bg-gradient-to-r from-yellow-400 to-yellow-500 rounded-full animate-float"
            style="animation-delay: 0.2s"
          ></div>
          <div 
            class="absolute bottom-1/4 right-1/4 w-24 h-24 bg-gradient-to-br from-white to-gray-200 rounded-full animate-float"
            style="animation-delay: 0.5s"
          ></div>
        </div>
      </div>

      <!-- Right Side - Login Card -->
      <div class="w-1/2 flex items-center justify-center p-8 lg:p-12 bg-gray-50 relative">
        <div class="max-w-md w-full fade-in">
          <div class="bg-white rounded-2xl shadow-xl p-8 sm:p-10 lg:p-12 transition-all duration-300 hover:shadow-2xl">
            <div class="text-center mb-8">
              <div class="mb-4">
                <div class="w-12 h-12 mb-4 bg-maroon-600/10 rounded-xl flex items-center justify-center mx-auto">
                  <span class="material-icons text-2xl text-maroon-600">lock</span>
                </div>
                <h2 class="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h2>
              </div>
              <p class="text-gray-600">Sign in to continue your learning journey</p>
            </div>

            <!-- Google Sign In -->
            <button 
              @click="handleGoogleSignIn"
              class="w-full flex justify-center items-center py-3.5 px-6 rounded-xl shadow-sm bg-white border border-gray-200/80 text-gray-700 font-medium hover:border-maroon-500/30 hover:bg-maroon-50/50 focus:outline-none focus:ring-2 focus:ring-maroon-500/20 focus:ring-offset-2 transition-all duration-300 mb-6"
            >
              <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" class="w-5 h-5 mr-3">
              <span class="truncate">Continue with Google</span>
            </button>

            <!-- Divider -->
            <div class="relative my-8">
              <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-gray-200/60"></div>
              </div>
              <div class="relative flex justify-center text-sm">
                <span class="px-3 bg-white text-gray-500 font-medium">Or with email</span>
              </div>
            </div>

            <!-- Email Sign In Form -->
            <form v-if="showEmailForm" @submit.prevent="handleSubmit" class="space-y-5">
              <div>
                <label for="email" class="block text-sm font-medium text-gray-700 mb-2">Email address</label>
                <div class="relative">
                  <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                    <span class="material-icons text-xl">mail</span>
                  </span>
                  <input 
                    type="email" 
                    id="email" 
                    v-model="form.email"
                    :class="[
                      'w-full pl-12 pr-4 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-all duration-300',
                      errors.email 
                        ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500/30'
                        : 'border-gray-200 hover:border-gray-300 focus:border-maroon-500 focus:ring-maroon-500/30'
                    ]"
                    placeholder="name@iitm.ac.in"
                    required
                  >
                </div>
                <p v-if="errors.email" class="mt-2 text-sm text-red-600 animate-fade-in">{{ errors.email }}</p>
              </div>

              <div>
                <label for="password" class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                <div class="relative">
                  <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                    <span class="material-icons text-xl">lock</span>
                  </span>
                  <input 
                    :type="showPassword ? 'text' : 'password'"
                    id="password" 
                    v-model="form.password"
                    :class="[
                      'w-full pl-12 pr-12 py-3 border rounded-xl focus:outline-none focus:ring-2 transition-all duration-300',
                      errors.password 
                        ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500/30'
                        : 'border-gray-200 hover:border-gray-300 focus:border-maroon-500 focus:ring-maroon-500/30'
                    ]"
                    placeholder="••••••••"
                    required
                  >
                  <button 
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-500 transition-colors"
                    :aria-label="showPassword ? 'Hide password' : 'Show password'"
                  >
                    <span class="material-icons text-xl">{{ showPassword ? 'visibility_off' : 'visibility' }}</span>
                  </button>
                </div>
                <p v-if="errors.password" class="mt-2 text-sm text-red-600 animate-fade-in">{{ errors.password }}</p>
              </div>

              <div class="flex items-center justify-between">
                <label class="flex items-center space-x-2 cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.remember"
                    class="h-4 w-4 text-maroon-600 rounded border-gray-300 focus:ring-maroon-500 transition"
                  >
                  <span class="text-sm text-gray-600">Remember me</span>
                </label>
                <router-link 
                  to="/forgot-password" 
                  class="text-sm text-maroon-600 hover:text-maroon-700 transition-colors"
                >
                  Forgot password?
                </router-link>
              </div>

              <button 
                type="submit"
                :disabled="loading"
                class="w-full flex justify-center items-center py-3.5 px-6 rounded-xl text-sm font-medium text-white bg-maroon-600 hover:bg-maroon-700 focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:ring-offset-2 transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed"
              >
                <span v-if="loading" class="material-icons animate-spin mr-2">refresh</span>
                {{ loading ? 'Authenticating...' : 'Continue' }}
              </button>
            </form>

            <!-- Email Sign In Toggle -->
            <button 
              v-if="!showEmailForm"
              @click="showEmailForm = true"
              class="w-full flex justify-center items-center py-3.5 px-6 rounded-xl border-2 border-dashed border-gray-200 text-gray-600 font-medium hover:border-maroon-500/30 hover:bg-maroon-50/50 hover:text-maroon-700 focus:outline-none focus:ring-2 focus:ring-maroon-500/20 focus:ring-offset-2 transition-all duration-300"
            >
              <span class="material-icons mr-2">alternate_email</span>
              Continue with Email
            </button>

            <!-- Help Text -->
            <p class="mt-6 text-center text-sm text-gray-600">
              Need access? Contact administrator
              <router-link 
                to="/contact" 
                class="font-medium text-maroon-600 hover:text-maroon-700 inline-flex items-center transition-colors"
              >
                Get help
                <span class="material-icons ml-1 text-sm">arrow_forward</span>
              </router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginView',
  data() {
    return {
      showEmailForm: false,
      showPassword: false,
      loading: false,
      features: [
        { icon: 'auto_awesome', text: 'Adaptive learning paths powered by AI' },
        { icon: 'psychology', text: 'Smart course navigation & concept mapping' },
        { icon: 'insights', text: 'Performance analytics & progress tracking' }
      ],
      form: {
        email: '',
        password: '',
        remember: false
      },
      errors: {
        email: '',
        password: ''
      }
    }
  },
  methods: {
    validateForm() {
      let isValid = true
      this.errors = { email: '', password: '' }

      if (!this.form.email) {
        this.errors.email = 'Email is required'
        isValid = false
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.form.email)) {
        this.errors.email = 'Please enter a valid email address'
        isValid = false
      }

      if (!this.form.password) {
        this.errors.password = 'Password is required'
        isValid = false
      } else if (this.form.password.length < 8) {
        this.errors.password = 'Password must be at least 8 characters'
        isValid = false
      }

      return isValid
    },
    async handleSubmit() {
      if (!this.validateForm()) return

      this.loading = true
      try {
        await new Promise(resolve => setTimeout(resolve, 1500))
        this.$router.push('/dashboard')
      } catch (error) {
        console.error('Login error:', error)
      } finally {
        this.loading = false
      }
    },
    async handleGoogleSignIn() {
      try {
        // Implement Google Sign In
        console.log('Google Sign In clicked')
      } catch (error) {
        console.error('Google Sign In error:', error)
      }
    }
  }
}
</script>

<style scoped>
.fade-in {
  animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.delay-100 {
  animation-delay: 100ms;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.05); }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

.animate-float {
  animation: float 6s ease-in-out infinite;
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@media (max-width: 1023px) {
  .w-1\/2 {
    width: 100%;
  }
  
  .flex {
    flex-direction: column;
  }
}
</style>
