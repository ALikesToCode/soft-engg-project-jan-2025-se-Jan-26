import { ref } from 'vue'

const MAX_NOTIFICATIONS = 5
const NOTIFICATION_DURATION = 3000
const notifications = ref([])
let timeouts = new Map()

export function useNotification() {
  const notify = {
    success(message, options = {}) {
      addNotification({
        type: 'success',
        message,
        icon: 'check_circle',
        color: 'bg-green-100 text-green-800',
        ...options
      })
    },
    
    error(message, options = {}) {
      addNotification({
        type: 'error',
        message,
        icon: 'error_outline',
        color: 'bg-red-100 text-red-800',
        ...options
      })
    },
    
    info(message, options = {}) {
      addNotification({
        type: 'info',
        message,
        icon: 'info',
        color: 'bg-blue-100 text-blue-800',
        ...options
      })
    }
  }

  const addNotification = (notification) => {
    const id = Date.now()
    
    // Check for duplicates
    const isDuplicate = notifications.value.some(n => 
      n.message === notification.message && 
      n.type === notification.type &&
      Date.now() - n.id < NOTIFICATION_DURATION
    )
    
    if (isDuplicate) return

    // Remove oldest notification if at max
    if (notifications.value.length >= MAX_NOTIFICATIONS) {
      const oldestId = notifications.value[0].id
      removeNotification(oldestId)
    }

    // Add new notification
    notifications.value.push({
      id,
      ...notification,
      timestamp: Date.now()
    })

    // Set timeout for auto-removal
    const timeout = setTimeout(() => removeNotification(id), NOTIFICATION_DURATION)
    timeouts.set(id, timeout)
  }

  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
      
      // Clear timeout
      const timeout = timeouts.get(id)
      if (timeout) {
        clearTimeout(timeout)
        timeouts.delete(id)
      }
    }
  }

  // Cleanup function for component unmount
  const cleanup = () => {
    timeouts.forEach(timeout => clearTimeout(timeout))
    timeouts.clear()
    notifications.value = []
  }

  return {
    notifications,
    notify,
    removeNotification,
    cleanup
  }
} 