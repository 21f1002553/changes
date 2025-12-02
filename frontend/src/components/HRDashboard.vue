<template>
  <DashboardLayout>
    <div class="hr-dashboard">
      <!-- Header -->
      <div class="dashboard-header">
        <div class="header-content">
          <h1>
            <i class="fas fa-tachometer-alt"></i>
            HR Dashboard
          </h1>
          <p>Welcome back, {{ userName }}! Here's your HR overview for today.</p>
        </div>
        <div class="quick-actions">
          <button @click="navigate('hr-vacancy')" class="quick-btn primary">
            <i class="fas fa-plus"></i>
            Post New Job
          </button>
          <button @click="navigate('hr-onboarding')" class="quick-btn secondary">
            <i class="fas fa-user-plus"></i>
            New Employee
          </button>
        </div>
      </div>

      <!-- Stats Overview -->
      <div class="stats-grid">
        <div class="stat-card primary">
          <div class="stat-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="stat-content">
            <h3>{{ hrStats.totalEmployees }}</h3>
            <p>Total Employees</p>
            <span class="stat-change positive">+{{ hrStats.newEmployeesThisMonth }} this month</span>
          </div>
        </div>

        <div class="stat-card success">
          <div class="stat-icon">
            <i class="fas fa-file-alt"></i>
          </div>
          <div class="stat-content">
            <h3>{{ hrStats.pendingApplications }}</h3>
            <p>Pending Applications</p>
            <span class="stat-change">{{ hrStats.newApplicationsToday }} new today</span>
          </div>
        </div>

        <div class="stat-card warning">
          <div class="stat-icon">
            <i class="fas fa-calendar-check"></i>
          </div>
          <div class="stat-content">
            <h3>{{ hrStats.upcomingInterviews }}</h3>
            <p>Interviews Today</p>
            <span class="stat-change">{{ hrStats.totalInterviewsWeek }} this week</span>
          </div>
        </div>

        <div class="stat-card danger">
          <div class="stat-icon">
            <i class="fas fa-briefcase"></i>
          </div>
          <div class="stat-content">
            <h3>{{ hrStats.openPositions }}</h3>
            <p>Open Positions</p>
            <span class="stat-change">{{ hrStats.urgentPositions }} urgent</span>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="dashboard-grid">
        <!-- Recent Applications -->
        <div class="dashboard-card applications">
          <div class="card-header">
            <h3><i class="fas fa-inbox"></i> Recent Applications</h3>
            <button @click="navigate('hr-applications')" class="view-all-btn">View All</button>
          </div>
          <div class="applications-list">
            <div v-for="application in recentApplications" :key="application.id" class="application-item">
              <div class="applicant-avatar">
                <img :src="application.avatar || '/default-avatar.png'" :alt="application.name">
              </div>
              <div class="applicant-info">
                <h4>{{ application.name }}</h4>
                <p>{{ application.position }}</p>
                <span class="application-date">{{ formatDate(application.applied_date) }}</span>
              </div>
              <div class="application-actions">
                <button class="btn-review" @click="reviewApplication(application.id)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="btn-approve" @click="approveApplication(application.id)">
                  <i class="fas fa-check"></i>
                </button>
                <button class="btn-reject" @click="rejectApplication(application.id)">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Interviews -->
        <div class="dashboard-card interviews">
          <div class="card-header">
            <h3><i class="fas fa-calendar-alt"></i> Today's Interviews</h3>
            <button @click="navigate('hr-interviews')" class="view-all-btn">Schedule More</button>
          </div>
          <div class="interviews-list">
            <div v-for="interview in upcomingInterviews" :key="interview.id" class="interview-item">
              <div class="interview-time">
                <span class="time">{{ formatTime(interview.scheduled_time) }}</span>
                <span class="duration">{{ interview.duration }}min</span>
              </div>
              <div class="interview-info">
                <h4>{{ interview.candidate_name }}</h4>
                <p>{{ interview.position }}</p>
                <span class="interviewer">with {{ interview.interviewer }}</span>
              </div>
              <div class="interview-actions">
                <button class="btn-join" @click="joinInterview(interview.id)">
                  <i class="fas fa-video"></i>
                </button>
                <button class="btn-reschedule" @click="rescheduleInterview(interview.id)">
                  <i class="fas fa-clock"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Recruitment Pipeline -->
        <div class="dashboard-card pipeline">
          <div class="card-header">
            <h3><i class="fas fa-funnel-dollar"></i> Recruitment Pipeline</h3>
            <select v-model="selectedPosition" class="position-filter">
              <option value="">All Positions</option>
              <option v-for="position in openPositions" :key="position.id" :value="position.id">
                {{ position.title }}
              </option>
            </select>
          </div>
          <div class="pipeline-stages">
            <div v-for="stage in pipelineStages" :key="stage.name" class="pipeline-stage">
              <div class="stage-header">
                <h4>{{ stage.name }}</h4>
                <span class="stage-count">{{ stage.count }}</span>
              </div>
              <div class="stage-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: stage.percentage + '%' }"></div>
                </div>
                <span class="progress-text">{{ stage.percentage }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Employee Analytics -->
        <div class="dashboard-card analytics">
          <div class="card-header">
            <h3><i class="fas fa-chart-pie"></i> Employee Analytics</h3>
            <div class="analytics-tabs">
              <button @click="analyticsTab = 'department'" :class="{ active: analyticsTab === 'department' }">
                Departments
              </button>
              <button @click="analyticsTab = 'performance'" :class="{ active: analyticsTab === 'performance' }">
                Performance
              </button>
            </div>
          </div>
          <div class="analytics-content">
            <div v-if="analyticsTab === 'department'" class="department-breakdown">
              <div v-for="dept in departmentStats" :key="dept.name" class="dept-item">
                <div class="dept-info">
                  <span class="dept-name">{{ dept.name }}</span>
                  <span class="dept-count">{{ dept.count }} employees</span>
                </div>
                <div class="dept-bar">
                  <div class="bar-fill" :style="{ width: dept.percentage + '%' }"></div>
                </div>
              </div>
            </div>
            
            <div v-if="analyticsTab === 'performance'" class="performance-metrics">
              <div class="metric-item">
                <span class="metric-label">Average Performance Score</span>
                <span class="metric-value">{{ performanceStats.avgScore }}/5</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Top Performers</span>
                <span class="metric-value">{{ performanceStats.topPerformers }}%</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Needs Improvement</span>
                <span class="metric-value">{{ performanceStats.needsImprovement }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Tasks -->
        <div class="dashboard-card quick-tasks">
          <div class="card-header">
            <h3><i class="fas fa-tasks"></i> Quick Tasks</h3>
          </div>
          <div class="tasks-list">
            <div v-for="task in quickTasks" :key="task.id" class="task-item" :class="{ urgent: task.urgent }">
              <div class="task-checkbox">
                <input type="checkbox" :id="'task-' + task.id" v-model="task.completed" @change="updateTask(task)">
                <label :for="'task-' + task.id"></label>
              </div>
              <div class="task-content">
                <h4>{{ task.title }}</h4>
                <p>{{ task.description }}</p>
                <span class="task-due">Due: {{ formatDate(task.due_date) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activities -->
        <div class="dashboard-card activities">
          <div class="card-header">
            <h3><i class="fas fa-history"></i> Recent Activities</h3>
          </div>
          <div class="activities-list">
            <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
              <div class="activity-icon" :class="activity.type">
                <i :class="activity.icon"></i>
              </div>
              <div class="activity-content">
                <p>{{ activity.description }}</p>
                <span class="activity-time">{{ formatDateTime(activity.timestamp) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const router = useRouter()

// State
const userName = ref('HR Manager')
const analyticsTab = ref('department')
const selectedPosition = ref('')

// Data
const hrStats = ref({
  totalEmployees: 156,
  newEmployeesThisMonth: 8,
  pendingApplications: 24,
  newApplicationsToday: 5,
  upcomingInterviews: 7,
  totalInterviewsWeek: 23,
  openPositions: 12,
  urgentPositions: 3
})

const recentApplications = ref([
  {
    id: 1,
    name: 'Sarah Johnson',
    position: 'Frontend Developer',
    applied_date: '2024-01-15',
    avatar: null
  }
  // Add more applications
])

const upcomingInterviews = ref([
  {
    id: 1,
    candidate_name: 'John Doe',
    position: 'Backend Developer',
    scheduled_time: '2024-01-16T10:00:00',
    duration: 60,
    interviewer: 'Mike Smith'
  }
  // Add more interviews
])

const openPositions = ref([
  { id: 1, title: 'Frontend Developer' },
  { id: 2, title: 'Backend Developer' },
  { id: 3, title: 'UI/UX Designer' }
])

const pipelineStages = ref([
  { name: 'Applied', count: 45, percentage: 100 },
  { name: 'Screening', count: 32, percentage: 71 },
  { name: 'Interview', count: 18, percentage: 40 },
  { name: 'Final Review', count: 8, percentage: 18 },
  { name: 'Offer', count: 3, percentage: 7 }
])

const departmentStats = ref([
  { name: 'Engineering', count: 45, percentage: 75 },
  { name: 'Marketing', count: 28, percentage: 47 },
  { name: 'Sales', count: 35, percentage: 58 },
  { name: 'HR', count: 12, percentage: 20 },
  { name: 'Finance', count: 18, percentage: 30 }
])

const performanceStats = ref({
  avgScore: 4.2,
  topPerformers: 25,
  needsImprovement: 8
})

const quickTasks = ref([
  {
    id: 1,
    title: 'Review Sarah Johnson\'s Application',
    description: 'Frontend Developer position',
    due_date: '2024-01-16',
    urgent: true,
    completed: false
  }
  // Add more tasks
])

const recentActivities = ref([
  {
    id: 1,
    type: 'application',
    icon: 'fas fa-user-plus',
    description: 'New application received for Backend Developer',
    timestamp: '2024-01-15T14:30:00'
  }
  // Add more activities
])

// Functions
function navigate(page) {
  router.push(`/${page}`)
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}

function formatTime(dateString) {
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Action functions
function reviewApplication(id) {
  console.log('Reviewing application:', id)
  // Navigate to application review page
}

function approveApplication(id) {
  console.log('Approving application:', id)
  // Handle approval logic
}

function rejectApplication(id) {
  console.log('Rejecting application:', id)
  // Handle rejection logic
}

function joinInterview(id) {
  console.log('Joining interview:', id)
  // Open video call or interview page
}

function rescheduleInterview(id) {
  console.log('Rescheduling interview:', id)
  // Open reschedule modal
}

function updateTask(task) {
  console.log('Updating task:', task)
  // Update task status
}

// Load data on mount
onMounted(async () => {
  // Load HR dashboard data
  // await loadHRData()
})
</script>

<style scoped>
.hr-dashboard {
  padding: 0;
  max-width: 100%;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  gap: 20px;
}

.header-content h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-content p {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

.quick-actions {
  display: flex;
  gap: 15px;
}

.quick-btn {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.quick-btn.primary {
  background: #3498db;
  color: white;
}

.quick-btn.secondary {
  background: #27ae60;
  color: white;
}

.quick-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  border-left: 4px solid;
}

.stat-card.primary { border-left-color: #3498db; }
.stat-card.success { border-left-color: #27ae60; }
.stat-card.warning { border-left-color: #f39c12; }
.stat-card.danger { border-left-color: #e74c3c; }

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.stat-card.primary .stat-icon { background: #3498db; }
.stat-card.success .stat-icon { background: #27ae60; }
.stat-card.warning .stat-icon { background: #f39c12; }
.stat-card.danger .stat-icon { background: #e74c3c; }

.stat-content h3 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.stat-content p {
  margin: 0 0 8px 0;
  color: #7f8c8d;
  font-weight: 600;
}

.stat-change {
  font-size: 0.85rem;
  padding: 3px 8px;
  border-radius: 12px;
  background: #ecf0f1;
  color: #7f8c8d;
}

.stat-change.positive {
  background: #d5f4e6;
  color: #27ae60;
}

/* Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
}

.dashboard-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  border: 1px solid #ecf0f1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ecf0f1;
}

.card-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.view-all-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background-color 0.3s ease;
}

.view-all-btn:hover {
  background: #2980b9;
}

/* Applications List */
.application-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 0;
  border-bottom: 1px solid #ecf0f1;
}

.application-item:last-child {
  border-bottom: none;
}

.applicant-avatar img {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  object-fit: cover;
}

.applicant-info {
  flex: 1;
}

.applicant-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 1rem;
}

.applicant-info p {
  margin: 0 0 5px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.application-date {
  font-size: 0.8rem;
  color: #bdc3c7;
}

.application-actions {
  display: flex;
  gap: 8px;
}

.application-actions button {
  width: 35px;
  height: 35px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.btn-review { background: #3498db; color: white; }
.btn-approve { background: #27ae60; color: white; }
.btn-reject { background: #e74c3c; color: white; }

.application-actions button:hover {
  transform: translateY(-1px);
}

/* Interview Items */
.interview-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 0;
  border-bottom: 1px solid #ecf0f1;
}

.interview-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 70px;
}

.interview-time .time {
  font-weight: 600;
  color: #2c3e50;
}

.interview-time .duration {
  font-size: 0.8rem;
  color: #7f8c8d;
}

.interview-info {
  flex: 1;
}

.interview-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.interview-info p {
  margin: 0 0 5px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.interviewer {
  font-size: 0.8rem;
  color: #bdc3c7;
}

.interview-actions {
  display: flex;
  gap: 8px;
}

.btn-join { background: #27ae60; color: white; }
.btn-reschedule { background: #f39c12; color: white; }

/* Pipeline Stages */
.pipeline-stages {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.pipeline-stage {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.stage-header {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 120px;
}

.stage-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 0.9rem;
}

.stage-count {
  background: #3498db;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.stage-progress {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3498db;
  transition: width 0.3s ease;
}

.progress-text {
  min-width: 40px;
  text-align: right;
  font-size: 0.9rem;
  font-weight: 600;
  color: #7f8c8d;
}

/* Analytics */
.analytics-tabs {
  display: flex;
  gap: 10px;
}

.analytics-tabs button {
  padding: 8px 15px;
  border: 1px solid #ecf0f1;
  background: white;
  color: #7f8c8d;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.analytics-tabs button.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.dept-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
}

.dept-info {
  display: flex;
  flex-direction: column;
  min-width: 120px;
}

.dept-name {
  font-weight: 600;
  color: #2c3e50;
}

.dept-count {
  font-size: 0.8rem;
  color: #7f8c8d;
}

.dept-bar {
  flex: 1;
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  margin-left: 15px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: #3498db;
  transition: width 0.3s ease;
}

.performance-metrics {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  color: #7f8c8d;
}

.metric-value {
  font-weight: 600;
  color: #2c3e50;
}

/* Tasks */
.task-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px 0;
  border-bottom: 1px solid #ecf0f1;
}

.task-item.urgent {
  background: #fff5f5;
  padding: 15px;
  border-left: 3px solid #e74c3c;
  border-radius: 6px;
}

.task-checkbox {
  position: relative;
}

.task-checkbox input[type="checkbox"] {
  width: 20px;
  height: 20px;
  margin: 0;
}

.task-content h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 0.95rem;
}

.task-content p {
  margin: 0 0 5px 0;
  color: #7f8c8d;
  font-size: 0.85rem;
}

.task-due {
  font-size: 0.8rem;
  color: #e74c3c;
  font-weight: 600;
}

/* Activities */
.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px 0;
  border-bottom: 1px solid #ecf0f1;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
}

.activity-icon.application { background: #3498db; }
.activity-icon.interview { background: #f39c12; }
.activity-icon.hire { background: #27ae60; }

.activity-content p {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 0.9rem;
}

.activity-time {
  font-size: 0.8rem;
  color: #7f8c8d;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .pipeline-stage {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .stage-progress {
    width: 100%;
  }
}
</style>