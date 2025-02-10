<template>
  <div class="w-full lg:w-80 xl:w-96 bg-white border-r border-gray-200/80 overflow-y-auto transition-all duration-300">
    <div class="p-5">
      <div class="mb-6 space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-bold text-gray-900">Course Journey</h2>
          <span class="text-sm text-gray-600 font-medium bg-gray-100 px-3 py-1 rounded-full">
            {{ completedLectures }}/{{ totalLectures }} lessons
          </span>
        </div>
        <div class="relative w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-r from-primary-500 to-primary-400 rounded-full transition-all duration-500"
               :style="{ width: `${(completedLectures/totalLectures) * 100}%` }"></div>
        </div>
      </div>
      
      <div class="space-y-3">
        <div v-for="(week, weekIndex) in weeks" :key="weekIndex" 
             class="group bg-white rounded-xl border border-gray-200/80 hover:border-primary-100
                   transition-all duration-300 shadow-sm hover:shadow-md">
          <div class="flex items-center justify-between p-4 cursor-pointer"
               @click="week.isExpanded = !week.isExpanded">
            <div class="space-y-1">
              <h3 class="font-semibold text-gray-900">Week {{ weekIndex + 1 }}</h3>
              <p class="text-sm text-gray-500">{{ week.lectures.length }} modules • {{ week.duration }}</p>
            </div>
            <div class="flex items-center space-x-2">
              <div class="w-16 h-8 bg-primary-50 rounded-lg flex items-center justify-center">
                <span class="text-sm font-medium text-primary-600">{{ getWeekProgress(week) }}%</span>
              </div>
              <i class="fas text-gray-500 transition-transform duration-300 transform group-hover:text-primary-600"
                 :class="[week.isExpanded ? 'fa-chevron-down rotate-180' : 'fa-chevron-right']"></i>
            </div>
          </div>
          
          <div v-show="week.isExpanded" class="border-t border-gray-100/80 pt-2">
            <div v-for="(lecture, lectureIndex) in week.lectures" 
                 :key="lectureIndex"
                 @click="$emit('select-lecture', lecture)"
                 class="flex items-start p-3 mx-2 mb-2 rounded-lg cursor-pointer transition-all duration-300
                        hover:bg-primary-50/50 border border-transparent hover:border-primary-100"
                 :class="{'bg-primary-50 border-primary-200': lecture.id === selectedLecture?.id}">
              <div class="flex-shrink-0 mt-1.5">
                <i class="fas text-sm transform transition-all"
                   :class="[lecture.completed ? 'fa-check-circle text-green-500 scale-110' : 
                          lecture.id === selectedLecture?.id ? 'fa-play-circle text-primary-600 scale-110' : 
                          'fa-circle text-gray-400 hover:text-primary-500']"></i>
              </div>
              <div class="ml-3 flex-grow">
                <h4 class="text-sm font-medium text-gray-900">{{ lecture.title }}</h4>
                <div class="flex items-center mt-1.5 space-x-3">
                  <div class="flex items-center space-x-1 text-gray-500 text-xs">
                    <i class="fas fa-clock opacity-70"></i>
                    <span>{{ lecture.duration || '15 min' }}</span>
                  </div>
                  <div v-if="lecture.materials?.length" class="flex items-center space-x-1 text-gray-500 text-xs">
                    <i class="fas fa-paperclip opacity-70"></i>
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
      required: true
    },
    selectedLecture: {
      type: Object,
      default: null
    },
    completedLectures: {
      type: Number,
      required: true
    },
    totalLectures: {
      type: Number,
      required: true
    }
  },
  emits: ['select-lecture'],
  methods: {
    getWeekProgress(week) {
      const completedInWeek = week.lectures.filter(lecture => lecture.completed).length
      return Math.round((completedInWeek / week.lectures.length) * 100) || 0
    }
  }
}
</script> 