<template>
  <div class="support-role-indicator">
    <div class="role-status" :class="{ active: isActive }">
      <span class="role-label">Support Role</span>
      <span class="status-dot"></span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const isActive = ref(true) // This should be connected to your actual support role status
</script>

<style scoped>
.support-role-indicator {
  padding: 8px 16px;
  border-radius: 4px;
  background-color: #f5f5f5;
}

.role-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.role-label {
  font-weight: 500;
  color: #666;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #ccc;
}

.role-status.active .status-dot {
  background-color: #4CAF50;
}
</style>
