// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

import HomePage from '@/components/HomePage.vue'
import VacancyList from '@/components/VacancyList.vue'
import JobPosting from '@/components/JobPosting.vue'
import ApplyForm from '@/components/ApplyForm.vue'
import ScreeningPage from '@/components/ScreeningPage.vue'
import HiringPipeline from '@/components/HiringPipeline.vue'
import OnboardingPage from '@/components/OnboardingPage.vue'
import TrainingPage from '@/components/TrainingPage.vue'
import ReportingPage from '@/components/ReportingPage.vue'
import ExpenseManagement from '@/components/ExpenseManagement.vue'
import LoginPage from '@/components/LoginPage.vue'
import SignupPage from '@/components/SignupPage.vue'
import AdminDashboard from '@/components/AdminDashboard.vue'
import HRDashboard from '@/components/HRDashboard.vue'
import CandidateDashboard from '@/components/CandidateDashboard.vue'
import ProfileEnhacement from '@/components/ai_profile_enhancement.vue'
import CandidateProfile from '@/components/CandidateProfile.vue'
import CandidateCoursePage from '../components/CandidateCoursePage.vue'
import ManagerDashboard from '@/components/ManagerDashboard.vue'
import CandidateJobRecommendations from '../components/CandidateJobRecommendations.vue'
import CandidateJobSearch from '../components/CandidateJobSearch.vue'
import CandidateVacanciesPage from '../components/CandidateVacanciesPage.vue'
import CandidateApplicationsPage from '../components/CandidateApplicationsPage.vue'


// Define your routes
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
  { path: '/', 
    name: 'Home', 
    component: HomePage, },
  { path: '/login', name: 'Login', component: LoginPage },
  { path: '/signup', name: 'Signup', component: SignupPage },
  { path: '/vacancy', name: 'VacancyList', component: VacancyList },
  { path: '/job-posting', name: 'JobPosting', component: JobPosting },
  { path: '/apply', name: 'ApplyForm', component: ApplyForm },
  { path: '/screening', name: 'ScreeningPage', component: ScreeningPage },
  { path: '/hiring-pipeline', name: 'HiringPipeline', component: HiringPipeline },
  { path: '/onboarding', name: 'OnboardingPage', component: OnboardingPage },
  { path: '/training', name: 'TrainingPage', component: TrainingPage },
  { path: '/reporting', name: 'ReportingPage', component: ReportingPage },
  { path: '/expense', name: 'ExpenseManagement', component: ExpenseManagement },
  { path: '/adminDashboard', name: 'AdminDashboard', component: AdminDashboard },
  { path: '/hrDashboard', name: 'HRDashboard', component: HRDashboard },
  { path: '/candidateDashboard', name: 'CandidateDashboard', component: CandidateDashboard },
  { path: '/candidate/ai-enhancement', name: 'ProfileEnhacement', component: ProfileEnhacement, meta: { requiresAuth: true, role: 'candidate' } },
  {
  path: '/candidate/candidate-profile',
  name: 'ResumeProfile',
  component: CandidateProfile,
  meta: { requiresAuth: true, role: 'candidate' }
  },
  {
    path:'/candidate/courses',
    name:'CandidateCoursePage',
    component: CandidateCoursePage,
    meta: { requiresAuth: true, role: 'candidate' }

  },
  { path:'/manager/dashboard', name: 'ManagerDashboard', component: ManagerDashboard, meta: { requiresAuth: true, role: 'manager' }},
  // You can add more routes as needed, like account or settings pages.
  
  ,{
    path:'/candidate/job-recommend',
    name: 'CandidateJobRecommendations',
    component: CandidateJobRecommendations,
    meta: { requiresAuth: true, role: 'candidate' }
  },
  {
    path:'/candidate/job-search',
    name: 'CandidateJobSearch',
    component: CandidateJobSearch,
    meta: { requiresAuth: true, role: 'candidate' }
  },
  {
    path:'/candidate/vacancies',
    name:'CandidateVacanciesPage',
    component: CandidateVacanciesPage,
    meta: { requiresAuth: true, role: 'candidate' }
  },
  {
  path: '/candidate/applications',
  name: 'CandidateApplicationsPage',
  component: CandidateApplicationsPage,
  meta: { requiresAuth: true, role: 'candidate' }
  }
  
]
});


// Export the router for use in main.js
export default router
