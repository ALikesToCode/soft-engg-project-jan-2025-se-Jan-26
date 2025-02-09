<template>
  <div class="faculty-course-list bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <p class="text-gray-600 mb-4">Drag and drop to reorder your courses:</p>
    
    <draggable 
      v-model="localCourses" 
      class="space-y-3"
      :animation="200"
      ghost-class="ghost"
      @start="dragStart"
      @end="dragEnd"
      item-key="id"
    >
      <template #item="{ element }">
        <div 
          class="course-item p-4 bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-move"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-800">{{ element.title }}</h3>
              <p class="text-gray-600 text-sm mt-1">{{ element.description }}</p>
              
              <div class="flex items-center space-x-4 mt-2">
                <span class="text-sm text-gray-500">
                  <span class="material-icons text-sm mr-1">people</span>
                  {{ element.studentsCount || 0 }} Students
                </span>
                <span class="text-sm text-gray-500">
                  <span class="material-icons text-sm mr-1">schedule</span>
                  {{ element.duration }}
                </span>
                <span 
                  class="text-sm px-2 py-1 rounded-full"
                  :class="{
                    'bg-green-100 text-green-800': element.status === 'active',
                    'bg-yellow-100 text-yellow-800': element.status === 'draft',
                    'bg-gray-100 text-gray-800': element.status === 'archived'
                  }"
                >
                  {{ element.status }}
                </span>
              </div>
            </div>
            
            <div class="flex items-center space-x-2">
              <button 
                class="p-2 text-gray-400 hover:text-maroon-600 transition-colors"
                @click="$emit('edit-course', element)"
              >
                <span class="material-icons">edit</span>
              </button>
              <button 
                class="p-2 text-gray-400 hover:text-maroon-600 transition-colors"
                @click="$emit('preview-course', element)"
              >
                <span class="material-icons">visibility</span>
              </button>
            </div>
          </div>
        </div>
      </template>
    </draggable>
    
    <div v-if="!modelValue.length" class="text-center py-8">
      <p class="text-gray-500">No courses available</p>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import draggable from 'vuedraggable/src/vuedraggable';

export default defineComponent({
  name: 'FacultyCourseList',
  components: {
    draggable
  },
  props: {
    modelValue: {
      type: Array,
      required: true
    }
  },
  emits: ['update:modelValue', 'order-updated', 'edit-course', 'preview-course'],
  computed: {
    localCourses: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
        this.$emit('order-updated');
      }
    }
  },
  methods: {
    dragStart() {
      document.body.style.cursor = 'grabbing';
    },
    dragEnd() {
      document.body.style.cursor = '';
    }
  }
});
</script>

<style scoped>
.ghost {
  opacity: 0.5;
  background: #f3f4f6;
}

.course-item:hover {
  border-color: #9f1239;
}
</style> 