import axios from 'axios';
import api from '@/utils/api';

// Mock data for development or fallback
const mockFaqs = [
  {
    id: 1,
    question: 'How do I reset my password?',
    answer: 'To reset your password:<br>1. Click on "Forgot Password" on the login page<br>2. Enter your email address<br>3. Check your email for reset instructions<br>4. Follow the link and create a new password',
    categoryId: 'account',
    priority: 5
  },
  {
    id: 2,
    question: 'How do I enroll in a course?',
    answer: 'To enroll in a course:<br>1. Go to the Courses page<br>2. Find the course you want to join<br>3. Click the "Enroll" button<br>4. Confirm your enrollment',
    categoryId: 'courses',
    priority: 4
  },
  {
    id: 3,
    question: 'What should I do if I encounter technical issues during a quiz?',
    answer: 'If you experience technical issues during a quiz:<br>1. Take a screenshot of the error<br>2. Contact support immediately<br>3. Do not close your browser<br>4. Wait for support staff assistance',
    categoryId: 'technical',
    priority: 4
  },
  {
    id: 4,
    question: 'How can I track my course progress?',
    answer: 'You can track your course progress by:<br>1. Going to your Dashboard<br>2. Checking the progress bars for each course<br>3. Viewing detailed analytics in the Course History section',
    categoryId: 'general',
    priority: 3
  },
  {
    id: 5,
    question: 'What file formats are supported for assignment submissions?',
    answer: 'The following file formats are supported:<br>- PDF (.pdf)<br>- Word documents (.doc, .docx)<br>- Text files (.txt)<br>- Images (.jpg, .png)<br>- ZIP archives (.zip) for multiple files',
    categoryId: 'technical',
    priority: 3
  },
  {
    id: 6,
    question: 'How do I contact my course instructor?',
    answer: 'To contact your instructor:<br>1. Go to the course page<br>2. Click on the "Contact Instructor" button<br>3. Fill out the contact form<br>4. Your message will be sent directly to the instructor',
    categoryId: 'courses',
    priority: 2
  },
  {
    id: 7,
    question: 'What are the system requirements for video lectures?',
    answer: 'Recommended system requirements:<br>- Modern web browser (Chrome, Firefox, Safari)<br>- Stable internet connection (minimum 5 Mbps)<br>- Updated video codecs<br>- Enabled JavaScript',
    categoryId: 'technical',
    priority: 2
  },
  {
    id: 8,
    question: 'How do I get a certificate after completing a course?',
    answer: 'To receive your certificate:<br>1. Complete all required course modules<br>2. Pass the final assessment<br>3. Go to the Course Completion page<br>4. Click "Generate Certificate"<br>5. Download or share your certificate',
    categoryId: 'courses',
    priority: 3
  }
]

// Check if we're in development mode
const isDevelopment = import.meta.env.MODE === 'development';
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class FAQService {
  async getAllFaqs() {
    try {
      const response = await api.get('/faqs/faqs/');
      return response.data;
    } catch (error) {
      console.error('Error fetching FAQs:', error);
      // Fallback to mock data in case of error
      return mockFaqs;
    }
  }

  async getFaqsByCategory(category) {
    try {
      const url = category === 'all' 
        ? '/faqs/faqs/' 
        : `/faqs/faqs/?category_id=${category}`;
      
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Error fetching FAQs by category:', error);
      // Fallback to mock data in case of error
      const filteredFaqs = category === 'all' 
        ? mockFaqs 
        : mockFaqs.filter(faq => faq.categoryId === category);
      return filteredFaqs;
    }
  }

  async createFaq(faqData) {
    try {
      const response = await api.post('/faqs/faqs/', faqData);
      return response.data;
    } catch (error) {
      console.error('Error creating FAQ:', error);
      throw error;
    }
  }

  async updateFaq(faqId, faqData) {
    try {
      const response = await api.put(`/faqs/faqs/${faqId}`, faqData);
      return response.data;
    } catch (error) {
      console.error('Error updating FAQ:', error);
      throw error;
    }
  }

  async deleteFaq(faqId) {
    try {
      await api.delete(`/faqs/faqs/${faqId}`);
      return true;
    } catch (error) {
      console.error('Error deleting FAQ:', error);
      throw error;
    }
  }

  async rateFaq(faqId, isHelpful) {
    try {
      const response = await api.post(`/faqs/faqs/${faqId}/rate`, { isHelpful });
      return response.data;
    } catch (error) {
      console.error('Error rating FAQ:', error);
      throw error;
    }
  }

  async searchFaqs(query) {
    try {
      const response = await api.post('/faqs/faqs/search', { query });
      return response.data;
    } catch (error) {
      console.error('Error searching FAQs:', error);
      // Fallback to client-side search in case of error
      const lowercaseQuery = query.toLowerCase();
      return mockFaqs.filter(
        faq =>
          faq.question.toLowerCase().includes(lowercaseQuery) ||
          faq.answer.toLowerCase().includes(lowercaseQuery)
      );
    }
  }

  async submitSupportRequest(requestData) {
    // This would typically send the support request to a backend endpoint
    // For now, just log it and return a success message
    console.log('Support request submitted:', requestData);
    return { success: true };
  }
}

export default new FAQService() 