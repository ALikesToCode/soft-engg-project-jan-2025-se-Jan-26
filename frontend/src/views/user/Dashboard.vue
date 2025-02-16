<template>
  <div class="container mx-auto px-4 py-6">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Dashboard content -->
      <div v-for="(card, index) in dashboardCards" 
           :key="index" 
           class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-800">{{ card.title }}</h3>
          <span class="material-symbols-outlined text-maroon-600">{{ card.icon }}</span>
        </div>
        <div class="space-y-4">
          <div v-if="card.content" class="text-gray-600">
            {{ card.content }}
          </div>
          <div v-if="card.stats" class="flex justify-between items-center">
            <div class="text-3xl font-bold text-maroon-600">
              {{ card.stats.value }}
            </div>
            <div class="text-sm text-gray-500">
              {{ card.stats.label }}
            </div>
          </div>
          <div v-if="card.list" class="space-y-2">
            <div v-for="(item, i) in card.list" 
                 :key="i"
                 class="flex items-center justify-between p-2 rounded bg-gray-50 hover:bg-gray-100 transition-colors duration-200">
              <span class="text-gray-700">{{ item.label }}</span>
              <span class="text-maroon-600 font-medium">{{ item.value }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const dashboardCards = [
  {
    title: 'Current Courses',
    icon: 'school',
    stats: {
      value: '5',
      label: 'Active Courses'
    },
    list: [
      { label: 'In Progress', value: '3' },
      { label: 'Completed', value: '2' },
      { label: 'Upcoming', value: '1' }
    ]
  },
  {
    title: 'Recent Activity',
    icon: 'history',
    content: 'You have completed 2 assignments this week and have 3 pending submissions.',
    list: [
      { label: 'Assignments Due', value: '3' },
      { label: 'Completed', value: '2' },
      { label: 'Graded', value: '1' }
    ]
  },
  {
    title: 'Performance',
    icon: 'analytics',
    stats: {
      value: '85%',
      label: 'Average Score'
    },
    list: [
      { label: 'Highest Score', value: '95%' },
      { label: 'Lowest Score', value: '75%' },
      { label: 'Improvement', value: '+5%' }
    ]
  }
]
</script>

<style scoped>
.material-symbols-outlined {
  font-variation-settings:
    'FILL' 0,
    'wght' 400,
    'GRAD' 0,
    'opsz' 24;
}
</style> 