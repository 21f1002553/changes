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
          <p>Welcome back, {{ userData.name }}! Here's your HR overview for today.</p>
        </div>
        <div class="quick-actions">
          <button @click="openPostModal" class="quick-btn primary">
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
            <h3>
              <i class="fas fa-calendar-alt"></i>
              Today's Interviews
              <span class="today-count" v-if="upcomingInterviews.length > 0">
                {{ upcomingInterviews.length }}
              </span>
            </h3>
            <button @click="navigateToHiringPipeline" class="view-all-btn">
              <i class="fas fa-plus"></i>
              Schedule More
            </button>
          </div>

          <div class="interviews-list" v-if="upcomingInterviews.length > 0">
            <div v-for="interview in upcomingInterviews" :key="interview.id" class="interview-item">
              <div class="interview-time">
                <span class="time">{{ formatTime(interview.scheduled_time) }}</span>
                <span class="duration">{{ interview.duration }}min</span>
              </div>

              <div class="interview-info">
                <h4>{{ interview.candidate_name }}</h4>
                <p>{{ interview.position }}</p>
                <div class="interview-meta">
                  <span class="interviewer">
                    <i class="fas fa-user-tie"></i>
                    {{ interview.interviewer }}
                  </span>
                  <span class="interview-type-badge" :style="{
                    backgroundColor: getInterviewTypeColor(interview.interview_type),
                    color: 'white'
                  }">
                    {{ formatInterviewType(interview.interview_type) }}
                  </span>
                </div>
              </div>

              <div class="interview-actions">
                <button class="btn-join" @click="joinInterview(interview.id)" :disabled="!interview.meeting_link"
                  :title="interview.meeting_link ? 'Join Meeting' : 'No meeting link'">
                  <i class="fas fa-video"></i>
                </button>
                <button class="btn-reschedule" @click="rescheduleInterview(interview.id)" title="Reschedule Interview">
                  <i class="fas fa-clock"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="interviews-empty">
            <i class="fas fa-calendar-check"></i>
            <p>No interviews scheduled for today</p>
            <button @click="navigateToHiringPipeline" class="btn-schedule-now">
              <i class="fas fa-plus"></i>
              Schedule Interviews
            </button>
          </div>
        </div>
        <!-- Recruitment Pipeline -->
        <div class="dashboard-card pipeline">
          <div class="card-header">
            <h3><i class="fas fa-funnel-dollar"></i> Recruitment Pipeline</h3>
            <div class="pipeline-summary">
              <span class="total-candidates">
                <i class="fas fa-users"></i>
                {{ totalCandidates }} Total
              </span>
              <!--  Create Pipeline Stage Button -->
              <button @click="showCreateStageModal = true" class="btn-create-stage">
                <i class="fas fa-plus"></i>
                Add Stage
              </button>
              <!-- <select v-model="selectedPosition" class="position-filter">
                <option value="">All Positions</option>
                <option v-for="position in openPositions" :key="position.id" :value="position.id">
                  {{ position.title }}
                </option>
              </select> -->
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="pipelineStages.length === 0" class="pipeline-loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading pipeline data...</p>
          </div>

          <!-- Pipeline Stages -->
          <div v-else class="pipeline-stages">
            <div v-for="stage in pipelineStagesWithPercentage" :key="stage.id" class="pipeline-stage"
              :class="{ 'has-candidates': stage.candidate_count > 0 }">
              <div class="stage-header">
                <div class="stage-info">
                  <h4>{{ stage.name }}</h4>
                  <span class="stage-description">{{ stage.description }}</span>
                </div>
                <span class="stage-count" :class="getStageCountClass(stage.candidate_count)">
                  {{ stage.candidate_count }}
                </span>
              </div>

              <div class="stage-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{
                    width: stage.percentage + '%',
                    backgroundColor: getStageColor(stage.order_index)
                  }">
                    <span v-if="stage.percentage > 5" class="progress-label">
                      {{ stage.percentage.toFixed(1) }}%
                    </span>
                  </div>
                </div>
                <span class="progress-text">{{ (stage.percentage || 0).toFixed(1) }}%</span>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="pipelineStages.length > 0 && totalCandidates === 0" class="pipeline-empty">
            <i class="fas fa-inbox"></i>
            <p>No candidates in the pipeline</p>
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

      <!-- Job Post Modal -->
      <JobPostModal v-if="showJobPostModal" @close="closeJobPostModal" @job-posted="handleJobPosted" />

      <!-- Success/Error Messages -->
      <div v-if="successMessage" class="toast success">
        <i class="fas fa-check-circle"></i>
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="toast error">
        <i class="fas fa-exclamation-circle"></i>
        {{ errorMessage }}
      </div>

    </div>
    <div v-if="showCreateStageModal" class="modal-overlay" @click="closeCreateStageModal">
      <div class="modal-container create-stage-modal" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="fas fa-plus-circle"></i>
            Create New Pipeline Stage
          </h3>
          <button @click="closeCreateStageModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <form @submit.prevent="createNewPipelineStage" class="modal-body">
          <!-- Stage Name -->
          <div class="form-group">
            <label for="stage-name" class="required">
              <i class="fas fa-tag"></i>
              Stage Name
            </label>
            <input id="stage-name" v-model="newStage.name" type="text" class="form-input"
              :class="{ 'error': stageErrors.name }" placeholder="e.g., Phone Interview, Hired" maxlength="100"
              @input="clearError('name')" />
            <span v-if="stageErrors.name" class="error-message">
              {{ stageErrors.name }}
            </span>
          </div>

          <!-- Stage Description -->
          <div class="form-group">
            <label for="stage-description" class="required">
              <i class="fas fa-align-left"></i>
              Description
            </label>
            <textarea id="stage-description" v-model="newStage.description" class="form-textarea"
              :class="{ 'error': stageErrors.description }" placeholder="Describe what happens in this stage..."
              rows="3" maxlength="500" @input="clearError('description')"></textarea>
            <div class="char-count">
              {{ newStage.description.length }}/500
            </div>
            <span v-if="stageErrors.description" class="error-message">
              {{ stageErrors.description }}
            </span>
          </div>

          <!-- Order Index -->
          <div class="form-group">
            <label for="stage-order">
              <i class="fas fa-sort-numeric-up"></i>
              Order Index
            </label>
            <input id="stage-order" v-model.number="newStage.order_index" type="number" class="form-input"
              placeholder="Auto-generated if left empty" min="1" max="99" />
            <span class="help-text">
              Leave empty to add at the end. Lower numbers appear first.
            </span>
          </div>

          <!-- Active Status -->
          <div class="form-group">
            <div class="checkbox-group">
              <input id="stage-active" v-model="newStage.is_active" type="checkbox" class="form-checkbox" />
              <label for="stage-active" class="checkbox-label">
                <i class="fas fa-toggle-on"></i>
                Active Stage
              </label>
            </div>
            <span class="help-text">
              Only active stages are shown in the pipeline
            </span>
          </div>
        </form>

        <div class="modal-footer">
          <button @click="closeCreateStageModal" type="button" class="btn-secondary" :disabled="creatingStage">
            Cancel
          </button>
          <button @click="createNewPipelineStage" type="button" class="btn-primary"
            :disabled="creatingStage || !isFormValid">
            <i v-if="creatingStage" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-plus"></i>
            {{ creatingStage ? 'Creating...' : 'Create Stage' }}
          </button>
        </div>
      </div>
    </div>
    <div v-if="showCreateStageModal" class="modal-overlay" @click="closeCreateStageModal">
      <div class="modal-container create-stage-modal" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="fas fa-plus-circle"></i>
            Create New Pipeline Stage
          </h3>
          <button @click="closeCreateStageModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <form @submit.prevent="createNewPipelineStage" class="modal-body">
          <!-- Stage Name -->
          <div class="form-group">
            <label for="stage-name" class="required">
              <i class="fas fa-tag"></i>
              Stage Name
            </label>
            <input id="stage-name" v-model="newStage.name" type="text" class="form-input"
              :class="{ 'error': stageErrors.name }" placeholder="e.g., Phone Interview, Hired" maxlength="100"
              @input="clearError('name')" />
            <span v-if="stageErrors.name" class="error-message">
              {{ stageErrors.name }}
            </span>
          </div>

          <!-- Stage Description -->
          <div class="form-group">
            <label for="stage-description" class="required">
              <i class="fas fa-align-left"></i>
              Description
            </label>
            <textarea id="stage-description" v-model="newStage.description" class="form-textarea"
              :class="{ 'error': stageErrors.description }" placeholder="Describe what happens in this stage..."
              rows="3" maxlength="500" @input="clearError('description')"></textarea>
            <div class="char-count">
              {{ newStage.description.length }}/500
            </div>
            <span v-if="stageErrors.description" class="error-message">
              {{ stageErrors.description }}
            </span>
          </div>

          <!-- Order Index -->
          <div class="form-group">
            <label for="stage-order">
              <i class="fas fa-sort-numeric-up"></i>
              Order Index
            </label>
            <input id="stage-order" v-model.number="newStage.order_index" type="number" class="form-input"
              placeholder="Auto-generated if left empty" min="1" max="99" />
            <span class="help-text">
              Leave empty to add at the end. Lower numbers appear first.
            </span>
          </div>

          <!-- Active Status -->
          <div class="form-group">
            <div class="checkbox-group">
              <input id="stage-active" v-model="newStage.is_active" type="checkbox" class="form-checkbox" />
              <label for="stage-active" class="checkbox-label">
                <i class="fas fa-toggle-on"></i>
                Active Stage
              </label>
            </div>
            <span class="help-text">
              Only active stages are shown in the pipeline
            </span>
          </div>
        </form>

        <div class="modal-footer">
          <button @click="closeCreateStageModal" type="button" class="btn-secondary" :disabled="creatingStage">
            Cancel
          </button>
          <button @click="createNewPipelineStage" type="button" class="btn-primary"
            :disabled="creatingStage || !isFormValid">
            <i v-if="creatingStage" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-plus"></i>
            {{ creatingStage ? 'Creating...' : 'Create Stage' }}
          </button>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'
import JobPostModal from './JobPostModal.vue'

const router = useRouter()

// State
const userData = ref([])
const analyticsTab = ref('department')
const selectedPosition = ref('')
const showJobPostModal = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const showCreateStageModal = ref(false)
const creatingStage = ref(false)

const newStage = ref({
  name: '',
  description: '',
  order_index: null,
  is_active: true
})

const stageErrors = ref({
  name: '',
  description: ''
})

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

const openPostModal = () => {
  showJobPostModal.value = true
}

const closeJobPostModal = () => {
  showJobPostModal.value = false
}

const handleJobPosted = async (jobData) => {
  showToast('Job posted successfully!')
  await new Promise(resolve => setTimeout(resolve, 3000))
  closeJobPostModal()
}

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

const pipelineStages = ref([])

const totalCandidates = computed(() => {
  return pipelineStages.value.reduce((sum, stage) => sum + stage.candidate_count, 0)
})

const pipelineStagesWithPercentage = computed(() => {
  const total = totalCandidates.value

  if (total === 0) {
    return pipelineStages.value.map(stage => ({
      ...stage,
      percentage: 0
    }))
  }

  return pipelineStages.value.map(stage => ({
    ...stage,
    percentage: ((stage.candidate_count / total) * 100)
  }))
})

const isFormValid = computed(() => {
  return newStage.value.name.trim().length > 0 &&
    newStage.value.description.trim().length > 0 &&
    !stageErrors.value.name &&
    !stageErrors.value.description
})


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


const getAuthToken = () => localStorage.getItem('access_token')


function navigate(page) {
  router.push(`/${page}`)
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}

// function formatTime(dateString) {
//   return new Date(dateString).toLocaleTimeString('en-US', {
//     hour: '2-digit',
//     minute: '2-digit'
//   })
// }

function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}


function clearError(field) {
  stageErrors.value[field] = ''
}

function validateForm() {
  let isValid = true

  // Reset errors
  stageErrors.value = {
    name: '',
    description: ''
  }

  // Validate name
  if (!newStage.value.name.trim()) {
    stageErrors.value.name = 'Stage name is required'
    isValid = false
  } else if (newStage.value.name.trim().length < 2) {
    stageErrors.value.name = 'Stage name must be at least 2 characters'
    isValid = false
  } else if (newStage.value.name.trim().length > 100) {
    stageErrors.value.name = 'Stage name cannot exceed 100 characters'
    isValid = false
  }

  // Check if name already exists
  const nameExists = pipelineStages.value.some(stage =>
    stage.name.toLowerCase() === newStage.value.name.trim().toLowerCase()
  )
  if (nameExists) {
    stageErrors.value.name = 'A stage with this name already exists'
    isValid = false
  }

  // Validate description
  if (!newStage.value.description.trim()) {
    stageErrors.value.description = 'Stage description is required'
    isValid = false
  } else if (newStage.value.description.trim().length < 10) {
    stageErrors.value.description = 'Description must be at least 10 characters'
    isValid = false
  } else if (newStage.value.description.trim().length > 500) {
    stageErrors.value.description = 'Description cannot exceed 500 characters'
    isValid = false
  }

  return isValid
}

function closeCreateStageModal() {
  showCreateStageModal.value = false
  // Reset form
  newStage.value = {
    name: '',
    description: '',
    order_index: null,
    is_active: true
  }
  // Clear errors
  stageErrors.value = {
    name: '',
    description: ''
  }
}

//helper functions

function getStageColor(orderIndex) {
  const colors = [
    '#3498db',
    '#9b59b6',
    '#e67e22',
    '#f39c12',
    '#1abc9c',
    '#16a085',
    '#27ae60',
    '#2ecc71',
    '#27ae60'
  ]

  return colors[orderIndex - 1] || '#3498db'
}

function getStageCountClass(count) {
  if (count === 0) return 'zero'
  if (count <= 3) return 'low'
  if (count <= 7) return 'medium'
  return 'high'
}

// API calls

async function loadHRData() {
  // Load HR dashboard data
  try {
    const response = await axios.get('/api/users/', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      userData.value = response.data
    }
  }
  catch (error) {
    console.error('Failed to load HR data:', error)
  }
}

// load hiring pipeline stages

async function loadHiringPipelineStages() {
  try {
    console.log('Loading pipeline stages...')

    const response = await axios.get('/api/pipeline/stages', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data && response.data.stages) {
      // Store the stages data
      pipelineStages.value = response.data.stages.map(stage => ({
        id: stage.id,
        name: stage.name,
        description: stage.description,
        candidate_count: stage.candidate_count || 0,
        order_index: stage.order_index,
        is_active: stage.is_active
      }))

      console.log('Pipeline stages loaded:', pipelineStages.value)
      console.log('Total candidates in pipeline:', totalCandidates.value)

      // Update stats
      hrStats.value.pendingApplications = totalCandidates.value
    }
  } catch (error) {
    console.error(' Failed to load hiring pipeline stages:', error)
    pipelineStages.value = []
  }
}

// Load pipeline statistics
async function loadPipelineStats() {
  try {
    const response = await axios.get('/api/pipeline/stats', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      console.log('Pipeline stats:', response.data)

      // Update stats from API
      const stats = response.data.pipeline_stats
      const interviewStats = response.data.interview_stats

      if (stats) {
        hrStats.value.pendingApplications = stats.total_candidates || 0
      }

      if (interviewStats) {
        hrStats.value.upcomingInterviews = interviewStats.scheduled || 0
        hrStats.value.totalInterviewsWeek = interviewStats.total_interviews || 0
      }
    }
  } catch (error) {
    console.error('Failed to load pipeline stats:', error)
  }
}

// create pipeline stages

async function createNewPipelineStage() {
  if (!validateForm()) {
    return
  }

  try {
    creatingStage.value = true

    console.log('Creating new pipeline stage...')

    const response = await axios.post('/api/pipeline/stages', {
      name: newStage.value.name.trim(),
      description: newStage.value.description.trim(),
      order_index: newStage.value.order_index || undefined,
      is_active: newStage.value.is_active
    }, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data && response.data.stage) {
      // Add new stage to local state
      const createdStage = response.data.stage
      pipelineStages.value.push({
        id: createdStage.id,
        name: createdStage.name,
        description: createdStage.description,
        candidate_count: 0,
        order_index: createdStage.order_index,
        is_active: createdStage.is_active
      })

      // Sort stages by order index
      pipelineStages.value.sort((a, b) => a.order_index - b.order_index)

      // Show success message
      alert(`Pipeline stage "${createdStage.name}" created successfully!`)

      // Close modal
      closeCreateStageModal()

      console.log('Pipeline stage created:', createdStage.name)
    }

  } catch (error) {
    console.error('Failed to create pipeline stage:', error)

    // Handle specific errors
    if (error.response?.status === 400) {
      const errorMsg = error.response.data?.error || 'Invalid stage data'
      alert(`Failed to create stage: ${errorMsg}`)
    } else if (error.response?.status === 409) {
      stageErrors.value.name = 'A stage with this name already exists'
    } else {
      alert('Failed to create pipeline stage. Please try again.')
    }

  } finally {
    creatingStage.value = false
  }
}


async function loadTodayInterviews() {
  try {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)

    const response = await axios.get('/api/pipeline/interview-assignments', {
      params: {
        status: 'scheduled',
        upcoming_only: true
      },
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data?.interview_assignments) {
      // Filter for today's interviews only
      const todayInterviews = response.data.interview_assignments.filter(interview => {
        const scheduledDate = new Date(interview.scheduled_at)
        return scheduledDate >= today && scheduledDate < tomorrow
      })

      // Map to the format needed for the UI
      upcomingInterviews.value = todayInterviews.map(interview => ({
        id: interview.id,
        candidate_name: interview.candidate_name || 'Unknown Candidate',
        position: interview.job_title || 'Unknown Position',
        scheduled_time: interview.scheduled_at,
        duration: interview.duration_minutes || 60,
        interviewer: interview.interviewer_name || 'Unknown Interviewer',
        interview_type: interview.interview_type,
        meeting_link: interview.meeting_link,
        candidate_id: interview.candidate_id,
        job_id: interview.job_id
      }))

      // Update stats
      hrStats.value.upcomingInterviews = todayInterviews.length

      console.log(`📅 Loaded ${todayInterviews.length} interviews for today`)
    }
  } catch (error) {
    console.error('❌ Failed to load today\'s interviews:', error)
    upcomingInterviews.value = []
  }
}

// Navigate to hiring pipeline
function navigateToHiringPipeline() {
  router.push('/hr/hiring-pipeline')
}



// Format time helper
function formatTime(dateString) {
  if (!dateString) return 'N/A'

  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

// Format interview type
function formatInterviewType(type) {
  const typeMap = {
    'technical_assessment': 'Technical Assessment',
    'technical_interview': 'Technical Interview',
    'behavioral_interview': 'Behavioral Interview',
    'communication_interview': 'Communication Interview'
  }
  return typeMap[type] || type
}

// Get interview type color
function getInterviewTypeColor(type) {
  const colorMap = {
    'technical_assessment': '#3498db',
    'technical_interview': '#9b59b6',
    'behavioral_interview': '#e67e22',
    'communication_interview': '#27ae60'
  }
  return colorMap[type] || '#95a5a6'
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

function joinInterview(interviewId) {
  const interview = upcomingInterviews.value.find(i => i.id === interviewId)

  if (interview?.meeting_link) {
    // Open meeting link in new tab
    window.open(interview.meeting_link, '_blank')
  } else {
    alert('No meeting link available for this interview.')
  }
}

function rescheduleInterview(interviewId) {
  const interview = upcomingInterviews.value.find(i => i.id === interviewId)

  if (interview) {
    // Store interview details in sessionStorage for the pipeline page
    sessionStorage.setItem('reschedule_interview', JSON.stringify({
      interview_id: interviewId,
      candidate_id: interview.candidate_id,
      job_id: interview.job_id
    }))

    // Navigate to hiring pipeline
    router.push('/hr/hiring-pipeline')
  }
}

function updateTask(task) {
  console.log('Updating task:', task)
  // Update task status
}

// Load data on mount
onMounted(async () => {
  await loadHRData()
  await loadHiringPipelineStages()
  await loadPipelineStats()
  await loadTodayInterviews()
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  border-left: 4px solid;
}

.stat-card.primary {
  border-left-color: #3498db;
}

.stat-card.success {
  border-left-color: #27ae60;
}

.stat-card.warning {
  border-left-color: #f39c12;
}

.stat-card.danger {
  border-left-color: #e74c3c;
}

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

.stat-card.primary .stat-icon {
  background: #3498db;
}

.stat-card.success .stat-icon {
  background: #27ae60;
}

.stat-card.warning .stat-icon {
  background: #f39c12;
}

.stat-card.danger .stat-icon {
  background: #e74c3c;
}

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
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  border: 1px solid #ecf0f1;
}

.dashboard-card.interviews {
  grid-column: span 2;
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
  background: #27ae60;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.view-all-btn:hover {
  background: #229954;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(39, 174, 96, 0.3);
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

.btn-review {
  background: #3498db;
  color: white;
}

.btn-approve {
  background: #27ae60;
  color: white;
}

.btn-reject {
  background: #e74c3c;
  color: white;
}

.application-actions button:hover {
  transform: translateY(-1px);
}

/* Interview Items */
.interview-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 0;
  margin-bottom: 0px;
  border-radius: 8px;
  background: #f8f9fa;
  transition: all 0.3s ease;
  border: 1px solid #ecf0f1;

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

/* Update the interviews section styles */
.interviews-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: none;
  overflow-y: visible;
}

.interviews-list::-webkit-scrollbar {
  width: 6px;
}

.interviews-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.interviews-list::-webkit-scrollbar-thumb {
  background: #bdc3c7;
  border-radius: 3px;
}

.interview-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  margin-bottom: 12px;
  border-radius: 8px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.interview-item:hover {
  background: #e3f2fd;
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #3498db;
}


.interview-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
  padding: 10px;
  background: white;
  border-radius: 8px;
  border-left: 3px solid #3498db;
}

.interview-time .time {
  font-weight: 700;
  color: #2c3e50;
  font-size: 1rem;
  margin-bottom: 4px;
}

.interview-time .duration {
  font-size: 0.75rem;
  color: #7f8c8d;
  background: #ecf0f1;
  padding: 2px 8px;
  border-radius: 10px;
}

.interview-info {
  flex: 1;
  min-width: 0;
}

.interview-info h4 {
  margin: 0 0 4px 0;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
}

.interview-info p {
  margin: 0 0 8px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.interview-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.interviewer {
  font-size: 0.8rem;
  color: #7f8c8d;
  display: flex;
  align-items: center;
  gap: 4px;
}

.interviewer i {
  color: #3498db;
}

.interview-type-badge {
  font-size: 0.7rem;
  padding: 3px 8px;
  border-radius: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.interview-actions {
  display: flex;
  gap: 8px;
}

.interview-actions button {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.btn-join {
  background: #27ae60;
  color: white;
}

.btn-join:hover:not(:disabled) {
  background: #229954;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.btn-join:disabled {
  background: #95a5a6;
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-reschedule {
  background: #f39c12;
  color: white;
}

.btn-reschedule:hover {
  background: #e67e22;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(243, 156, 18, 0.3);
}

/* Today count badge */
.today-count {
  background: #27ae60;
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  margin-left: 10px;
  font-weight: 600;
}

.interviews-empty {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.interviews-empty i {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
  color: #bdc3c7;
}

.interviews-empty p {
  margin: 0 0 20px 0;
  font-size: 1.1rem;
}


.btn-schedule-now {
  background: #3498db;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-schedule-now:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-join {
  background: #27ae60;
  color: white;
}

.btn-reschedule {
  background: #f39c12;
  color: white;
}

/* Pipeline Stages */
.pipeline-stages {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
  padding: 10px;
  background: white;
  border-radius: 8px;
  border-left: 3px solid #3498db;
}

.interview-time .time {
  font-weight: 700;
  color: #2c3e50;
  font-size: 1rem;
  margin-bottom: 4px;
}

.interview-time .duration {
  font-size: 0.75rem;
  color: #7f8c8d;
  background: #ecf0f1;
  padding: 2px 8px;
  border-radius: 10px;
}

.interview-info {
  flex: 1;
  min-width: 0;
}

.interview-info h4 {
  margin: 0 0 4px 0;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
}

.interview-info p {
  margin: 0 0 8px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.interview-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.interviewer {
  font-size: 0.8rem;
  color: #7f8c8d;
  display: flex;
  align-items: center;
  gap: 4px;
}

.interviewer i {
  color: #3498db;
}

.interview-type-badge {
  font-size: 0.7rem;
  padding: 3px 8px;
  border-radius: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.interview-actions {
  display: flex;
  gap: 8px;
}

.interview-actions button {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.btn-join {
  background: #27ae60;
  color: white;
}

.btn-join:hover:not(:disabled) {
  background: #229954;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.btn-join:disabled {
  background: #95a5a6;
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-reschedule {
  background: #f39c12;
  color: white;
}

.btn-reschedule:hover {
  background: #e67e22;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(243, 156, 18, 0.3);
}

/* Today count badge */
.today-count {
  background: #27ae60;
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  margin-left: 10px;
  font-weight: 600;
}

.interviews-empty {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.interviews-empty i {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
  color: #bdc3c7;
}

.interviews-empty p {
  margin: 0 0 20px 0;
  font-size: 1.1rem;
}


.btn-schedule-now {
  background: #3498db;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-schedule-now:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-join {
  background: #27ae60;
  color: white;
}

.btn-reschedule {
  background: #f39c12;
  color: white;
}

/* Pipeline Stages */
.pipeline-summary {
  display: flex;
  align-items: center;
  gap: 15px;
}

.total-candidates {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #e8f4f8;
  color: #3498db;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
}

.pipeline-loading,
.pipeline-empty {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.pipeline-loading i,
.pipeline-empty i {
  font-size: 2rem;
  margin-bottom: 10px;
  display: block;
}

.pipeline-stages {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 10px;
}

.pipeline-stages::-webkit-scrollbar {
  width: 6px;
}

.pipeline-stages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.pipeline-stages::-webkit-scrollbar-thumb {
  background: #3498db;
  border-radius: 3px;
}

.pipeline-stage {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
  width: 100%;
  max-width: -moz-available;
}

.pipeline-stage.has-candidates {
  background: white;
  border: 1px solid #ecf0f1;
}

.pipeline-stage.has-candidates:hover {
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stage-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 15px;
}

.stage-info {
  flex: 1;
}

.stage-info h4 {
  margin: 0 0 4px 0;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
}

.stage-description {
  font-size: 0.8rem;
  color: #7f8c8d;
  line-height: 1.4;
}

.stage-count {
  min-width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.stage-count.zero {
  background: #bdc3c7;
}

.stage-count.low {
  background: #f39c12;
}

.stage-count.medium {
  background: #3498db;
}

.stage-count.high {
  background: #27ae60;
}

.stage-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 20px;
  background: #ecf0f1;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease, background-color 0.3s ease;
  position: relative;
  display: flex;
  align-items: center;
  padding: 0 8px;
}

.progress-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  white-space: nowrap;
}

.progress-text {
  min-width: 50px;
  text-align: right;
  font-size: 0.9rem;
  font-weight: 600;
  color: #2c3e50;
}

.btn-create-stage {
  background: #27ae60;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-create-stage:hover {
  background: #229954;
  transform: translateY(-1px);
}

/* modal create stages */

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 200px;
}

.modal-container.create-stage-modal {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 25px;
  border-bottom: 2px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #7f8c8d;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #ecf0f1;
  color: #2c3e50;
}

.modal-body {
  padding: 25px;
  overflow-y: auto;
  flex: 1;
}

/* form styling */

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 1rem;
}

.form-group label.required::after {
  content: '*';
  color: #e74c3c;
  margin-left: 4px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  color: #2c3e50;
  background: white;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-input.error,
.form-textarea.error {
  border-color: #e74c3c;
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.char-count {
  font-size: 0.8rem;
  color: #7f8c8d;
  text-align: right;
  margin-top: 5px;
}

.error-message {
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.error-message::before {
  content: '⚠';
}

.help-text {
  color: #7f8c8d;
  font-size: 0.85rem;
  margin-top: 6px;
  font-style: italic;
}


/* Checkbox styles */
.checkbox-group {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.form-checkbox {
  width: 20px;
  height: 20px;
  accent-color: #3498db;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #2c3e50;
  cursor: pointer;
}

.modal-footer {
  padding: 20px 25px;
  border-top: 2px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.btn-secondary,
.btn-primary {
  padding: 12px 25px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
}

.btn-secondary {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-secondary:hover:not(:disabled) {
  background: #bdc3c7;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-1px);
}

.btn-secondary:disabled,
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
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

.activity-icon.application {
  background: #3498db;
}

.activity-icon.interview {
  background: #f39c12;
}

.activity-icon.hire {
  background: #27ae60;
}

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

@media (min-height: 800px) {
  .interviews-list {
    max-height: 500px;
    overflow-y: auto;
  }
}


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

  .pipeline-summary {
    flex-direction: column;
    align-items: flex-start;
  }


  .pipeline-stage {
    padding: 12px;
    width: 100%;
  }

  .stage-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .stage-count {
    align-self: flex-end;
  }


  .stage-progress {
    width: 100%;
  }

  .modal-container.create-stage-modal {
    margin: 10px;
    max-width: none;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 20px;
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .btn-secondary,
  .btn-primary {
    width: 100%;
    justify-content: center;
  }

  .interview-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .interview-time {
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
  }

  .interview-actions {
    width: 100%;
    justify-content: flex-end;
  }


}
</style>