<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-container interview-assignment-modal" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <h3>
          <i class="fas fa-calendar-plus"></i>
          Schedule Interview - {{ candidate?.name }}
        </h3>
        <button @click="$emit('close')" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <!-- Modal Body -->
      <div class="modal-body">
        <form @submit.prevent="handleSubmit" class="interview-form">
          <!-- Candidate Info Display -->
          <div class="candidate-info-section">
            <div class="info-row">
              <div class="info-item">
                <label>Candidate:</label>
                <span>{{ candidate?.name }}</span>
              </div>
              <div class="info-item">
                <label>Position:</label>
                <span>{{ candidate?.job_title }}</span>
              </div>
            </div>
            <div class="info-row">
              <div class="info-item">
                <label>Stage:</label>
                <span class="stage-badge">{{ stage?.name }}</span>
              </div>
              <div class="info-item">
                <label>Match Score:</label>
                <span :class="getScoreClass(candidate?.score)">{{ candidate?.score || 'N/A' }}%</span>
              </div>
            </div>
          </div>

          <!-- Interview Type Display -->
          <div class="form-group">
            <label class="form-label">
              <i class="fas fa-clipboard-list"></i>
              Interview Type
            </label>
            <div class="interview-type-display">
              {{ formatInterviewType(interviewType) }}
            </div>
          </div>

          <!-- Select Interviewer -->
          <div class="form-group">
            <label class="form-label required">
              <i class="fas fa-user-tie"></i>
              Select Interviewer
            </label>
            <select v-model="formData.interviewer_id" required class="form-select">
              <option value="">Choose an interviewer...</option>
              <option 
                v-for="interviewer in availableInterviewers" 
                :key="interviewer.id" 
                :value="interviewer.id"
              >
                {{ interviewer.name }} - {{ interviewer.role_name }}
              </option>
            </select>
          </div>

          <!-- Interview Date -->
          <div class="form-group">
            <label class="form-label required">
              <i class="fas fa-calendar"></i>
              Interview Date
            </label>
            <input 
              v-model="formData.interview_date" 
              type="date" 
              required 
              :min="minDate"
              class="form-input"
            />
          </div>

          <!-- Interview Time -->
          <div class="form-group">
            <label class="form-label required">
              <i class="fas fa-clock"></i>
              Interview Time
            </label>
            <input 
              v-model="formData.interview_time" 
              type="time" 
              required 
              class="form-input"
            />
          </div>

          <!-- Duration -->
          <div class="form-group">
            <label class="form-label required">
              <i class="fas fa-hourglass-half"></i>
              Duration (minutes)
            </label>
            <select v-model="formData.duration_minutes" required class="form-select">
              <option value="30">30 minutes</option>
              <option value="45">45 minutes</option>
              <option value="60" selected>60 minutes</option>
              <option value="90">90 minutes</option>
              <option value="120">120 minutes</option>
            </select>
          </div>

          <!-- Meeting Link (Optional) -->
          <div class="form-group">
            <label class="form-label">
              <i class="fas fa-video"></i>
              Meeting Link (Optional)
            </label>
            <input 
              v-model="formData.meeting_link" 
              type="url" 
              placeholder="https://meet.google.com/xxx or https://zoom.us/j/xxx"
              class="form-input"
            />
            <small class="form-hint">Add video conference link if interview is remote</small>
          </div>

          <!-- Notes -->
          <div class="form-group">
            <label class="form-label">
              <i class="fas fa-sticky-note"></i>
              Additional Notes
            </label>
            <textarea 
              v-model="formData.notes" 
              rows="3"
              placeholder="Any special instructions or topics to cover..."
              class="form-textarea"
            ></textarea>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            {{ errorMessage }}
          </div>

          <!-- Success Message -->
          <div v-if="successMessage" class="success-message">
            <i class="fas fa-check-circle"></i>
            {{ successMessage }}
          </div>
        </form>
      </div>
      
      <!-- Modal Footer -->
      <div class="modal-footer">
        <button @click="$emit('close')" type="button" class="btn-secondary" :disabled="submitting">
          Cancel
        </button>
        <button @click="handleSubmit" type="submit" class="btn-primary" :disabled="submitting || !isFormValid">
          <i class="fas fa-spinner fa-spin" v-if="submitting"></i>
          <i class="fas fa-check" v-else></i>
          {{ submitting ? 'Assigning...' : 'Assign Interview' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  candidate: {
    type: Object,
    required: true
  },
  stage: {
    type: Object,
    required: true
  },
  availableInterviewers: {
    type: Array,
    required: true
  },
  assigner: {
    type: Object,
    required: true
  }

})

const emit = defineEmits(['close', 'assigned'])

// Form State
const formData = ref({
  interviewer_id: '',
  interview_date: '',
  interview_time: '',
  duration_minutes: 60,
  meeting_link: '',
  notes: ''
})

const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Computed
const minDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

const interviewType = computed(() => {
  const typeMap = {
    'Technical Assessment': 'technical_assessment',
    'Technical Interview': 'technical_interview',
    'Behavioral Interview': 'behavioral_interview',
    'Final Interview': 'final_interview'
  }
  return typeMap[props.stage.name] || 'general'
})

const isFormValid = computed(() => {
  return formData.value.interviewer_id &&
         formData.value.interview_date &&
         formData.value.interview_time &&
         formData.value.duration_minutes
})

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

const getCurrentUserId = () => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  return user.id || localStorage.getItem('user_id') || null
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
    'final_interview': 'Final Interview'
  }
  return typeMap[type] || type
}

// Submit Handler
async function handleSubmit() {
  if (!isFormValid.value) {
    errorMessage.value = 'Please fill in all required fields'
    return
  }

  try {
    submitting.value = true
    errorMessage.value = ''
    successMessage.value = ''

    // Combine date and time into ISO format
    const scheduledDateTime = new Date(`${formData.value.interview_date}T${formData.value.interview_time}`)
    
    const payload = {
      candidate_id: props.candidate.id,
      job_id: props.candidate.job_id,
      interviewer_id: formData.value.interviewer_id,
      interview_type: interviewType.value,
      scheduled_at: scheduledDateTime.toISOString(),
      duration_minutes: parseInt(formData.value.duration_minutes),
      meeting_link: formData.value.meeting_link || null,
      notes: formData.value.notes || null,
      assigned_by_id: props.assigner.id
    }

    const response = await axios.post('/api/pipeline/assign-interviewer', payload, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data?.assignment) {
      successMessage.value = 'Interview assigned successfully!'
      
      // Get interviewer name
      const interviewer = props.availableInterviewers.find(i => i.id === formData.value.interviewer_id)
      
      // Emit success event with assignment details
      setTimeout(() => {
        emit('assigned', {
          ...response.data.assignment,
          interviewer_name: interviewer?.name || 'Unknown',
          candidate_id: props.candidate.id
        })
        emit('close')
      }, 1000)
    }

  } catch (error) {
    console.error('❌ Failed to assign interview:', error)
    errorMessage.value = error.response?.data?.error || 'Failed to assign interview. Please try again.'
  } finally {
    submitting.value = false
  }
}



// Initialize default date/time
onMounted(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  formData.value.interview_date = tomorrow.toISOString().split('T')[0]
  formData.value.interview_time = '10:00'
})
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

.modal-container.interview-assignment-modal {
  background: white;
  border-radius: 16px;
  max-width: 600px;
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
  padding: 28px;
  overflow-y: auto;
  flex: 1;
}

/* Candidate Info Section */
.candidate-info-section {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ebf0 100%);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  border-left: 4px solid #667eea;
}

.info-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 12px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  font-size: 0.8rem;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
}

.info-item span {
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 600;
}

.stage-badge {
  background: #667eea;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  display: inline-block;
}

.score-excellent { color: #27ae60; }
.score-good { color: #2ecc71; }
.score-average { color: #f39c12; }
.score-poor { color: #e74c3c; }
.score-na { color: #95a5a6; font-style: italic; }

/* Form Groups */
.interview-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-label.required::after {
  content: '*';
  color: #e74c3c;
  margin-left: 4px;
}

.form-label i {
  color: #667eea;
  width: 16px;
}

.interview-type-display {
  background: #e3f2fd;
  color: #1976d2;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 600;
  border-left: 4px solid #1976d2;
}

.form-input,
.form-select,
.form-textarea {
  padding: 12px 16px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  font-size: 0.95rem;
  color: #2c3e50;
  background: white;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-select {
  cursor: pointer;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-hint {
  color: #7f8c8d;
  font-size: 0.85rem;
  font-style: italic;
  margin-top: 4px;
}

/* Messages */
.error-message,
.success-message {
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.error-message {
  background: #ffebee;
  color: #c62828;
  border-left: 4px solid #e74c3c;
}

.success-message {
  background: #e8f5e9;
  color: #2e7d32;
  border-left: 4px solid #4caf50;
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

.btn-secondary:hover:not(:disabled) {
  background: #bdc3c7;
  transform: translateY(-1px);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Responsive */
@media (max-width: 768px) {
  .modal-container.interview-assignment-modal {
    max-width: 95%;
    margin: 10px;
  }

  .modal-header {
    padding: 20px;
  }

  .modal-header h3 {
    font-size: 1.2rem;
  }

  .modal-body {
    padding: 20px;
  }

  .info-row {
    grid-template-columns: 1fr;
    gap: 12px;
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