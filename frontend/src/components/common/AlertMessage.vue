<template>
  <transition name="fade">
    <div
      v-if="message"
      :class="alertClass"
      class="fixed top-16 left-1/2 transform -translate-x-1/2 px-6 py-3 rounded-lg shadow-md w-3/4 md:w-1/2 text-center z-50"
    >
      {{ message }}
    </div>
  </transition>
</template>

<script>
export default {
  name: 'AlertMessage',
  props: {
    message: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      default: 'info', // Can be 'success', 'error', 'warning', 'info'
    },
  },
  computed: {
    alertClass() {
      return {
        'bg-green-500 text-white': this.type === 'success',
        'bg-red-500 text-white': this.type === 'error',
        'bg-yellow-500 text-gray-800': this.type === 'warning',
        'bg-blue-500 text-white': this.type === 'info',
      }
    },
  },
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>
