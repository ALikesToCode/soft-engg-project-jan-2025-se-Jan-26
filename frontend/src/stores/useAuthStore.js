import { defineStore } from 'pinia';

import FetchFunction from '../utils/FetchFunction';
import router from '../router/index';
import { User } from '@/models/User';

import { APP_BASE_URL, ROLE } from '@/AppConstants/globalConstants';

// For development only - remove in production
const DEV_MODE = import.meta.env.VITE_NODE_ENV === 'development';

const useAuthStore = defineStore({
    id: 'auth',
    state: () => ({
        token: JSON.parse(localStorage.getItem('token')),
        returnUrl: null,
        user: new User(null, "", "", ""),
        userRole: localStorage.getItem('userRole') || ROLE.STUDENT,
        isAdmin: false,
        isDevelopment: DEV_MODE
    }),
    actions: {
        // Development only - helper to switch roles
        switchRole(role) {
            if (!this.isDevelopment) return;
            if (Object.values(ROLE).includes(role)) {
                this.setUserRole(role);
                // Don't redirect, let the router handle navigation
            }
        },

        async login(email, pswd) {
            if (this.isDevelopment) {
                // For development, just set a dummy token and keep current role
                this.token = "dummy-token";
                localStorage.setItem('token', JSON.stringify(this.token));
                
                // Navigate based on current role
                this.navigateToRoleDashboard();
                return;
            }

            try {
                const data = await FetchFunction({
                    url: `${APP_BASE_URL}/${user}`,
                    init_obj: {
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        method: 'POST',
                        body: JSON.stringify(user),
                    }
                }).catch((err) => {
                    throw new Error("Error = " + err);
                })
                if (data) {
                    this.token = data.response.user.authentication_token;
                    this.setUserRole(data.role);
                    localStorage.setItem('token', JSON.stringify(this.token));
                    this.navigateToRoleDashboard();
                }
            } catch (error) {
                console.log("error = " + error);
                router.push({ path: '/', query: { error: 'true' } });
            }
        },

        // Helper method to navigate based on role
        navigateToRoleDashboard() {
            switch(this.userRole) {
                case ROLE.STUDENT:
                    router.push('/user/dashboard');
                    break;
                case ROLE.FACULTY:
                    router.push('/faculty/dashboard');
                    break;
                case ROLE.SUPPORT:
                    router.push('/support/dashboard');
                    break;
                default:
                    router.push('/');
            }
        },

        logout() {
            this.user = null;
            this.token = null;
            this.userRole = ROLE.STUDENT;
            localStorage.removeItem('token');
            localStorage.removeItem('userRole');
        },

        setUser(userData) {
            this.user.id = userData.id;
            this.user.name = userData.name;
            this.user.email = userData.email;
            this.user.role = userData.role;
            this.setUserRole(userData.role);
        },

        setUserRole(role) {
            if (Object.values(ROLE).includes(role)) {
                this.userRole = role;
                localStorage.setItem('userRole', role);
            } else {
                console.warn('Invalid role:', role);
                this.userRole = ROLE.STUDENT;
                localStorage.setItem('userRole', ROLE.STUDENT);
            }
        },

        clearUser() {
            this.user = new User(null, "", "", "");
            this.userRole = ROLE.STUDENT;
            localStorage.removeItem('userRole');
        },
    }
});

export default useAuthStore;