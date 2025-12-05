// src/stores/auth.js
import { defineStore } from 'pinia';
import axios from 'axios';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,
    user: null,
    role: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    

    dashboardRoute: (state) => {
      const role = state.role ? state.role.toLowerCase() : '';
      switch (role) {
        case 'candidate': return '/candidateDashboard';
        case 'hr': return '/hrDashboard';
        case 'manager': return '/managerDashboard';
        case 'admin': return '/adminDashboard';
        default: return '/login';
      }
    }
  },

  actions: {

    async fetchUser() {
      if (!this.token) return;
      
      try {
        const response = await axios.get('/api/users/', {
          headers: { Authorization: `Bearer ${this.token}` }
        });
        
        this.user = response.data;

        this.role = (response.data.role_name || '').toLowerCase().trim();
      } catch (error) {
        console.error('Auth Store: Failed to fetch user', error);
        this.logout();
      }
    },


    hasAccess(requiredRoles) {
      if (!this.role) return false;
      

      const allowed = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles];
      

      return allowed.some(r => r.toLowerCase() === this.role);
    },

    logout() {
      this.token = null;
      this.user = null;
      this.role = null;
      localStorage.removeItem('access_token');
    }
  }
});