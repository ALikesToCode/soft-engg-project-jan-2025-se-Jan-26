<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Side Navigation -->
    <SideNavBar />

    <!-- Main Content -->
    <div class="flex-1 overflow-auto">
      <div class="py-6">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <!-- Header -->
          <div class="mb-8">
            <div class="flex justify-between items-center">
              <div>
                <h1 class="text-2xl font-semibold text-gray-900">User Management</h1>
                <p class="mt-2 text-sm text-gray-600">
                  Manage user accounts, roles, and permissions
                </p>
              </div>
              <button
                @click="openUserModal()"
                class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                Add User
              </button>
            </div>
          </div>

          <!-- Search and Filters -->
          <div class="mb-6 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <!-- Search -->
            <div class="col-span-1 sm:col-span-2">
              <label for="search" class="block text-sm font-medium text-gray-700">Search Users</label>
              <div class="mt-1 relative rounded-md shadow-sm">
                <input
                  type="text"
                  id="search"
                  v-model="searchQuery"
                  @input="handleSearch"
                  class="block w-full pr-10 sm:text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Search by name, email..."
                />
                <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>

            <!-- Role Filter -->
            <div>
              <label for="role" class="block text-sm font-medium text-gray-700">Role</label>
              <select
                id="role"
                v-model="selectedRole"
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="all">All Roles</option>
                <option value="student">Student</option>
                <option value="faculty">Faculty</option>
                <option value="support">Support</option>
              </select>
            </div>

            <!-- Status Filter -->
            <div>
              <label for="status" class="block text-sm font-medium text-gray-700">Status</label>
              <select
                id="status"
                v-model="selectedStatus"
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="pending">Pending</option>
              </select>
            </div>
          </div>

          <!-- Users Table -->
          <div class="bg-white shadow overflow-hidden sm:rounded-md">
            <div v-if="loading" class="flex justify-center items-center py-12">
              <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>

            <div v-else>
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Role
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Active
                    </th>
                    <th scope="col" class="relative px-6 py-3">
                      <span class="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="user in paginatedUsers" :key="user.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10">
                          <img
                            :src="user.avatar || defaultAvatar"
                            :alt="user.name"
                            class="h-10 w-10 rounded-full"
                          />
                        </div>
                        <div class="ml-4">
                          <div class="text-sm font-medium text-gray-900">{{ user.name }}</div>
                          <div class="text-sm text-gray-500">{{ user.email }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span :class="[
                        user.role === 'support' ? 'bg-purple-100 text-purple-800' :
                        user.role === 'faculty' ? 'bg-blue-100 text-blue-800' :
                        'bg-green-100 text-green-800',
                        'px-2 inline-flex text-xs leading-5 font-semibold rounded-full'
                      ]">
                        {{ user.role }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span :class="[
                        user.status === 'active' ? 'bg-green-100 text-green-800' :
                        user.status === 'inactive' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800',
                        'px-2 inline-flex text-xs leading-5 font-semibold rounded-full'
                      ]">
                        {{ user.status }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ user.lastActive? formatDate(user.lastActive) : 'N/A' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div class="flex justify-end space-x-3">
                        <button
                          @click="openUserModal(user)"
                          class="text-blue-600 hover:text-blue-900"
                        >
                          Edit
                        </button>
                        <button
                          v-if="user.status === 'active'"
                          @click="deactivateUser(user)"
                          class="text-red-600 hover:text-red-900"
                        >
                          Deactivate
                        </button>
                        <button
                          v-else
                          @click="activateUser(user)"
                          class="text-green-600 hover:text-green-900"
                        >
                          Activate
                        </button>
                        <button
                          @click="handleDeleteUser(user)"
                          class="p-2 text-red-600 hover:text-red-900"
                        >
                          <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>

              <!-- Pagination -->
              <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
                <div class="flex-1 flex justify-between sm:hidden">
                  <button
                    @click="previousPage"
                    :disabled="currentPage === 1"
                    class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Previous
                  </button>
                  <button
                    @click="nextPage"
                    :disabled="currentPage === totalPages"
                    class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Next
                  </button>
                </div>
                <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p class="text-sm text-gray-700">
                      Showing
                      <span class="font-medium">{{ paginationStart }}</span>
                      to
                      <span class="font-medium">{{ paginationEnd }}</span>
                      of
                      <span class="font-medium">{{ filteredUsers.length }}</span>
                      results
                    </p>
                  </div>
                  <div>
                    <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                      <button
                        @click="previousPage"
                        :disabled="currentPage === 1"
                        class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                      >
                        <span class="sr-only">Previous</span>
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                        </svg>
                      </button>
                      <button
                        v-for="page in displayedPages"
                        :key="page"
                        @click="goToPage(page)"
                        :class="[
                          page === currentPage
                            ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50',
                          'relative inline-flex items-center px-4 py-2 border text-sm font-medium'
                        ]"
                      >
                        {{ page }}
                      </button>
                      <button
                        @click="nextPage"
                        :disabled="currentPage === totalPages"
                        class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                      >
                        <span class="sr-only">Next</span>
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- User Modal -->
    <div v-if="showUserModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex justify-between items-start mb-4">
          <h2 class="text-lg font-medium text-gray-900">
            {{ editingUser.id ? 'Edit User' : 'Add New User' }}
          </h2>
          <button @click="closeUserModal" class="text-gray-400 hover:text-gray-500">
            <span class="sr-only">Close</span>
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="saveUser" class="space-y-4">
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-medium text-gray-700">First Name</label>
              <input
                type="text"
                v-model="editingUser.firstName"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Last Name</label>
              <input
                type="text"
                v-model="editingUser.lastName"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              v-model="editingUser.email"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Role</label>
            <select
              v-model="editingUser.role"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="student">Student</option>
              <option value="faculty">Faculty</option>
              <option value="support">Support</option>
            </select>
          </div>

          <div v-if="!editingUser.id">
            <label class="block text-sm font-medium text-gray-700">Password</label>
            <input
              type="password"
              v-model="editingUser.password"
              :required="!editingUser.id"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
            <p class="mt-1 text-sm text-gray-500">
              Password must be at least 8 characters long
            </p>
          </div>

          <div>
            <label class="flex items-center">
              <input
                type="checkbox"
                v-model="editingUser.status"
                :true-value="'active'"
                :false-value="'inactive'"
                class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-600">Active Account</span>
            </label>
          </div>

          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="closeUserModal"
              class="px-4 py-2 border rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              {{ editingUser.id ? 'Update' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useRouter } from 'vue-router'
import { format } from 'date-fns'
import { debounce } from 'lodash'
import SideNavBar from '@/layouts/SideNavBar.vue'
import useAuthStore from '@/stores/useAuthStore'
import { useUserStore } from '@/stores/userStore'

export default {
  name: 'UserManagement',
  components: {
    SideNavBar
  },
  setup() {
    const toast = useToast()
    const router = useRouter()
    const authStore = useAuthStore()
    const userStore = useUserStore()

    // Check if user has admin access
    const isAuthorized = computed(() => {
      if (import.meta.env.DEV) return true
      return authStore.userRole === 'support'
    })

    // Redirect unauthorized users
    if (!isAuthorized.value && !import.meta.env.DEV) {
      toast.error('Unauthorized access')
      router.push('/support/dashboard')
    }

    // State
    const loading = ref(false)
    const searchQuery = ref('')
    const selectedRole = ref('all')
    const selectedStatus = ref('all')
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const showUserModal = ref(false)
    const editingUser = ref({
      firstName: '',
      lastName: '',
      email: '',
      role: 'student',
      status: 'active',
      password: ''
    })
    const defaultAvatar = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iMzYiIHI9IjIwIiBmaWxsPSIjOTA5MDkwIi8+PHBhdGggZD0iTTIwLDg1IEMzMCw2NSA3MCw2NSA4MCw4NSIgZmlsbD0iIzkwOTA5MCIvPjwvc3ZnPg=='

    // Computed
    const filteredUsers = computed(() => {
      let users = userStore.users

      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        users = users.filter(user => 
          user.name.toLowerCase().includes(query) ||
          user.email.toLowerCase().includes(query)
        )
      }

      if (selectedRole.value !== 'all') {
        users = users.filter(user => user.role === selectedRole.value)
      }

      if (selectedStatus.value !== 'all') {
        users = users.filter(user => user.status === selectedStatus.value)
      }

      return users
    })

    const totalPages = computed(() => Math.ceil(filteredUsers.value.length / itemsPerPage.value))

    const paginatedUsers = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return filteredUsers.value.slice(start, end)
    })

    const paginationStart = computed(() => {
      return (currentPage.value - 1) * itemsPerPage.value + 1
    })

    const paginationEnd = computed(() => {
      return Math.min(currentPage.value * itemsPerPage.value, filteredUsers.value.length)
    })

    const displayedPages = computed(() => {
      const pages = []
      const maxPages = 5
      let start = Math.max(1, currentPage.value - Math.floor(maxPages / 2))
      let end = Math.min(totalPages.value, start + maxPages - 1)

      if (end - start + 1 < maxPages) {
        start = Math.max(1, end - maxPages + 1)
      }

      for (let i = start; i <= end; i++) {
        pages.push(i)
      }

      return pages
    })

    // Methods
    function formatDate(date) {
      if (!date || isNaN(new Date(date))) {
        return 'N/A' // Fallback text for invalid dates
      }
      return format(new Date(date), 'MMM d, yyyy HH:mm')
    }

    const handleSearch = debounce((value) => {
      searchQuery.value = value
      currentPage.value = 1
    }, 300)

    function openUserModal(user = null) {
      if (user) {
        const [firstName, ...lastNameParts] = user.name.split(' ')
        editingUser.value = {
          ...user,
          firstName,
          lastName: lastNameParts.join(' '),
          password: ''
        }
      } else {
        editingUser.value = {
          firstName: '',
          lastName: '',
          email: '',
          role: 'student',
          status: 'active',
          password: ''
        }
      }
      showUserModal.value = true
    }

    function closeUserModal() {
      if (confirm('Are you sure you want to close? Any unsaved changes will be lost.')) {
        showUserModal.value = false
        editingUser.value = {
          firstName: '',
          lastName: '',
          email: '',
          role: 'student',
          status: 'active',
          password: ''
        }
      }
    }

    async function saveUser() {
      try {
        loading.value = true
        const userData = {
          ...editingUser.value,
          name: `${editingUser.value.firstName} ${editingUser.value.lastName}`
        }

        if (userData.id) {
          await userStore.updateUser(userData.id, userData)
          toast.success('User updated successfully')
        } else {
          await userStore.createUser(userData)
          toast.success('User created successfully')
        }

        showUserModal.value = false
        await loadUsers()
      } catch (error) {
        toast.error(error.message || 'Failed to save user')
      } finally {
        loading.value = false
      }
    }

    async function loadUsers() {
      try {
        loading.value = true
        await userStore.fetchUsers()
      } catch (error) {
        toast.error('Failed to load users')
      } finally {
        loading.value = false
      }
    }

    async function handleDeleteUser(user) {
      if (confirm(`Are you sure you want to delete ${user.name}? This action cannot be undone.`)) {
        try {
          await userStore.deleteUser(user.id)
          toast.success('User deleted successfully')
          await loadUsers() // Refresh the user list
        } catch (error) {
          toast.error(error.message || 'Failed to delete user')
        }
      }
    }

    async function deactivateUser(user) {
      if (confirm(`Are you sure you want to deactivate ${user.name}?`)) {
        try {
          await userStore.updateUser(user.id, { ...user, status: 'inactive' })
          toast.success('User deactivated successfully')
          await loadUsers()
        } catch (error) {
          toast.error('Failed to deactivate user')
        }
      }
    }

    async function activateUser(user) {
      try {
        await userStore.updateUser(user.id, { ...user, status: 'active' })
        toast.success('User activated successfully')
        await loadUsers()
      } catch (error) {
        toast.error('Failed to activate user')
      }
    }

    function previousPage() {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }

    function nextPage() {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }

    function goToPage(page) {
      currentPage.value = page
    }

    // Load initial data
    onMounted(async () => {
      if (isAuthorized.value) {
        await loadUsers()
      }
    })

    return {
      loading,
      searchQuery,
      selectedRole,
      selectedStatus,
      currentPage,
      showUserModal,
      editingUser,
      defaultAvatar,
      filteredUsers,
      paginatedUsers,
      totalPages,
      paginationStart,
      paginationEnd,
      displayedPages,
      handleSearch,
      formatDate,
      openUserModal,
      closeUserModal,
      saveUser,
      handleDeleteUser,
      deactivateUser,
      activateUser,
      previousPage,
      nextPage,
      goToPage,
      isAuthorized
    }
  }
}
</script> 