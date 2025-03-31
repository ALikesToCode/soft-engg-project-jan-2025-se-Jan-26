import ContentUpload from '../views/faculty/ContentUpload.vue'
import FacultyDashboard from '../views/faculty/FacultyDashboard.vue'
import FacultyDetails from '../views/faculty/FacultyDetails.vue'
import ProfilePage from '../views/faculty/ProfilePage.vue'
import NotificationsView from '../views/faculty/NotificationsView.vue'
import CourseEnrollmentView from '@/views/faculty/CourseEnrollmentView.vue'
import AcademicIntegrityMonitoring from '../views/faculty/AcademicIntegrityMonitoring.vue'
import FacultyNotifications from '../views/faculty/FacultyNotifications.vue'

// Base64 dummy image
const dummyAvatar = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iMzYiIHI9IjIwIiBmaWxsPSIjOTA5MDkwIi8+PHBhdGggZD0iTTIwLDg1IEMzMCw2NSA3MCw2NSA4MCw4NSIgZmlsbD0iIzkwOTA5MCIvPjwvc3ZnPg=="

const facultyRoutes = {
    path: '/faculty',
    name: 'facultyDashboard',
    children: [
        {
            path: 'dashboard',
            component: FacultyDashboard,
            meta: {
                title: 'Faculty Dashboard',
                hideNavbar: true,
                hideFooter: true
            }
        },
        {
            path: 'content-upload',
            component: ContentUpload,
            meta: {
                title: 'Upload Content',
                hideNavbar: true,
                hideFooter: true
            }
        },
        {
            path: 'details',
            component: FacultyDetails,
            meta: {
                title: 'User Details'
            }
        },
        {
            path: 'notifications',
            component: NotificationsView,
            meta: {
                title: 'Send Notifications',
                hideNavbar: true,
                hideFooter: true
            }
        },
        {
            path: 'profile',
            component: ProfilePage,
            props: {
                userType: 'faculty',
                userInfo: {
                    name: "Dr. Jane Smith",
                    email: "jane.smith@faculty.example.com",
                    profilePictureUrl: dummyAvatar,
                    department: "Computer Science",
                    coursesCount: 3,
                    studentsCount: 150,
                    rating: 4.8
                },
                initialCourses: [
                    {
                        id: 1,
                        title: "Advanced Algorithms",
                        description: "Deep dive into algorithmic complexity and optimization",
                        status: "active",
                        studentsCount: 45,
                        duration: "12 weeks",
                        instructor: {
                            name: "Dr. Jane Smith",
                            avatar: dummyAvatar
                        }
                    },
                    {
                        id: 2,
                        title: "Machine Learning Fundamentals",
                        description: "Introduction to ML concepts and applications",
                        status: "active",
                        studentsCount: 60,
                        duration: "10 weeks",
                        instructor: {
                            name: "Dr. Jane Smith",
                            avatar: dummyAvatar
                        }
                    },
                    {
                        id: 3,
                        title: "Data Structures",
                        description: "Comprehensive study of data structures",
                        status: "draft",
                        studentsCount: 0,
                        duration: "8 weeks",
                        instructor: {
                            name: "Dr. Jane Smith",
                            avatar: dummyAvatar
                        }
                    }
                ]
            },
            meta: {
                title: 'Faculty Profile',
                hideNavbar: true,
                hideFooter: true,
                isProfilePage: true
            }
        },
        {
            path: '/faculty/course/enrollment',
            name: 'CourseEnrollment',
            component: CourseEnrollmentView,
            meta: {
                requiresFacultyAuth: true,
                hideFooter: true,
            }
        },
        {
            path: 'academic-integrity',
            component: AcademicIntegrityMonitoring,
            meta: {
                title: 'Academic Integrity Monitoring',
                hideNavbar: true,
                hideFooter: true
            }
        },
        {
            path: 'notifications',
            component: FacultyNotifications,
            meta: {
                title: 'Notifications',
                hideNavbar: true,
                hideFooter: true
            }
        }
    ]
};

export default facultyRoutes;