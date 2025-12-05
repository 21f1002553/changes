<template>
  <DashboardLayout>
    <div class="ho-dashboard">
      <!-- Header -->
      <div class="dashboard-header">
        <div class="welcome-section">
          <h1>Head Office Dashboard</h1>
          <p>Welcome back, {{ hoName }}! Manage vacancies, interviews, and tasks.</p>
        </div>
        <div class="quick-actions">
          <button class="quick-action-btn" @click="showVacancyModal = true">
            <i class="fas fa-plus-circle"></i>
            Create Vacancy
          </button>
          <button class="quick-action-btn" @click="showTaskModal = true">
            <i class="fas fa-tasks"></i>
            Assign Task
          </button>
          <button class="quick-action-btn" @click="showLeaveModal = true">
            <i class="fas fa-calendar-alt"></i>
            Apply Leave
          </button>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="stats-grid">
        <div class="stat-card">
          <i class="fas fa-building stat-icon"></i>
          <div class="stat-info">
            <h3>{{ stats.activeVacancies }}</h3>
            <p>Active Vacancies</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-laptop-code stat-icon"></i>
          <div class="stat-info">
            <h3>{{ stats.technicalInterviews }}</h3>
            <p>Technical Interviews</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-clipboard-list stat-icon"></i>
          <div class="stat-info">
            <h3>{{ stats.assignedTasks }}</h3>
            <p>Active Tasks</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-umbrella-beach stat-icon"></i>
          <div class="stat-info">
            <h3>{{ stats.leaveBalance }}</h3>
            <p>Leave Balance</p>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="content-grid">
        <!-- Vacancies Section -->
        <div class="dashboard-card vacancies-card full-width">
          <div class="card-header">
            <h3><i class="fas fa-briefcase"></i> Recent Vacancies</h3>
            <button class="view-all-btn" @click="navigate('vacancies')">
              View All
            </button>
          </div>
          <div class="card-body">
            <div v-if="vacanciesLoading" class="loading-state">
              <i class="fas fa-spinner fa-spin"></i>
              <p>Loading vacancies...</p>
            </div>
            <div v-else-if="recentVacancies.length === 0" class="empty-state">
              <i class="fas fa-briefcase"></i>
              <p>No vacancies created yet</p>
            </div>
            <div v-else class="vacancies-grid">
              <div 
                v-for="vacancy in recentVacancies" 
                :key="vacancy.id"
                class="vacancy-item"
              >
                <div class="vacancy-header">
                  <h4>{{ vacancy.title }}</h4>
                  <span :class="['status-badge', vacancy.status]">
                    {{ vacancy.status }}
                  </span>
                </div>
                <div class="vacancy-details">
                  <div class="detail-item">
                    <i class="fas fa-map-marker-alt"></i>
                    {{ vacancy.location }}
                  </div>
                  <div class="detail-item" v-if="vacancy.school">
                    <i class="fas fa-school"></i>
                    {{ vacancy.school }}
                  </div>
                  <div class="detail-item">
                    <i class="fas fa-calendar"></i>
                    {{ formatDate(vacancy.created_at) }}
                  </div>
                </div>
                <button class="btn-notify" @click="notifyHR(vacancy)" :disabled="vacancy.notified">
                  <i class="fas fa-bell"></i>
                  {{ vacancy.notified ? 'Notified' : 'Notify HR' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Technical Interviews -->
        <div class="dashboard-card interviews-card">
          <div class="card-header">
            <h3><i class="fas fa-laptop-code"></i> Technical Interviews</h3>
            <button class="refresh-btn" @click="loadTechnicalInterviews">
              <i class="fas fa-sync-alt"></i>
            </button>
          </div>
          <div class="card-body">
            <div v-if="interviewsLoading" class="loading-state">
              <i class="fas fa-spinner fa-spin"></i>
            </div>
            <div v-else-if="technicalInterviews.length === 0" class="empty-state">
              <i class="fas fa-laptop-code"></i>
              <p>No technical interviews scheduled</p>
            </div>
            <div v-else class="interviews-list">
              <div 
                v-for="interview in technicalInterviews" 
                :key="interview.id"
                class="interview-item"
              >
                <div class="interview-time">
                  <div class="date">{{ formatDate(interview.scheduled_at) }}</div>
                  <div class="time">{{ formatTime(interview.scheduled_at) }}</div>
                </div>
                <div class="interview-info">
                  <h4>{{ interview.candidate_name }}</h4>
                  <p><i class="fas fa-briefcase"></i> {{ interview.job_title }}</p>
                  <span :class="['status-badge', interview.status]">
                    {{ formatInterviewStatus(interview.status) }}
                  </span>
                </div>
                <div class="interview-actions">
                  <button 
                    v-if="interview.meeting_link" 
                    class="btn-join" 
                    @click="openMeeting(interview.meeting_link)"
                    :disabled="!isInterviewSoon(interview.scheduled_at)"
                  >
                    <i class="fas fa-video"></i> Join
                  </button>
                  <button 
                    class="btn-evaluate" 
                    @click="openEvaluationModal(interview)"
                    :disabled="interview.status !== 'completed' && !isInterviewSoon(interview.scheduled_at)"
                  >
                    <i class="fas fa-clipboard-check"></i> Evaluate
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tasks Assigned -->
        <div class="dashboard-card tasks-card">
          <div class="card-header">
            <h3><i class="fas fa-tasks"></i> Tasks Assigned</h3>
          </div>
          <div class="card-body">
            <div v-if="tasksLoading" class="loading-state">
              <i class="fas fa-spinner fa-spin"></i>
            </div>
            <div v-else-if="assignedTasks.length === 0" class="empty-state">
              <i class="fas fa-clipboard-list"></i>
              <p>No tasks assigned yet</p>
            </div>
            <div v-else class="tasks-list">
              <div 
                v-for="task in assignedTasks" 
                :key="task.id"
                class="task-item"
              >
                <div class="task-header">
                  <h4>{{ task.title }}</h4>
                  <span :class="['priority-badge', task.priority]">
                    {{ task.priority }}
                  </span>
                </div>
                <div class="task-meta">
                  <div class="meta-item">
                    <i class="fas fa-user"></i>
                    {{ task.assigned_to_name }}
                  </div>
                  <div class="meta-item">
                    <i class="fas fa-calendar"></i>
                    {{ formatDate(task.deadline) }}
                  </div>
                  <span :class="['status-badge', task.status]">
                    {{ formatTaskStatus(task.status) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Leave Balance -->
        <div class="dashboard-card leave-card">
          <div class="card-header">
            <h3><i class="fas fa-umbrella-beach"></i> Leave Summary</h3>
          </div>
          <div class="card-body">
            <div v-if="leaveBalance" class="leave-balance-grid">
              <div class="balance-item">
                <div class="balance-label">Sick Leave</div>
                <div class="balance-value">{{ leaveBalance.sick_leave }}</div>
              </div>
              <div class="balance-item">
                <div class="balance-label">Casual Leave</div>
                <div class="balance-value">{{ leaveBalance.casual_leave }}</div>
              </div>
              <div class="balance-item">
                <div class="balance-label">LOP</div>
                <div class="balance-value lop">{{ leaveBalance.lop_leave }}</div>
              </div>
            </div>
            <div v-if="recentLeaves.length > 0" class="recent-leaves">
              <h4>Recent Applications</h4>
              <div 
                v-for="leave in recentLeaves.slice(0, 3)" 
                :key="leave.id"
                class="leave-item"
              >
                <div class="leave-dates">
                  {{ formatDate(leave.start_date) }} - {{ formatDate(leave.end_date) }}
                </div>
                <span :class="['status-badge', leave.status]">
                  {{ leave.status }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Vacancy Creation Modal -->
      <div v-if="showVacancyModal" class="modal-overlay" @click.self="showVacancyModal = false">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Create New Vacancy</h3>
            <button class="close-btn" @click="showVacancyModal = false">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitVacancy">
              <div class="form-group">
                <label>Job Title *</label>
                <input 
                  v-model="vacancyForm.title" 
                  type="text"
                  placeholder="e.g., Software Engineer"
                  required
                />
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Location *</label>
                  <input 
                    v-model="vacancyForm.location" 
                    type="text"
                    placeholder="e.g., Mumbai"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>Organization Type *</label>
                  <select v-model="vacancyForm.org_type" required>
                    <option value="">Select Type</option>
                    <option value="school">School</option>
                    <option value="company">Company</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label>School/Company Name *</label>
                <input 
                  v-model="vacancyForm.school" 
                  type="text"
                  :placeholder="vacancyForm.org_type === 'school' ? 'School Name' : 'Company Name'"
                  required
                />
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Level</label>
                  <select v-model="vacancyForm.level">
                    <option value="">Select Level</option>
                    <option value="junior">Junior</option>
                    <option value="mid">Mid-Level</option>
                    <option value="senior">Senior</option>
                    <option value="lead">Lead</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Number of Positions *</label>
                  <input 
                    v-model.number="vacancyForm.count" 
                    type="number"
                    min="1"
                    required
                  />
                </div>
              </div>
              <div class="form-group">
                <label>Description</label>
                <textarea 
                  v-model="vacancyForm.description"
                  placeholder="Job description..."
                  rows="3"
                ></textarea>
              </div>
              <div class="form-group">
                <label>Requirements</label>
                <textarea 
                  v-model="vacancyForm.requirements"
                  placeholder="Job requirements..."
                  rows="3"
                ></textarea>
              </div>
              <div class="form-group">
                <label>Salary Range</label>
                <input 
                  v-model="vacancyForm.salary_range" 
                  type="text"
                  placeholder="e.g., 5-8 LPA"
                />
              </div>
              <div class="form-group">
                <label>
                  <input 
                    v-model="vacancyForm.notify_hr" 
                    type="checkbox"
                  />
                  Notify HR immediately
                </label>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn-cancel" @click="showVacancyModal = false">
                  Cancel
                </button>
                <button type="submit" class="btn-submit" :disabled="submittingVacancy">
                  <i class="fas fa-spinner fa-spin" v-if="submittingVacancy"></i>
                  {{ submittingVacancy ? 'Creating...' : 'Create Vacancy' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Task Assignment Modal -->
      <div v-if="showTaskModal" class="modal-overlay" @click.self="showTaskModal = false">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Assign Task to Candidate</h3>
            <button class="close-btn" @click="showTaskModal = false">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitTask">
              <div class="form-group">
                <label>Select Candidate *</label>
                <select v-model="taskForm.assigned_to_id" required>
                  <option value="">Choose Candidate</option>
                  <option 
                    v-for="candidate in candidates" 
                    :key="candidate.id"
                    :value="candidate.id"
                  >
                    {{ candidate.name }} - {{ candidate.email }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Task Title *</label>
                <input 
                  v-model="taskForm.title" 
                  type="text"
                  placeholder="e.g., Complete Python Assignment"
                  required
                />
              </div>
              <div class="form-group">
                <label>Description *</label>
                <textarea 
                  v-model="taskForm.description"
                  placeholder="Detailed task description..."
                  rows="4"
                  required
                ></textarea>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Deadline *</label>
                  <input 
                    v-model="taskForm.deadline" 
                    type="datetime-local"
                    :min="getCurrentDateTime()"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>Priority *</label>
                  <select v-model="taskForm.priority" required>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn-cancel" @click="showTaskModal = false">
                  Cancel
                </button>
                <button type="submit" class="btn-submit" :disabled="submittingTask">
                  <i class="fas fa-spinner fa-spin" v-if="submittingTask"></i>
                  {{ submittingTask ? 'Assigning...' : 'Assign Task' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Leave Application Modal -->
      <div v-if="showLeaveModal" class="modal-overlay" @click.self="showLeaveModal = false">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Apply for Leave</h3>
            <button class="close-btn" @click="showLeaveModal = false">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitLeave">
              <div class="form-group">
                <label>Leave Type *</label>
                <select v-model="leaveForm.leave_type" required>
                  <option value="">Select Leave Type</option>
                  <option value="sick">Sick Leave</option>
                  <option value="casual">Casual Leave</option>
                  <option value="lop">Leave Without Pay</option>
                </select>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Start Date *</label>
                  <input 
                    v-model="leaveForm.start_date" 
                    type="date" 
                    :min="getCurrentDate()"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>End Date *</label>
                  <input 
                    v-model="leaveForm.end_date" 
                    type="date" 
                    :min="leaveForm.start_date || getCurrentDate()"
                    required
                  />
                </div>
              </div>
              <div class="form-group">
                <label>Reason *</label>
                <textarea 
                  v-model="leaveForm.reason"
                  placeholder="Reason for leave..."
                  rows="3"
                  required
                ></textarea>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn-cancel" @click="showLeaveModal = false">
                  Cancel
                </button>
                <button type="submit" class="btn-submit" :disabled="submittingLeave">
                  <i class="fas fa-spinner fa-spin" v-if="submittingLeave"></i>
                  {{ submittingLeave ? 'Submitting...' : 'Apply' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Technical Interview Evaluation Modal -->
      <div v-if="showEvaluationModal" class="modal-overlay" @click.self="closeEvaluationModal">
        <div class="modal-container evaluation-modal">
          <div class="modal-header">
            <h3>Technical Interview Evaluation - {{ selectedInterview?.candidate_name }}</h3>
            <button class="close-btn" @click="closeEvaluationModal">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitEvaluation">
              <div class="evaluation-section">
                <h4>Technical Assessment</h4>
                <div class="form-group">
                  <label>Technical Score (0-100) *</label>
                  <input 
                    v-model.number="evaluationForm.technical_score" 
                    type="number" 
                    min="0" 
                    max="100"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>Problem Solving Score (0-100) *</label>
                  <input 
                    v-model.number="evaluationForm.problem_solving_score" 
                    type="number" 
                    min="0" 
                    max="100"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>Communication Score (0-100) *</label>
                  <input 
                    v-model.number="evaluationForm.communication_score" 
                    type="number" 
                    min="0" 
                    max="100"
                    required
                  />
                </div>
              </div>

              <div class="form-group">
                <label>Technical Strengths *</label>
                <textarea 
                  v-model="evaluationForm.strengths"
                  placeholder="Technical skills and strengths observed..."
                  rows="3"
                  required
                ></textarea>
              </div>

              <div class="form-group">
                <label>Areas for Improvement *</label>
                <textarea 
                  v-model="evaluationForm.weaknesses"
                  placeholder="Technical gaps or areas to improve..."
                  rows="3"
                  required
                ></textarea>
              </div>

              <div class="form-group">
                <label>Additional Technical Feedback</label>
                <textarea 
                  v-model="evaluationForm.feedback_notes"
                  placeholder="Any additional technical observations..."
                  rows="3"
                ></textarea>
              </div>

              <div class="form-group">
                <label>Recommendation *</label>
                <select v-model="evaluationForm.recommendation" required>
                  <option value="">Select Recommendation</option>
                  <option value="strong_hire">Strong Hire</option>
                  <option value="hire">Hire</option>
                  <option value="maybe">Maybe</option>
                  <option value="no_hire">No Hire</option>
                </select>
              </div>

              <div class="modal-footer">
                <button type="button" class="btn-cancel" @click="closeEvaluationModal">
                  Cancel
                </button>
                <button type="submit" class="btn-submit" :disabled="submittingEvaluation">
                  <i class="fas fa-spinner fa-spin" v-if="submittingEvaluation"></i>
                  {{ submittingEvaluation ? 'Submitting...' : 'Submit Evaluation' }}
                </button>
              </div>
            </form>
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
const hoName = ref('')
const hoId = ref('')
const stats = ref({
  activeVacancies: 0,
  technicalInterviews: 0,
  assignedTasks: 0,
  leaveBalance: 0
})

// Data arrays
const recentVacancies = ref([])
const technicalInterviews = ref([])
const assignedTasks = ref([])
const candidates = ref([])
const recentLeaves = ref([])
const leaveBalance = ref(null)

// Loading states
const vacanciesLoading = ref(false)
const interviewsLoading = ref(false)
const tasksLoading = ref(false)

// Modal states
const showVacancyModal = ref(false)
const showTaskModal = ref(false)
const showLeaveModal = ref(false)
const showEvaluationModal = ref(false)
const selectedInterview = ref(null)

// Form states
const submittingVacancy = ref(false)
const submittingTask = ref(false)
const submittingLeave = ref(false)
const submittingEvaluation = ref(false)

// Forms
const vacancyForm = ref({
  title: '',
  location: '',
  org_type: '',
  school: '',
  level: '',
  count: 1,
  description: '',
  requirements: '',
  salary_range: '',
  notify_hr: true
})

const taskForm = ref({
  assigned_to_id: '',
  title: '',
  description: '',
  deadline: '',
  priority: 'medium'
})

const leaveForm = ref({
  leave_type: '',
  start_date: '',
  end_date: '',
  reason: ''
})

const evaluationForm = ref({
  technical_score: 0,
  problem_solving_score: 0,
  communication_score: 0,
  strengths: '',
  weaknesses: '',
  feedback_notes: '',
  recommendation: ''
})

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

function getCurrentDate() {
  return new Date().toISOString().split('T')[0]
}

function getCurrentDateTime() {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  return now.toISOString().slice(0, 16)
}

function calculateDays(startDate, endDate) {
  const start = new Date(startDate)
  const end = new Date(endDate)
  const diffTime = Math.abs(end - start)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
  return diffDays
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

function formatTime(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

function formatInterviewStatus(status) {
  const statusMap = {
    'scheduled': 'Scheduled',
    'confirmed': 'Confirmed',
    'completed': 'Completed',
    'cancelled': 'Cancelled'
  }
  return statusMap[status] || status
}

function formatTaskStatus(status) {
  const statusMap = {
    'pending': 'Pending',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'reviewed': 'Reviewed'
  }
  return statusMap[status] || status
}

function isInterviewSoon(scheduledAt) {
  const now = new Date()
  const interviewTime = new Date(scheduledAt)
  const diffMinutes = (interviewTime - now) / (1000 * 60)
  return diffMinutes <= 30 && diffMinutes >= -30
}

function navigate(page) {
  const routes = {
    'vacancies': '/ho/vacancies'
  }
  if (routes[page]) {
    router.push(routes[page])
  }
}

function openMeeting(link) {
  window.open(link, '_blank')
}

function openEvaluationModal(interview) {
  selectedInterview.value = interview
  showEvaluationModal.value = true
  
  // Reset form
  evaluationForm.value = {
    technical_score: 0,
    problem_solving_score: 0,
    communication_score: 0,
    strengths: '',
    weaknesses: '',
    feedback_notes: '',
    recommendation: ''
  }
}

function closeEvaluationModal() {
  showEvaluationModal.value = false
  selectedInterview.value = null
}

// API Functions
async function loadHOData() {
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/users/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    hoName.value = response.data.name
    hoId.value = response.data.id
  } catch (error) {
    console.error('Error loading HO data:', error)
  }
}

async function loadRecentVacancies() {
  vacanciesLoading.value = true
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/vacancies/', {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        limit: 10
      }
    })
    
    recentVacancies.value = response.data.vacancies || []
    stats.value.activeVacancies = recentVacancies.value.filter(v => v.status === 'active').length
  } catch (error) {
    console.error('Error loading vacancies:', error)
  } finally {
    vacanciesLoading.value = false
  }
}

async function loadTechnicalInterviews() {
  interviewsLoading.value = true
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/pipeline/interview-assignments', {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        interviewer_id: hoId.value,
        upcoming_only: true
      }
    })
    
    // Filter for technical interviews only
    technicalInterviews.value = response.data.assignments.filter(
      interview => interview.interview_type === 'technical'
    ).map(interview => ({
      ...interview,
      candidate_name: interview.candidate_details?.name || 'Unknown',
      job_title: interview.job_details?.title || 'Unknown Position'
    }))
    
    stats.value.technicalInterviews = technicalInterviews.value.length
  } catch (error) {
    console.error('Error loading interviews:', error)
  } finally {
    interviewsLoading.value = false
  }
}

async function loadAssignedTasks() {
  tasksLoading.value = true
  try {
    const token = getAuthToken()
    // Get tasks created by this HO user
    const response = await axios.get('/api/tasks/', {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        assigned_by_id: hoId.value,
        limit: 10
      }
    })
    
    assignedTasks.value = response.data.tasks || []
    stats.value.assignedTasks = assignedTasks.value.filter(t => t.status !== 'completed').length
  } catch (error) {
    console.error('Error loading tasks:', error)
  } finally {
    tasksLoading.value = false
  }
}

async function loadCandidates() {
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/users/role/candidate', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    candidates.value = response.data || []
  } catch (error) {
    console.error('Error loading candidates:', error)
  }
}

async function loadLeaveBalance() {
  try {
    const token = getAuthToken()
    const response = await axios.get(`/api/leave/balance/${hoId.value}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    leaveBalance.value = response.data.data.leave_balance
    leaveBalance.value.sick_leave = leaveBalance.value.sick
    leaveBalance.value.casual_leave = leaveBalance.value.casual
    leaveBalance.value.lop_leave = leaveBalance.value.lop
    stats.value.leaveBalance = (leaveBalance.value?.sick_leave || 0) + 
                                (leaveBalance.value?.casual_leave || 0)
  } catch (error) {
    console.error('Error loading leave balance:', error)
  }
}

async function loadRecentLeaves() {
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/leave/history', {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        employee_id: hoId.value
      }
    })
    
    recentLeaves.value = (response.data.data || []).slice(0, 5)
  } catch (error) {
    console.error('Error loading leaves:', error)
  }
}

async function submitVacancy() {
  submittingVacancy.value = true
  try {
    const token = getAuthToken()
    
    const vacancyData = {
      title: vacancyForm.value.title,
      location: vacancyForm.value.location,
      school: vacancyForm.value.school,
      level: vacancyForm.value.level,
      description: vacancyForm.value.description,
      requirements: vacancyForm.value.requirements,
      salary_range: vacancyForm.value.salary_range,
      posted_by_id: hoId.value,
      status: 'active'
    }
    
    const response = await axios.post('/api/vacancies/', vacancyData, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // Notify HR if checkbox is selected
    if (vacancyForm.value.notify_hr) {
      await notifyHR(response.data.vacancy)
    }
    
    alert('Vacancy created successfully!')
    showVacancyModal.value = false
    
    // Reset form
    vacancyForm.value = {
      title: '',
      location: '',
      org_type: '',
      school: '',
      level: '',
      count: 1,
      description: '',
      requirements: '',
      salary_range: '',
      notify_hr: true
    }
    
    loadRecentVacancies()
  } catch (error) {
    console.error('Error creating vacancy:', error)
    alert('Failed to create vacancy: ' + (error.response?.data?.error || error.message))
  } finally {
    submittingVacancy.value = false
  }
}

async function notifyHR(vacancy) {
  try {
    const token = getAuthToken()
    
    // Get all HR users
    const hrResponse = await axios.get('/api/users/role/hr', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    const hrUsers = hrResponse.data || []
    
    // Create notification for each HR user
    for (const hr of hrUsers) {
      await axios.post('/api/notifications/', {
        recipient_id: hr.id,
        message: `New vacancy created: ${vacancy.title} at ${vacancy.school || vacancy.location}`,
        type: 'vacancy'
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
    }
    
    alert('HR team notified successfully!')
    vacancy.notified = true
  } catch (error) {
    console.error('Error notifying HR:', error)
    alert('Failed to notify HR: ' + (error.response?.data?.error || error.message))
  }
}

async function submitTask() {
  submittingTask.value = true
  try {
    const token = getAuthToken()
    
    await axios.post('/api/tasks/', {
      assigned_to_id: taskForm.value.assigned_to_id,
      assigned_by_id: hoId.value,
      title: taskForm.value.title,
      description: taskForm.value.description,
      deadline: new Date(taskForm.value.deadline).toISOString(),
      priority: taskForm.value.priority,
      status: 'pending'
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    alert('Task assigned successfully!')
    showTaskModal.value = false
    
    // Reset form
    taskForm.value = {
      assigned_to_id: '',
      title: '',
      description: '',
      deadline: '',
      priority: 'medium'
    }
    
    loadAssignedTasks()
  } catch (error) {
    console.error('Error assigning task:', error)
    alert('Failed to assign task: ' + (error.response?.data?.error || error.message))
  } finally {
    submittingTask.value = false
  }
}

async function submitLeave() {
  submittingLeave.value = true
  try {
    const token = getAuthToken()
    
    await axios.post('/api/leave/request', {
      employee_id: hoId.value,
      leave_type: leaveForm.value.leave_type,
      start_date: leaveForm.value.start_date,
      days: calculateDays(leaveForm.value.start_date, leaveForm.value.end_date),
      reason: leaveForm.value.reason
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    alert('Leave application submitted successfully!')
    showLeaveModal.value = false
    
    // Reset form
    leaveForm.value = {
      leave_type: '',
      start_date: '',
      end_date: '',
      reason: ''
    }
    
    loadLeaveBalance()
    loadRecentLeaves()
  } catch (error) {
    console.error('Error applying leave:', error)
    alert('Failed to apply leave: ' + (error.response?.data?.error || error.message))
  } finally {
    submittingLeave.value = false
  }
}

async function submitEvaluation() {
  submittingEvaluation.value = true
  try {
    const token = getAuthToken()
    
    // Calculate overall score
    const overallScore = Math.round(
      (evaluationForm.value.technical_score +
       evaluationForm.value.problem_solving_score +
       evaluationForm.value.communication_score) / 3
    )
    
    await axios.post('/api/pipeline/scorecard', {
      interview_assignment_id: selectedInterview.value.id,
      interviewer_id: hoId.value,
      technical_score: evaluationForm.value.technical_score,
      problem_solving_score: evaluationForm.value.problem_solving_score,
      communication_score: evaluationForm.value.communication_score,
      overall_score: overallScore,
      strengths: evaluationForm.value.strengths,
      weaknesses: evaluationForm.value.weaknesses,
      feedback_notes: evaluationForm.value.feedback_notes,
      recommendation: evaluationForm.value.recommendation,
      is_final: true
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    alert('Technical evaluation submitted successfully!')
    closeEvaluationModal()
    loadTechnicalInterviews()
  } catch (error) {
    console.error('Error submitting evaluation:', error)
    alert('Failed to submit evaluation: ' + (error.response?.data?.error || error.message))
  } finally {
    submittingEvaluation.value = false
  }
}

// Load data on mount
onMounted(async () => {
  await loadHOData()
  loadRecentVacancies()
  loadTechnicalInterviews()
  loadAssignedTasks()
  loadCandidates()
  loadLeaveBalance()
  loadRecentLeaves()
})
</script>

<style scoped>
/* Same styles as BDA Dashboard with slight modifications */
.ho-dashboard {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
}

.welcome-section h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 8px;
}

.welcome-section p {
  color: #7f8c8d;
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.quick-action-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.quick-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(240, 147, 251, 0.4);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 2.5rem;
  color: #f093fb;
  opacity: 0.8;
}

.stat-info h3 {
  font-size: 2rem;
  margin: 0;
  color: #2c3e50;
}

.stat-info p {
  margin: 4px 0 0 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.dashboard-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.dashboard-card.full-width {
  grid-column: 1 / -1;
}

.card-header {
  padding: 20px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.refresh-btn,
.view-all-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.refresh-btn:hover,
.view-all-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.card-body {
  padding: 20px;
  max-height: 500px;
  overflow-y: auto;
}

/* Loading & Empty States */
.loading-state,
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.loading-state i,
.empty-state i {
  font-size: 3rem;
  margin-bottom: 12px;
  opacity: 0.5;
}

/* Vacancies Grid */
.vacancies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.vacancy-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #f093fb;
}

.vacancy-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 12px;
}

.vacancy-header h4 {
  margin: 0;
  color: #2c3e50;
  flex: 1;
}

.vacancy-details {
  margin-bottom: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-bottom: 6px;
}

.detail-item i {
  color: #f093fb;
}

.btn-notify {
  width: 100%;
  padding: 8px 16px;
  background: #f093fb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.btn-notify:hover:not(:disabled) {
  background: #f5576c;
}

.btn-notify:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Interviews List - same as BDA */
.interviews-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.interview-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #f093fb;
}

.interview-time {
  text-align: center;
  min-width: 80px;
}

.interview-time .date {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 4px;
}

.interview-time .time {
  font-weight: 600;
  color: #2c3e50;
}

.interview-info {
  flex: 1;
}

.interview-info h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.interview-info p {
  margin: 4px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  display: inline-block;
  margin-top: 8px;
}

.status-badge.scheduled,
.status-badge.confirmed {
  background: #d4edda;
  color: #155724;
}

.status-badge.completed {
  background: #cce5ff;
  color: #004085;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.approved {
  background: #d4edda;
  color: #155724;
}

.status-badge.rejected {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.closed {
  background: #e2e3e5;
  color: #383d41;
}

.interview-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.btn-join,
.btn-evaluate {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: center;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-join {
  background: #28a745;
  color: white;
}

.btn-join:hover:not(:disabled) {
  background: #218838;
}

.btn-evaluate {
  background: #f093fb;
  color: white;
}

.btn-evaluate:hover:not(:disabled) {
  background: #f5576c;
}

.btn-join:disabled,
.btn-evaluate:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Tasks List */
.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #f093fb;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 8px;
}

.task-header h4 {
  margin: 0;
  color: #2c3e50;
  flex: 1;
}

.priority-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.priority-badge.high {
  background: #f8d7da;
  color: #721c24;
}

.priority-badge.medium {
  background: #fff3cd;
  color: #856404;
}

.priority-badge.low {
  background: #d4edda;
  color: #155724;
}

.task-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.meta-item {
  color: #7f8c8d;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-item i {
  color: #f093fb;
}

/* Leave Card */
.leave-balance-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.balance-item {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.balance-label {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.balance-value {
  font-size: 2rem;
  font-weight: 600;
  color: #f093fb;
}

.balance-value.lop {
  color: #e74c3c;
}

.recent-leaves h4 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-size: 1rem;
}

.leave-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 8px;
}

.leave-dates {
  color: #2c3e50;
  font-size: 0.9rem;
}

/* Modal Styles - same as BDO */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-container.evaluation-modal {
  max-width: 700px;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 4px 8px;
  transition: opacity 0.3s ease;
}

.close-btn:hover {
  opacity: 0.7;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #2c3e50;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f093fb;
}

.form-group input[type="checkbox"] {
  width: auto;
  margin-right: 8px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.evaluation-section {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.evaluation-section h4 {
  margin: 0 0 16px 0;
  color: #2c3e50;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel,
.btn-submit {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-cancel:hover {
  background: #dde1e3;
}

.btn-submit {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(240, 147, 251, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .content-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .interview-item {
    flex-direction: column;
  }

  .interview-actions {
    flex-direction: row;
    width: 100%;
  }

  .leave-balance-grid {
    grid-template-columns: 1fr;
  }

  .vacancies-grid {
    grid-template-columns: 1fr;
  }
}
</style>
