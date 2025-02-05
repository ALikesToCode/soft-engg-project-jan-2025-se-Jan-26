<script>
import { GoogleLogin } from "vue3-google-login";

export default {
  components: {
    GoogleLogin,
  },
  data() {
    return {
      googleClientId: "YOUR_GOOGLE_CLIENT_ID",  
    };
  },
  methods: {
    handleLoginSuccess(response) {
      console.log("Login Success:", response);
    },
    handleLoginFailure(error) {
      console.log("Login Failed:", error);
    },
  },
};
</script>

<template>
  <div class="flex items-center justify-center h-screen bg-gradient-to-r from-rose-400 to-red-700">
    <div class="bg-white p-8 rounded-2xl shadow-lg w-96 text-center">
      <h2 class="text-xl font-bold mb-6">Sign In</h2>
      <p class="text-gray-600 text-sm mb-4 py-4">
        Sign-in using the Google account you registered with to access your application or course dashboard.
      </p>
      <GoogleLogin
        class="flex items-center justify-center w-full py-2 px-4 bg-white border border-gray-300 rounded-md shadow-sm text-gray-700 font-medium hover:bg-gray-100 transition duration-200 hover:cursor-pointer"
        :client-id="googleClientId"
        @success="handleLoginSuccess"
        @error="handleLoginFailure"
      >
        <div class="flex items-center justify-center w-full space-x-2">
          <img src="https://developers.google.com/identity/images/g-logo.png" class="h-5 w-5" alt="Google logo" />
          <span class="text-center pl-2">Login with Google</span>
        </div>
      </GoogleLogin>
    </div>
  </div>
</template>

  
  <style scoped>

  </style>
  