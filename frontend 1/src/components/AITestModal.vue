<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-container ai-test-modal" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <h3>
          <i class="fas fa-magic"></i>
          AI Technical Test - {{ candidate?.name }}
        </h3>
        <button @click="$emit('close')" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <!-- Modal Body -->
      <div class="modal-body">
        <form @submit.prevent="generateTest" class="test-form">
          <!-- Candidate Info -->
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
          </div>

          <!-- Job Details (Auto-filled) -->
          <div class="form-group">
            <label class="form-label">
              <i class="fas fa-briefcase"></i>
              Job Title
            </label>
            <input 
              v-model="testData.job_title" 
              type="text" 
              class="form-input" 
              readonly
            />
          </div>

          <div class="form-group">
            <label class="form-label">
              <i class="fas fa-align-left"></i>
              Job Description
            </label>
            <textarea 
              v-model="testData.job_description" 
              class="form-textarea"
              readonly
              rows="4"
            ></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">
              <i class="fas fa-list-check"></i>
              Requirements
            </label>
            <textarea 
              v-model="testData.job_requirements" 
              class="form-textarea"
              readonly
              rows="3"
            ></textarea>
          </div>

          <!-- Test Configuration -->
          <div class="form-row">
            <div class="form-group">
              <label class="form-label required">
                <i class="fas fa-clock"></i>
                Test Duration (minutes)
              </label>
              <select v-model="testData.duration" required class="form-select">
                <option value="30">30 minutes</option>
                <option value="45">45 minutes</option>
                <option value="60">60 minutes</option>
                <option value="90">90 minutes</option>
                <option value="120">120 minutes</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label required">
                <i class="fas fa-calendar-alt"></i>
                Test Deadline
              </label>
              <input 
                v-model="testData.deadline" 
                type="datetime-local" 
                required 
                class="form-input"
                :min="minDateTime"
              />
            </div>
          </div>

          <!-- Question Distribution -->
          <div class="question-distribution">
            <h4><i class="fas fa-chart-pie"></i> Question Distribution</h4>
            <div class="distribution-grid">
              <div class="distribution-item">
                <label>Easy Questions:</label>
                <span class="count">3</span>
              </div>
              <div class="distribution-item">
                <label>Medium Questions:</label>
                <span class="count">3</span>
              </div>
              <div class="distribution-item">
                <label>Hard Questions:</label>
                <span class="count">10</span>
              </div>
              <div class="distribution-item total">
                <label>Total Questions:</label>
                <span class="count">16</span>
              </div>
            </div>
          </div>

          <!-- Instructions -->
          <div class="form-group">
            <label class="form-label">
              <i class="fas fa-info-circle"></i>
              Additional Instructions (Optional)
            </label>
            <textarea 
              v-model="testData.instructions" 
              class="form-textarea"
              placeholder="Any specific instructions for the candidate..."
              rows="2"
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
        <button @click="$emit('close')" type="button" class="btn-secondary" :disabled="generating">
          Cancel
        </button>
        <button @click="generateTest" type="submit" class="btn-primary" :disabled="generating || !isFormValid">
          <i class="fas fa-spinner fa-spin" v-if="generating"></i>
          <i class="fas fa-magic" v-else></i>
          {{ generating ? 'Generating Test...' : 'Generate & Schedule Test' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

const props = defineProps({
  candidate: {
    type: Object,
    required: true
  },
  jobDetails: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'testGenerated'])

// Form State
const testData = ref({
  job_title: '',
  job_description: '',
  job_requirements: '',
  duration: 60,
  deadline: '',
  instructions: ''
})

const generating = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Computed
const minDateTime = computed(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toISOString().slice(0, 16)
})

const isFormValid = computed(() => {
  return testData.value.duration && testData.value.deadline
})

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

// Watch for jobDetails changes and update form
watch(() => props.jobDetails, (newJobDetails) => {
  if (newJobDetails) {
    testData.value.job_title = newJobDetails.title || ''
    testData.value.job_description = newJobDetails.description || ''
    testData.value.job_requirements = newJobDetails.requirements || ''
  }
}, { immediate: true })

// Generate Test
async function generateTest() {
  if (!isFormValid.value) {
    errorMessage.value = 'Please fill in all required fields'
    return
  }

  try {
    generating.value = true
    errorMessage.value = ''
    successMessage.value = ''

    console.log('🤖 Generating AI test for job:', props.jobDetails.id)

    // Step 1: Generate interview questions using AI
    const questionsResponse = await axios.get(`/api/ai/interview_questions/${props.jobDetails.id}`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (!questionsResponse.data?.interview_questions) {
      throw new Error('Failed to generate test questions')
    }

    const questions = questionsResponse.data.interview_questions
    console.log('📝 Generated questions:', questions)

    // Step 2: Create test assignment record
    const testAssignment = {
      candidate_id: props.candidate.id,
      job_id: props.jobDetails.id,
      test_type: 'ai_technical_test',
      questions: JSON.stringify(questions),
      duration_minutes: testData.value.duration,
      deadline: testData.value.deadline,
      instructions: testData.value.instructions || 'Complete all questions to the best of your ability.',
      status: 'scheduled',
      created_by: getCurrentUserId()
    }

    // Step 3: Save test (you'll need to create this endpoint)
    const saveResponse = await axios.post('/api/ai/schedule-test', testAssignment, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (saveResponse.data) {
      successMessage.value = 'AI test generated and scheduled successfully!'
      
      setTimeout(() => {
        emit('testGenerated', {
          test_id: saveResponse.data.test_id,
          candidate_id: props.candidate.id,
          questions_count: questions.length,
          deadline: testData.value.deadline
        })
        emit('close')
      }, 2000)
    }

  } catch (error) {
    console.error('❌ Failed to generate AI test:', error)
    errorMessage.value = error.response?.data?.error || 'Failed to generate test. Please try again.'
  } finally {
    generating.value = false
  }
}

function getCurrentUserId() {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  return user.id || localStorage.getItem('user_id') || null
}


onMounted(() => {

  if (props.jobDetails) {
    testData.value.job_title = props.jobDetails.title || ''
    testData.value.job_description = props.jobDetails.description || ''
    testData.value.job_requirements = props.jobDetails.requirements || ''
  }
  

  const defaultDeadline = new Date()
  defaultDeadline.setDate(defaultDeadline.getDate() + 3)
  testData.value.deadline = defaultDeadline.toISOString().slice(0, 16)
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

.modal-container.ai-test-modal {
  background: white;
  border-radius: 16px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  animation: slideUp 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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

/* Form Groups */
.test-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
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

.form-input:read-only,
.form-textarea:read-only {
  background: #f8f9fa;
  color: #7f8c8d;
}

.form-select {
  cursor: pointer;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

/* Question Distribution */
.question-distribution {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 12px;
  border-left: 4px solid #27ae60;
}

.question-distribution h4 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.distribution-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.distribution-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #ecf0f1;
}

.distribution-item.total {
  background: #e8f5e9;
  border-color: #27ae60;
  font-weight: 700;
}

.distribution-item label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.distribution-item .count {
  color: #2c3e50;
  font-weight: 700;
  font-size: 1.1rem;
}

.distribution-item.total .count {
  color: #27ae60;
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
  .modal-container.ai-test-modal {
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

  .form-row {
    grid-template-columns: 1fr;
  }

  .distribution-grid {
    grid-template-columns: 1fr;
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