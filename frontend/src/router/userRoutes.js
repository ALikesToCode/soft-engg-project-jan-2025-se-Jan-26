import UserDashboard from '../views/user/UserDashboard.vue'
import UserCourses from '../views/user/UserCourses.vue'
import UserDetails from '../views/user/UserDetails.vue'
import ProfilePage from '../views/user/ProfilePage.vue'
import CourseHistory from '../views/user/CourseHistory.vue'

// Base64 dummy image
const dummyAvatar = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iMzYiIHI9IjIwIiBmaWxsPSIjOTA5MDkwIi8+PHBhdGggZD0iTTIwLDg1IEMzMCw2NSA3MCw2NSA4MCw4NSIgZmlsbD0iIzkwOTA5MCIvPjwvc3ZnPg=="

const userRoutes = {
    path: '/user',
    name: 'userDashboard',
    children: [
        {
            path: 'dashboard',
            component: UserDashboard,
            meta: {
                title: 'User Dashboard',
                hideNavbar: false,
                hideFooter: true,
                hideUserNavbar: false
            }
        },
        {
            path: 'courses',
            component: UserCourses,
            meta: {
                title: 'User Courses',
                hideNavbar: false,
                hideFooter: true,
                hideUserNavbar: false
            }
        },
        {
            path: 'details',
            component: UserDetails,
            meta: {
                title: 'User Details',
                hideNavbar: false,
                hideFooter: true,
                hideUserNavbar: false
            }
        },
        {
            path: 'course-history',
            component: CourseHistory,
            meta: {
                title: 'Course History',
                hideNavbar: false,
                hideFooter: true,
                hideUserNavbar: false
            }
        },
        {
            path: 'profile',
            component: ProfilePage,
            props: {
                userType: 'student',
                userInfo: {
                    name: "John Doe",
                    email: "john.doe@example.com",
                    profilePictureUrl: dummyAvatar,
                    coursesCount: 5,
                    studentsCount: 0,
                    rating: 4.5
                },
                initialCourses: [
                    {
                        id: 1,
                        title: "Introduction to Programming",
                        description: "Learn the basics of programming",
                        status: "active",
                        progress: 60,
                        duration: "8 weeks",
                        studentsCount: 30,
                        instructor: {
                            name: "Dr. Smith",
                            avatar: dummyAvatar
                        }
                    },
                    {
                        id: 2,
                        title: "Web Development",
                        description: "Master web development fundamentals",
                        status: "active",
                        progress: 30,
                        duration: "10 weeks",
                        studentsCount: 25,
                        instructor: {
                            name: "Prof. Johnson",
                            avatar: dummyAvatar
                        }
                    }
                ]
            },
            meta: {
                title: 'User Profile',
                hideNavbar: true,
                hideFooter: true,
                isProfilePage: true
            }
        }
    ]
};

export default userRoutes;