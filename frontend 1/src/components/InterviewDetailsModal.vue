<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-container interview-details-modal" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <h3>
          <i class="fas fa-calendar-check"></i>
          Interview Details
        </h3>
        <button @click="$emit('close')" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <!-- Modal Body -->
      <div class="modal-body">
        <!-- Candidate Info Section -->
        <div class="candidate-info-banner">
          <div class="candidate-avatar-large">
            {{ getInitials(candidate?.name) }}
          </div>
          <div class="candidate-details">
            <h2>{{ candidate?.name }}</h2>
            <p class="job-title">{{ candidate?.job_title }}</p>
            <div class="contact-info">
              <span><i class="fas fa-envelope"></i> {{ candidate?.email }}</span>
            </div>
          </div>
          <div class="match-score-badge" :class="getScoreClass(candidate?.score)">
            <div class="score-number">{{ candidate?.score || 'N/A' }}%</div>
            <div class="score-label">Match Score</div>
          </div>
        </div>

        <!-- Interview Assignment Details -->
        <div class="interview-details-section">
          <h4><i class="fas fa-clipboard-list"></i> Interview Information</h4>
          
          <div class="detail-grid">
            <!-- Interview Type -->
            <div class="detail-item">
              <label>Interview Type:</label>
              <span class="interview-type-badge" :class="getInterviewTypeClass(interviewAssignment?.interview_type)">
                <i :class="getInterviewTypeIcon(interviewAssignment?.interview_type)"></i>
                {{ formatInterviewType(interviewAssignment?.interview_type) }}
              </span>
            </div>

            <!-- Interviewer -->
            <div class="detail-item">
              <label>Interviewer:</label>
              <span class="interviewer-name">
                <i class="fas fa-user-tie"></i>
                {{ interviewAssignment?.interviewer_name || 'Not Assigned' }}
              </span>
            </div>

            <!-- Status -->
            <div class="detail-item">
              <label>Status:</label>
              <span class="status-badge" :class="interviewAssignment?.status">
                <i :class="getStatusIcon(interviewAssignment?.status)"></i>
                {{ formatInterviewStatus(interviewAssignment?.status) }}
              </span>
            </div>

            <!-- Scheduled Date & Time -->
            <div class="detail-item" v-if="interviewAssignment?.scheduled_at">
              <label>Scheduled:</label>
              <span class="datetime">
                <i class="fas fa-calendar"></i>
                {{ formatDateTime(interviewAssignment.scheduled_at) }}
              </span>
            </div>

            <!-- Duration -->
            <div class="detail-item" v-if="interviewAssignment?.duration">
              <label>Duration:</label>
              <span>
                <i class="fas fa-clock"></i>
                {{ interviewAssignment.duration }} minutes
              </span>
            </div>

            <!-- Assigned Date -->
            <div class="detail-item" v-if="interviewAssignment?.assigned_at">
              <label>Assigned On:</label>
              <span>
                <i class="fas fa-calendar-plus"></i>
                {{ formatDate(interviewAssignment.assigned_at) }}
              </span>
            </div>
          </div>

          <!-- Meeting Link -->
          <div v-if="interviewAssignment?.meeting_link" class="meeting-link-section">
            <label><i class="fas fa-video"></i> Meeting Link:</label>
            <a :href="interviewAssignment.meeting_link" target="_blank" class="meeting-link">
              {{ interviewAssignment.meeting_link }}
              <i class="fas fa-external-link-alt"></i>
            </a>
          </div>
        </div>

        <!-- Stage Information -->
        <div class="stage-info-section">
          <h4><i class="fas fa-stream"></i> Pipeline Stage</h4>
          <div class="stage-details">
            <div class="current-stage">
              <label>Current Stage:</label>
              <span class="stage-name">{{ stage?.name }}</span>
            </div>
            <div class="time-in-stage">
              <label>Time in Stage:</label>
              <span>{{ getDaysInStage(candidate?.entered_at) }} days</span>
            </div>
          </div>
        </div>

        <!-- Additional Actions -->
        <div class="quick-actions">
          <button @click="viewResume" class="action-btn btn-resume">
            <i class="fas fa-file-pdf"></i>
            View Resume
          </button>
          <button 
            v-if="interviewAssignment?.status === 'completed'" 
            @click="viewScorecard" 
            class="action-btn btn-scorecard"
          >
            <i class="fas fa-chart-bar"></i>
            View Scorecard
          </button>
          <button 
            v-if="canReschedule" 
            @click="rescheduleInterview" 
            class="action-btn btn-reschedule"
          >
            <i class="fas fa-calendar-alt"></i>
            Reschedule
          </button>
        </div>

        <!-- Notes Section (if any) -->
        <div v-if="interviewAssignment?.notes" class="notes-section">
          <h4><i class="fas fa-sticky-note"></i> Notes</h4>
          <div class="notes-content">
            {{ interviewAssignment.notes }}
          </div>
        </div>
      </div>
      
      <!-- Modal Footer -->
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn-secondary">
          Close
        </button>
        <button 
          v-if="canEdit" 
          @click="editInterview" 
          class="btn-primary"
        >
          <i class="fas fa-edit"></i>
          Edit Details
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  candidate: {
    type: Object,
    required: true
  },
  stage: {
    type: Object,
    required: true
  },
  interviewAssignment: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'viewResume', 'viewScorecard', 'reschedule', 'edit'])

// Computed
const canReschedule = computed(() => {
  return props.interviewAssignment?.status === 'scheduled'
})

const canEdit = computed(() => {
  return props.interviewAssignment?.status !== 'completed' && 
         props.interviewAssignment?.status !== 'cancelled'
})

// Helper Functions
function getInitials(name) {
  if (!name) return '?'
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
}

function getScoreClass(score) {
  if (!score) return 'score-na'
  if (score >= 90) return 'score-excellent'
  if (score >= 75) return 'score-good'
  if (score >= 60) return 'score-average'
  return 'score-poor'
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

function formatInterviewStatus(status) {
  const statusMap = {
    'scheduled': 'Scheduled',
    'completed': 'Completed',
    'cancelled': 'Cancelled',
    'rescheduled': 'Rescheduled'
  }
  return statusMap[status] || status
}

function getInterviewTypeClass(type) {
  const classMap = {
    'technical_assessment': 'type-technical',
    'technical_interview': 'type-technical',
    'behavioral_interview': 'type-behavioral',
    'communication_interview': 'type-communication'
  }
  return classMap[type] || 'type-default'
}

function getInterviewTypeIcon(type) {
  const iconMap = {
    'technical_assessment': 'fas fa-code',
    'technical_interview': 'fas fa-laptop-code',
    'behavioral_interview': 'fas fa-users',
    'communication_interview': 'fas fa-comments'
  }
  return iconMap[type] || 'fas fa-clipboard-list'
}

function getStatusIcon(status) {
  const iconMap = {
    'scheduled': 'fas fa-calendar-check',
    'completed': 'fas fa-check-circle',
    'cancelled': 'fas fa-times-circle',
    'rescheduled': 'fas fa-calendar-alt'
  }
  return iconMap[status] || 'fas fa-question-circle'
}

function formatDateTime(dateString) {
  if (!dateString) return 'Not scheduled'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function getDaysInStage(enteredAt) {
  if (!enteredAt) return 0
  const entered = new Date(enteredAt)
  const now = new Date()
  const diffTime = Math.abs(now - entered)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

// Action Functions
function viewResume() {
  emit('viewResume', props.candidate)
}

function viewScorecard() {
  emit('viewScorecard', props.candidate)
}

function rescheduleInterview() {
  emit('reschedule', props.interviewAssignment)
}

function editInterview() {
  emit('edit', props.interviewAssignment)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-container.interview-details-modal {
  background: white;
  border-radius: 16px;
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Modal Header */
.modal-header {
  padding: 24px 28px;
  border-bottom: 2px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.close-btn {
  background: rgba(255,255,255,0.2);
  border: none;
  font-size: 1.5rem;
  color: white;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255,255,255,0.3);
  transform: rotate(90deg);
}

/* Modal Body */
.modal-body {
  padding: 0;
  overflow-y: auto;
  flex: 1;
}

/* Candidate Info Banner */
.candidate-info-banner {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ebf0 100%);
  padding: 28px;
  display: flex;
  align-items: center;
  gap: 20px;
  border-bottom: 2px solid #ecf0f1;
}

.candidate-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 2rem;
  flex-shrink: 0;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.candidate-details {
  flex: 1;
}

.candidate-details h2 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 1.6rem;
  font-weight: 700;
}

.job-title {
  margin: 0 0 12px 0;
  color: #7f8c8d;
  font-size: 1.1rem;
  font-weight: 500;
}

.contact-info {
  display: flex;
  gap: 20px;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.contact-info i {
  margin-right: 6px;
  color: #667eea;
}

.match-score-badge {
  text-align: center;
  padding: 15px 20px;
  border-radius: 12px;
  min-width: 100px;
}

.score-number {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}

.score-label {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  opacity: 0.8;
}

.match-score-badge.score-excellent {
  background: #c8e6c9;
  color: #2e7d32;
}

.match-score-badge.score-good {
  background: #e8f5e9;
  color: #388e3c;
}

.match-score-badge.score-average {
  background: #fff3e0;
  color: #f57c00;
}

.match-score-badge.score-poor {
  background: #ffebee;
  color: #c62828;
}

.match-score-badge.score-na {
  background: #f5f5f5;
  color: #95a5a6;
}

/* Interview Details Section */
.interview-details-section,
.stage-info-section,
.notes-section {
  padding: 28px;
  border-bottom: 1px solid #ecf0f1;
}

.interview-details-section h4,
.stage-info-section h4,
.notes-section h4 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 1.1rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
}

.interview-details-section h4 i,
.stage-info-section h4 i,
.notes-section h4 i {
  color: #667eea;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item label {
  font-size: 0.85rem;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
}

.detail-item span {
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.interview-type-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
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

.interviewer-name {
  font-weight: 600;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.85rem;
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
  background: #ffebee;
  color: #c62828;
}

.status-badge.rescheduled {
  background: #e3f2fd;
  color: #1976d2;
}

.datetime {
  font-weight: 600;
}

/* Meeting Link */
.meeting-link-section {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.meeting-link-section label {
  display: block;
  font-size: 0.85rem;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.meeting-link {
  color: #667eea;
  font-weight: 600;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
  word-break: break-all;
  transition: all 0.3s ease;
}

.meeting-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* Stage Info */
.stage-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.current-stage,
.time-in-stage {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.current-stage label,
.time-in-stage label {
  font-size: 0.85rem;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
}

.stage-name {
  background: #667eea;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  display: inline-block;
}

/* Quick Actions */
.quick-actions {
  padding: 20px 28px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  background: #f8f9fa;
  border-bottom: 1px solid #ecf0f1;
}

.action-btn {
  flex: 1;
  min-width: 150px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.btn-resume {
  background: #f3e5f5;
  color: #7b1fa2;
}

.btn-resume:hover {
  background: #e1bee7;
  transform: translateY(-2px);
}

.btn-scorecard {
  background: #e3f2fd;
  color: #1976d2;
}

.btn-scorecard:hover {
  background: #bbdefb;
  transform: translateY(-2px);
}

.btn-reschedule {
  background: #fff3e0;
  color: #f57c00;
}

.btn-reschedule:hover {
  background: #ffe0b2;
  transform: translateY(-2px);
}

/* Notes */
.notes-content {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  color: #2c3e50;
  line-height: 1.6;
}

/* Modal Footer */
.modal-footer {
  padding: 20px 28px;
  border-top: 2px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: #f8f9fa;
  border-radius: 0 0 16px 16px;
}

.btn-secondary,
.btn-primary {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-secondary:hover {
  background: #bdc3c7;
  transform: translateY(-1px);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

/* Responsive */
@media (max-width: 768px) {
  .candidate-info-banner {
    flex-direction: column;
    text-align: center;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .stage-details {
    grid-template-columns: 1fr;
  }

  .quick-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .btn-secondary,
  .btn-primary {
    width: 100%;
    justify-content: center;
  }
}
</style>