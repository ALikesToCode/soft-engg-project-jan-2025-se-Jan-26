import axios from 'axios';

const handleError = (error) => {
  if (error.response) {
    // Server responded with an error status
    const message = error.response.data?.message || 'Server error occurred';
    const status = error.response.status;
    throw new Error(`API Error (${status}): ${message}`);
  } else if (error.request) {
    // Request was made but no response received
    throw new Error('No response received from server. Please check your connection.');
  } else {
    // Error in request configuration
    throw new Error(`Request failed: ${error.message}`);
  }
};

export const analyticsService = {
  async getFacultyAnalytics(filters) {
    try {
      if (!filters || Object.keys(filters).length === 0) {
        throw new Error('No filters provided for analytics');
      }

      console.log('Fetching analytics with filters:', filters);
      const response = await axios.get('/api/v1/analytics', { 
        params: filters,
        timeout: 10000 // 10 second timeout
      });
      
      if (!response.data) {
        throw new Error('No data received from analytics endpoint');
      }

      return response.data;
    } catch (error) {
      console.error('Analytics fetch error:', {
        message: error.message,
        filters,
        stack: error.stack
      });
      handleError(error);
    }
  },

  async getAIInsights(data) {
    try {
      if (!data) {
        throw new Error('No data provided for AI insights');
      }

      console.log('Fetching AI insights for data:', data);
      const response = await axios.post('/api/v1/analytics/ai-insights', data, {
        timeout: 15000 // 15 second timeout for AI processing
      });

      if (!response.data) {
        throw new Error('No insights received from AI endpoint');
      }

      return response.data;
    } catch (error) {
      console.error('AI insights error:', {
        message: error.message,
        data,
        stack: error.stack
      });
      handleError(error);
    }
  },

  async exportAnalytics(format, filters) {
    try {
      if (!format || !filters) {
        throw new Error('Missing format or filters for export');
      }

      console.log('Exporting analytics:', { format, filters });
      const response = await axios.get(`/api/v1/analytics/export/${format}`, {
        params: filters,
        responseType: 'blob',
        timeout: 30000 // 30 second timeout for exports
      });

      return response.data;
    } catch (error) {
      console.error('Export error:', {
        message: error.message,
        format,
        filters,
        stack: error.stack
      });
      handleError(error);
    }
  }
}; 