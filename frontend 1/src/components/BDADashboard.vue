<template>
  <DashboardLayout>
    <div class="bda-dashboard">
      <!-- Header -->
      <div class="dashboard-header">
        <div class="welcome-section">
          <h1>Business Development Associate Dashboard</h1>
          <p>Welcome back, {{ bdaName }}! Here's your overview for today.</p>
        </div>
        <div class="quick-actions">
          <button class="quick-action-btn" @click="showExpenseModal = true">
            <i class="fas fa-receipt"></i>
            Submit Expense
          </button>
          <button class="quick-action-btn" @click="showEODModal = true">
            <i class="fas fa-clipboard-list"></i>
            EOD Report
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
          <i class="fas fa-file-invoice-dollar stat-icon"></i>
          <div class="stat-info">
            <h3>{{ stats.pendingExpenses }}</h3>
            <p>Pending Expenses</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-users stat-icon"></i>
          <div class="stat-info">
            <h3>{{ stats.upcomingInterviews }}</h3>
            <p>Upcoming Interviews</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-calendar-check stat-icon"></i>
          <div class="stat-info">
            <h3>{{ stats.eodReports }}</h3>
            <p>EOD Reports This Month</p>
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
        <!-- Upcoming Behavioral Interviews -->
        <div class="dashboard-card interviews-card">
          <div class="card-header">
            <h3><i class="fas fa-comments"></i> Upcoming Behavioral Interviews</h3>
            <button class="refresh-btn" @click="loadUpcomingInterviews">
              <i class="fas fa-sync-alt"></i>
            </button>
          </div>
          <div class="card-body">
            <div v-if="interviewsLoading" class="loading-state">
              <i class="fas fa-spinner fa-spin"></i>
              <p>Loading interviews...</p>
            </div>
            <div v-else-if="upcomingInterviews.length === 0" class="empty-state">
              <i class="fas fa-user-tie"></i>
              <p>No upcoming behavioral interviews</p>
            </div>
            <div v-else class="interviews-list">
              <div 
                v-for="interview in upcomingInterviews" 
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
                  <div class="interview-meta">
                    <span class="duration">
                      <i class="fas fa-clock"></i> {{ interview.duration_minutes }} min
                    </span>
                    <span :class="['status-badge', interview.status]">
                      {{ formatInterviewStatus(interview.status) }}
                    </span>
                  </div>
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

        <!-- Recent Expenses -->
        <div class="dashboard-card expenses-card">
          <div class="card-header">
            <h3><i class="fas fa-receipt"></i> Recent Expenses</h3>
            <button class="view-all-btn" @click="navigate('expenses')">
              View All
            </button>
          </div>
          <div class="card-body">
            <div v-if="expensesLoading" class="loading-state">
              <i class="fas fa-spinner fa-spin"></i>
            </div>
            <div v-else-if="recentExpenses.length === 0" class="empty-state">
              <i class="fas fa-file-invoice"></i>
              <p>No expenses submitted yet</p>
            </div>
            <div v-else class="expenses-list">
              <div 
                v-for="expense in recentExpenses" 
                :key="expense.id"
                class="expense-item"
              >
                <div class="expense-icon">
                  <i class="fas fa-file-invoice-dollar"></i>
                </div>
                <div class="expense-info">
                  <h4>{{ expense.category || 'General Expense' }}</h4>
                  <p>{{ formatDate(expense.created_at) }}</p>
                </div>
                <div class="expense-amount">
                  <span class="amount">₹{{ expense.total }}</span>
                  <span :class="['status-badge', expense.status]">
                    {{ expense.status }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- EOD Reports -->
        <div class="dashboard-card eod-card">
          <div class="card-header">
            <h3><i class="fas fa-clipboard-list"></i> Recent EOD Reports</h3>
          </div>
          <div class="card-body">
            <div v-if="eodLoading" class="loading-state">
              <i class="fas fa-spinner fa-spin"></i>
            </div>
            <div v-else-if="recentEODReports.length === 0" class="empty-state">
              <i class="fas fa-clipboard"></i>
              <p>No EOD reports submitted yet</p>
            </div>
            <div v-else class="eod-list">
              <div 
                v-for="report in recentEODReports" 
                :key="report.id"
                class="eod-item"
              >
                <div class="eod-date">
                  <i class="fas fa-calendar"></i>
                  {{ formatDate(report.date) }}
                </div>
                <div class="eod-summary">
                  <p v-if="report.ai_summary">{{ truncateText(report.ai_summary, 100) }}</p>
                  <p v-else>EOD Report - {{ report.role }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Leave Balance & History -->
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
              <h4>Recent Leave Applications</h4>
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

      <!-- Expense Modal -->
      <div v-if="showExpenseModal" class="modal-overlay" @click.self="showExpenseModal = false">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Submit Expense Report</h3>
            <button class="close-btn" @click="showExpenseModal = false">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitExpense">
              <div class="form-group">
                <label>Category</label>
                <select v-model="expenseForm.category" required>
                  <option value="">Select Category</option>
                  <option value="travel">Travel</option>
                  <option value="meals">Meals</option>
                  <option value="accommodation">Accommodation</option>
                  <option value="office_supplies">Office Supplies</option>
                  <option value="client_meeting">Client Meeting</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div class="form-group">
                <label>Amount (₹)</label>
                <input 
                  v-model.number="expenseForm.amount" 
                  type="number" 
                  step="0.01"
                  placeholder="Enter amount"
                  required
                />
              </div>
              <div class="form-group">
                <label>Description</label>
                <textarea 
                  v-model="expenseForm.description"
                  placeholder="Describe the expense..."
                  rows="3"
                  required
                ></textarea>
              </div>
              <div class="form-group">
                <label>Receipt (Optional)</label>
                <input 
                  type="file" 
                  @change="handleReceiptUpload"
                  accept=".pdf,.jpg,.jpeg,.png"
                />
              </div>
              <div class="modal-footer">
                <button type="button" class="btn-cancel" @click="showExpenseModal = false">
                  Cancel
                </button>
                <button type="submit" class="btn-submit" :disabled="submittingExpense">
                  <i class="fas fa-spinner fa-spin" v-if="submittingExpense"></i>
                  {{ submittingExpense ? 'Submitting...' : 'Submit' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- EOD Report Modal -->
      <div v-if="showEODModal" class="modal-overlay" @click.self="showEODModal = false">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Submit End of Day Report</h3>
            <button class="close-btn" @click="showEODModal = false">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitEOD">
              <div class="form-group">
                <label>Date</label>
                <input 
                  v-model="eodForm.date" 
                  type="date" 
                  :max="getCurrentDate()"
                  required
                />
              </div>
              <div class="form-group">
                <label>Client Visits</label>
                <textarea 
                  v-model="eodForm.client_visits"
                  placeholder="List client visits and outcomes..."
                  rows="3"
                  required
                ></textarea>
              </div>
              <div class="form-group">
                <label>Leads Generated</label>
                <input 
                  v-model.number="eodForm.leads_generated" 
                  type="number"
                  min="0"
                  placeholder="Number of leads"
                  required
                />
              </div>
              <div class="form-group">
                <label>Follow-ups Completed</label>
                <input 
                  v-model.number="eodForm.followups_completed" 
                  type="number"
                  min="0"
                  placeholder="Number of follow-ups"
                  required
                />
              </div>
              <div class="form-group">
                <label>Challenges Faced</label>
                <textarea 
                  v-model="eodForm.challenges"
                  placeholder="Any challenges or issues..."
                  rows="2"
                ></textarea>
              </div>
              <div class="form-group">
                <label>Next Day Plan</label>
                <textarea 
                  v-model="eodForm.next_day_plan"
                  placeholder="Plan for tomorrow..."
                  rows="2"
                ></textarea>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn-cancel" @click="showEODModal = false">
                  Cancel
                </button>
                <button type="submit" class="btn-submit" :disabled="submittingEOD">
                  <i class="fas fa-spinner fa-spin" v-if="submittingEOD"></i>
                  {{ submittingEOD ? 'Submitting...' : 'Submit' }}
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
                <label>Leave Type</label>
                <select v-model="leaveForm.leave_type" required>
                  <option value="">Select Leave Type</option>
                  <option value="sick">Sick Leave</option>
                  <option value="casual">Casual Leave</option>
                  <option value="lop">Leave Without Pay</option>
                </select>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Start Date</label>
                  <input 
                    v-model="leaveForm.start_date" 
                    type="date" 
                    :min="getCurrentDate()"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>End Date</label>
                  <input 
                    v-model="leaveForm.end_date" 
                    type="date" 
                    :min="leaveForm.start_date || getCurrentDate()"
                    required
                  />
                </div>
              </div>
              <div class="form-group">
                <label>Reason</label>
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

      <!-- Interview Evaluation Modal -->
      <div v-if="showEvaluationModal" class="modal-overlay" @click.self="closeEvaluationModal">
        <div class="modal-container evaluation-modal">
          <div class="modal-header">
            <h3>Interview Evaluation - {{ selectedInterview?.candidate_name }}</h3>
            <button class="close-btn" @click="closeEvaluationModal">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitEvaluation">
              <div class="evaluation-section">
                <h4>Behavioral Assessment</h4>
                <div class="form-group">
                  <label>Communication Score (0-100)</label>
                  <input 
                    v-model.number="evaluationForm.communication_score" 
                    type="number" 
                    min="0" 
                    max="100"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>Cultural Fit Score (0-100)</label>
                  <input 
                    v-model.number="evaluationForm.cultural_fit_score" 
                    type="number" 
                    min="0" 
                    max="100"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>Problem Solving Score (0-100)</label>
                  <input 
                    v-model.number="evaluationForm.problem_solving_score" 
                    type="number" 
                    min="0" 
                    max="100"
                    required
                  />
                </div>
              </div>

              <div class="form-group">
                <label>Strengths</label>
                <textarea 
                  v-model="evaluationForm.strengths"
                  placeholder="Key strengths observed..."
                  rows="3"
                  required
                ></textarea>
              </div>

              <div class="form-group">
                <label>Weaknesses</label>
                <textarea 
                  v-model="evaluationForm.weaknesses"
                  placeholder="Areas for improvement..."
                  rows="3"
                  required
                ></textarea>
              </div>

              <div class="form-group">
                <label>Additional Feedback</label>
                <textarea 
                  v-model="evaluationForm.feedback_notes"
                  placeholder="Any additional comments..."
                  rows="3"
                ></textarea>
              </div>

              <div class="form-group">
                <label>Recommendation</label>
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
const bdaName = ref('')
const bdaId = ref('')
const stats = ref({
  pendingExpenses: 0,
  upcomingInterviews: 0,
  eodReports: 0,
  leaveBalance: 0
})

// Data arrays
const upcomingInterviews = ref([])
const recentExpenses = ref([])
const recentEODReports = ref([])
const recentLeaves = ref([])
const leaveBalance = ref(null)

// Loading states
const interviewsLoading = ref(false)
const expensesLoading = ref(false)
const eodLoading = ref(false)

// Modal states
const showExpenseModal = ref(false)
const showEODModal = ref(false)
const showLeaveModal = ref(false)
const showEvaluationModal = ref(false)
const selectedInterview = ref(null)

// Form states
const submittingExpense = ref(false)
const submittingEOD = ref(false)
const submittingLeave = ref(false)
const submittingEvaluation = ref(false)

// Forms
const expenseForm = ref({
  category: '',
  amount: 0,
  description: '',
  receipt: null
})

const eodForm = ref({
  date: getCurrentDate(),
  client_visits: '',
  leads_generated: 0,
  followups_completed: 0,
  challenges: '',
  next_day_plan: ''
})

const leaveForm = ref({
  leave_type: '',
  start_date: '',
  end_date: '',
  reason: ''
})

const evaluationForm = ref({
  communication_score: 0,
  cultural_fit_score: 0,
  problem_solving_score: 0,
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

function truncateText(text, length) {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

function isInterviewSoon(scheduledAt) {
  const now = new Date()
  const interviewTime = new Date(scheduledAt)
  const diffMinutes = (interviewTime - now) / (1000 * 60)
  return diffMinutes <= 30 && diffMinutes >= -30
}

function navigate(page) {
  const routes = {
    'expenses': '/bda/expenses'
  }
  if (routes[page]) {
    router.push(routes[page])
  }
}

function openMeeting(link) {
  window.open(link, '_blank')
}

function handleReceiptUpload(event) {
  expenseForm.value.receipt = event.target.files[0]
}

function openEvaluationModal(interview) {
  selectedInterview.value = interview
  showEvaluationModal.value = true
  
  // Reset form
  evaluationForm.value = {
    communication_score: 0,
    cultural_fit_score: 0,
    problem_solving_score: 0,
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
async function loadBDAData() {
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/users/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    bdaName.value = response.data.name
    bdaId.value = response.data.id
  } catch (error) {
    console.error('Error loading BDO data:', error)
  }
}

async function loadUpcomingInterviews() {
  interviewsLoading.value = true
  try {
    const token = getAuthToken()
    // Get interviews where BDO is the interviewer and type is behavioral
    const response = await axios.get('/api/pipeline/interview-assignments', {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        interviewer_id: bdaId.value,
        upcoming_only: true
      }
    })
    
    // Filter for behavioral interviews only
    upcomingInterviews.value = response.data.assignments.filter(
      interview => interview.interview_type === 'behavioral'
    ).map(interview => ({
      ...interview,
      candidate_name: interview.candidate_details?.name || 'Unknown',
      job_title: interview.job_details?.title || 'Unknown Position'
    }))
    
    stats.value.upcomingInterviews = upcomingInterviews.value.length
  } catch (error) {
    console.error('Error loading interviews:', error)
  } finally {
    interviewsLoading.value = false
  }
}

async function loadRecentExpenses() {
  expensesLoading.value = true
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/expenses/', {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        user_id: bdaId.value,
        limit: 5
      }
    })
    
    recentExpenses.value = response.data.expenses || []
    stats.value.pendingExpenses = recentExpenses.value.filter(e => e.status === 'pending').length
  } catch (error) {
    console.error('Error loading expenses:', error)
  } finally {
    expensesLoading.value = false
  }
}

async function loadRecentEOD() {
  eodLoading.value = true
  try {
    const token = getAuthToken()
    const response = await axios.get('/api/eod/submissions', {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        employee: bdaId.value,
        limit: 5
      }
    })
    
    recentEODReports.value = response.data.data || []
    stats.value.eodReports = response.data.total_count || 0
  } catch (error) {
    console.error('Error loading EOD reports:', error)
  } finally {
    eodLoading.value = false
  }
}

async function loadLeaveBalance() {
  try {
    const token = getAuthToken()
    const response = await axios.get(`/api/leave/balance/${bdaId.value}`, {
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
        employee_id: bdaId.value
      }
    })
    
    recentLeaves.value = (response.data.data || []).slice(0, 5)
  } catch (error) {
    console.error('Error loading leaves:', error)
  }
}

async function submitExpense() {
  submittingExpense.value = true
  try {
    const token = getAuthToken()
    const formData = new FormData()
    
    formData.append('user_id', bdaId.value)
    formData.append('category', expenseForm.value.category)
    formData.append('total', expenseForm.value.amount)
    formData.append('description', expenseForm.value.description)
    
    if (expenseForm.value.receipt) {
      formData.append('receipt', expenseForm.value.receipt)
    }
    
    await axios.post('/api/expenses/submit', formData, {
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    })
    
    alert('Expense submitted successfully!')
    showExpenseModal.value = false
    
    // Reset form
    expenseForm.value = {
      category: '',
      amount: 0,
      description: '',
      receipt: null
    }
    
    loadRecentExpenses()
  } catch (error) {
    console.error('Error submitting expense:', error)
    alert('Failed to submit expense: ' + (error.response?.data?.error || error.message))
  } finally {
    submittingExpense.value = false
  }
}

async function submitEOD() {
  submittingEOD.value = true
  try {
    const token = getAuthToken()
    
    // Create report first
    const reportResponse = await axios.post('/api/reporting/generate', {
      report_type: 'eod',
      start_date: eodForm.value.date,
      end_date: eodForm.value.date,
      format: 'json',
      user_id: bdaId.value
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    const reportId = reportResponse.data.report.id
    
    // Submit EOD data
    await axios.post('/api/eod/submit', {
      employee_id: bdaId.value,
      report_id: reportId,
      role: 'bda',
      date: eodForm.value.date,
      time: new Date().toLocaleTimeString('en-US', { hour12: false }),
      data: {
        client_visits: eodForm.value.client_visits,
        leads_generated: eodForm.value.leads_generated,
        followups_completed: eodForm.value.followups_completed,
        challenges: eodForm.value.challenges,
        next_day_plan: eodForm.value.next_day_plan
      }
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    alert('EOD Report submitted successfully!')
    showEODModal.value = false
    
    // Reset form
    eodForm.value = {
      date: getCurrentDate(),
      client_visits: '',
      leads_generated: 0,
      followups_completed: 0,
      challenges: '',
      next_day_plan: ''
    }
    
    loadRecentEOD()
  } catch (error) {
    console.error('Error submitting EOD:', error)
    alert('Failed to submit EOD: ' + (error.response?.data?.error || error.message))
  } finally {
    submittingEOD.value = false
  }
}

async function submitLeave() {
  submittingLeave.value = true
  try {
    const token = getAuthToken()
    
    await axios.post('/api/leave/request', {
      employee_id: bdaId.value,
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
      (evaluationForm.value.communication_score +
       evaluationForm.value.cultural_fit_score +
       evaluationForm.value.problem_solving_score) / 3
    )
    
    await axios.post('/api/pipeline/scorecard', {
      interview_assignment_id: selectedInterview.value.id,
      interviewer_id: bdoId.value,
      communication_score: evaluationForm.value.communication_score,
      cultural_fit_score: evaluationForm.value.cultural_fit_score,
      problem_solving_score: evaluationForm.value.problem_solving_score,
      overall_score: overallScore,
      strengths: evaluationForm.value.strengths,
      weaknesses: evaluationForm.value.weaknesses,
      feedback_notes: evaluationForm.value.feedback_notes,
      recommendation: evaluationForm.value.recommendation,
      is_final: true
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    alert('Evaluation submitted successfully!')
    closeEvaluationModal()
    loadUpcomingInterviews()
  } catch (error) {
    console.error('Error submitting evaluation:', error)
    alert('Failed to submit evaluation: ' + (error.response?.data?.error || error.message))
  } finally {
    submittingEvaluation.value = false
  }
}

// Load data on mount
onMounted(async () => {
  await loadBDAData()
  loadUpcomingInterviews()
  loadRecentExpenses()
  loadRecentEOD()
  loadLeaveBalance()
  loadRecentLeaves()
})
</script>

<style scoped>
.bda-dashboard {
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
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
  color: #667eea;
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

.card-header {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

/* Interviews */
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
  border-left: 4px solid #667eea;
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

.interview-meta {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.duration {
  color: #7f8c8d;
  font-size: 0.85rem;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
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
}

.btn-join {
  background: #28a745;
  color: white;
}

.btn-join:hover:not(:disabled) {
  background: #218838;
}

.btn-evaluate {
  background: #667eea;
  color: white;
}

.btn-evaluate:hover:not(:disabled) {
  background: #5568d3;
}

.btn-join:disabled,
.btn-evaluate:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Expenses */
.expenses-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.expense-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.expense-icon {
  font-size: 1.5rem;
  color: #667eea;
}

.expense-info {
  flex: 1;
}

.expense-info h4 {
  margin: 0 0 4px 0;
  color: #2c3e50;
}

.expense-info p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.85rem;
}

.expense-amount {
  text-align: right;
}

.expense-amount .amount {
  display: block;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

/* EOD Reports */
.eod-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.eod-item {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #764ba2;
}

.eod-date {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.eod-summary p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
  line-height: 1.5;
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
  color: #667eea;
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

/* Modal Styles */
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  border-color: #667eea;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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
}
</style>
