<template>
  <div>
    <!-- Mobile Toggle Button - Only visible on small screens -->
    <button
      v-if="isCollapsible"
      @click="toggleSidebar"
      class="lg:hidden fixed bottom-4 right-4 z-50 rounded-full bg-maroon-600 text-white p-3 shadow-lg hover:bg-maroon-700 transition-all duration-300"
      aria-label="Toggle course navigation"
    >
      <span class="material-symbols-outlined">
        {{ isCollapsed ? 'menu' : 'close' }}
      </span>
    </button>

    <!-- Sidebar -->
    <div
      class="fixed lg:relative inset-y-0 left-0 z-40 bg-slate-50 border-r border-slate-200 overflow-y-auto transition-all duration-300 h-full transform lg:transform-none"
      :class="[
        isCollapsed ? '-translate-x-full' : 'translate-x-0',
        isCollapsible ? 'w-full sm:w-3/4 md:w-2/3 lg:w-80 xl:w-96' : 'w-full lg:w-80 xl:w-96',
      ]"
    >
      <!-- Mobile Header - Only visible on small screens when sidebar is open -->
      <div
        v-if="isCollapsible"
        class="lg:hidden flex items-center justify-between p-4 border-b border-slate-200"
      >
        <h2 class="text-lg font-bold text-slate-900">Course Navigation</h2>
        <button
          @click="toggleSidebar"
          class="p-2 rounded-full hover:bg-slate-200 transition-colors"
        >
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <!-- Sidebar Content -->
      <div class="p-5 h-full overflow-y-auto pb-24 lg:pb-5">
        <div class="mb-6 space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-bold text-slate-900">Course Journey</h2>
            <!-- <span class="text-sm text-slate-600 font-medium bg-slate-100 px-3 py-1 rounded-full">
              {{ completedLectureCount }}/{{ totalLectures }} lessons
            </span> -->
          </div>
          <div class="relative w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
            <div
              class="absolute inset-0 bg-gradient-to-r from-maroon-500 to-maroon-600 rounded-full transition-all duration-500"
              :style="{ width: `${(completedLectureCount / totalLectures) * 100}%` }"
            ></div>
          </div>
        </div>

        <!-- Weeks List -->
        <div class="space-y-3">
          <div
            v-for="(week, weekIndex) in weeks"
            :key="weekIndex"
            class="group bg-white rounded-xl border border-slate-200 hover:border-maroon-200 transition-all duration-300 shadow-sm hover:shadow-md"
          >
            <div
              class="flex items-center justify-between p-4 cursor-pointer"
              @click="toggleWeek(week)"
            >
              <div class="space-y-1">
                <h3 class="font-semibold text-slate-900">Week {{ weekIndex + 1 }}</h3>
                <p class="text-sm text-slate-500 flex flex-wrap items-center gap-1">
                  <span>{{ week.lectures.length }} modules</span>
                  <span class="text-slate-300">•</span>
                  <span>{{ week.duration }}</span>
                </p>
              </div>
              <div class="flex items-center space-x-2">
                <!-- <div class="w-16 h-8 bg-maroon-50 rounded-lg flex items-center justify-center">
                  <span class="text-sm font-medium text-maroon-600"
                    >{{ getWeekProgress(week) }}%</span
                  >
                </div> -->
                <span
                  class="material-symbols-outlined text-maroon-400 transition-transform duration-300 transform group-hover:text-maroon-600"
                  :class="[week.isExpanded ? 'rotate-180' : '']"
                  >expand_more</span
                >
              </div>
            </div>

            <!-- Week Lectures -->
            <div
              v-show="week.isExpanded"
              class="border-t border-slate-100 pt-2 transition-all duration-300"
            >
              <div
                v-for="(lecture, lectureIndex) in week.lectures"
                :key="lectureIndex"
                @click="selectLecture(lecture)"
                class="flex items-start p-3 mx-2 mb-2 rounded-lg cursor-pointer transition-all duration-300 hover:bg-maroon-50/50 border border-transparent hover:border-maroon-200"
                :class="{ 'bg-maroon-50 border-maroon-200': lecture.id === selectedLecture?.id }"
              >
                <div class="flex-shrink-0 mt-1.5">
                  <span
                    class="material-symbols-outlined text-sm transform transition-all"
                    :class="[
                      lecture.completed
                        ? 'text-emerald-500 scale-110'
                        : lecture.id === selectedLecture?.id
                          ? getActivityIcon(lecture.type).color + ' scale-110'
                          : getActivityIcon(lecture.type).baseColor +
                            ' hover:' +
                            getActivityIcon(lecture.type).color,
                    ]"
                    >{{
                      lecture.completed
                        ? 'check_circle'
                        : getActivityIcon(lecture.type).materialIcon
                    }}</span
                  >
                </div>
                <div class="ml-3 flex-grow">
                  <h4 class="text-sm font-medium text-slate-900">{{ lecture.title }}</h4>
                  <div class="flex flex-wrap items-center mt-1.5 gap-x-3 gap-y-1">
                    <div class="flex items-center space-x-1 text-slate-500 text-xs">
                      <span class="material-symbols-outlined text-slate-400 text-sm">schedule</span>
                      <span>{{ lecture.duration || '15 min' }}</span>
                    </div>
                    <div
                      v-if="lecture.type !== 'video'"
                      class="flex items-center space-x-1 text-xs"
                      :class="getActivityIcon(lecture.type).textColor"
                    >
                      <span class="material-symbols-outlined text-sm">{{
                        getActivityBadgeIcon(lecture.type)
                      }}</span>
                      <span>{{ getActivityLabel(lecture.type) }}</span>
                    </div>
                    <div
                      v-if="lecture.materials?.length"
                      class="flex items-center space-x-1 text-slate-500 text-xs"
                    >
                      <span class="material-symbols-outlined text-maroon-400 text-sm"
                        >attach_file</span
                      >
                      <span>{{ lecture.materials.length }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Backdrop overlay for mobile - only visible when sidebar is open on mobile -->
    <div
      v-if="isCollapsible && !isCollapsed"
      class="fixed inset-0 bg-slate-900/50 z-30 lg:hidden"
      @click="toggleSidebar"
    ></div>
  </div>
</template>

<script>
export default {
  name: 'CourseSideNav',
  props: {
    weeks: {
      type: Array,
      required: true,
    },
    selectedLecture: {
      type: Object,
      default: null,
    },
    completedLectures: {
      type: Array,
      default: () => [],
    },
    totalLectures: {
      type: Number,
      required: true,
    },
    isCollapsed: {
      type: Boolean,
      default: false,
    },
    isCollapsible: {
      type: Boolean,
      default: true,
    },
  },
  emits: ['select-lecture', 'toggle'],
  computed: {
    completedLectureCount() {
      return this.completedLectures?.length || 0
    },
  },
  methods: {
    toggleSidebar() {
      this.$emit('toggle')
    },
    toggleWeek(week) {
      // Use Vue.set for reactivity with arrays/objects
      week.isExpanded = !week.isExpanded
    },
    selectLecture(lecture) {
      this.$emit('select-lecture', lecture)

      // On mobile, automatically collapse the sidebar after selection
      if (this.isCollapsible && window.innerWidth < 1024) {
        this.$emit('toggle')
      }
    },
    getWeekProgress(week) {
      if (!week.lectures || week.lectures.length === 0) return 0

      const completedInWeek = week.lectures.filter((lecture) =>
        this.completedLectures.includes(lecture.id),
      ).length
      return Math.round((completedInWeek / week.lectures.length) * 100)
    },
    getActivityIcon(type) {
      const icons = {
        video: {
          materialIcon: 'play_circle',
          baseColor: 'text-maroon-400',
          color: 'text-maroon-600',
          textColor: 'text-maroon-600',
        },
        assignment: {
          materialIcon: 'description',
          baseColor: 'text-yellow-400',
          color: 'text-yellow-600',
          textColor: 'text-yellow-600',
        },
        'graded-assignment': {
          materialIcon: 'grade',
          baseColor: 'text-maroon-400',
          color: 'text-maroon-600',
          textColor: 'text-maroon-600',
        },
        quiz: {
          materialIcon: 'quiz',
          baseColor: 'text-yellow-400',
          color: 'text-yellow-600',
          textColor: 'text-yellow-600',
        },
      }
      return icons[type] || icons.video
    },
    getActivityBadgeIcon(type) {
      const icons = {
        assignment: 'edit',
        'graded-assignment': 'school',
        quiz: 'timer',
      }
      return icons[type] || ''
    },
    getActivityLabel(type) {
      const labels = {
        assignment: 'Assignment',
        'graded-assignment': 'Graded',
        quiz: 'Quiz',
      }
      return labels[type] || ''
    },
  },
  mounted() {
    // Expand the week containing the selected lecture (if any)
    if (this.selectedLecture && this.weeks) {
      const weekWithSelectedLecture = this.weeks.find((week) =>
        week.lectures.some((lecture) => lecture.id === this.selectedLecture.id),
      )

      if (weekWithSelectedLecture) {
        this.$nextTick(() => {
          weekWithSelectedLecture.isExpanded = true
        })
      }
    }
  },
}
</script>

<style scoped>
/* Add slide-in/out animation */
.transform {
  transition-property: transform;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* Add space at the bottom on mobile for the floating toggle button */
@media (max-width: 1023px) {
  .pb-24 {
    padding-bottom: 6rem;
  }
}
</style>
