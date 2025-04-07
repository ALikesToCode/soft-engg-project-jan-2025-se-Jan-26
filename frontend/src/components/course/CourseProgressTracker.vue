<template>
  <div class="progress-tracker">
    <div class="header">
      <h3 class="title">Course Progress</h3>
      <div class="progress-stats">
        <div class="progress-percentage">
          {{ progressPercentage }}% Complete
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progressPercentage}%` }"></div>
        </div>
      </div>
    </div>
    
    <div class="modules">
      <div v-for="(module, moduleIndex) in modules" :key="moduleIndex" class="module">
        <div 
          class="module-header" 
          @click="toggleModule(moduleIndex)"
          :class="{ 'expanded': expandedModules.includes(moduleIndex) }"
        >
          <div class="module-title">
            <span class="material-symbols-outlined mr-2">
              {{ expandedModules.includes(moduleIndex) ? 'expand_more' : 'chevron_right' }}
            </span>
            {{ module.title }}
          </div>
          <div class="module-completion">
            {{ getModuleCompletionCount(module) }}/{{ module.lectures.length }}
          </div>
        </div>
        
        <div v-if="expandedModules.includes(moduleIndex)" class="lecture-list">
          <div v-for="lecture in module.lectures" :key="lecture.id" class="lecture-item">
            <div class="lecture-status">
              <span 
                class="material-symbols-outlined"
                :class="{ 
                  'completed': isLectureCompleted(lecture.id),
                  'current': currentLectureId === lecture.id
                }"
              >
                {{ getLectureStatusIcon(lecture.id) }}
              </span>
            </div>
            <div class="lecture-title" @click="selectLecture(lecture.id)">
              {{ lecture.title }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="actions">
      <button @click="markAsCompleted" class="action-button">
        <span class="material-symbols-outlined mr-1">check_circle</span>
        Mark as Completed
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';

export default {
  name: 'CourseProgressTracker',
  props: {
    courseId: {
      type: [String, Number],
      required: true
    },
    currentLectureId: {
      type: [String, Number],
      default: null
    },
    completedLectures: {
      type: Array,
      default: () => []
    },
    modules: {
      type: Array,
      default: () => []
    }
  },
  
  setup(props, { emit }) {
    const expandedModules = ref([0]); // First module expanded by default
    
    // Calculate progress percentage
    const progressPercentage = computed(() => {
      if (!props.modules || props.modules.length === 0) return 0;
      
      const totalLectures = props.modules.reduce((total, module) => {
        return total + module.lectures.length;
      }, 0);
      
      if (totalLectures === 0) return 0;
      
      return Math.round((props.completedLectures.length / totalLectures) * 100);
    });
    
    // Toggle module expansion
    const toggleModule = (moduleIndex) => {
      if (expandedModules.value.includes(moduleIndex)) {
        expandedModules.value = expandedModules.value.filter(index => index !== moduleIndex);
      } else {
        expandedModules.value.push(moduleIndex);
      }
    };
    
    // Check if lecture is completed
    const isLectureCompleted = (lectureId) => {
      return props.completedLectures.includes(lectureId);
    };
    
    // Get module completion count
    const getModuleCompletionCount = (module) => {
      if (!module.lectures) return 0;
      
      return module.lectures.filter(lecture => 
        props.completedLectures.includes(lecture.id)
      ).length;
    };
    
    // Get lecture status icon
    const getLectureStatusIcon = (lectureId) => {
      if (isLectureCompleted(lectureId)) {
        return 'check_circle';
      } else if (props.currentLectureId === lectureId) {
        return 'play_circle';
      }
      return 'radio_button_unchecked';
    };
    
    // Select a lecture
    const selectLecture = (lectureId) => {
      emit('select-lecture', lectureId);
    };
    
    // Mark current lecture as completed
    const markAsCompleted = () => {
      if (props.currentLectureId) {
        emit('mark-completed', props.currentLectureId);
      }
    };
    
    // Expand the module containing the current lecture
    onMounted(() => {
      if (props.currentLectureId) {
        props.modules.forEach((module, index) => {
          const hasCurrentLecture = module.lectures.some(
            lecture => lecture.id === props.currentLectureId
          );
          
          if (hasCurrentLecture && !expandedModules.value.includes(index)) {
            expandedModules.value.push(index);
          }
        });
      }
    });
    
    return {
      expandedModules,
      progressPercentage,
      toggleModule,
      isLectureCompleted,
      getModuleCompletionCount,
      getLectureStatusIcon,
      selectLecture,
      markAsCompleted
    };
  }
};
</script>

<style scoped>
.progress-tracker {
  @apply bg-white rounded-lg shadow-md p-4;
}

.header {
  @apply mb-4;
}

.title {
  @apply text-lg font-semibold text-slate-800 mb-2;
}

.progress-stats {
  @apply mb-4;
}

.progress-percentage {
  @apply text-sm font-medium text-slate-600 mb-1;
}

.progress-bar {
  @apply h-2 bg-slate-200 rounded-full overflow-hidden;
}

.progress-fill {
  @apply h-full bg-maroon-500 rounded-full transition-all duration-300;
}

.modules {
  @apply space-y-2;
}

.module {
  @apply border border-slate-200 rounded-lg overflow-hidden;
}

.module-header {
  @apply flex justify-between items-center p-3 bg-slate-50 cursor-pointer hover:bg-slate-100 transition-colors;
}

.module-header.expanded {
  @apply bg-maroon-50;
}

.module-title {
  @apply flex items-center font-medium text-slate-700;
}

.module-completion {
  @apply text-sm text-slate-500;
}

.lecture-list {
  @apply divide-y divide-slate-100;
}

.lecture-item {
  @apply flex items-center p-3 hover:bg-slate-50 transition-colors cursor-pointer;
}

.lecture-status {
  @apply mr-3;
}

.lecture-status .material-symbols-outlined {
  @apply text-slate-400;
}

.lecture-status .material-symbols-outlined.completed {
  @apply text-green-500;
}

.lecture-status .material-symbols-outlined.current {
  @apply text-maroon-500;
}

.lecture-title {
  @apply text-sm text-slate-700 flex-1;
}

.actions {
  @apply mt-4 flex justify-center;
}

.action-button {
  @apply flex items-center px-4 py-2 bg-maroon-600 text-white rounded-lg 
         hover:bg-maroon-700 transition-colors focus:outline-none focus:ring-2 
         focus:ring-maroon-500 focus:ring-offset-2;
}
</style> 