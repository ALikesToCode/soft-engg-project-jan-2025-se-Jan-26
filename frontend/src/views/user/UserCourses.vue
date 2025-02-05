<script>
import ChatBotBox from '../../components/ChatBotBox.vue'
export default {
    
  data() {
    return {
      courses: ["Software Engineering", "Software Testing", "Python", "Mathematics"],
      weeks: ["Week 1", "Week 3", "Week 4", "Week 5", "Week 6", "Week 4", "Week 5", "Week 6"],
      lectures: ["Course Information","Lecture 1",,"Lecture 2", "Lecture 3", "Lecture 4", "Lecture 5","Practice Assignment", "Graded Assignment"],
      activeCourse: 0,
      activeWeek: 0,
      v_title: "Introduction to Python"
    };
    },
    components: {
        ChatBotBox, 
  },
};
</script>

<template>
    <div class="p-4 py-2">
      <div class="flex gap-x-6 border-b pb-2 justify-center">
        <button
          v-for="(course, index) in courses"
          :key="index"
          @click="activeCourse = index"
          class="px-6 py-2 border rounded hover:text-red-800 hover:cursor-pointer"
          :class="activeCourse === index ? 'border-red-600 text-red-800 font-semibold bg-gray-100' : 'border-red-300'"
        >
          {{ course }}
        </button>
      </div>
  
      <div class="flex gap-x-4 mt-4 border-b py-2 justify-center">
        <button
          v-for="(week, index) in weeks"
          :key="index"
          @click="activeWeek = index"
          class="px-4 py-2 border rounded hover:text-red-800 hover:cursor-pointer"
          :class="activeWeek === index ? 'border-red-600 font-semibold bg-gray-100' : 'border-gray-300'"
        >
          {{ week }}
        </button>
      </div>
  
      <div class="grid grid-cols-6 gap-4 !my-2">
        <div class="col-span-1 border p-2 py-3 rounded text-center flex flex-col justify-between h-full">
          <ul class="mt-2 space-y-2">
            <li v-for="(lecture, index) in lectures" :key="index" class="py-[0.7px] rounded hover:underline hover:cursor-pointer hover:text-red-800">
              
            <!-- <span v-if="index===0" class="py-2 px-4 my-2 rounded bg-red-600 text-white hover:text-gray-100">{{ lecture }}</span> -->
            <span >{{ lecture }}</span>
            </li>
          </ul>
          <div class="mt-auto mb-8" id="supp">
            <p class="text-gray-600 underline underline-offset-4 cursor-pointer hover:text-red-800">Supplementary contents</p>
          </div>
        </div>
  
        <div class="col-span-3 border rounded text-center sm:min-h-[400px] flex justify-center">
            <div class="flex flex-col h-full w-full">
                <div class="h-full w-full border-[1px]">
                <p class="font-semibold">Lecture Video</p>
                </div>
                <div class="mt-auto w-full px-12 py-1">
                <p class="font-black text-lg">Title : {{ v_title }}</p>
                </div>
            </div>
        </div>
        <div class="col-span-2 border rounded">
            <ChatBotBox />
        </div>
      </div>
    </div>
  </template>
  
  <style scoped>
  button {
    transition: all 0.2s ease-in-out;
  }
  button:hover {
    background-color: #f3f4f6;
  }
  </style>
  