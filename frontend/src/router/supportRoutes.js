import SupportDashboard from '../views/support/SupportDashboard.vue'
import NotificationsView from '../views/support/NotificationsView.vue'
import ProfilePage from '../views/support/ProfilePage.vue'
import FAQManagement from '../views/support/FAQManagement.vue'
import SystemSettings from '../views/support/SystemSettings.vue'
import UserManagement from '../views/support/UserManagement.vue'
import CourseAssignmentManagement from '../views/support/CourseAssignmentManagement.vue'

const dummyAvatar = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iMzYiIHI9IjIwIiBmaWxsPSIjOTA5MDkwIi8+PHBhdGggZD0iTTIwLDg1IEMzMCw2NSA3MCw2NSA4MCw4NSIgZmlsbD0iIzkwOTA5MCIvPjwvc3ZnPg=="

const supportRoutes = {
    path: '/support',
    name: 'supportDashboard',
    meta: { requiresAuth: true, role: 'support' },
    children: [
        {
            path: 'dashboard',
            component: SupportDashboard,
            meta: {
                title: 'Support Dashboard',
                hideNavbar: true,
                hideFooter: true,
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
            path: 'faq-management',
            component: FAQManagement,
            meta: {
                title: 'FAQ Management',
                hideNavbar: true,
                hideFooter: true
            }
        },
        {
            path: 'system-settings',
            component: SystemSettings,
            meta: {
                title: 'System Settings',
                hideNavbar: true,
                hideFooter: true,
                requiresAdmin: true
            }
        },
        {
            path: 'user-management',
            component: UserManagement,
            meta: {
                title: 'User Management',
                hideNavbar: true,
                hideFooter: true,
                requiresAdmin: true
            }
        },
        {
            path: 'course-assignments',
            component: CourseAssignmentManagement,
            meta: {
                title: 'Course Assignment Management',
                hideNavbar: true,
                hideFooter: true,
                requiresAdmin: true
            }
        },
        {
            path: 'profile',
            component: ProfilePage,
            props: {
                userType: 'support',
                userInfo: {
                    name: "Dr. Jane Smith",
                    email: "jane.smith@support.example.com",
                    profilePictureUrl: dummyAvatar,
                    // department: "Mechanical Engineering",
                    coursesCount: 2,
                    studentsCount: 150,
                    rating: 5.0
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
                ]
            },
            meta: {
                title: 'Support Profile',
                hideNavbar: true,
                hideFooter: true,
                isProfilePage: true
            }
        }
    ]
};

export default supportRoutes;