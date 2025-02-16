<script>
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'

// Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  name: 'CourseEngagementChart',
  components: { Bar },
  props: {
    courseData: {
      type: Object,
      required: true,
    },
    xlabel: {
      type: Array,
      default: 'Courses',
    },
    ylabel: {
      type: String,
      default: 'Number of Students',
    },
    chartTitle: {
      type: String,
    },
  },
  computed: {
    chartData() {
      return {
        labels: this.courseData.map((course) => course.name),
        datasets: [
          {
            label: this.xlabel,
            data: this.courseData.map((course) => course.students),
            backgroundColor: '#B5303E', // Maroon-like color
            borderRadius: 5,
          },
        ],
      }
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: this.ylabel,
            },
          },
          x: {
            title: {
              display: true,
              text: this.xlabel,
            },
          },
        },
      }
    },
  },
  methods: {},
}
</script>

<template>
  <div class="bg-white p-2 shadow-md rounded-lg">
    <h2 class="font-medium mb-3 text-center">{{ chartTitle }}</h2>
    <div class="h-80">
      <!-- Adjust height dynamically -->
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<style scoped>
/* Custom styling if needed */
</style>
