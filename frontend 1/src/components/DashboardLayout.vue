<template>
  <div id="app">
    <div class="sidebar">
      <h2 class="title">
        {{ dashboardTitle }}
      </h2>

      <!-- Dynamic Navigation based on user role -->
      <ul v-if="isCandidate">
        <!-- Candidate Navigation -->
        <li @click="navigate('candidate-home')">
          <a href="#"><i class="fas fa-home"></i> Dashboard</a>
        </li>

        <li @click="toggleProfileMenu" :class="{ 'menu-open': showProfileMenu }">
          <a href="#"><i class="fas fa-user-circle"></i> Profile</a>
          <ul v-if="showProfileMenu">
            <li @click.stop="navigate('candidate-profile')"><a href="#">My Profile</a></li>
          </ul>
        </li>
        <li @click="navigate('apply_leaves')">
          <a href="#"><i class="fas fa-calendar-check"></i> Apply for Leave</a>
        </li>

        <li @click="navigate('job-search')">
          <a href="#"><i class="fas fa-search"></i> Job Search</a>
        </li>

        <li @click="navigate('job-recommend')">
          <a href="#"><i class="fas fa-briefcase"></i> Job Recommendations</a>
        </li>

        <li @click="navigate('applications')">
          <a href="#"><i class="fas fa-file-alt"></i> My Applications</a>
        </li>

        <li @click="toggleAIMenu" :class="{ 'menu-open': showAIMenu }">
          <a href="#"><i class="fas fa-brain"></i> AI Tools</a>
          <ul v-if="showAIMenu">
            <li @click.stop="navigate('ai-enhancement')"><a href="#">Profile Enhancement</a></li>
            <li @click.stop="navigate('upskilling')"><a href="#">Upskilling Path</a></li>
            <li @click.stop="navigate('interview-prep')"><a href="#">Interview Prep</a></li>
          </ul>
        </li>

        <li @click="navigate('performance')">
          <a href="#"><i class="fas fa-chart-line"></i> Performance</a>
        </li>

        <li @click="navigate('courses')">
          <a href="#"><i class="fas fa-bell"></i> Courses</a>
        </li>
        <li @click="navigate('notifications')">
          <a href="#"><i class="fas fa-bell"></i> Notifications</a>
        </li>
        <li @click="navigate('Vacancies')">
          <a href="#"><i class="fas fa-bell"></i> Vacancies</a>
        </li>
        <li @click="navigate('Applications')">
          <a href="#"><i class="fas fa-bell"></i> Applications</a>
        </li>
      </ul>
      <ul v-else-if="isHR">
        <li @click="navigate('hr-home')">
          <a href="#"><i class="fas fa-home"></i> Dashboard</a>
        </li>

        <li @click="toggleRecruitmentMenu" :class="{ 'menu-open': showRecruitmentMenu }">
          <a href="#"><i class="fas fa-users"></i> Recruitment</a>
          <ul v-if="showRecruitmentMenu">
            <li @click.stop="navigate('hr-vacancy')"><a href="#">Job Postings</a></li>
            <li @click.stop="navigate('hr-applications')"><a href="#">Applications</a></li>
            <li @click.stop="navigate('hr-screening')"><a href="#">Screening</a></li>
            <li @click.stop="navigate('hr-interviews')"><a href="#">Interviews</a></li>
            <li @click.stop="navigate('hr-hiring-pipeline')"><a href="#">Hiring Pipeline</a></li>
          </ul>
        </li>

        <li @click="toggleEmployeeMenu" :class="{ 'menu-open': showEmployeeMenu }">
          <a href="#"><i class="fas fa-user-friends"></i> Employee Management</a>
          <ul v-if="showEmployeeMenu">
            <li @click.stop="navigate('hr-employees')"><a href="#">All Employees</a></li>
            <li @click.stop="navigate('hr-onboarding')"><a href="#">Onboarding</a></li>
            <li @click.stop="navigate('hr-performance')"><a href="#">Performance Reviews</a></li>
            <li @click.stop="navigate('hr-attendance')"><a href="#">Attendance</a></li>
          </ul>
        </li>

        <li @click="navigate('hr-leave')">
          <a href="#">
            <i class="fas fa-calendar-check"></i>
            Leave Management
            <span class="leave-badge" v-if="leaveNotificationsCount > 0">{{ leaveNotificationsCount }}</span>
          </a>
        </li>

        <li @click="toggleTrainingMenu" :class="{ 'menu-open': showTrainingMenu }">
          <a href="#"><i class="fas fa-graduation-cap"></i> Training & Development</a>
          <ul v-if="showTrainingMenu">
            <li @click.stop="navigate('hr-training-programs')"><a href="#">Training Programs</a></li>
            <li @click.stop="navigate('hr-courses')"><a href="#">Course Management</a></li>
          </ul>
        </li>

        <li @click="navigate('hr-reports')">
          <a href="#"><i class="fas fa-chart-bar"></i> Reports & Analytics</a>
        </li>

        <li @click="navigate('hr-policies')">
          <a href="#"><i class="fas fa-file-contract"></i> Policies & Procedures</a>
        </li>

        <li @click="navigate('hr-payroll')">
          <a href="#"><i class="fas fa-money-bill-wave"></i> Payroll & Benefits</a>
        </li>

        <li @click="navigate('hr-notifications')">
          <a href="#"><i class="fas fa-bell"></i> Notifications</a>
        </li>
      </ul>

      <!-- Manager Navigation -->
      <ul v-else-if="isManager">
        <li @click="navigate('manager-home')">
          <a href="#"><i class="fas fa-home"></i> Dashboard</a>
        </li>

        <li @click="toggleTeamMenu" :class="{ 'menu-open': showTeamMenu }">
          <a href="#"><i class="fas fa-users"></i> Team Management</a>
          <ul v-if="showTeamMenu">
            <li @click.stop="navigate('manager-team-overview')"><a href="#">Team Overview</a></li>
            <li @click.stop="navigate('manager-team-performance')"><a href="#">Team Performance</a></li>
            <li @click.stop="navigate('manager-team-tasks')"><a href="#">Task Assignment</a></li>
            <li @click.stop="navigate('manager-team-schedule')"><a href="#">Team Schedule</a></li>
          </ul>
        </li>

        <li @click="toggleRecruitmentMenu" :class="{ 'menu-open': showRecruitmentMenu }">
          <a href="#"><i class="fas fa-user-plus"></i> Recruitment</a>
          <ul v-if="showRecruitmentMenu">
            <li @click.stop="navigate('manager-job-requisitions')"><a href="#">Job Requisitions</a></li>
            <li @click.stop="navigate('manager-candidate-review')"><a href="#">Candidate Review</a></li>
            <li @click.stop="navigate('manager-interviews')"><a href="#">Interview Scheduling</a></li>
            <li @click.stop="navigate('manager-hiring-decisions')"><a href="#">Hiring Decisions</a></li>
          </ul>
        </li>

        <li @click="togglePerformanceMenu" :class="{ 'menu-open': showPerformanceMenu }">
          <a href="#"><i class="fas fa-chart-line"></i> Performance Management</a>
          <ul v-if="showPerformanceMenu">
            <li @click.stop="navigate('manager-performance-reviews')"><a href="#">Performance Reviews</a></li>
            <li @click.stop="navigate('manager-goal-setting')"><a href="#">Goal Setting</a></li>
            <li @click.stop="navigate('manager-feedback')"><a href="#">360° Feedback</a></li>
            <li @click.stop="navigate('manager-development-plans')"><a href="#">Development Plans</a></li>
          </ul>
        </li>

        <li @click="navigate('manager-projects')">
          <a href="#"><i class="fas fa-project-diagram"></i> Project Management</a>
        </li>

        <li @click="navigate('manager-budget')">
          <a href="#"><i class="fas fa-calculator"></i> Budget & Resources</a>
        </li>

        <li @click="navigate('manager-reports')">
          <a href="#"><i class="fas fa-file-alt"></i> Reports</a>
        </li>

        <li @click="navigate('manager-notifications')">
          <a href="#"><i class="fas fa-bell"></i> Notifications</a>
        </li>
      </ul>

      <!-- BDA Navigation -->
      <ul v-else-if="isBDA">
        <li @click="navigate('bdo-home')">
          <a href="#"><i class="fas fa-home"></i> Dashboard</a>
        </li>

        <li @click="navigate('bdo-expenses')">
          <a href="#"><i class="fas fa-file-invoice-dollar"></i> Expense Reports</a>
        </li>

        <li @click="navigate('bdo-eod')">
          <a href="#"><i class="fas fa-clipboard-list"></i> EOD Reports</a>
        </li>

        <li @click="navigate('bdo-interviews')">
          <a href="#"><i class="fas fa-user-friends"></i> Behavioral Interviews</a>
        </li>

        <li @click="navigate('bdo-leaves')">
          <a href="#"><i class="fas fa-umbrella-beach"></i> Leave Management</a>
        </li>

        <li @click="navigate('bdo-notifications')">
          <a href="#"><i class="fas fa-bell"></i> Notifications</a>
        </li>
      </ul>

      <!-- HO Navigation -->
      <ul v-else-if="isHO">
        <li @click="navigate('ho-home')">
          <a href="#"><i class="fas fa-home"></i> Dashboard</a>
        </li>

        <li @click="navigate('ho-vacancies')">
          <a href="#"><i class="fas fa-briefcase"></i> Vacancies</a>
        </li>

        <li @click="navigate('ho-interviews')">
          <a href="#"><i class="fas fa-laptop-code"></i> Technical Interviews</a>
        </li>

        <li @click="navigate('ho-tasks')">
          <a href="#"><i class="fas fa-tasks"></i> Task Management</a>
        </li>

        <li @click="navigate('ho-leaves')">
          <a href="#"><i class="fas fa-umbrella-beach"></i> Leave Management</a>
        </li>

        <li @click="navigate('ho-notifications')">
          <a href="#"><i class="fas fa-bell"></i> Notifications</a>
        </li>
      </ul>

      <!-- Admin/HR Navigation (existing) -->
      <ul v-else>
        <li @click="navigate('home')"><a href="#"><i class="fas fa-home"></i> Home</a></li>
        <li @click="toggleRecruitmentMenu" :class="{ 'menu-open': showRecruitmentMenu }">
          <a href="#"><i class="fas fa-users"></i> Recruitment</a>
          <ul v-if="showRecruitmentMenu">
            <li @click.stop="navigate('vacancy')"><a href="#">Vacancy List</a></li>
            <li @click.stop="navigate('jobPosting')"><a href="#">Job Posting</a></li>
            <li @click.stop="navigate('apply')"><a href="#">Apply</a></li>
            <li @click.stop="navigate('screening')"><a href="#">Screening</a></li>
            <li @click.stop="navigate('hiringPipeline')"><a href="#">Hiring Pipeline</a></li>
          </ul>
        </li>
        <li @click="navigate('onboarding')"><a href="#"><i class="fas fa-user-check"></i> Onboarding</a></li>
        <li @click="navigate('training')"><a href="#"><i class="fas fa-chalkboard-teacher"></i> Training</a></li>
        <li @click="navigate('expense')"><a href="#"><i class="fas fa-file-invoice-dollar"></i> Expense Mgmt</a></li>
        <li @click="navigate('reporting')"><a href="#"><i class="fas fa-chart-bar"></i> Reporting</a></li>
        <li @click="navigate('account')"><a href="#"><i class="fas fa-user-circle"></i> Account</a></li>
      </ul>

      <!--create manager navigation-->

      <!-- Common items -->
      <div class="sidebar-footer">
        <li @click="navigate('settings')"><a href="#"><i class="fas fa-cog"></i> Settings</a></li>
        <li @click="logout"><a href="#"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
      </div>
    </div>

    <div class="main-content">
      <!-- Top Navigation Bar -->
      <nav class="top-navbar" v-if="isCandidate">
        <div class="nav-left">
          <h3>{{ currentPageTitle }}</h3>
        </div>
        <div class="nav-right">
          <div class="nav-item" @click="navigate('notifications')">
            <i class="fas fa-bell"></i>
            <span class="notification-badge" v-if="notificationCount > 0">{{ notificationCount }}</span>
          </div>
          <div class="nav-item dropdown" @click="toggleUserMenu" ref="userDropdown">
            <img :src="userAvatar" alt="Profile" class="profile-avatar">
            <span>{{ userName }}</span>
            <i class="fas fa-chevron-down"></i>

            <div class="dropdown-menu" v-if="showUserMenu">
              <a @click.stop="navigate('candidate-profile')">
                <i class="fas fa-user"></i> My Profile
              </a>
              <a @click.stop="navigate('settings')">
                <i class="fas fa-cog"></i> Settings
              </a>
              <hr>
              <a @click.stop="logout" class="logout-item">
                <i class="fas fa-sign-out-alt"></i> Logout
              </a>
            </div>
          </div>
        </div>
      </nav>

      <!-- FIXED: Add the missing content-area wrapper -->
      <div class="content-area">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const showRecruitmentMenu = ref(false)
const showProfileMenu = ref(false)
const showAIMenu = ref(false)
const showUserMenu = ref(false)
const router = useRouter()
const route = useRoute()
const showEmployeeMenu = ref(false)
const showTeamMenu = ref(false)
const showTrainingMenu = ref(false)
const showPerformanceMenu = ref(false)
// User state (you should get this from your auth store/service)
const userRole = ref(null) // or get from localStorage/auth service
const userName = ref(null) // get from auth
const userAvatar = ref('/default-avatar.png') // get from auth
const userStatus = ref(null);
const notificationCount = ref(null) // get from API
const leaveNotificationsCount = ref(null)


onMounted(() => {
  loadUserData()
  fetchLeaveNotificationsCount()
})

async function fetchLeaveNotificationsCount() {
  try {
    const resp = await axios.get('/api/leave/history', {
      headers: { Authorization: `bearer ${localStorage.getItem('access_token')}` }
    })
    leaveNotificationsCount.value = resp.data.data.filter(leave => leave.status === 'Pending').length || 0
    console.log("Pending leaves", leaveNotificationsCount.value)
  } catch (error) {
    console.error('Failed to fetch leave notifications count:', error)
    leaveNotificationsCount.value = 0
  }
}

defineExpose({
  fetchLeaveNotificationsCount
})

// Computed properties
const isCandidate = computed(() => userRole.value === 'candidate')
const isHR = computed(() => userRole.value === 'hr' || userRole.value === 'admin')
const isManager = computed(() => userRole.value === 'manager')
const isAdmin = computed(() => userRole.value === 'admin')
const isBDA = computed(() => userRole.value === 'bda')
const isHO = computed(() => userRole.value === 'ho')
// const dashboardTitle = computed(() => isCandidate.value ? 'Candidate Portal' : 'Dashboard')

const dashboardTitle = computed(() => {
  if (isCandidate.value) return 'Candidate Portal'
  if (isHR.value) return 'HR Management'
  if (isManager.value) return 'Manager Portal'
  if (isAdmin.value) return 'Admin Dashboard'
  if (isBDA.value) return 'BDA Dashboard'
  if (isHO.value) return 'HO Dashboard'
})

const currentPageTitle = computed(() => {
  const pageTitles = {
    '/candidatedashboard': 'Dashboard',
    '/candidate/candidate-profile': 'My Profile',
    '/candidate/job-search': 'Job Search',
    '/candidate/job-recommend': 'Job Recommendations',
    '/candidate/applications': 'My Applications',
    '/candidate/ai-enhancement': 'AI Enhancement',
    '/candidate/performance': 'Performance',
    '/candidate/training': 'Training',

    '/hr/dashboard': 'HR Dashboard',
    '/hr/vacancy': 'Job Postings',
    '/hr/applications': 'Applications',
    '/hr/employees': 'Employee Management',
    '/hr/onboarding': 'Onboarding',
    '/hr/training-programs': 'Training Programs',
    '/hr/reports': 'HR Reports',

    // Manager pages
    '/manager/dashboard': 'Manager Dashboard',
    '/manager/team-overview': 'Team Overview',
    '/manager/team-performance': 'Team Performance',
    '/manager/job-requisitions': 'Job Requisitions',
    '/manager/performance-reviews': 'Performance Reviews',
    '/manager/projects': 'Project Management'
  }
  return pageTitles[route.path] || 'Dashboard'
})

// Functions
function toggleRecruitmentMenu() {
  showRecruitmentMenu.value = !showRecruitmentMenu.value
}

function toggleProfileMenu() {
  showProfileMenu.value = !showProfileMenu.value
}

function toggleAIMenu() {
  showAIMenu.value = !showAIMenu.value
}

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}

function toggleEmployeeMenu() { showEmployeeMenu.value = !showEmployeeMenu.value }
function toggleTrainingMenu() { showTrainingMenu.value = !showTrainingMenu.value }
function toggleTeamMenu() { showTeamMenu.value = !showTeamMenu.value }
function togglePerformanceMenu() { showPerformanceMenu.value = !showPerformanceMenu.value }


function navigate(page) {
  // Close menus when navigating
  if (!['recruitment', 'profile', 'ai'].includes(page)) {
    showRecruitmentMenu.value = false
    showProfileMenu.value = false
    showAIMenu.value = false
  }

  showUserMenu.value = false
  showEmployeeMenu.value = false
  showTrainingMenu.value = false
  showTeamMenu.value = false
  showPerformanceMenu.value = false

  const pageMap = {
    // Candidate routes
    'candidate-home': '/candidateDashboard',
    'candidate-profile': '/candidate/candidate-profile',
    'personal-info': '/candidate/personal-info',
    'skills': '/candidate/skills',
    'job-search': '/candidate/job-search',
    'job-recommend': '/candidate/job-recommend',
    'applications': '/candidate/applications',
    'ai-enhancement': '/candidate/ai-enhancement',
    'upskilling': '/candidate/upskilling',
    'interview-prep': '/candidate/interview-prep',
    'performance': '/candidate/performance',
    'training': '/candidate/training',
    'notifications': '/candidate/notifications',
    'courses': '/candidate/courses',
    'Vacancies': '/candidate/Vacancies',
    'Applications': '/candidate/applications',
    'apply_leaves': '/candidate/apply-leave',


    'hr-home': '/hrDashboard',
    'hr-vacancy': '/hr/vacancy',
    'hr-applications': '/hr/applications',
    'hr-screening': '/hr/screening',
    'hr-interviews': '/hr/interviews',
    'hr-hiring-pipeline': '/hr/hiring-pipeline',
    'hr-employees': '/hr/employees',
    'hr-onboarding': '/hr/onboarding',
    'hr-performance': '/hr/performance',
    'hr-attendance': '/hr/attendance',
    'hr-training-programs': '/hr/training-programs',
    'hr-courses': '/hr/courses',
    'hr-skills-assessment': '/hr/skills-assessment',
    'hr-reports': '/hr/reports',
    'hr-policies': '/hr/policies',
    'hr-payroll': '/hr/payroll',
    'hr-notifications': '/hr/notifications',
    'hr-leave': '/hr/leave-management',

    // Manager routes
    'manager-home': '/managerDashboard',
    'manager-team-overview': '/manager/team-overview',
    'manager-team-performance': '/manager/team-performance',
    'manager-team-tasks': '/manager/team-tasks',
    'manager-team-schedule': '/manager/team-schedule',
    'manager-job-requisitions': '/manager/job-requisitions',
    'manager-candidate-review': '/manager/candidate-review',
    'manager-interviews': '/manager/interviews',
    'manager-hiring-decisions': '/manager/hiring-decisions',
    'manager-performance-reviews': '/manager/performance-reviews',
    'manager-goal-setting': '/manager/goal-setting',
    'manager-feedback': '/manager/feedback',
    'manager-development-plans': '/manager/development-plans',
    'manager-projects': '/manager/projects',
    'manager-budget': '/manager/budget',
    'manager-reports': '/manager/reports',
    'manager-notifications': '/manager/notifications',

    // BDA routes
    'bda-home': '/bda/dashboard',
    'bda-expenses': '/bda/expenses',
    'bda-eod': '/bda/eod',
    'bda-interviews': '/bda/interviews',
    'bda-leaves': '/bda/leaves',
    'bda-notifications': '/bda/notifications',

    // HO routes
    'ho-home': '/ho/dashboard',
    'ho-vacancies': '/ho/vacancies',
    'ho-interviews': '/ho/interviews',
    'ho-tasks': '/ho/tasks',
    'ho-leaves': '/ho/leaves',
    'ho-notifications': '/ho/notifications',

    // Admin routes (existing)
    home: '/',
    vacancy: '/vacancy',
    jobPosting: '/job-posting',
    apply: '/apply',
    screening: '/screening',
    hiringPipeline: '/hiring-pipeline',
    onboarding: '/onboarding',
    expense: '/expense',
    reporting: '/reporting',
    account: '/account'
  }

  if (pageMap[page]) {
    router.push(pageMap[page])
  }
}

function logout() {
  localStorage.removeItem('auth')
  localStorage.removeItem('access_token')
  router.push('/login')
}

// Close dropdown when clicking outside
function handleClickOutside(event) {
  if (!event.target.closest('.dropdown')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  // Load user data from auth service/localStorage
  loadUserData()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

async function loadUserData() {
  // Get user data from localStorage or API
  const userData = await axios.get('/api/users/', {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  })

  const userNotifications = await axios.get('/api/notifications/', {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  })



  userRole.value = userData.data.role_name
  userName.value = userData.data.name
  userStatus.value = userData.data.status
  notificationCount.value = userNotifications.data.length

}
</script>

<style scoped>
/* Global reset and viewport constraints */
#app {
  display: flex;
  height: 100vh;
  width: 100%;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
  overflow: hidden;
  box-sizing: border-box;
}

.leave-badge {
  display: inline-block;
  background-color: #2afd5b;
  border-radius: 50%;
  padding: 2px 8px;
  font-size: 0.75rem;
  font-weight: bold;
  color: rgb(0, 0, 0);
  box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.05);
}

.sidebar {
  width: 280px;
  min-width: 280px;
  flex-shrink: 0;
  height: 100vh;
  overflow-y: auto;
  background: linear-gradient(180deg, #2c3e50, #34495e);
  color: #ecf0f1;
  padding: 25px;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.main-content {
  flex: 1;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
  /* IMPORTANT: Allows flex item to shrink below content size */
}

.top-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 25px;
  background: #fff;
  border-bottom: 1px solid #ecf0f1;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  height: 70px;
  min-height: 70px;
  flex-shrink: 0;
  z-index: 100;
  box-sizing: border-box;
}

/* FIXED: Content area with proper scrolling */
.content-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 30px;
  height: calc(100vh - 70px);
  box-sizing: border-box;
}

/* Responsive navbar text */
.nav-left h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
}

.nav-item {
  position: relative;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background-color 0.3s ease;
  white-space: nowrap;
}

.nav-item:hover {
  background-color: #f8f9fa;
}

.nav-item i {
  font-size: 1.2rem;
  color: #7f8c8d;
}

.notification-badge {
  position: absolute;
  top: 5px;
  right: 5px;
  background: #e74c3c;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: bold;
}

.dropdown {
  position: relative;
}

.profile-avatar {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  margin-right: 10px;
  object-fit: cover;
  flex-shrink: 0;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  min-width: 180px;
  border-radius: 8px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  padding: 8px 0;
  border: 1px solid #ecf0f1;
}

.dropdown-menu a {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  color: #2c3e50;
  text-decoration: none;
  transition: background-color 0.3s ease;
}

.dropdown-menu a:hover {
  background-color: #f8f9fa;
}

.dropdown-menu hr {
  margin: 8px 0;
  border: none;
  border-top: 1px solid #ecf0f1;
}

.logout-item {
  color: #e74c3c !important;
}

.sidebar-footer {
  margin-top: auto;
  border-top: 1px solid #34495e;
  padding-top: 20px;
}

.title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 30px;
  text-align: center;
  cursor: pointer;
  color: #fff;
  word-break: break-word;
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar li {
  margin-bottom: 8px;
  border-radius: 6px;
  transition: background-color 0.2s ease;
}

.sidebar li.menu-open>a {
  background-color: #3498db;
  color: white;
}

.sidebar a {
  text-decoration: none;
  color: #bdc3c7;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-radius: 6px;
  transition: all 0.3s ease;
  word-break: break-word;
}

.sidebar li:hover>a,
.sidebar a:hover {
  background-color: #34495e;
  color: #fff;
}

.sidebar ul ul {
  margin-left: 25px;
  padding-top: 10px;
  border-left: 2px solid #34495e;
}

.sidebar ul ul li a {
  padding: 10px 15px;
  font-size: 0.9rem;
}

/* Mobile and tablet responsiveness */
@media (max-width: 1024px) {
  .sidebar {
    width: 250px;
    min-width: 250px;
  }

  .content-area {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  #app {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    min-width: 100%;
    height: auto;
    max-height: 200px;
    padding: 15px;
  }

  .sidebar .title {
    font-size: 1.4rem;
    margin-bottom: 15px;
  }

  .sidebar ul {
    display: flex;
    gap: 10px;
    overflow-x: auto;
    padding-bottom: 10px;
  }

  .sidebar li {
    flex-shrink: 0;
    margin-bottom: 0;
  }

  .sidebar ul ul {
    display: none;
    /* Hide submenus on mobile */
  }

  .main-content {
    height: calc(100vh - 200px);
  }

  .top-navbar {
    padding: 10px 15px;
    height: 60px;
    min-height: 60px;
  }

  .content-area {
    height: calc(100vh - 260px);
    padding: 15px;
  }

  .nav-left h3 {
    font-size: 1.2rem;
    max-width: 150px;
  }

  .nav-right {
    gap: 10px;
  }

  .nav-item span {
    display: none;
    /* Hide username on mobile */
  }

  .dropdown-menu {
    right: -10px;
    min-width: 150px;
  }
}

@media (max-width: 480px) {
  .content-area {
    padding: 10px;
  }

  .top-navbar {
    padding: 8px 10px;
  }

  .nav-left h3 {
    font-size: 1rem;
    max-width: 120px;
  }
}

/* High zoom levels */
@media (min-resolution: 150dpi) {
  .nav-item span {
    font-size: 0.9rem;
  }

  .sidebar a {
    font-size: 0.9rem;
  }
}
</style>