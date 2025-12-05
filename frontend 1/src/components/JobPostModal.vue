<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <h2 style="padding-left: 28px">Create Job Post</h2>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <div class="form-row">
          <label>Title *</label>
          <input v-model="title" type="text" placeholder="Job title" />
        </div>

        <div class="form-row">
          <label>Requirements</label>
          <textarea v-model="requirements" rows="3" placeholder="Key requirements"></textarea>
        </div>

        <div class="form-row form-grid">
          <div>
            <label>Location</label>
            <input v-model="location" type="text" placeholder="Location" />
          </div>
          <div>
            <label>School</label>
            <input v-model="school" type="text" placeholder="School (optional)" />
          </div>
        </div>

        <div class="form-row form-grid">
          <div>
            <label>Level</label>
            <input v-model="level" type="text" placeholder="e.g., Junior, Senior" />
          </div>
          <div>
            <label>Status</label>
            <select v-model="status">
              <option value="active">Active</option>
              <option value="draft">Draft</option>
              <option value="closed">Closed</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="description-header">
            <label>Description</label>
            <button @click="generateDescriptionWithAI" class="btn-generate-ai"
              :disabled="!title || generatingDescription">
              {{ generatingDescription ? 'Generating...' : 'Generate with AI' }}
            </button>
          </div>
          <textarea v-model="description" rows="4" placeholder="Job description or click 'Generate with AI'"></textarea>
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
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <button @click="closeModal" class="btn-cancel">Cancel</button>
        <button @click="createJob" class="btn-upload" :disabled="submitting">
          <i class="fas fa-spinner fa-spin" v-if="submitting"></i>
          <i class="fas fa-save" v-else></i>
          {{ submitting ? 'Creating...' : 'Create Job' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits(['close', 'job-created'])

// Form state
const title = ref('')
const description = ref('')
const requirements = ref('')
const location = ref('')
const school = ref('')
const level = ref('')
const status = ref('active')

const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const generatingDescription = ref(false)

const getAuthToken = () => localStorage.getItem('access_token')
const getUserId = () => localStorage.getItem('userId')

const resetForm = () => {
  title.value = ''
  description.value = ''
  requirements.value = ''
  location.value = ''
  school.value = ''
  level.value = ''
  status.value = 'active'
}

const createJob = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (!title.value || title.value.trim().length === 0) {
    errorMessage.value = 'Title is required.'
    return
  }

  const posted_by_id = getUserId()
  if (!posted_by_id) {
    errorMessage.value = 'User not authenticated. Please login before creating a job.'
    return
  }

  const payload = {
    title: title.value,
    description: description.value,
    requirements: requirements.value,
    location: location.value,
    school: school.value,
    level: level.value,
    posted_by_id,
    status: status.value
  }

  submitting.value = true
  try {
    const resp = await axios.post('/api/jobs/', payload, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      }
    })

    if (resp.status === 201) {
      successMessage.value = 'Job created successfully.'
      emit('job-created', resp.data.job)
      // reset after a short delay so user sees message
      setTimeout(() => {
        resetForm()
        emit('close')
      }, 800)
      console.log("Success")
    } else {
      console.log("Failure")
      errorMessage.value = resp.data?.error || 'Unexpected response from server.'
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.error || err.message || 'Failed to create job.'
  } finally {
    submitting.value = false
  }
}

const closeModal = () => {
  if (!submitting.value) emit('close')
}

const generateDescriptionWithAI = async () => {
  if (!title.value || title.value.trim().length === 0) {
    errorMessage.value = 'Please enter a job title first.'
    return
  }

  generatingDescription.value = true
  errorMessage.value = ''

  try {
    const payload = {
      job_title: title.value,
      level: level.value || 'Not specified',
      location: location.value || 'Not specified'
    }

    const resp = await axios.post('/api/jobs/generate-description', payload, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      }
    })

    if (resp.status === 200 && resp.data.job_description) {
      const jobDesc = resp.data.job_description.description
      // Handle both string and object responses
      description.value = typeof jobDesc === 'string' ? jobDesc : JSON.stringify(jobDesc, null, 2)
      successMessage.value = 'Job description generated successfully!'
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = resp.data?.error || 'Failed to generate job description.'
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.error || err.message || 'Error generating job description.'
  } finally {
    generatingDescription.value = false
  }
}
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
}

.modal-container {
  background: white;
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* Modal Header */
.btn-generate-ai {
  font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif;
  padding: 10px 16px;
  /* Rich, saturated gradient for a vivid button */
  background: linear-gradient(90deg, #7c3aed 0%, #06b6d4 100%);
  color: #ffffff;
  border: 0;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  box-shadow: 0 8px 22px rgba(124, 58, 237, 0.35);
  position: relative;
  z-index: 1;
}

.btn-generate-ai::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 14px;
  padding: 2px;
  /* Brighter chroma sweep for the border */
  background: linear-gradient(90deg, #ff007a 0%, #ff7a00 33%, #00f5a0 66%, #7a00ff 100%);
  background-size: 300% 100%;
  animation: chromaBorder 5s linear infinite;
  z-index: 0;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
}

/* Modal Body */
.modal-body {
  padding: 25px 30px;
}

/* Form fields */
.form-row {
  margin-bottom: 18px;
  display: block;
}

.form-row:last-of-type {
  margin-bottom: 12px;
}

.form-row label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #34495e;
  font-size: 0.95rem;
}

.description-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.description-header label {
  margin-bottom: 0;
}

@keyframes chromaBorder {
  0% {
    background-position: 0% center;
  }

  100% {
    background-position: 300% center;
  }
}

.btn-generate-ai:hover:not(:disabled) {
  box-shadow: 0 14px 36px rgba(124, 58, 237, 0.36), 0 6px 18px rgba(6, 182, 212, 0.12);
  transform: translateY(-3px) scale(1.01);
}

.btn-generate-ai:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-generate-ai i {
  font-size: 0.95rem;
}

.form-row input[type="text"],
.form-row input[type="email"],
.form-row textarea,
.form-row select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d7dee5;
  border-radius: 8px;
  background: #fff;
  color: #2c3e50;
  font-size: 0.95rem;
  box-shadow: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.form-row textarea {
  resize: vertical;
  min-height: 80px;
}

.form-row input:focus,
.form-row textarea:focus,
.form-row select:focus {
  outline: none;
  border-color: #4aa3df;
  box-shadow: 0 0 0 4px rgba(74, 163, 223, 0.08);
}

.form-grid {
  display: grid;
  /* use minmax(0, 1fr) so children can shrink properly and avoid overlap */
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  align-items: start;
}

.form-grid>div {
  display: flex;
  flex-direction: column;
  /* ensure children can shrink instead of overflowing the grid cell */
  min-width: 0;
}

/* Ensure form controls use border-box sizing so padding doesn't cause overflow */
.form-row input[type="text"],
.form-row input[type="email"],
.form-row textarea,
.form-row select {
  box-sizing: border-box;
}

/* Tweak modal spacing for smaller screens */
@media (max-width: 600px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .modal-body {
    padding: 20px;
  }
}

.upload-area {
  border: 3px dashed #bdc3c7;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-area.drag-over {
  border-color: #3498db;
  background: #e8f4f8;
}

.upload-icon {
  font-size: 4rem;
  color: #3498db;
  margin-bottom: 20px;
}

.upload-area h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.upload-area p {
  color: #7f8c8d;
  margin: 10px 0;
}

.btn-browse {
  background: #3498db;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  margin: 20px 0;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: background 0.3s ease;
}

.btn-browse:hover {
  background: #2980b9;
}

.upload-note {
  font-size: 0.85rem;
  color: #95a5a6;
}

/* Selected File */
.selected-file {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.file-icon {
  width: 50px;
  height: 50px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  color: #e74c3c;
}

.file-details h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.file-details p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.btn-remove-file {
  background: #e74c3c;
  color: white;
  border: none;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Upload Progress */
.upload-progress {
  margin-top: 20px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #ecf0f1;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.3s ease;
}

.upload-progress p {
  text-align: center;
  color: #7f8c8d;
  margin: 0;
}

/* Messages */
.error-message,
.success-message {
  margin-top: 16px;
  padding: 12px 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 0.9rem;
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

/* Modal Footer */
.modal-footer {
  padding: 18px 30px;
  border-top: 1px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: #f9fafb;
}

.btn-cancel,
.btn-upload {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.btn-cancel {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-upload {
  background: #27ae60;
  color: white;
}

.btn-cancel:hover {
  background: #d5dbdb;
}

.btn-upload:hover:not(:disabled) {
  background: #229954;
}

.btn-upload:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .modal-container {
    max-width: 100%;
    margin: 0;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 20px;
  }

  .upload-area {
    padding: 30px 15px;
  }
}
</style>