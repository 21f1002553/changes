<template>
  <DashboardLayout>
    <div class="leave-page">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>
            <i class="fas fa-calendar-alt"></i>
            Apply for Leave
          </h1>
          <p>Submit a leave request and view your leave balance and history</p>
        </div>
      </div>

      <!-- Leave Application Form -->
      <div class="job-selection-section">
        <div class="section-title">
          <i class="fas fa-file-alt"></i>
          <h3>New Leave Request</h3>
        </div>

        <div class="form-group">
          <label for="leave-type">
            <i class="fas fa-tag"></i>
            Leave Type
          </label>
          <select id="leave-type" v-model="leaveType" class="job-select">
            <option value="">-- Choose a leave type --</option>
            <option v-for="t in leaveTypes" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="start-date">
              <i class="fas fa-calendar"></i>
              Start Date
            </label>
            <input id="start-date" type="date" v-model="startDate" class="job-select" />
          </div>

          <div class="form-group">
            <label for="days">
              <i class="fas fa-clock"></i>
              Number of Days
            </label>
            <input id="days" type="number" min="0.5" step="0.5" v-model.number="days"
              :max="maxAllowedDays !== null ? maxAllowedDays : null" class="job-select" placeholder="e.g., 1, 1.5, 2" />
            <div v-if="maxAllowedDays !== null" class="helper-note">
              <small>Maximum allowed for selected type: {{ maxAllowedDays }} day(s)</small>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="reason">
            <i class="fas fa-edit"></i>
            Reason
          </label>
          <textarea id="reason" v-model="reason" rows="4" class="job-select"
            placeholder="Please provide a reason for your leave request..."></textarea>
        </div>

        <div class="form-actions">
          <button class="btn-primary" :disabled="submitting || !leaveType || !startDate || !days" @click="submitLeave">
            <i class="fas" :class="submitting ? 'fa-spinner fa-spin' : 'fa-paper-plane'"></i>
            {{ submitting ? 'Submitting...' : 'Apply for Leave' }}
          </button>
        </div>

        <transition name="fade">
          <div v-if="error" class="error-message" key="error">
            <i class="fas fa-exclamation-circle"></i>
            {{ error }}
          </div>
        </transition>
        <transition name="fade">
          <div v-if="success" class="success-message" key="success">
            <i class="fas fa-check-circle"></i>
            {{ success }}
          </div>
        </transition>
      </div>

      <!-- Leave Balance Section -->
      <div class="results-section">
        <div class="section-header">
          <h3>
            <i class="fas fa-wallet"></i>
            Your Leave Balance
          </h3>
        </div>
        <div class="balance-grid">
          <div class="balance-card sick">
            <div class="balance-icon">
              <i class="fas fa-thermometer-half"></i>
            </div>
            <div class="balance-info">
              <strong>Sick Leave</strong>
              <div class="balance-value">{{ leaveBalance.sick }} days</div>
            </div>
          </div>
          <div class="balance-card casual">
            <div class="balance-icon">
              <i class="fas fa-umbrella-beach"></i>
            </div>
            <div class="balance-info">
              <strong>Casual Leave</strong>
              <div class="balance-value">{{ leaveBalance.casual }} days</div>
            </div>
          </div>
          <div class="balance-card lop">
            <div class="balance-icon">
              <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="balance-info">
              <strong>LOP</strong>
              <div class="balance-value">{{ leaveBalance.lop }} days</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Leave History Section -->
      <div class="results-section">
        <div class="section-header">
          <h3>
            <i class="fas fa-history"></i>
            Leave History
          </h3>
          <div class="filter-stats">
            <span class="stat-badge total">Total: {{ leaveHistory.length }}</span>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="historyLoading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading leave history...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="leaveHistory.length === 0" class="empty-state">
          <i class="fas fa-inbox"></i>
          <h3>No Leave Records</h3>
          <p>You have not submitted any leave requests yet.</p>
        </div>

        <!-- History Table -->
        <div v-else class="table-container">
          <table class="candidates-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Days</th>
                <th>Reason</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rec in leaveHistory" :key="rec.id">
                <td>
                  <div class="date-cell">
                    <i class="fas fa-calendar-day"></i>
                    {{ formatDate(rec.date) }}
                  </div>
                </td>
                <td>
                  <span class="type-badge" :class="getTypeClass(rec.leave_type)">
                    {{ rec.leave_type }}
                  </span>
                </td>
                <td>
                  <div class="days-cell">
                    <i class="fas fa-clock"></i>
                    {{ rec.days }} {{ rec.days === 1 ? 'day' : 'days' }}
                  </div>
                </td>
                <td>
                  <div class="reason-cell">{{ rec.reason || 'N/A' }}</div>
                </td>
                <td>
                  <span class="status-badge" :class="getStatusClass(rec.status)">
                    {{ formatStatus(rec.status) }}
                  </span>
                </td>
                <td>
                  <div class="actions">
                    <button v-if="rec.status !== 'Approved' && rec.status !== 'approved'" class="btn-reject"
                      @click="deleteLeave(rec)">
                      <i class="fas fa-trash"></i>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, computed } from 'vue'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const leaveTypes = ref([])
const leaveType = ref('')
const startDate = ref('')
const days = ref(1)
const reason = ref('')
const submitting = ref(false)
const error = ref('')
const success = ref('')
const leaveBalance = ref({ sick: 0, casual: 0, lop: 0 })
const leaveHistory = ref([])
const historyLoading = ref(false)
const userId = ref('')

// timers for auto-dismiss
let errorTimer = null
let successTimer = null

const getAuthToken = () => localStorage.getItem('access_token')

// Maximum allowed days for current selection (null means no limit)
const maxAllowedDays = computed(() => {
  const t = leaveType.value
  if (!t) return null
  if (t === 'Sick') return Number(leaveBalance.value.sick ?? 0)
  if (t === 'Casual') return Number(leaveBalance.value.casual ?? 0)
  // LOP has no limit
  return null
})

// Clamp days when leaveType or balances change
watch([leaveType, () => leaveBalance.value.sick, () => leaveBalance.value.casual], () => {
  const max = maxAllowedDays.value
  if (max !== null && days.value > max) {
    days.value = max
  }
})

async function loadUser() {
  try {
    const resp = await axios.get('/api/users/', { headers: { Authorization: `Bearer ${getAuthToken()}` } })
    if (resp.data && resp.data.id) {
      userId.value = resp.data.id
    }
  } catch (e) {
    console.error('Failed to load user data', e)
  }
}

async function loadLeaveTypes() {
  try {
    const resp = await axios.get('/api/leave/types', { headers: { Authorization: `Bearer ${getAuthToken()}` } })
    if (resp.data && resp.data.data) {
      leaveTypes.value = resp.data.data
    } else if (Array.isArray(resp.data)) {
      leaveTypes.value = resp.data
    }
  } catch (e) {
    console.error('Failed to load leave types', e)
  }
}

async function loadBalance() {
  if (!userId.value) return
  try {
    const resp = await axios.get(`/api/leave/balance/${userId.value}`, { headers: { Authorization: `Bearer ${getAuthToken()}` } })
    if (resp.data && resp.data.data && resp.data.data.leave_balance) {
      const b = resp.data.data.leave_balance
      console.log(b)
      leaveBalance.value = { sick: b.sick, casual: b.casual, lop: b.lop }
    }
  } catch (e) {
    console.error('Failed to load leave balance', e)
  }
}

async function loadHistory() {
  if (!userId.value) return
  historyLoading.value = true
  try {
    const resp = await axios.get('/api/leave/history', { params: { employee_id: userId.value }, headers: { Authorization: `Bearer ${getAuthToken()}` } })
    if (resp.data && resp.data.data) {
      leaveHistory.value = resp.data.data
    } else if (Array.isArray(resp.data)) {
      leaveHistory.value = resp.data
    } else {
      leaveHistory.value = []
    }
  } catch (e) {
    console.error('Failed to load leave history', e)
    leaveHistory.value = []
  } finally {
    historyLoading.value = false
  }
}

async function submitLeave() {
  error.value = ''
  success.value = ''
  if (!leaveType.value) { error.value = 'Please select a leave type.'; return }
  if (!startDate.value) { error.value = 'Please select a start date.'; return }
  if (!days.value || days.value <= 0) { error.value = 'Please enter a valid number of days.'; return }

  // Enforce max for Sick/Casual
  const max = maxAllowedDays.value
  if (max !== null && days.value > max) {
    error.value = `You cannot request more than ${max} day(s) for ${leaveType.value} leave.`
    return
  }

  submitting.value = true
  try {
    const payload = {
      employee_id: userId.value,
      leave_type: leaveType.value,
      days: days.value,
      start_date: startDate.value,
      reason: reason.value
    }
    const resp = await axios.post('/api/leave/request', payload, { headers: { Authorization: `Bearer ${getAuthToken()}` } })
    if (resp.data && resp.data.success) {
      success.value = 'Leave request submitted successfully!'
      await loadBalance()
      await loadHistory()
      leaveType.value = ''
      startDate.value = ''
      days.value = 1
      reason.value = ''
    } else {
      error.value = resp.data?.error || 'Failed to submit leave request.'
    }
  } catch (e) {
    console.error('Submit leave error', e)
    error.value = e.response?.data?.error || e.message || 'Failed to submit leave request.'
  } finally {
    submitting.value = false
  }
}

async function deleteLeave(rec) {
  if (!confirm('Delete this leave request? This cannot be undone.')) return
  try {
    const resp = await axios.delete(`/api/leave/${rec.id}`, { headers: { Authorization: `Bearer ${getAuthToken()}` } })
    if (resp.data && resp.data.success) {
      success.value = resp.data.message || 'Leave deleted successfully.'
      await loadBalance()
      await loadHistory()
    } else {
      error.value = resp.data?.error || 'Failed to delete leave.'
    }
  } catch (e) {
    console.error('Delete leave error', e)
    error.value = e.response?.data?.error || e.message || 'Failed to delete leave.'
  }
}

// auto-clear messages after 3 seconds with watchers
watch(error, (val) => {
  if (val) {
    if (errorTimer) clearTimeout(errorTimer)
    errorTimer = setTimeout(() => {
      error.value = ''
      errorTimer = null
    }, 3000)
  }
})

watch(success, (val) => {
  if (val) {
    if (successTimer) clearTimeout(successTimer)
    successTimer = setTimeout(() => {
      success.value = ''
      successTimer = null
    }, 3000)
  }
})

onUnmounted(() => {
  if (errorTimer) clearTimeout(errorTimer)
  if (successTimer) clearTimeout(successTimer)
})

function formatDate(d) {
  if (!d) return 'N/A'
  try {
    return new Date(d).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch (e) {
    return d
  }
}

function formatStatus(status) {
  const statusMap = {
    'pending': 'Pending',
    'approved': 'Approved',
    'rejected': 'Rejected',
    'cancelled': 'Cancelled'
  }
  return statusMap[status] || status
}

function getStatusClass(status) {
  const classMap = {
    'Pending': 'status-pending',
    'Approved': 'status-approved',
    'Rejected': 'status-rejected',
    'cancelled': 'status-cancelled'
  }
  return classMap[status] || 'status-default'
}

function getTypeClass(type) {
  const classMap = {
    'Sick': 'type-sick',
    'Casual': 'type-casual',
    'LOP': 'type-lop'
  }
  return classMap[type] || 'type-default'
}

onMounted(async () => {
  await loadUser()
  await Promise.all([loadLeaveTypes(), loadBalance(), loadHistory()])
})
</script>

<style scoped>
.leave-page {
  padding: 0;
  max-width: 100%;
}

/* Page Header */
.page-header {
  margin-bottom: 30px;
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

/* Form Section */
.job-selection-section {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #ecf0f1;
}

.btn-reject {
  background: #e74c3c;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.section-title h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.section-title i {
  color: #3498db;
  font-size: 1.2rem;
}

.form-group {
  margin-bottom: 20px;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.job-select {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  color: #2c3e50;
  background: white;
  transition: all 0.3s ease;
  max-width: -moz-available;
}

.job-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.helper-note {
  margin-top: 8px;
  color: #7f8c8d;
  font-size: 0.9rem;
}

textarea.job-select {
  resize: vertical;
  font-family: inherit;
  max-width: -moz-available;
}

.form-actions {
  margin-top: 25px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Messages */
.error-message,
.success-message {
  margin-top: 15px;
  padding: 12px 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  border-left: 4px solid #c62828;
}

.success-message {
  background: #e8f5e9;
  color: #2e7d32;
  border-left: 4px solid #2e7d32;
}

/* Results Section */
.results-section {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #ecf0f1;
}

.section-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-stats {
  display: flex;
  gap: 10px;
}

.stat-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.stat-badge.total {
  background: #3498db;
  color: white;
}

/* Balance Cards */
.balance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.balance-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 15px;
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.balance-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.balance-card.sick {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.balance-card.casual {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.balance-card.lop {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.balance-icon {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.balance-info {
  flex: 1;
}

.balance-info strong {
  display: block;
  font-size: 0.9rem;
  opacity: 0.9;
  margin-bottom: 5px;
}

.balance-value {
  font-size: 1.8rem;
  font-weight: 700;
}

/* Loading and Empty States */
.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.loading-state i,
.empty-state i {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
  color: #bdc3c7;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.empty-state p {
  font-size: 1rem;
  line-height: 1.6;
}

/* Table */
.table-container {
  overflow-x: auto;
}

.candidates-table {
  width: 100%;
  border-collapse: collapse;
}

.candidates-table thead {
  background: #f8f9fa;
}

.candidates-table th {
  padding: 15px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #ecf0f1;
  white-space: nowrap;
}

.candidates-table td {
  padding: 15px;
  border-bottom: 1px solid #ecf0f1;
  vertical-align: middle;
}

.candidates-table tbody tr:hover {
  background: #f8f9fa;
}

/* Table Cell Styles */
.date-cell,
.days-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2c3e50;
}

.date-cell i,
.days-cell i {
  color: #7f8c8d;
}

.reason-cell {
  color: #2c3e50;
  max-width: 300px;
  line-height: 1.5;
}

/* Type Badges */
.type-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-block;
}

.type-sick {
  background: #ffebee;
  color: #c62828;
}

.type-casual {
  background: #e3f2fd;
  color: #1976d2;
}

.type-lop {
  background: #fff3e0;
  color: #f57c00;
}

.type-default {
  background: #f5f5f5;
  color: #616161;
}

/* Status Badges */
.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-block;
}

.status-pending {
  background: #fff3e0;
  color: #f57c00;
}

.status-approved {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-rejected {
  background: #ffebee;
  color: #c62828;
}

.status-cancelled {
  background: #f5f5f5;
  color: #616161;
}

.status-default {
  background: #fff3e0;
  color: #f57c00;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content h1 {
    font-size: 2rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .balance-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .balance-value {
    font-size: 1.5rem;
  }

  .candidates-table {
    font-size: 0.9rem;
  }
}

/* Fade transition for messages */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.35s ease, transform 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
  transform: translateY(0);
}
</style>