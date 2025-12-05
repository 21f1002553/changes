<template>
  <DashboardLayout>
    <div class="interview-details-page">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>
            <i class="fas fa-calendar-alt"></i>
            Interview Schedule
          </h1>
          <p>Manage and track all scheduled interviews</p>
        </div>
        <div class="header-actions">
          <button @click="refreshInterviews" class="btn-refresh" :disabled="loading">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
            Refresh
          </button>
        </div>
      </div>

      <!-- Filters Section -->
      <div class="filters-section">
        <div class="filter-group">
          <label>
            <i class="fas fa-briefcase"></i>
            Job Position
          </label>
          <select v-model="filters.job_id" @change="applyFilters" class="filter-select">
            <option value="">All Positions</option>
            <option v-for="job in jobs" :key="job.id" :value="job.id">
              {{ job.title }} - {{ job.location }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>
            <i class="fas fa-clipboard-list"></i>
            Interview Type
          </label>
          <select v-model="filters.interview_type" @change="applyFilters" class="filter-select">
            <option value="">All Types</option>
            <option value="technical_assessment">Technical Assessment</option>
            <option value="technical_interview">Technical Interview</option>
            <option value="behavioral_interview">Behavioral Interview</option>
            <option value="communication_interview">Communication Interview</option>
          </select>
        </div>

        <div class="filter-group">
          <label>
            <i class="fas fa-info-circle"></i>
            Status
          </label>
          <select v-model="filters.status" @change="applyFilters" class="filter-select">
            <option value="">All Status</option>
            <option value="scheduled">Scheduled</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
            <option value="rescheduled">Rescheduled</option>
          </select>
        </div>

        <div class="filter-group">
          <label>
            <i class="fas fa-user-tie"></i>
            Interviewer
          </label>
          <select v-model="filters.interviewer_id" @change="applyFilters" class="filter-select">
            <option value="">All Interviewers</option>
            <option v-for="interviewer in allInterviewers" :key="interviewer.id" :value="interviewer.id">
              {{ interviewer.name }} ({{ interviewer.role_name }})
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>
            <i class="fas fa-calendar"></i>
            Date Range
          </label>
          <select v-model="filters.date_range" @change="applyFilters" class="filter-select">
            <option value="all">All Time</option>
            <option value="today">Today</option>
            <option value="tomorrow">Tomorrow</option>
            <option value="this_week">This Week</option>
            <option value="next_week">Next Week</option>
            <option value="this_month">This Month</option>
          </select>
        </div>

        <button @click="clearFilters" class="btn-clear-filters">
          <i class="fas fa-times"></i>
          Clear Filters
        </button>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card total">
          <div class="stat-icon">
            <i class="fas fa-calendar-alt"></i>
          </div>
          <div class="stat-content">
            <h3>{{ stats.total }}</h3>
            <p>Total Interviews</p>
          </div>
        </div>

        <div class="stat-card scheduled">
          <div class="stat-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-content">
            <h3>{{ stats.scheduled }}</h3>
            <p>Scheduled</p>
          </div>
        </div>

        <div class="stat-card completed">
          <div class="stat-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-content">
            <h3>{{ stats.completed }}</h3>
            <p>Completed</p>
          </div>
        </div>

        <div class="stat-card today">
          <div class="stat-icon">
            <i class="fas fa-calendar-day"></i>
          </div>
          <div class="stat-content">
            <h3>{{ stats.today }}</h3>
            <p>Today's Interviews</p>
          </div>
        </div>
      </div>

      <!-- Interviews List -->
      <div class="interviews-container">
        <div class="section-header">
          <h2>
            <i class="fas fa-list"></i>
            Interview Schedule
          </h2>
          <div class="view-toggle">
            <button 
              @click="viewMode = 'list'" 
              :class="{ active: viewMode === 'list' }"
              class="toggle-btn"
            >
              <i class="fas fa-list"></i>
              List View
            </button>
            <button 
              @click="viewMode = 'calendar'" 
              :class="{ active: viewMode === 'calendar' }"
              class="toggle-btn"
            >
              <i class="fas fa-calendar"></i>
              Calendar View
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading interviews...</p>
        </div>

        <!-- List View -->
        <div v-else-if="viewMode === 'list'" class="interviews-list">
          <div v-if="filteredInterviews.length === 0" class="empty-state">
            <i class="fas fa-calendar-times"></i>
            <h3>No interviews found</h3>
            <p>Try adjusting your filters or schedule a new interview</p>
            <button @click="navigateToHiringPipeline" class="btn-schedule">
              <i class="fas fa-plus"></i>
              Schedule Interview
            </button>
          </div>

          <div v-else class="interview-items">
            <div 
              v-for="interview in filteredInterviews" 
              :key="interview.id" 
              class="interview-item"
              :class="[
                `status-${interview.status}`,
                { 'is-today': isToday(interview.scheduled_at) }
              ]"
            >
              <!-- Interview Date & Time -->
              <div class="interview-datetime">
                <div class="date">
                  <i class="fas fa-calendar"></i>
                  {{ formatDate(interview.scheduled_at) }}
                </div>
                <div class="time">
                  <i class="fas fa-clock"></i>
                  {{ formatTime(interview.scheduled_at) }}
                </div>
                <div class="duration">
                  {{ interview.duration_minutes }}min
                </div>
              </div>

              <!-- Candidate Info -->
              <div class="candidate-section">
                <div class="candidate-avatar">
                  {{ getInitials(interview.candidate_name) }}
                </div>
                <div class="candidate-details">
                  <h4>{{ interview.candidate_name }}</h4>
                  <p class="job-title">{{ interview.job_title }}</p>
                  <div class="interview-meta">
                    <span class="interview-type-badge" :class="getTypeClass(interview.interview_type)">
                      <i :class="getTypeIcon(interview.interview_type)"></i>
                      {{ formatInterviewType(interview.interview_type) }}
                    </span>
                    <span class="status-badge" :class="interview.status">
                      {{ formatStatus(interview.status) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Interviewer Info -->
              <div class="interviewer-section">
                <div class="interviewer-label">
                  <i class="fas fa-user-tie"></i>
                  Interviewer
                </div>
                <div class="interviewer-name">{{ interview.interviewer_name }}</div>
              </div>

              <!-- Meeting Link -->
              <div class="meeting-section" v-if="interview.meeting_link">
                <a 
                  :href="interview.meeting_link" 
                  target="_blank" 
                  class="meeting-link"
                >
                  <i class="fas fa-video"></i>
                  Join Meeting
                </a>
              </div>

              <!-- Actions -->
              <div class="interview-actions">
                <button 
                  @click="viewInterviewDetails(interview)" 
                  class="action-btn view-btn"
                  title="View Details"
                >
                  <i class="fas fa-eye"></i>
                </button>
                <button 
                  v-if="interview.status === 'scheduled'"
                  @click="rescheduleInterview(interview)" 
                  class="action-btn reschedule-btn"
                  title="Reschedule"
                >
                  <i class="fas fa-calendar-alt"></i>
                </button>
                <button 
                  v-if="interview.status === 'scheduled'"
                  @click="cancelInterview(interview)" 
                  class="action-btn cancel-btn"
                  title="Cancel"
                >
                  <i class="fas fa-times"></i>
                </button>
                <button 
                  v-if="interview.status === 'completed'"
                  @click="viewScorecard(interview)" 
                  class="action-btn scorecard-btn"
                  title="View Scorecard"
                >
                  <i class="fas fa-chart-bar"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Calendar View -->
        <div v-else class="calendar-view">
          <div class="calendar-header">
            <button @click="previousMonth" class="nav-btn">
              <i class="fas fa-chevron-left"></i>
            </button>
            <h3>{{ currentMonthYear }}</h3>
            <button @click="nextMonth" class="nav-btn">
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
          
          <div class="calendar-grid">
            <div class="calendar-day-header" v-for="day in weekDays" :key="day">
              {{ day }}
            </div>
            <div 
              v-for="(day, index) in calendarDays" 
              :key="index" 
              class="calendar-day"
              :class="{
                'other-month': day.isOtherMonth,
                'today': day.isToday,
                'has-interviews': day.interviewCount > 0
              }"
            >
              <div class="day-number">{{ day.date }}</div>
              <div v-if="day.interviewCount > 0" class="interview-count-badge">
                {{ day.interviewCount }} {{ day.interviewCount === 1 ? 'interview' : 'interviews' }}
              </div>
              <div class="day-interviews">
                <div 
                  v-for="interview in day.interviews" 
                  :key="interview.id"
                  class="calendar-interview"
                  :class="getTypeClass(interview.interview_type)"
                  @click="viewInterviewDetails(interview)"
                >
                  {{ formatTime(interview.scheduled_at) }} - {{ interview.candidate_name }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Interview Details Modal -->
    <InterviewDetailsModal
      v-if="showDetailsModal"
      :candidate="selectedInterview"
      :stage="{ name: formatInterviewType(selectedInterview?.interview_type) }"
      :interviewAssignment="selectedInterview"
      @close="closeDetailsModal"
      @viewResume="handleViewResume"
      @viewScorecard="handleViewScorecard"
      @reschedule="handleReschedule"
      @edit="handleEdit"
    />
  </DashboardLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'
import InterviewDetailsModal from './InterviewDetailsModal.vue'

const router = useRouter()

// State
const loading = ref(false)
const viewMode = ref('list') // 'list' or 'calendar'
const interviews = ref([])
const jobs = ref([])
const allInterviewers = ref([])
const currentMonth = ref(new Date().getMonth())
const currentYear = ref(new Date().getFullYear())

// Filters
const filters = ref({
  job_id: '',
  interview_type: '',
  status: '',
  interviewer_id: '',
  date_range: 'all'
})

// Modal State
const showDetailsModal = ref(false)
const selectedInterview = ref(null)

// Calendar
const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

function getInitials(name) {
  if (!name) return '?'
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

function formatTime(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

function formatInterviewType(type) {
  const typeMap = {
    'technical_assessment': 'Technical Assessment',
    'technical_interview': 'Technical Interview',
    'behavioral_interview': 'Behavioral Interview',
    'communication_interview': 'Communication Interview'
  }
  return typeMap[type] || type
}

function formatStatus(status) {
  const statusMap = {
    'scheduled': 'Scheduled',
    'completed': 'Completed',
    'cancelled': 'Cancelled',
    'rescheduled': 'Rescheduled'
  }
  return statusMap[status] || status
}

function getTypeClass(type) {
  const classMap = {
    'technical_assessment': 'type-technical',
    'technical_interview': 'type-technical',
    'behavioral_interview': 'type-behavioral',
    'communication_interview': 'type-communication'
  }
  return classMap[type] || 'type-default'
}

function getTypeIcon(type) {
  const iconMap = {
    'technical_assessment': 'fas fa-code',
    'technical_interview': 'fas fa-laptop-code',
    'behavioral_interview': 'fas fa-users',
    'communication_interview': 'fas fa-comments'
  }
  return iconMap[type] || 'fas fa-clipboard-list'
}

function isToday(dateString) {
  const date = new Date(dateString)
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

// Computed
const stats = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)

  return {
    total: interviews.value.length,
    scheduled: interviews.value.filter(i => i.status === 'scheduled').length,
    completed: interviews.value.filter(i => i.status === 'completed').length,
    today: interviews.value.filter(i => {
      const interviewDate = new Date(i.scheduled_at)
      return interviewDate >= today && interviewDate < tomorrow
    }).length
  }
})

const filteredInterviews = computed(() => {
  let result = [...interviews.value]

  // Filter by job
  if (filters.value.job_id) {
    result = result.filter(i => i.job_id === filters.value.job_id)
  }

  // Filter by interview type
  if (filters.value.interview_type) {
    result = result.filter(i => i.interview_type === filters.value.interview_type)
  }

  // Filter by status
  if (filters.value.status) {
    result = result.filter(i => i.status === filters.value.status)
  }

  // Filter by interviewer
  if (filters.value.interviewer_id) {
    result = result.filter(i => i.interviewer_id === filters.value.interviewer_id)
  }

  // Filter by date range
  if (filters.value.date_range !== 'all') {
    const now = new Date()
    result = result.filter(i => {
      const interviewDate = new Date(i.scheduled_at)
      
      switch (filters.value.date_range) {
        case 'today':
          return interviewDate.toDateString() === now.toDateString()
        case 'tomorrow':
          const tomorrow = new Date(now)
          tomorrow.setDate(tomorrow.getDate() + 1)
          return interviewDate.toDateString() === tomorrow.toDateString()
        case 'this_week':
          const weekStart = new Date(now)
          weekStart.setDate(now.getDate() - now.getDay())
          const weekEnd = new Date(weekStart)
          weekEnd.setDate(weekStart.getDate() + 7)
          return interviewDate >= weekStart && interviewDate < weekEnd
        case 'next_week':
          const nextWeekStart = new Date(now)
          nextWeekStart.setDate(now.getDate() - now.getDay() + 7)
          const nextWeekEnd = new Date(nextWeekStart)
          nextWeekEnd.setDate(nextWeekStart.getDate() + 7)
          return interviewDate >= nextWeekStart && interviewDate < nextWeekEnd
        case 'this_month':
          return interviewDate.getMonth() === now.getMonth() && 
                 interviewDate.getFullYear() === now.getFullYear()
        default:
          return true
      }
    })
  }

  // Sort by date (earliest first)
  result.sort((a, b) => new Date(a.scheduled_at) - new Date(b.scheduled_at))

  return result
})

const currentMonthYear = computed(() => {
  const date = new Date(currentYear.value, currentMonth.value)
  return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
})

const calendarDays = computed(() => {
  const firstDay = new Date(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
  const prevLastDay = new Date(currentYear.value, currentMonth.value, 0)
  
  const firstDayIndex = firstDay.getDay()
  const lastDayDate = lastDay.getDate()
  const prevLastDayDate = prevLastDay.getDate()
  
  const days = []
  
  // Previous month days
  for (let i = firstDayIndex; i > 0; i--) {
    days.push({
      date: prevLastDayDate - i + 1,
      isOtherMonth: true,
      isToday: false,
      interviews: [],
      interviewCount: 0
    })
  }
  
  // Current month days
  const today = new Date()
  for (let i = 1; i <= lastDayDate; i++) {
    const date = new Date(currentYear.value, currentMonth.value, i)
    const dayInterviews = filteredInterviews.value.filter(interview => {
      const interviewDate = new Date(interview.scheduled_at)
      return interviewDate.toDateString() === date.toDateString()
    })
    
    days.push({
      date: i,
      isOtherMonth: false,
      isToday: date.toDateString() === today.toDateString(),
      interviews: dayInterviews.slice(0, 3), // Show max 3 interviews
      interviewCount: dayInterviews.length
    })
  }
  
  // Next month days
  const remainingDays = 42 - days.length // 6 rows × 7 days
  for (let i = 1; i <= remainingDays; i++) {
    days.push({
      date: i,
      isOtherMonth: true,
      isToday: false,
      interviews: [],
      interviewCount: 0
    })
  }
  
  return days
})

// API Functions
async function loadInterviews() {
  try {
    loading.value = true
    
    const response = await axios.get('/api/pipeline/interview-assignments', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    
    if (response.data?.interview_assignments) {
      interviews.value = response.data.interview_assignments
    }
  } catch (error) {
    console.error('❌ Failed to load interviews:', error)
    interviews.value = []
  } finally {
    loading.value = false
  }
}

async function loadJobs() {
  try {
    const response = await axios.get('/api/jobs/', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    
    if (response.data) {
      jobs.value = response.data.filter(job => job.status === 'active')
    }
  } catch (error) {
    console.error('❌ Failed to load jobs:', error)
  }
}

async function loadInterviewers() {
  try {
    const [hrResponse, bdaResponse, managerResponse] = await Promise.all([
      axios.get('/api/users/role/hr', { headers: { Authorization: `Bearer ${getAuthToken()}` } }),
      axios.get('/api/users/role/bda', { headers: { Authorization: `Bearer ${getAuthToken()}` } }),
      axios.get('/api/users/role/manager', { headers: { Authorization: `Bearer ${getAuthToken()}` } })
    ])
    
    allInterviewers.value = [
      ...(hrResponse.data || []),
      ...(bdaResponse.data || []),
      ...(managerResponse.data || [])
    ]
  } catch (error) {
    console.error('❌ Failed to load interviewers:', error)
  }
}

// Action Functions
function applyFilters() {
  // Filters are automatically applied through computed property
}

function clearFilters() {
  filters.value = {
    job_id: '',
    interview_type: '',
    status: '',
    interviewer_id: '',
    date_range: 'all'
  }
}

async function refreshInterviews() {
  await loadInterviews()
}

function navigateToHiringPipeline() {
  router.push('/hr/hiring-pipeline')
}

function viewInterviewDetails(interview) {
  selectedInterview.value = interview
  showDetailsModal.value = true
}

function closeDetailsModal() {
  showDetailsModal.value = false
  selectedInterview.value = null
}

function handleViewResume(interview) {
  console.log('View resume for:', interview)
  // Implement resume viewing logic
}

function handleViewScorecard(interview) {
  console.log('View scorecard for:', interview)
  // Implement scorecard viewing logic
}

function handleReschedule(interview) {
  console.log('Reschedule interview:', interview)
  closeDetailsModal()
  // Navigate to hiring pipeline with reschedule context
  sessionStorage.setItem('reschedule_interview', JSON.stringify({
    interview_id: interview.id,
    candidate_id: interview.candidate_id,
    job_id: interview.job_id
  }))
  router.push('/hr/hiring-pipeline')
}

function handleEdit(interview) {
  console.log('Edit interview:', interview)
  handleReschedule(interview)
}

async function rescheduleInterview(interview) {
  handleReschedule(interview)
}

async function cancelInterview(interview) {
  if (!confirm(`Cancel interview with ${interview.candidate_name}?`)) return
  
  try {
    const response = await axios.put(
      `/api/pipeline/interview-assignments/${interview.id}`,
      { status: 'cancelled' },
      { headers: { Authorization: `Bearer ${getAuthToken()}` } }
    )
    
    if (response.data) {
      alert('Interview cancelled successfully')
      await loadInterviews()
    }
  } catch (error) {
    console.error('❌ Failed to cancel interview:', error)
    alert('Failed to cancel interview')
  }
}

function viewScorecard(interview) {
  console.log('View scorecard:', interview)
  // Implement scorecard viewing
}

// Calendar Navigation
function previousMonth() {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

function nextMonth() {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

// Load data on mount
onMounted(async () => {
  await Promise.all([
    loadInterviews(),
    loadJobs(),
    loadInterviewers()
  ])
})
</script>

<style scoped>
.interview-details-page {
  padding: 0;
  background: #f5f7fa;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  background: white;
  border-bottom: 2px solid #ecf0f1;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.header-content h1 {
  font-size: 2.2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-content p {
  color: #7f8c8d;
  font-size: 1.05rem;
  margin: 0;
}

.btn-refresh {
  padding: 12px 24px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-refresh:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-1px);
}

/* Filters Section */
.filters-section {
  display: flex;
  gap: 15px;
  padding: 20px 30px;
  background: white;
  border-bottom: 1px solid #ecf0f1;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 200px;
}

.filter-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-select {
  padding: 10px 15px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  background: white;
  color: #2c3e50;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.btn-clear-filters {
  padding: 10px 20px;
  background: #ecf0f1;
  color: #2c3e50;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-clear-filters:hover {
  background: #bdc3c7;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  padding: 20px 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  gap: 15px;
  border-left: 4px solid;
}

.stat-card.total { border-left-color: #3498db; }
.stat-card.scheduled { border-left-color: #f39c12; }
.stat-card.completed { border-left-color: #27ae60; }
.stat-card.today { border-left-color: #e74c3c; }

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  color: white;
}

.stat-card.total .stat-icon { background: #3498db; }
.stat-card.scheduled .stat-icon { background: #f39c12; }
.stat-card.completed .stat-icon { background: #27ae60; }
.stat-card.today .stat-icon { background: #e74c3c; }

.stat-content h3 {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.stat-content p {
  margin: 0;
  color: #7f8c8d;
  font-weight: 600;
  font-size: 0.9rem;
}

/* Interviews Container */
.interviews-container {
  padding: 20px 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.view-toggle {
  display: flex;
  gap: 10px;
}

.toggle-btn {
  padding: 10px 20px;
  background: white;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  color: #7f8c8d;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-btn.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.toggle-btn:hover:not(.active) {
  border-color: #3498db;
  color: #3498db;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  color: #7f8c8d;
}

.loading-state i {
  font-size: 3rem;
  margin-bottom: 15px;
  color: #3498db;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 12px;
}

.empty-state i {
  font-size: 4rem;
  color: #bdc3c7;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #2c3e50;
  margin: 0 0 10px 0;
}

.empty-state p {
  color: #7f8c8d;
  margin: 0 0 25px 0;
}

.btn-schedule {
  padding: 12px 24px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-schedule:hover {
  background: #2980b9;
  transform: translateY(-2px);
}

/* Interview Items */
.interview-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.interview-item {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  display: grid;
  grid-template-columns: 150px 1fr 180px 150px 120px;
  gap: 20px;
  align-items: center;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.interview-item:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.interview-item.is-today {
  border-left-color: #e74c3c;
  background: #fff5f5;
}

.interview-item.status-scheduled {
  border-left-color: #f39c12;
}

.interview-item.status-completed {
  border-left-color: #27ae60;
}

.interview-item.status-cancelled {
  border-left-color: #95a5a6;
  opacity: 0.7;
}

/* Interview DateTime */
.interview-datetime {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.interview-datetime .date,
.interview-datetime .time {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.9rem;
}

.interview-datetime .duration {
  background: #ecf0f1;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #7f8c8d;
  text-align: center;
}

/* Candidate Section */
.candidate-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.candidate-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.candidate-details h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 1.05rem;
  font-weight: 600;
}

.candidate-details .job-title {
  margin: 0 0 8px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.interview-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.interview-type-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.interview-type-badge.type-technical {
  background: #e3f2fd;
  color: #1976d2;
}

.interview-type-badge.type-behavioral {
  background: #f3e5f5;
  color: #7b1fa2;
}

.interview-type-badge.type-communication {
  background: #e8f5e9;
  color: #388e3c;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.scheduled {
  background: #fff3e0;
  color: #f57c00;
}

.status-badge.completed {
  background: #e8f5e9;
  color: #388e3c;
}

.status-badge.cancelled {
  background: #ecf0f1;
  color: #95a5a6;
}

/* Interviewer Section */
.interviewer-section {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.interviewer-label {
  font-size: 0.8rem;
  color: #7f8c8d;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
}

.interviewer-name {
  color: #2c3e50;
  font-weight: 600;
}

/* Meeting Section */
.meeting-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 15px;
  background: #27ae60;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.meeting-link:hover {
  background: #229954;
  transform: translateY(-1px);
}

/* Interview Actions */
.interview-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.action-btn {
  width: 38px;
  height: 38px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.view-btn {
  background: #3498db;
  color: white;
}

.reschedule-btn {
  background: #f39c12;
  color: white;
}

.cancel-btn {
  background: #e74c3c;
  color: white;
}

.scorecard-btn {
  background: #9b59b6;
  color: white;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* Calendar View */
.calendar-view {
  background: white;
  border-radius: 12px;
  padding: 20px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.calendar-header h3 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin: 0;
}

.nav-btn {
  padding: 8px 12px;
  background: #ecf0f1;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  color: #2c3e50;
  transition: all 0.3s ease;
}

.nav-btn:hover {
  background: #bdc3c7;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #ecf0f1;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  overflow: hidden;
}

.calendar-day-header {
  background: #667eea;
  color: white;
  padding: 12px;
  text-align: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.calendar-day {
  background: white;
  min-height: 100px;
  padding: 8px;
  position: relative;
}

.calendar-day.other-month {
  background: #f8f9fa;
  opacity: 0.6;
}

.calendar-day.today {
  background: #fff5f5;
  border: 2px solid #e74c3c;
}

.calendar-day.has-interviews {
  background: #f0f8ff;
}

.day-number {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 5px;
}

.interview-count-badge {
  font-size: 0.7rem;
  background: #3498db;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  display: inline-block;
  margin-bottom: 5px;
}

.day-interviews {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.calendar-interview {
  font-size: 0.7rem;
  padding: 3px 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.calendar-interview.type-technical {
  background: #e3f2fd;
  color: #1976d2;
}

.calendar-interview.type-behavioral {
  background: #f3e5f5;
  color: #7b1fa2;
}

.calendar-interview.type-communication {
  background: #e8f5e9;
  color: #388e3c;
}

.calendar-interview:hover {
  transform: scale(1.02);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Responsive */
@media (max-width: 1400px) {
  .interview-item {
    grid-template-columns: 130px 1fr 160px 130px 100px;
    gap: 15px;
  }
}

@media (max-width: 1200px) {
  .interview-item {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .interview-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .filters-section {
    padding: 15px 20px;
  }
  
  .filter-group {
    min-width: 100%;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    padding: 15px 20px;
  }
  
  .interviews-container {
    padding: 15px 20px;
  }
  
  .calendar-day {
    min-height: 80px;
  }
}
</style>