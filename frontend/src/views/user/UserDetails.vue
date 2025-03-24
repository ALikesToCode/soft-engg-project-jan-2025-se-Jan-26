<template>
  <div class="flex h-screen bg-gray-50">
    <SideNavBar />
    <div class="flex-1 p-6 overflow-y-auto">
      <div class="max-w-5xl mx-auto">
        <!-- Profile Header -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
          <div class="flex items-center space-x-6">
            <div class="relative">
              <img
                :src="userProfile.avatar"
                alt="Profile"
                class="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg"
              />
              <button
                class="absolute bottom-0 right-0 bg-blue-600 text-white p-2 rounded-full shadow-lg hover:bg-blue-700"
              >
                <i class="fas fa-camera text-sm"></i>
              </button>
            </div>
            <div class="flex-1">
              <div class="flex items-center justify-between">
                <div>
                  <h1 class="text-2xl font-bold text-gray-800">{{ userProfile.name }}</h1>
                  <p class="text-gray-600">{{ userProfile.email }}</p>
                </div>
                <button
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Edit Profile
                </button>
              </div>
              <div class="mt-4 flex space-x-4">
                <div class="text-center">
                  <p class="text-2xl font-bold text-gray-800">{{ userProfile.coursesCompleted }}</p>
                  <p class="text-sm text-gray-600">Courses Completed</p>
                </div>
                <div class="text-center">
                  <p class="text-2xl font-bold text-gray-800">
                    {{ userProfile.certificatesEarned }}
                  </p>
                  <p class="text-sm text-gray-600">Certificates</p>
                </div>
                <div class="text-center">
                  <p class="text-2xl font-bold text-gray-800">{{ userProfile.hoursLearned }}</p>
                  <p class="text-sm text-gray-600">Hours Learned</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Personal Information -->
          <div class="md:col-span-2">
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
              <h2 class="text-xl font-semibold text-gray-800 mb-4">Personal Information</h2>
              <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                    <input
                      type="text"
                      v-model="userProfile.name"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
                    <input
                      type="text"
                      v-model="userProfile.username"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    v-model="userProfile.email"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Bio</label>
                  <textarea
                    v-model="userProfile.bio"
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Learning Preferences -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 class="text-xl font-semibold text-gray-800 mb-4">Learning Preferences</h2>
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2"
                    >Preferred Learning Time</label
                  >
                  <div class="flex space-x-4">
                    <label v-for="time in learningTimes" :key="time" class="flex items-center">
                      <input
                        type="radio"
                        :value="time"
                        v-model="userProfile.preferredTime"
                        class="mr-2"
                      />
                      <span>{{ time }}</span>
                    </label>
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Learning Goals</label>
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="goal in learningGoals"
                      :key="goal"
                      :class="[
                        'px-3 py-1 rounded-full text-sm',
                        userProfile.selectedGoals.includes(goal)
                          ? 'bg-blue-100 text-blue-800 border-blue-200'
                          : 'bg-gray-100 text-gray-800 border-gray-200',
                      ]"
                      @click="toggleGoal(goal)"
                    >
                      {{ goal }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Achievements and Badges -->
          <div class="md:col-span-1">
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 class="text-xl font-semibold text-gray-800 mb-4">Achievements</h2>
              <div class="space-y-4">
                <div
                  v-for="badge in userProfile.badges"
                  :key="badge.id"
                  class="flex items-center p-3 bg-gray-50 rounded-lg"
                >
                  <img :src="badge.icon" :alt="badge.name" class="w-12 h-12 mr-4" />
                  <div>
                    <h3 class="font-medium text-gray-800">{{ badge.name }}</h3>
                    <p class="text-sm text-gray-600">{{ badge.description }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SideNavBar from '../../layouts/SideNavBar.vue'
import api from '@/utils/api'

export default {
  components: {
    SideNavBar,
  },
  data() {
    return {
      userProfile: {
        name: 'John Doe',
        username: 'johndoe',
        email: 'john.doe@example.com',
        avatar: '/images/profile-avatar.jpg',
        bio: 'Passionate learner interested in web development and artificial intelligence.',
        coursesCompleted: 12,
        certificatesEarned: 5,
        hoursLearned: 156,
        preferredTime: 'Morning',
        selectedGoals: ['Web Development', 'Machine Learning'],
        badges: [
          {
            id: 1,
            name: 'Quick Learner',
            description: 'Completed 5 courses in one month',
            icon: '/images/badges/quick-learner.svg',
          },
          {
            id: 2,
            name: 'Perfect Score',
            description: 'Achieved 100% in course assessment',
            icon: '/images/badges/perfect-score.svg',
          },
          {
            id: 3,
            name: 'Consistent Learner',
            description: '30 days learning streak',
            icon: '/images/badges/consistent-learner.svg',
          },
        ],
      },
      learningTimes: ['Morning', 'Afternoon', 'Evening', 'Night'],
      learningGoals: [
        'Web Development',
        'Machine Learning',
        'Mobile Development',
        'Data Science',
        'Cloud Computing',
        'Cybersecurity',
      ],
    }
  },
  methods: {
    toggleGoal(goal) {
      if (this.userProfile.selectedGoals.includes(goal)) {
        this.userProfile.selectedGoals = this.userProfile.selectedGoals.filter((g) => g !== goal)
      } else {
        this.userProfile.selectedGoals.push(goal)
      }
    },
  },
}
</script>

<style scoped>
input:focus,
textarea:focus {
  outline: none;
}
</style>
