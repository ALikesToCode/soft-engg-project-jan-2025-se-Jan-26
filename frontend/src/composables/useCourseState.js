import { ref, computed } from 'vue'
import { useStorage } from '@vueuse/core'

const STORAGE_KEY = 'course_state'

export function useCourseState() {
  // Persistent state using localStorage
  const courseState = useStorage(STORAGE_KEY, {
    lastViewedCourseId: null,
    lastViewedLectureId: null,
    completedLectures: {},
    bookmarkedCourses: [],
    notes: {},
    videoProgress: {}
  })

  // Computed getters
  const lastViewedCourse = computed(() => courseState.value.lastViewedCourseId)
  const lastViewedLecture = computed(() => courseState.value.lastViewedLectureId)
  const completedLectures = computed(() => courseState.value.completedLectures)
  const bookmarkedCourses = computed(() => courseState.value.bookmarkedCourses)

  // Methods
  const updateLastViewed = (courseId, lectureId) => {
    courseState.value.lastViewedCourseId = courseId
    courseState.value.lastViewedLectureId = lectureId
  }

  const toggleLectureCompletion = (courseId, lectureId) => {
    if (!courseState.value.completedLectures[courseId]) {
      courseState.value.completedLectures[courseId] = []
    }

    const index = courseState.value.completedLectures[courseId].indexOf(lectureId)
    if (index === -1) {
      courseState.value.completedLectures[courseId].push(lectureId)
    } else {
      courseState.value.completedLectures[courseId].splice(index, 1)
    }
  }

  const toggleBookmark = (courseId) => {
    const index = courseState.value.bookmarkedCourses.indexOf(courseId)
    if (index === -1) {
      courseState.value.bookmarkedCourses.push(courseId)
    } else {
      courseState.value.bookmarkedCourses.splice(index, 1)
    }
  }

  const saveNote = (courseId, lectureId, note) => {
    if (!courseState.value.notes[courseId]) {
      courseState.value.notes[courseId] = {}
    }
    courseState.value.notes[courseId][lectureId] = note
  }

  const getNote = (courseId, lectureId) => {
    return courseState.value.notes[courseId]?.[lectureId] || ''
  }

  const saveVideoProgress = (courseId, lectureId, progress) => {
    if (!courseState.value.videoProgress[courseId]) {
      courseState.value.videoProgress[courseId] = {}
    }
    courseState.value.videoProgress[courseId][lectureId] = progress
  }

  const getVideoProgress = (courseId, lectureId) => {
    return courseState.value.videoProgress[courseId]?.[lectureId] || 0
  }

  const isLectureCompleted = (courseId, lectureId) => {
    return courseState.value.completedLectures[courseId]?.includes(lectureId) || false
  }

  const isCourseBookmarked = (courseId) => {
    return courseState.value.bookmarkedCourses.includes(courseId)
  }

  const getCourseProgress = (courseId, totalLectures) => {
    const completed = courseState.value.completedLectures[courseId]?.length || 0
    return totalLectures > 0 ? Math.round((completed / totalLectures) * 100) : 0
  }

  return {
    // State
    lastViewedCourse,
    lastViewedLecture,
    completedLectures,
    bookmarkedCourses,

    // Methods
    updateLastViewed,
    toggleLectureCompletion,
    toggleBookmark,
    saveNote,
    getNote,
    saveVideoProgress,
    getVideoProgress,
    isLectureCompleted,
    isCourseBookmarked,
    getCourseProgress
  }
} 