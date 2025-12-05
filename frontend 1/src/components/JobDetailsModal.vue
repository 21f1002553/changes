<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <h2><i class="fas fa-briefcase"></i> Job Details</h2>
        <button @click="closeModal" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <!-- Loading State -->
        <div v-if="loading" class="loading-container">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading job details...</p>
        </div>

        <!-- Job Details Content -->
        <div v-else-if="jobDetails" class="job-details-content">
          <!-- Job Summary -->
          <div class="job-summary">
            <!-- Top Row: Location & Status Badges -->
            <div class="summary-badges">
              <span class="badge badge-location">
                <i class="fas fa-map-marker-alt"></i>
                {{ jobDetails?.location || 'Location not specified' }}
              </span>
              <span class="badge badge-status" :class="(jobDetails?.status || 'active').toLowerCase()">
                <i class="fas fa-circle"></i>
                {{ jobDetails?.status || 'Active' }}
              </span>
            </div>

            <!-- Main Job Info -->
            <div class="summary-content">
              <div class="logo-section">
                <div class="company-logo">
                  <img :src="jobDetails?.companyLogo || '/default-company-logo.png'" :alt="jobDetails?.company" />
                </div>
              </div>
              <div class="job-title-section">
                <h3>{{ jobDetails?.title }}</h3>
                <p class="company-name">
                  <i class="fas fa-school" v-if="jobDetails?.school"></i>
                  {{ jobDetails?.school || jobDetails?.company || 'Organization' }}
                </p>
              </div>
            </div>
          </div>

          <!-- Job Meta Information -->
          <div class="job-meta">
            <div class="meta-item">
              <span class="meta-label"><i class="fas fa-briefcase"></i> Employment Type</span>
              <span class="meta-value">{{ jobDetails?.employment_type || 'Full-time' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label"><i class="fas fa-dollar-sign"></i> Salary</span>
              <span class="meta-value">{{ formatSalary(jobDetails?.salary) || 'Negotiable' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label"><i class="fas fa-calendar"></i> Posted</span>
              <span class="meta-value">{{ formatDate(jobDetails?.created_at) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label"><i class="fas fa-signal"></i> Experience Level</span>
              <span class="meta-value">{{ jobDetails?.level || 'Not specified' }}</span>
            </div>
          </div>

          <!-- Job Description -->
          <div class="section">
            <h4><i class="fas fa-file-alt"></i> Job Description</h4>
            <div class="section-content">
              <p>{{ jobDetails?.description || 'No description available' }}</p>
            </div>
          </div>

          <!-- Requirements -->
          <div class="section">
            <h4><i class="fas fa-list"></i> Requirements</h4>
            <div class="section-content">
              <ul v-if="jobDetails?.requirements">
                <li v-for="(req, index) in parseRequirements(jobDetails.requirements)" :key="index">
                  {{ req }}
                </li>
              </ul>
              <p v-else>No specific requirements listed</p>
            </div>
          </div>

          <!-- Skills -->
          <div class="section" v-if="jobDetails?.required_skills">
            <h4><i class="fas fa-star"></i> Required Skills</h4>
            <div class="skills-tags">
              <span v-for="(skill, index) in parseSkills(jobDetails.required_skills)" :key="index" class="skill-tag">
                {{ skill }}
              </span>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            {{ errorMessage }}
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="errorMessage" class="error-state">
          <i class="fas fa-exclamation-circle"></i>
          <p>{{ errorMessage }}</p>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <button @click="closeModal" class="btn-cancel">
          Close
        </button>
        <button @click="applyForJob" class="btn-apply" :disabled="loading || !jobDetails">
          <i class="fas fa-paper-plane"></i>
          Apply Now
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits } from 'vue'
import axios from 'axios'

const props = defineProps({
  jobId: {
    type: String,
    required: true
  },
  userId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close', 'apply'])

// State
const loading = ref(false)
const jobDetails = ref(null)
const errorMessage = ref('')

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const formatSalary = (salary) => {
  if (!salary) return null
  return `$${new Intl.NumberFormat('en-US').format(salary)}`
}

const parseRequirements = (requirements) => {
  if (typeof requirements === 'string') {
    return requirements.split('\n').filter(r => r.trim()).map(r => r.trim())
  }
  return Array.isArray(requirements) ? requirements : []
}

const parseSkills = (skills) => {
  if (typeof skills === 'string') {
    return skills.split(',').map(s => s.trim()).filter(s => s)
  }
  return Array.isArray(skills) ? skills : []
}

// API Functions
const loadJobDetails = async () => {
  try {
    loading.value = true
    errorMessage.value = ''

    const response = await axios.get(`/api/jobs/${props.jobId}`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      jobDetails.value = response.data
      console.log('Job details loaded:', jobDetails.value)
    } else {
      errorMessage.value = 'Failed to load job details'
    }
  } catch (error) {
    console.error('Failed to load job details:', error)
    errorMessage.value = error.response?.data?.error || 'Failed to load job details. Please try again.'
  } finally {
    loading.value = false
  }
}

// Action Functions
const closeModal = () => {
  emit('close')
}

const applyForJob = () => {
  if (jobDetails.value) {
    emit('apply', jobDetails.value)
    closeModal()
  }
}

// Load job details on mount
onMounted(() => {
  loadJobDetails()
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

/* Loading State */
.loading-container {
  text-align: center;
  padding: 40px 20px;
}

.loading-container i {
  font-size: 2.5rem;
  color: #3498db;
  margin-bottom: 15px;
}

.loading-container p {
  color: #7f8c8d;
}

/* Job Details Content */
.job-details-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* Job Summary */
.job-summary {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 14px;
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.25);
}

.summary-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: capitalize;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  white-space: nowrap;
}

.badge i {
  font-size: 0.75rem;
}

.badge-status.active {
  background: rgba(46, 213, 115, 0.3);
  border-color: rgba(46, 213, 115, 0.7);
  color: white;
}

.badge-status.draft {
  background: rgba(65, 73, 87, 0.3);
  border-color: rgba(156, 163, 175, 0.7);
  color: white;
}

.badge-status.closed {
  background: rgba(239, 68, 68, 0.3);
  border-color: rgba(239, 68, 68, 0.7);
  color: white;
}

.badge-location {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.summary-content {
  display: flex;
  align-items: flex-start;
  gap: 18px;
}

.logo-section {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.job-summary .company-logo {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 8px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.job-summary .company-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.job-title-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.job-title-section h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
  line-height: 1.3;
}

.company-name {
  margin: 0;
  opacity: 0.95;
  font-size: 0.95rem;
  font-weight: 500;
}

/* Job Meta Information */
.job-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 15px;
  padding: 0;
  background: transparent;
  border-radius: 12px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #f9fafb 100%);
  border-radius: 10px;
  border: 1px solid #ecf0f1;
  transition: all 0.3s ease;
}

.meta-item:hover {
  border-color: #3498db;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.1);
  transform: translateY(-2px);
}

.meta-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: #7f8c8d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-label i {
  color: #3498db;
  font-size: 0.9rem;
}

.meta-value {
  font-size: 1.05rem;
  font-weight: 700;
  color: #2c3e50;
}

/* Sections */
.section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.15rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
}

.section h4 i {
  color: #3498db;
  font-size: 1.1rem;
}

.section-content {
  padding: 18px;
  background: linear-gradient(135deg, #f5f7fa 0%, #f9fafb 100%);
  border-radius: 10px;
  border: 1px solid #ecf0f1;
  border-left: 4px solid #3498db;
}

.section-content p {
  margin: 0;
  color: #555;
  line-height: 1.7;
}

.section-content ul {
  margin: 0;
  padding-left: 25px;
  color: #555;
  line-height: 1.9;
}

.section-content li {
  margin-bottom: 10px;
  color: #555;
}

/* Skills Tags */
.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 18px;
  background: linear-gradient(135deg, #f5f7fa 0%, #f9fafb 100%);
  border-radius: 10px;
  border: 1px solid #ecf0f1;
  border-left: 4px solid #3498db;
}

.skill-tag {
  background: white;
  border: 1.5px solid #3498db;
  color: #3498db;
  padding: 8px 16px;
  border-radius: 18px;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  cursor: default;
}

.skill-tag:hover {
  background: #3498db;
  color: white;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

/* Status Section */

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.closed {
  background: #d6d8db;
  color: #383d41;
}

.status-badge i {
  font-size: 0.6rem;
}

/* Messages */
.error-message {
  padding: 15px;
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}

.error-state {
  text-align: center;
  padding: 40px 20px;
}

.error-state i {
  font-size: 2.5rem;
  color: #e74c3c;
  display: block;
  margin-bottom: 15px;
}

.error-state p {
  color: #7f8c8d;
  margin: 0;
}

/* Modal Footer */
.modal-footer {
  display: flex;
  gap: 15px;
  padding: 20px 30px;
  border-top: 1px solid #ecf0f1;
  background: linear-gradient(to right, #f9fafb, #ffffff);
}

.btn-cancel,
.btn-apply {
  flex: 1;
  padding: 13px 20px;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 1rem;
  letter-spacing: 0.3px;
}

.btn-cancel {
  background: #ecf0f1;
  color: #2c3e50;
  border: 1px solid #d5dbdb;
}

.btn-cancel:hover {
  background: #d5dbdb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.btn-apply {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(52, 152, 219, 0.25);
}

.btn-apply:hover:not(:disabled) {
  background: linear-gradient(135deg, #2980b9 0%, #1c5aa0 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
}

.btn-apply:disabled {
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
    gap: 16px;
    padding: 20px;
  }

  .summary-badges {
    flex-direction: column;
  }

  .badge {
    width: 100%;
    justify-content: center;
  }

  .summary-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .job-summary .company-logo {
    width: 70px;
    height: 70px;
  }

  .job-title-section h3 {
    font-size: 1.2rem;
  }

  .job-meta {
    grid-template-columns: 1fr;
  }

  .modal-footer {
    flex-direction: column;
    padding: 16px 20px;
  }

  .btn-cancel,
  .btn-apply {
    padding: 12px 16px;
  }
}
</style>
