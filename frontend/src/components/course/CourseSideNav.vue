<template>
  <div
    class="w-full lg:w-80 xl:w-96 bg-slate-50 border-r border-slate-200 overflow-y-auto transition-all duration-300 h-full"
  >
    <div class="p-5">
      <div class="mb-6 space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-bold text-slate-900">Course Journey</h2>
          <span class="text-sm text-slate-600 font-medium bg-slate-100 px-3 py-1 rounded-full">
            {{ completedLectureCount }}/{{ totalLectures }} lessons
          </span>
        </div>
        <div class="relative w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
          <div
            class="absolute inset-0 bg-gradient-to-r from-maroon-500 to-maroon-600 rounded-full transition-all duration-500"
            :style="{ width: `${(completedLectureCount / totalLectures) * 100}%` }"
          ></div>
        </div>
      </div>

      <div class="space-y-3">
        <div
          v-for="(week, weekIndex) in weeks"
          :key="weekIndex"
          class="group bg-white rounded-xl border border-slate-200 hover:border-maroon-200 transition-all duration-300 shadow-sm hover:shadow-md"
        >
          <div
            class="flex items-center justify-between p-4 cursor-pointer"
            @click="week.isExpanded = !week.isExpanded"
          >
            <div class="space-y-1">
              <h3 class="font-semibold text-slate-900">Week {{ weekIndex + 1 }}</h3>
              <p class="text-sm text-slate-500">
                {{ week.lectures.length }} modules • {{ week.duration }}
              </p>
            </div>
            <div class="flex items-center space-x-2">
              <div class="w-16 h-8 bg-maroon-50 rounded-lg flex items-center justify-center">
                <span class="text-sm font-medium text-maroon-600"
                  >{{ getWeekProgress(week) }}%</span
                >
              </div>
              <span
                class="material-symbols-outlined text-maroon-400 transition-transform duration-300 transform group-hover:text-maroon-600"
                :class="[week.isExpanded ? 'rotate-180' : '']"
                >expand_more</span
              >
            </div>
          </div>

          <div v-show="week.isExpanded" class="border-t border-slate-100 pt-2">
            <div
              v-for="(lecture, lectureIndex) in week.lectures"
              :key="lectureIndex"
              @click="$emit('select-lecture', lecture)"
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
                    lecture.completed ? 'check_circle' : getActivityIcon(lecture.type).materialIcon
                  }}</span
                >
              </div>
              <div class="ml-3 flex-grow">
                <h4 class="text-sm font-medium text-slate-900">{{ lecture.title }}</h4>
                <div class="flex items-center mt-1.5 space-x-3">
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
  },
  computed: {
    completedLectureCount() {
      return this.completedLectures?.length || 0
    },
  },
  emits: ['select-lecture'],
  methods: {
    getWeekProgress(week) {
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
}
</script>

<style scoped>
.material-symbols-outlined {
  font-variation-settings:
    'FILL' 1,
    'wght' 400,
    'GRAD' 0,
    'opsz' 24;
}

.material-symbols-outlined.text-sm {
  font-size: 20px;
}

button .material-symbols-outlined,
.cursor-pointer .material-symbols-outlined {
  font-variation-settings:
    'FILL' 0,
    'wght' 400,
    'GRAD' 0,
    'opsz' 24;
}

button:hover .material-symbols-outlined,
.cursor-pointer:hover .material-symbols-outlined,
.text-emerald-500.material-symbols-outlined {
  font-variation-settings:
    'FILL' 1,
    'wght' 400,
    'GRAD' 0,
    'opsz' 24;
}
</style>
