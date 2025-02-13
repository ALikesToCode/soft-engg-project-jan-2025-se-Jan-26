<script>
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, CategoryScale } from 'chart.js'

// Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale)

export default {
  name: 'GradeDistributionChart',
  data() {
    return {
      pieChartGradeData: {},
      activeCourse: '',
    }
  },
  components: { Pie },
  props: {
    gradeData: {
      type: Object, // Expecting an object with grade counts
      required: true,
    },
    xlabel: {
      type: String,
      default: 'Grades',
    },
    ylabel: {
      type: String,
      default: 'Number of Students',
    },
    pieChartTitle: {
      type: String,
      default: 'Grade Distribution',
    },
  },
  computed: {
    chartData() {
      return {
        labels: Object.keys(this.pieChartGradeData),
        datasets: [
          {
            label: this.xlabel,
            data: Object.values(this.pieChartGradeData),
            backgroundColor: ['#1E88E5', '#43A047', '#FFC107', '#FF9800', '#E53935', '#6D4C41'],
            borderWidth: 1,
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
            position: 'right',
          },
          tooltip: {
            callbacks: {
              label: (tooltipItem) => {
                let value = tooltipItem.raw
                let percentage = ((value / this.totalStudents) * 100).toFixed(1)
                return ` ${this.xlabel}: ${value} (${percentage}%)`
              },
            },
          },
        },
        elements: {
          arc: {
            borderWidth: 2,
          },
        },
      }
    },
    totalStudents() {
      return Object.values(this.pieChartGradeData).reduce((acc, val) => acc + val, 0)
    },
  },
  methods: {
    chooseSubjectData(course) {
      this.activeCourse = course
      this.pieChartGradeData = this.gradeData[course]
    },
  },
  mounted() {
    this.activeCourse = Object.keys(this.gradeData)[0]
    this.pieChartGradeData = this.gradeData[this.activeCourse]
  },
}
</script>

<template>
  <div class="bg-white p-2 shadow-md rounded-lg">
    <div class="mb-1">
      <span class="text-gray-700">Select a Course: </span>
      <button
        :class="course === activeCourse ? 'bg-red-700 text-gray-100' : 'text-gray-700'"
        @click="chooseSubjectData(course)"
        class="border border-red-700 px-2 py-[2px] mr-2 rounded font-medium"
        v-for="course in Object.keys(gradeData)"
        :key="course"
      >
        {{ course }}
      </button>
    </div>
    <h2 class="font-medium text-center mb-3">{{ pieChartTitle }}</h2>
    <div class="h-72 flex justify-center">
      <Pie :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<style scoped>
/* Custom styling if needed */
</style>
