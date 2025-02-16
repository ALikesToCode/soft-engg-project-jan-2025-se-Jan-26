<template>
  <div class="fixed top-4 right-4 z-50 space-y-2">
    <TransitionGroup name="notification">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="[
          'flex items-center p-4 rounded-lg shadow-lg transform transition-all duration-300',
          notification.color
        ]"
      >
        <span class="material-icons mr-2">{{ notification.icon }}</span>
        <span class="font-medium">{{ notification.message }}</span>
        <button
          @click="removeNotification(notification.id)"
          class="ml-4 p-1 rounded-full hover:bg-black/10 transition-colors"
        >
          <span class="material-icons text-sm">close</span>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script>
import { useNotification } from '@/composables/useNotification'

export default {
  name: 'NotificationToast',
  setup() {
    const { notifications, removeNotification } = useNotification()

    return {
      notifications,
      removeNotification
    }
  }
}
</script>

<style scoped>
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style> 