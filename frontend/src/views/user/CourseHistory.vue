<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-800">Course History</h1>
        <p class="text-gray-600 mt-1">View your completed courses and academic progress</p>
      </div>

      <!-- Stats Overview -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="text-sm text-gray-500 mb-1">Total Courses</div>
          <div class="text-2xl font-bold text-gray-800">{{ completedCourses.length }}</div>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="text-sm text-gray-500 mb-1">Average Grade</div>
          <div class="text-2xl font-bold text-gray-800">{{ averageGrade }}%</div>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="text-sm text-gray-500 mb-1">Total Credits</div>
          <div class="text-2xl font-bold text-gray-800">{{ totalCredits }}</div>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="text-sm text-gray-500 mb-1">Completion Rate</div>
          <div class="text-2xl font-bold text-gray-800">{{ completionRate }}%</div>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <div class="flex flex-wrap gap-4">
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 mb-2">Search Courses</label>
            <input 
              type="text"
              v-model="searchQuery"
              placeholder="Search by course name or instructor"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500"
            >
          </div>
          <div class="w-48">
            <label class="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
            <select 
              v-model="sortBy"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500"
            >
              <option value="date">Completion Date</option>
              <option value="name">Course Name</option>
              <option value="grade">Grade</option>
              <option value="credits">Credits</option>
            </select>
          </div>
          <div class="w-48">
            <label class="block text-sm font-medium text-gray-700 mb-2">Grade Filter</label>
            <select 
              v-model="gradeFilter"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500"
            >
              <option value="all">All Grades</option>
              <option value="A">A Grade</option>
              <option value="B">B Grade</option>
              <option value="C">C Grade</option>
              <option value="D">D Grade</option>
            </select>
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
                <h3 class="text-lg font-semibold text-gray-800">{{ course.title }}</h3>
                <span 
                  class="px-3 py-1 rounded-full text-sm font-medium"
                  :class="getGradeClass(course.grade)"
                >
                  Grade: {{ course.grade }}
                </span>
              </div>
              
              <p class="text-gray-600 mt-1">{{ course.description }}</p>
              
              <div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div class="text-sm text-gray-500">Instructor</div>
                  <div class="font-medium">{{ course.instructor }}</div>
                </div>
                <div>
                  <div class="text-sm text-gray-500">Completed On</div>
                  <div class="font-medium">{{ formatDate(course.completionDate) }}</div>
                </div>
                <div>
                  <div class="text-sm text-gray-500">Credits</div>
                  <div class="font-medium">{{ course.credits }}</div>
                </div>
                <div>
                  <div class="text-sm text-gray-500">Certificate</div>
                  <a 
                    v-if="course.certificateUrl"
                    :href="course.certificateUrl"
                    target="_blank"
                    class="text-maroon-600 hover:text-maroon-700 font-medium"
                  >
                    View Certificate
                  </a>
                  <span v-else class="text-gray-400">Not Available</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="filteredCourses.length === 0" class="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-100">
          <div class="text-gray-500">No courses found matching your criteria</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CourseHistory',
  data() {
    return {
      searchQuery: '',
      sortBy: 'date',
      gradeFilter: 'all',
      completedCourses: [
        {
          id: 1,
          title: 'Introduction to Programming',
          description: 'Fundamentals of programming using Python',
          instructor: 'Dr. Sarah Johnson',
          completionDate: new Date('2023-12-15'),
          grade: 'A',
          credits: 3,
          certificateUrl: '#'
        },
        {
          id: 2,
          title: 'Data Structures',
          description: 'Advanced data structures and algorithms',
          instructor: 'Prof. Michael Chen',
          completionDate: new Date('2023-11-20'),
          grade: 'B+',
          credits: 4,
          certificateUrl: '#'
        },
        {
          id: 3,
          title: 'Web Development',
          description: 'Full-stack web development with modern technologies',
          instructor: 'Dr. Emily Brown',
          completionDate: new Date('2023-10-05'),
          grade: 'A-',
          credits: 3,
          certificateUrl: '#'
        }
      ]
    }
  },
  computed: {
    filteredCourses() {
      let courses = [...this.completedCourses];

      // Apply search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        courses = courses.filter(course => 
          course.title.toLowerCase().includes(query) ||
          course.instructor.toLowerCase().includes(query)
        );
      }

      // Apply grade filter
      if (this.gradeFilter !== 'all') {
        courses = courses.filter(course => 
          course.grade.startsWith(this.gradeFilter)
        );
      }

      // Apply sorting
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
      return ((total / this.completedCourses.length) * 10).toFixed(1);
    },
    totalCredits() {
      return this.completedCourses.reduce((sum, course) => sum + course.credits, 0);
    },
    completionRate() {
      // Assuming total enrolled courses is stored somewhere
      const totalEnrolled = 10; // This should come from your data
      return Math.round((this.completedCourses.length / totalEnrolled) * 100);
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
    }
  }
}
</script> 