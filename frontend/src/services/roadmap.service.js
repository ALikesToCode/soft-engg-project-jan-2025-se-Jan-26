import api from '@/utils/api';

export const RoadmapService = {
  /**
   * Get a learning roadmap for a specific course
   * @param {string} courseId - ID of the course
   * @param {string} difficultyLevel - Optional difficulty level (beginner, intermediate, advanced)
   * @returns {Promise<Object>} - The roadmap data or error
   */
  async getRoadmap(courseId, difficultyLevel = 'intermediate') {
    try {
      console.log(`Fetching roadmap for course ${courseId} with difficulty ${difficultyLevel}`);
      
      let url = `/api/roadmap/generate/${courseId}`;
      if (difficultyLevel) {
        url += `?difficulty_level=${difficultyLevel}`;
      }
      
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Error fetching roadmap:', error);
      throw error;
    }
  },
  
  /**
   * Update a user's progress in a roadmap
   * @param {string} roadmapId - ID of the roadmap
   * @param {string} milestoneId - ID of the milestone
   * @param {string} status - New status (completed, in_progress, etc.)
   * @returns {Promise<Object>} - Updated progress data
   */
  async updateProgress(roadmapId, milestoneId, status) {
    try {
      const response = await api.post(`/api/roadmap/progress`, {
        roadmapId,
        milestoneId,
        status
      });
      return response.data;
    } catch (error) {
      console.error('Error updating roadmap progress:', error);
      throw error;
    }
  }
}; 