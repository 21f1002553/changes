<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <h2><i class="fas fa-paper-plane"></i> Apply for Position</h2>
        <button @click="closeModal" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <!-- Job Summary -->
        <div class="job-summary">
          <div class="company-logo">
            <img :src="job?.companyLogo || '/default-company-logo.png'" :alt="job?.company" />
          </div>
          <div class="job-info">
            <h3>{{ job?.title }}</h3>
            <p><i class="fas fa-building"></i> {{ job?.company || 'Company Name' }}</p>
            <p><i class="fas fa-map-marker-alt"></i> {{ job?.location || job?.requirements }}</p>
          </div>
        </div>

        <!-- Application Form -->
        <form @submit.prevent="submitApplication" class="application-form">
          <!-- Resume Selection -->
          <div class="form-group">
            <label for="resume">
              <i class="fas fa-file-alt"></i> Select Resume *
            </label>
            <select id="resume" v-model="formData.resumeId" required
              :disabled="loading || Object.keys(resumes).length === 0">
              <option value="">-- Select a resume --</option>
              <option v-for="(resume, id) in resumes" :key="id" :value="resume.id">
                {{ resume.filename }}
              </option>

            </select>
            <p v-if="resumes.length === 0" class="help-text error">
              <i class="fas fa-exclamation-triangle"></i>
              No resume found. Please upload a resume first.
            </p>
            <button v-if="resumes.length === 0" type="button" @click="navigateToProfile" class="upload-resume-btn">
              <i class="fas fa-upload"></i>
              Upload Resume
            </button>
          </div>

          <!-- Cover Letter -->
          <div class="form-group">
            <label for="coverLetter">
              <i class="fas fa-envelope"></i> Cover Letter *
            </label>
            <textarea id="coverLetter" v-model="formData.coverLetter"
              placeholder="Write a brief cover letter explaining why you're a great fit for this position..." rows="6"
              required :disabled="loading"></textarea>
            <p class="help-text">
              <i class="fas fa-info-circle"></i>
              {{ formData.coverLetter.length }}/1000 characters
            </p>
          </div>

          <!-- Additional Information -->
          <div class="form-group">
            <label for="additionalInfo">
              <i class="fas fa-plus-circle"></i> Additional Information (Optional)
            </label>
            <textarea id="additionalInfo" v-model="formData.additionalInfo"
              placeholder="Any additional information you'd like to share (certifications, portfolio links, etc.)"
              rows="4" :disabled="loading"></textarea>
          </div>

          <!-- Expected Salary -->
          <div class="form-group">
            <label for="expectedSalary">
              <i class="fas fa-dollar-sign"></i> Expected Salary (Optional)
            </label>
            <div class="input-group">
              <span class="input-prefix">$</span>
              <input id="expectedSalary" v-model.number="formData.expectedSalary" type="number" placeholder="50000"
                min="0" :disabled="loading" />
              <span class="input-suffix">per year</span>
            </div>
          </div>

          <!-- Availability -->
          <div class="form-group">
            <label for="availability">
              <i class="fas fa-calendar"></i> Availability *
            </label>
            <select id="availability" v-model="formData.availability" required :disabled="loading">
              <option value="">-- Select availability --</option>
              <option value="immediate">Immediate</option>
              <option value="2_weeks">2 Weeks Notice</option>
              <option value="1_month">1 Month</option>
              <option value="negotiable">Negotiable</option>
            </select>
          </div>

          <!-- Consent Checkbox -->
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="formData.consent" required :disabled="loading" />
              <span>
                I confirm that the information provided is accurate and I consent to the processing
                of my personal data for recruitment purposes.
              </span>
            </label>
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

          <!-- Submit Buttons -->
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-cancel" :disabled="loading">
              Cancel
            </button>
            <button type="submit" class="btn-submit" :disabled="loading || !formData.consent || resumes.length === 0">
              <i class="fas fa-spinner fa-spin" v-if="loading"></i>
              <i class="fas fa-paper-plane" v-else></i>
              {{ loading ? 'Submitting...' : 'Submit Application' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const props = defineProps({
  job: {
    type: Object,
    required: true
  },
  userId: {
    type: String,
    required: true,
    default: ''
  }
})

const emit = defineEmits(['close', 'application-submitted'])
const router = useRouter()

// State
const loading = ref(false)
const resumes = ref([])
const errorMessage = ref('')
const successMessage = ref('')
const uploadingResume = ref(false)

const formData = ref({
  resumeId: '',
  coverLetter: '',
  additionalInfo: '',
  expectedSalary: null,
  availability: '',
  consent: false
})

watch(() => props.userId, (newVal) => {
  console.log('JobApplicationModal - userId prop changed to:', newVal)
}, { immediate: true })

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

// API Functions

const uploadResume = async (event) => {
  try {
    const file = event.target.files[0]
    if (!file) return

    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type)) {
      errorMessage.value = 'Invalid file type. Please upload PDF or DOC/DOCX files only.'
      return
    }

    // Validate file size (16MB max)
    const maxSize = 16 * 1024 * 1024
    if (file.size > maxSize) {
      errorMessage.value = 'File size exceeds 16MB limit.'
      return
    }

    uploadingResume.value = true
    errorMessage.value = ''

    // Create FormData
    const formDataToSend = new FormData()
    formDataToSend.append('resume', file)
    formDataToSend.append('user_id', props.userId)

    // Upload using screening API
    const response = await axios.post('/api/screening/upload-resume', formDataToSend, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.resume) {
      successMessage.value = 'Resume uploaded successfully!'

      // Reload resumes list
      await loadResumes()

      // Auto-select the newly uploaded resume
      formData.value.resumeId = response.data.resume.id

      // Clear success message after 3 seconds
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    }

  } catch (error) {
    console.error('Failed to upload resume:', error)

    if (error.response?.data?.error) {
      errorMessage.value = error.response.data.error
    } else {
      errorMessage.value = 'Failed to upload resume. Please try again.'
    }
  } finally {
    uploadingResume.value = false
    // Clear file input
    event.target.value = ''
  }
}


const loadResumes = async () => {
  try {
    const response = await axios.get('/api/files/resume', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    console.log(response.data)

    if (response.data) {
      resumes.value = response.data
      console.log(resumes?.value.id)

    }
  } catch (error) {
    console.error('Failed to load resumes:', error)
    errorMessage.value = 'Failed to load resumes. Please try again.'
  }
}

const submitApplication = async () => {
  try {
    loading.value = true
    errorMessage.value = ''
    successMessage.value = ''

    // Validate form
    if (!formData.value.resumeId) {
      errorMessage.value = 'Please select a resume'
      return
    }

    if (!formData.value.coverLetter.trim()) {
      errorMessage.value = 'Please write a cover letter'
      return
    }

    if (formData.value.coverLetter.length > 1000) {
      errorMessage.value = 'Cover letter must not exceed 1000 characters'
      return
    }

    if (!formData.value.availability) {
      errorMessage.value = 'Please select your availability'
      return
    }

    if (!formData.value.consent) {
      errorMessage.value = 'Please confirm your consent'
      return
    }

    // Submit application

    const response = await axios.post('/api/applications/submit',
      {
        candidate_id: props.userId,
        job_id: props.job.job_id || props.job.id,
        resume_id: formData.value.resumeId,
        cover_letter: formData.value.coverLetter,
        expected_salary: formData.value.expectedSalary,
        availability: formData.value.availability,
        source: formData.value.additionalInfo,
        status: 'submitted'
      },
      {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      })

    if (response.data.success) {
      successMessage.value = 'Application submitted successfully!'

      // Emit success event with application data
      emit('application-submitted', {
        ...applicationData,
        job_title: props.job.title,
        company: props.job.company,
        applied_at: new Date().toISOString()
      })

      // Close modal after 1 seconds
      setTimeout(() => {
        closeModal()
      }, 1000)
    }
  } catch (error) {
    console.error('Failed to submit application:', error)

    if (error.response?.status === 400 && error.response?.data?.error) {
      errorMessage.value = error.response.data.error
    } else {
      errorMessage.value = 'Failed to submit application. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  emit('close')
}

const navigateToProfile = () => {
  closeModal()
  router.push('/candidate-profile')
}

// Load resumes on mount
onMounted(() => {
  loadResumes()
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  padding: 20px;
  overflow-y: auto;
}

.modal-container {
  background: white;
  border-radius: 16px;
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 1px solid #ecf0f1;
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
}

.modal-header h2 {
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
  cursor: pointer;
  color: #7f8c8d;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #ecf0f1;
  color: #e74c3c;
}

/* Modal Body */
.modal-body {
  padding: 30px;
}

/* Job Summary */
.job-summary {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  margin-bottom: 30px;
  color: white;
}

.job-summary .company-logo {
  width: 70px;
  height: 70px;
  flex-shrink: 0;
}

.job-summary .company-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: white;
  border-radius: 8px;
  padding: 8px;
}

.job-info h3 {
  margin: 0 0 10px 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.job-info p {
  margin: 5px 0;
  opacity: 0.9;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Application Form */
.application-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-group label i {
  color: #3498db;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select,
.form-group textarea {
  padding: 12px 15px;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.3s ease;
  outline: none;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #3498db;
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.input-group {
  display: flex;
  align-items: center;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.3s ease;
}

.input-group:focus-within {
  border-color: #3498db;
}

.input-prefix,
.input-suffix {
  padding: 12px 15px;
  background: #ecf0f1;
  color: #7f8c8d;
  font-weight: 600;
}

.input-group input {
  flex: 1;
  border: none;
  padding: 12px 15px;
  outline: none;
}

.help-text {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 5px;
}

.help-text.error {
  color: #e74c3c;
}

.upload-resume-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  transition: background 0.3s ease;
}

.upload-resume-btn:hover {
  background: #2980b9;
}

/* Checkbox Group */
.checkbox-group {
  margin-top: 10px;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
  font-weight: normal !important;
}

.checkbox-label input[type="checkbox"] {
  margin-top: 3px;
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-label span {
  flex: 1;
  color: #7f8c8d;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* Messages */
.error-message,
.success-message {
  padding: 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.success-message {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

/* Modal Actions */
.modal-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.btn-cancel,
.btn-submit {
  flex: 1;
  padding: 14px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 1rem;
}

.btn-cancel {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-cancel:hover:not(:disabled) {
  background: #d5dbdb;
}

.btn-submit {
  background: #3498db;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
}

.btn-submit:disabled,
.btn-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 768px) {
  .modal-container {
    max-height: 95vh;
  }

  .modal-header,
  .modal-body {
    padding: 20px;
  }

  .job-summary {
    flex-direction: column;
    text-align: center;
  }

  .job-summary .company-logo {
    margin: 0 auto;
  }

  .modal-actions {
    flex-direction: column;
  }

  .input-group {
    flex-wrap: wrap;
  }
}
</style>