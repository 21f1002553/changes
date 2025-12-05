<template>
  <DashboardLayout ref="layoutRef">
    <div class="hr-leave-page">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>
            <i class="fas fa-user-shield"></i>
            HR - Leave Requests
          </h1>
          <p>Review and act on leave requests submitted by employees</p>
        </div>
      </div>

      <!-- Leave Requests Section -->
      <div class="results-section">
        <div class="section-header">
          <h3>
            <i class="fas fa-list"></i>
            Applied Leaves
          </h3>
          <div class="filter-stats">
            <span class="stat-badge pending">Pending: {{ pendingCount }}</span>
            <span class="stat-badge approved">Approved: {{ approvedCount }}</span>
            <span class="stat-badge rejected">Rejected: {{ rejectedCount }}</span>
          </div>
        </div>

        <!-- Loading / Empty / Requests -->
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading leave requests...</p>
        </div>

        <div v-else-if="pendingRequests.length === 0" class="empty-state">
          <i class="fas fa-inbox"></i>
          <h3>No Pending Leave Requests</h3>
          <p>There are no pending leave requests at the moment.</p>
        </div>

        <!-- Requests Table -->
        <div v-else class="table-container">
          <table class="requests-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Employee</th>
                <th>Type</th>
                <th>Days</th>
                <th>Reason</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="req in pendingRequests" :key="req.id">
                <td>
                  <div class="date-cell">
                    <i class="fas fa-calendar-day"></i>
                    {{ formatDate(req.date) }}
                  </div>
                </td>
                <td>
                  <div class="employee-info">
                    <div class="employee-avatar">
                      {{ getInitials(req.employee_name || req.employee) }}
                    </div>
                    <span class="employee-name">{{ req.employee_name || req.employee || 'N/A' }}</span>
                  </div>
                </td>
                <td>
                  <span class="type-badge" :class="getTypeClass(req.leave_type)">
                    {{ req.leave_type }}
                  </span>
                </td>
                <td>
                  <div class="days-cell">
                    <i class="fas fa-clock"></i>
                    {{ req.days }} {{ req.days === 1 ? 'day' : 'days' }}
                  </div>
                </td>
                <td>
                  <div class="reason-cell">{{ req.reason || 'N/A' }}</div>
                </td>
                <td>
                  <span class="status-badge" :class="getStatusClass(req.status)">
                    {{ formatStatus(req.status) }}
                  </span>
                </td>
                <td>
                  <div class="actions" v-if="editingAdjustId !== req.id">
                    <button class="btn-approve" :disabled="actionLoading[req.id] || req.status !== 'Pending'"
                      @click="approveLeave(req)"
                      :title="req.status !== 'Pending' ? 'Already processed' : 'Approve leave'">
                      <i class="fas fa-check"></i>
                      Approve
                    </button>

                    <button class="btn-reject" :disabled="actionLoading[req.id] || req.status !== 'Pending'"
                      @click="rejectLeave(req)"
                      :title="req.status !== 'Pending' ? 'Already processed' : 'Reject leave'">
                      <i class="fas fa-times"></i>
                      Reject
                    </button>
                  </div>

                  <!-- Adjust Form (inline) -->
                  <div v-if="editingAdjustId === req.id" class="adjust-form">
                    <div class="adjust-header">
                      <h4>
                        <i class="fas fa-edit"></i>
                        Adjust Leave Details
                      </h4>
                    </div>

                    <div class="adjust-content">
                      <div class="form-group-inline">
                        <label for="adjust-type">
                          <i class="fas fa-tag"></i>
                          Leave Type
                        </label>
                        <select id="adjust-type" v-model="adjustForm.leave_type" class="small-input">
                          <option>Sick</option>
                          <option>Casual</option>
                          <option>LOP</option>
                        </select>
                      </div>

                      <div class="form-row-inline">
                        <div class="form-group-inline">
                          <label for="adjust-days">
                            <i class="fas fa-clock"></i>
                            Days
                          </label>
                          <input id="adjust-days" type="number" step="0.5" min="0" v-model.number="adjustForm.days"
                            class="small-input" />
                        </div>

                        <div class="form-group-inline">
                          <label for="adjust-date">
                            <i class="fas fa-calendar"></i>
                            Date
                          </label>
                          <input id="adjust-date" type="date" v-model="adjustForm.date" class="small-input" />
                        </div>
                      </div>

                      <div class="form-group-inline">
                        <label for="adjust-reason">
                          <i class="fas fa-comment"></i>
                          Reason
                        </label>
                        <input id="adjust-reason" type="text" v-model="adjustForm.reason" class="small-input"
                          placeholder="Enter adjustment reason..." />
                      </div>

                      <div class="adjust-actions">
                        <button class="btn-primary-adjust" @click="submitAdjust(req)" :disabled="adjustLoading">
                          <i class="fas" :class="adjustLoading ? 'fa-spinner fa-spin' : 'fa-check'"></i>
                          {{ adjustLoading ? 'Applying...' : 'Apply Adjustment' }}
                        </button>
                        <button class="btn-cancel" @click="closeAdjust">
                          <i class="fas fa-times"></i>
                          Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Messages -->
      <transition name="fade">
        <div v-if="error" class="error-message" key="hr-error">
          <i class="fas fa-exclamation-circle"></i>
          {{ error }}
        </div>
      </transition>
      <transition name="fade">
        <div v-if="success" class="success-message" key="hr-success">
          <i class="fas fa-check-circle"></i>
          {{ success }}
        </div>
      </transition>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const layoutRef = ref(null)
const requests = ref([])
const loading = ref(false)
const actionLoading = ref({})
const error = ref('')
const success = ref('')
const adjustForm = ref({ leave_type: 'Sick', days: 0, date: '', reason: '' })
const editingAdjustId = ref(null)
const adjustLoading = ref(false)

const getAuthToken = () => localStorage.getItem('access_token')

// Computed counts
const pendingCount = computed(() => {
  return requests.value.filter(r =>
    r.status === 'Pending' || r.status === 'pending'
  ).length
})

const approvedCount = computed(() => {
  return requests.value.filter(r =>
    r.status === 'Approved' || r.status === 'approved'
  ).length
})

const rejectedCount = computed(() => {
  return requests.value.filter(r =>
    r.status === "Rejected" || r.status === "rejected"
  ).length
})

const pendingRequests = computed(() => {
  return requests.value.filter(r => r.status === 'Pending' || r.status === 'pending')
})

async function loadRequests() {
  loading.value = true
  try {
    const resp = await axios.get('/api/leave/history', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    if (resp.data && resp.data.data) { requests.value = resp.data.data }
    else if (Array.isArray(resp.data)) requests.value = resp.data
    else requests.value = []
  } catch (e) {
    console.error('Failed to load leave requests', e)
    error.value = e.response?.data?.error || e.message || 'Failed to load leave requests.'
  } finally {
    loading.value = false
  }
}

function getInitials(name) {
  if (!name) return '?'
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
}

function formatDate(d) {
  if (!d) return 'N/A'
  try {
    return new Date(d).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch {
    return d
  }
}

function formatStatus(status) {
  const map = {
    'Pending': 'Pending',
    'pending': 'Pending',
    'Approved': 'Approved',
    'approved': 'Approved',
    'Rejected': 'Rejected',
    'rejected': 'Rejected'
  }
  return map[status] || status || 'N/A'
}

function getStatusClass(status) {
  const map = {
    'Pending': 'status-pending',
    'pending': 'status-pending',
    'Approved': 'status-approved',
    'approved': 'status-approved',
    'Rejected': 'status-rejected',
    'rejected': 'status-rejected'
  }
  return map[status] || 'status-default'
}

function getTypeClass(type) {
  const classMap = {
    'Sick': 'type-sick',
    'Casual': 'type-casual',
    'LOP': 'type-lop'
  }
  return classMap[type] || 'type-default'
}

async function approveLeave(req) {
  if (!confirm(`Approve leave request for ${req.employee_name || req.employee}?`)) return
  actionLoading.value = { ...actionLoading.value, [req.id]: true }
  try {
    const resp = await axios.put(`/api/leave/approve/${req.id}`, {}, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    success.value = resp.data?.message || 'Leave approved successfully.'
    await loadRequests()

    // after await loadRequests()
    try {
      // existing success assignment
      success.value = resp.data?.message || 'Leave approved successfully.'
      await loadRequests()

      // trigger dashboard to refresh notification count (safe-call)
      if (layoutRef.value?.fetchLeaveNotificationsCount) {
        await layoutRef.value.fetchLeaveNotificationsCount()
      }
    } catch (e) { console.log(e) }
  } catch (e) {
    console.error('Approve error', e)
    error.value = e.response?.data?.error || e.message || 'Failed to approve leave.'
  } finally {
    actionLoading.value = { ...actionLoading.value, [req.id]: false }
  }
}

async function rejectLeave(req) {
  if (!confirm(`Reject leave request for ${req.employee_name || req.employee}?`)) return
  actionLoading.value = { ...actionLoading.value, [req.id]: true }
  try {
    const resp = await axios.put(`/api/leave/reject/${req.id}`, {}, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    success.value = resp.data?.message || 'Leave rejected successfully.'
    await loadRequests()

    // after await loadRequests()
    try {
      // existing success assignment
      success.value = resp.data?.message || 'Leave approved successfully.'
      await loadRequests()

      // trigger dashboard to refresh notification count (safe-call)
      if (layoutRef.value?.fetchLeaveNotificationsCount) {
        await layoutRef.value.fetchLeaveNotificationsCount()
      }
    } catch (e) { console.log(e) }
  } catch (e) {
    console.error('Reject error', e)
    error.value = e.response?.data?.error || e.message || 'Failed to reject leave.'
  } finally {
    actionLoading.value = { ...actionLoading.value, [req.id]: false }
  }
}

function openAdjust(req) {
  editingAdjustId.value = req.id
  adjustForm.value.leave_type = req.leave_type || 'Sick'

  // Normalize date to yyyy-mm-dd
  try {
    const d = new Date(req.date)
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    adjustForm.value.date = `${y}-${m}-${day}`
  } catch {
    adjustForm.value.date = ''
  }

  adjustForm.value.days = req.days || 0
  adjustForm.value.reason = ''
}

function closeAdjust() {
  editingAdjustId.value = null
}

async function submitAdjust(req) {
  if (!adjustForm.value.leave_type || !adjustForm.value.date) {
    error.value = 'Please fill leave type and date.'
    return
  }

  adjustLoading.value = true
  try {
    const payload = {
      employee_id: req.employee_id || req.employee || req.employeeId,
      leave_type: adjustForm.value.leave_type,
      days: adjustForm.value.days,
      date: adjustForm.value.date,
      reason: adjustForm.value.reason
    }
    const resp = await axios.post('/api/leave/adjust', payload, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    success.value = resp.data?.data?.message || resp.data?.message || 'Adjustment applied successfully.'
    await loadRequests()
    closeAdjust()
  } catch (e) {
    console.error('Adjust error', e)
    error.value = e.response?.data?.error || e.message || 'Failed to apply adjustment.'
  } finally {
    adjustLoading.value = false
  }
}

// Auto-dismiss messages
let errTimer = null
let okTimer = null

watch(error, (v) => {
  if (v) {
    if (errTimer) clearTimeout(errTimer)
    errTimer = setTimeout(() => {
      error.value = ''
      errTimer = null
    }, 5000)
  }
})

watch(success, (v) => {
  if (v) {
    if (okTimer) clearTimeout(okTimer)
    okTimer = setTimeout(() => {
      success.value = ''
      okTimer = null
    }, 5000)
  }
})

onUnmounted(() => {
  if (errTimer) clearTimeout(errTimer)
  if (okTimer) clearTimeout(okTimer)
})

onMounted(async () => {
  await loadRequests()
})
</script>

<style scoped>
.hr-leave-page {
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

/* Results Section */
.results-section {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
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
  flex-wrap: wrap;
}

.stat-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.stat-badge.pending {
  background: #f39c12;
  color: white;
}

.stat-badge.approved {
  background: #27ae60;
  color: white;
}

.stat-badge.rejected {
  background: #E74C3C;
  color: white;
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

.requests-table {
  width: 100%;
  border-collapse: collapse;
}

.requests-table thead {
  background: #f8f9fa;
}

.requests-table th {
  padding: 15px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #ecf0f1;
  white-space: nowrap;
}

.requests-table td {
  padding: 15px;
  border-bottom: 1px solid #ecf0f1;
  vertical-align: top;
}

.requests-table tbody tr:hover {
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

/* Employee Info */
.employee-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.employee-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
}

.employee-name {
  font-weight: 600;
  color: #2c3e50;
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

.reason-cell {
  color: #2c3e50;
  max-width: 300px;
  line-height: 1.5;
  word-wrap: break-word;
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

.status-default {
  background: #e3f2fd;
  color: #1976d2;
}

/* Action Buttons */
.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-approve,
.btn-reject,
.btn-adjust {
  padding: 8px 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
  transition: all 0.3s ease;
}

.btn-approve {
  background: #27ae60;
}

.btn-approve:hover:not(:disabled) {
  background: #229954;
  transform: translateY(-1px);
}

.btn-reject {
  background: #e74c3c;
}

.btn-reject:hover:not(:disabled) {
  background: #c0392b;
  transform: translateY(-1px);
}

.btn-adjust {
  background: #f39c12;
}

.btn-adjust:hover {
  background: #e67e22;
  transform: translateY(-1px);
}

.btn-approve:disabled,
.btn-reject:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Adjust Form */
.adjust-form {
  margin-top: 15px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 10px;
  border: 2px solid #e3f2fd;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.adjust-header {
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e3f2fd;
}

.adjust-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.adjust-header i {
  color: #3498db;
}

.adjust-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group-inline {
  display: flex;
  flex-direction: column;
}

.form-group-inline label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.form-group-inline i {
  color: #7f8c8d;
  font-size: 0.85rem;
}

.form-row-inline {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.small-input {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #ecf0f1;
  border-radius: 6px;
  font-size: 0.95rem;
  color: #2c3e50;
  background: white;
  transition: all 0.3s ease;
}

.small-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.adjust-actions {
  display: flex;
  gap: 10px;
  margin-top: 5px;
}

.btn-primary-adjust {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-primary-adjust:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary-adjust:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-cancel {
  background: #ecf0f1;
  color: #2c3e50;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-cancel:hover {
  background: #bdc3c7;
}

/* Messages */
.error-message,
.success-message {
  position: fixed;
  top: 20px;
  right: 20px;
  max-width: 400px;
  padding: 15px 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.95rem;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
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

.error-message i,
.success-message i {
  font-size: 1.2rem;
}

/* Fade Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.35s ease, transform 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
  transform: translateY(0);
}

/* Responsive */
@media (max-width: 1200px) {
  .requests-table {
    font-size: 0.85rem;
  }

  .reason-cell {
    max-width: 200px;
  }
}

@media (max-width: 768px) {
  .header-content h1 {
    font-size: 2rem;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .filter-stats {
    width: 100%;
    justify-content: space-between;
  }

  .form-row-inline {
    grid-template-columns: 1fr;
  }

  .actions {
    flex-direction: column;
  }

  .adjust-actions {
    flex-direction: column;
  }

  .reason-cell {
    max-width: 150px;
  }

  .error-message,
  .success-message {
    max-width: 90%;
    right: 5%;
  }
}
</style>