import { defineStore } from 'pinia';

import FetchFunction from '../utils/FetchFunction';
import router from '../router/index';
import { User } from '@/models/User';

import { APP_BASE_URL, ROLE } from '@/AppConstants/globalConstants';

const useAuthStore = defineStore({
    id: 'auth',
    state: () => ({
        token: JSON.parse(localStorage.getItem('token')),
        returnUrl: null,
        user: new User(null, "", "", ""),
        userRole: 'SUPPORT',
        isAdmin: true
    }),
    actions: {
        async login(email, pswd) {
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
                    this.userRole = data.role;
                    localStorage.setItem('token', JSON.stringify(this.token));
                    if (this.userRole === ROLE.STUDENT) {
                        router.push('/user/dashboard');
                    }
                    else if (this.userRole === ROLE.FACULTY) {
                        router.push('/faculty/dashboard');
                    }
                    else if (this.userRole === ROLE.SUPPORT) {
                        router.push('/support/dashboard');
                    }
                    else {
                        router.push('/');
                    }
                }
            } catch (error) {
                console.log("error = " + error);
                router.push({ path: '/', query: { error: 'true' } });
            }
        },
        logout() {
            this.user = null
            this.token = null;
            localStorage.removeItem('token');
        },
        setUser(userData) {
            this.user.id = userData.id;
            this.user.name = userData.name;
            this.user.email = userData.email;
            this.user.role = userData.role;
        },
        clearUser() {
            this.user = new User(null, "", "", "");
        },
    }
});

export default useAuthStore;