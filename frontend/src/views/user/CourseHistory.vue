<template>
  <div class="flex h-screen bg-gray-50">
    <SideNavBar />
    <div class="flex-1 p-6 overflow-y-auto">
      <div class="max-w-7xl mx-auto">
        <!-- Header with Academic Progress -->
        <div class="mb-8">
          <div class="flex justify-between items-center mb-4">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">Course History</h1>
              <p class="text-gray-600 mt-1">Track your academic journey and achievements</p>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-gray-900">{{ averageGrade }}%</div>
              <div class="text-sm text-gray-600">Overall Grade Average</div>
            </div>
          </div>

          <!-- Progress Bar -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div class="flex items-center justify-between text-sm mb-2">
              <span class="font-medium text-gray-900">Academic Progress</span>
              <span class="text-gray-600">{{ completedCourses.length }} of {{ totalEnrolled }} Courses Completed</span>
            </div>
            <div class="w-full bg-gray-100 rounded-full h-2.5">
              <div 
                class="bg-maroon-600 h-2.5 rounded-full transition-all duration-500"
                :style="{ width: `${completionRate}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Stats Overview -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center">
            <div class="p-3 bg-maroon-50 rounded-lg mr-4">
              <span class="material-icons text-maroon-600">school</span>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ totalCredits }}</div>
              <div class="text-sm text-gray-600">Credits Earned</div>
            </div>
          </div>
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center">
            <div class="p-3 bg-blue-50 rounded-lg mr-4">
              <span class="material-icons text-blue-600">verified</span>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ certificatesCount }}</div>
              <div class="text-sm text-gray-600">Certificates Earned</div>
            </div>
          </div>
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center">
            <div class="p-3 bg-green-50 rounded-lg mr-4">
              <span class="material-icons text-green-600">trending_up</span>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ currentSemesterGPA }}</div>
              <div class="text-sm text-gray-600">Current Semester GPA</div>
            </div>
          </div>
        </div>

        <!-- Filters -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
          <div class="flex flex-wrap gap-6">
            <div class="flex-1 min-w-[250px]">
              <label class="block text-sm font-medium text-gray-900 mb-2">Search Courses</label>
              <div class="relative">
                <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="material-icons text-gray-400 text-lg">search</span>
                </span>
                <input 
                  type="text"
                  v-model="searchQuery"
                  placeholder="Search by course name or instructor"
                  class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 text-gray-900 placeholder-gray-500"
                >
              </div>
            </div>
            <div class="w-48">
              <label class="block text-sm font-medium text-gray-900 mb-2">Sort By</label>
              <div class="relative">
                <select 
                  v-model="sortBy"
                  class="w-full pl-3 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 text-gray-900 appearance-none"
                >
                  <option value="date">Recent First</option>
                  <option value="name">Course Name</option>
                  <option value="grade">Highest Grade</option>
                  <option value="credits">Most Credits</option>
                </select>
                <span class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <span class="material-icons text-gray-400 text-lg">expand_more</span>
                </span>
              </div>
            </div>
            <div class="w-48">
              <label class="block text-sm font-medium text-gray-900 mb-2">Grade Filter</label>
              <div class="relative">
                <select 
                  v-model="gradeFilter"
                  class="w-full pl-3 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 text-gray-900 appearance-none"
                >
                  <option value="all">All Grades</option>
                  <option value="A">A Grades (90-100)</option>
                  <option value="B">B Grades (80-89)</option>
                  <option value="C">C Grades (70-79)</option>
                  <option value="D">D Grades (60-69)</option>
                </select>
                <span class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <span class="material-icons text-gray-400 text-lg">expand_more</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Course List -->
        <div class="space-y-4">
          <div v-for="course in filteredCourses" 
               :key="course.id"
               class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-4">
                  <h3 class="text-lg font-semibold text-gray-900">{{ course.title }}</h3>
                  <span 
                    class="px-3 py-1 rounded-full text-sm font-medium flex items-center"
                    :class="getGradeClass(course.grade)"
                  >
                    <span class="material-icons text-sm mr-1">grade</span>
                    {{ course.grade }}
                  </span>
                </div>
                
                <p class="text-gray-700 mt-2">{{ course.description }}</p>
                
                <div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-6">
                  <div>
                    <div class="flex items-center text-sm text-gray-600 mb-1">
                      <span class="material-icons text-sm mr-1">person</span>
                      Instructor
                    </div>
                    <div class="font-medium text-gray-900">{{ course.instructor }}</div>
                  </div>
                  <div>
                    <div class="flex items-center text-sm text-gray-600 mb-1">
                      <span class="material-icons text-sm mr-1">event</span>
                      Completed
                    </div>
                    <div class="font-medium text-gray-900">{{ formatDate(course.completionDate) }}</div>
                  </div>
                  <div>
                    <div class="flex items-center text-sm text-gray-600 mb-1">
                      <span class="material-icons text-sm mr-1">stars</span>
                      Credits
                    </div>
                    <div class="font-medium text-gray-900">{{ course.credits }}</div>
                  </div>
                  <div>
                    <div class="flex items-center text-sm text-gray-600 mb-1">
                      <span class="material-icons text-sm mr-1">verified</span>
                      Certificate
                    </div>
                    <a 
                      v-if="course.certificateUrl"
                      :href="course.certificateUrl"
                      target="_blank"
                      class="text-maroon-600 hover:text-maroon-700 font-medium inline-flex items-center"
                    >
                      View Certificate
                      <span class="material-icons text-sm ml-1">open_in_new</span>
                    </a>
                    <span v-else class="text-gray-400">Not Available</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="filteredCourses.length === 0" class="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-100">
            <span class="material-icons text-gray-400 text-4xl mb-2">search_off</span>
            <div class="text-gray-600">No courses found matching your criteria</div>
            <button 
              @click="resetFilters"
              class="mt-4 text-maroon-600 hover:text-maroon-700 font-medium"
            >
              Reset Filters
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SideNavBar from '@/layouts/SideNavBar.vue'

export default {
  name: 'CourseHistory',
  components: {
    SideNavBar
  },
  data() {
    return {
      searchQuery: '',
      sortBy: 'date',
      gradeFilter: 'all',
      totalEnrolled: 10,
      completedCourses: [
        {
          id: 1,
          title: 'Introduction to Programming',
          description: 'Fundamentals of programming using Python, covering basic syntax, data structures, and algorithms.',
          instructor: 'Dr. Sarah Johnson',
          completionDate: new Date('2023-12-15'),
          grade: 'A',
          credits: 3,
          certificateUrl: '#',
          semester: 'Fall 2023'
        },
        {
          id: 2,
          title: 'Data Structures',
          description: 'Advanced data structures and algorithms, focusing on implementation and optimization techniques.',
          instructor: 'Prof. Michael Chen',
          completionDate: new Date('2023-11-20'),
          grade: 'B+',
          credits: 4,
          certificateUrl: '#',
          semester: 'Fall 2023'
        },
        {
          id: 3,
          title: 'Web Development',
          description: 'Full-stack web development covering modern frameworks and best practices.',
          instructor: 'Dr. Emily Brown',
          completionDate: new Date('2023-10-05'),
          grade: 'A-',
          credits: 3,
          certificateUrl: '#',
          semester: 'Fall 2023'
        }
      ]
    }
  },
  computed: {
    filteredCourses() {
      let courses = [...this.completedCourses];

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        courses = courses.filter(course => 
          course.title.toLowerCase().includes(query) ||
          course.instructor.toLowerCase().includes(query) ||
          course.description.toLowerCase().includes(query)
        );
      }

      if (this.gradeFilter !== 'all') {
        courses = courses.filter(course => 
          course.grade.startsWith(this.gradeFilter)
        );
      }

      courses.sort((a, b) => {
        switch (this.sortBy) {
          case 'date':
            return b.completionDate - a.completionDate;
          case 'name':
            return a.title.localeCompare(b.title);
          case 'grade':
            return this.getGradeValue(b.grade) - this.getGradeValue(a.grade);
          case 'credits':
            return b.credits - a.credits;
          default:
            return 0;
        }
      });

      return courses;
    },
    averageGrade() {
      if (this.completedCourses.length === 0) return 0;
      const total = this.completedCourses.reduce((sum, course) => 
        sum + this.getGradeValue(course.grade), 0);
      return (total / this.completedCourses.length).toFixed(1);
    },
    totalCredits() {
      return this.completedCourses.reduce((sum, course) => sum + course.credits, 0);
    },
    completionRate() {
      return Math.round((this.completedCourses.length / this.totalEnrolled) * 100);
    },
    certificatesCount() {
      return this.completedCourses.filter(course => course.certificateUrl).length;
    },
    currentSemesterGPA() {
      const currentSemester = 'Fall 2023';
      const semesterCourses = this.completedCourses.filter(course => course.semester === currentSemester);
      
      if (semesterCourses.length === 0) return '0.00';
      
      const totalPoints = semesterCourses.reduce((sum, course) => 
        sum + (this.getGradeValue(course.grade) * course.credits), 0);
      const totalCredits = semesterCourses.reduce((sum, course) => sum + course.credits, 0);
      
      return (totalPoints / (totalCredits * 100) * 4).toFixed(2);
    }
  },
  methods: {
    formatDate(date) {
      const d = new Date(date);
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
    },
    getGradeClass(grade) {
      const firstLetter = grade.charAt(0);
      switch (firstLetter) {
        case 'A':
          return 'bg-green-100 text-green-800';
        case 'B':
          return 'bg-blue-100 text-blue-800';
        case 'C':
          return 'bg-yellow-100 text-yellow-800';
        case 'D':
          return 'bg-orange-100 text-orange-800';
        default:
          return 'bg-red-100 text-red-800';
      }
    },
    getGradeValue(grade) {
      const gradeValues = {
        'A+': 100, 'A': 95, 'A-': 90,
        'B+': 87, 'B': 83, 'B-': 80,
        'C+': 77, 'C': 73, 'C-': 70,
        'D+': 67, 'D': 63, 'D-': 60,
        'F': 0
      };
      return gradeValues[grade] || 0;
    },
    resetFilters() {
      this.searchQuery = '';
      this.sortBy = 'date';
      this.gradeFilter = 'all';
    }
  }
}
</script>

<style scoped>
.material-icons {
  font-size: inherit;
  line-height: inherit;
  vertical-align: middle;
}
</style> 