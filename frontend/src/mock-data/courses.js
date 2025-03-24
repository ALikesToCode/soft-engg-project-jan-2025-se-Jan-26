export const MOCK_COURSES = [
  {
    id: 1,
    title: 'Introduction to Python Programming',
    description: 'A comprehensive course covering Python programming fundamentals with hands-on projects.',
    thumbnail: 'https://placehold.co/400x300',
    duration: '8 weeks',
    level: 'Beginner',
    rating: 4.8,
    totalStudents: 1250,
    lastUpdated: '2024-02-15',
    language: 'English',
    certificate: true,
    instructor: {
      id: 101,
      name: 'Dr. Sarah Johnson',
      title: 'Senior Python Developer & Educator',
      avatar: 'https://placehold.co/100x100',
      bio: 'PhD in Computer Science with 10+ years of teaching experience',
      rating: 4.9,
      totalStudents: 15000,
      totalCourses: 12
    },
    progress: 35,
    isBookmarked: false,
    syllabus: [
      {
        id: 1,
        title: 'Getting Started with Python',
        isExpanded: true,
        progress: 100,
        lectures: [
          {
            id: 101,
            title: 'Introduction to Python',
            duration: '15:00',
            type: 'video',
            completed: true,
            videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
            thumbnailUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/images/BigBuckBunny.jpg',
            description: 'Get started with Python programming language and understand its importance in modern development.',
            objectives: [
              'Understand what Python is and its applications in real world',
              'Learn about Python\'s history and evolution',
              'Set up Python development environment',
              'Write and run your first Python program'
            ],
            materials: [
              {
                id: 1001,
                title: 'Python Setup Guide',
                type: 'pdf',
                size: '2.5MB',
                downloadUrl: '/materials/python-setup-guide.pdf'
              },
              {
                id: 1002,
                title: 'Course Overview',
                type: 'pdf',
                size: '1.8MB',
                downloadUrl: '/materials/course-overview.pdf'
              },
              {
                id: 1003,
                title: 'Introduction Slides',
                type: 'ppt',
                size: '5.2MB',
                downloadUrl: '/materials/intro-slides.ppt'
              }
            ],
            questions: [
              {
                id: 1,
                question: 'What is Python and why is it popular?',
                type: 'discussion',
                responses: 15
              },
              {
                id: 2,
                question: 'How to install Python on different operating systems?',
                type: 'technical',
                responses: 8
              },
              {
                id: 3,
                question: 'Write a simple "Hello, World!" program in Python',
                type: 'exercise',
                responses: 25
              }
            ],
            notes: [],
            discussion: {
              totalComments: 45,
              comments: [
                {
                  id: 1,
                  user: {
                    id: 201,
                    name: 'John Doe',
                    avatar: 'https://placehold.co/50x50'
                  },
                  content: 'Great introduction to Python! Very clear explanation.',
                  timestamp: '2024-02-15T10:30:00Z',
                  likes: 12,
                  replies: []
                }
              ]
            }
          },
          {
            id: 102,
            title: 'Variables and Data Types',
            duration: '20:00',
            type: 'video',
            completed: true,
            videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
            thumbnailUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/images/ElephantsDream.jpg',
            description: 'Learn about variables and basic data types in Python programming.',
            objectives: [
              'Understand variables and their importance',
              'Learn different data types in Python',
              'Practice variable declaration and assignment',
              'Understand type conversion and type checking'
            ],
            materials: [
              {
                id: 1004,
                title: 'Variables Cheat Sheet',
                type: 'pdf',
                size: '1.5MB',
                downloadUrl: '/materials/variables-cheatsheet.pdf'
              },
              {
                id: 1005,
                title: 'Practice Problems',
                type: 'pdf',
                size: '2.1MB',
                downloadUrl: '/materials/practice-problems.pdf'
              }
            ]
          }
        ]
      },
      {
        id: 2,
        title: 'Control Flow and Functions',
        description: 'Learn about control structures and function definitions in Python',
        duration: '1 week',
        isExpanded: false,
        progress: 0,
        lectures: [
          {
            id: 103,
            title: 'Conditional Statements',
            duration: '25:00',
            type: 'video',
            completed: false,
            videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
            thumbnailUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerBlazes.jpg',
            description: 'Learn about if-else statements and control flow in Python.',
            materials: [
              {
                id: 1006,
                title: 'Control Flow Guide',
                type: 'pdf',
                size: '2.8MB',
                downloadUrl: '/materials/control-flow.pdf'
              }
            ]
          }
        ]
      }
    ]
  }
]
export const getCourseById = async (courseId) => {
  return MOCK_COURSES.find(course => course.id === courseId)
}

export const getLectureById = (courseId, lectureId) => {
  const course = getCourseById(courseId)
  if (!course) return null

  for (const week of course.syllabus) {
    const lecture = week.lectures.find(lecture => lecture.id === lectureId)
    if (lecture) return lecture
  }
  return null
} 