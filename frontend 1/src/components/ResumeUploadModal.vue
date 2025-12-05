<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <h2><i class="fas fa-upload"></i> Upload Resume</h2>
        <button @click="closeModal" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <!-- Upload Area -->
        <div class="upload-area" :class="{ 'drag-over': isDragOver }" @drop.prevent="handleDrop"
          @dragover.prevent="isDragOver = true" @dragleave.prevent="isDragOver = false">
          <input ref="fileInput" type="file" accept=".pdf,.doc,.docx" @change="handleFileSelect"
            style="display: none" />

          <div class="upload-icon">
            <i class="fas fa-cloud-upload-alt"></i>
          </div>

          <h3>Drag & Drop your resume here</h3>
          <p>or</p>
          <button @click="$refs.fileInput.click()" class="btn-browse">
            <i class="fas fa-folder-open"></i>
            Browse Files
          </button>

          <p class="upload-note">
            Supported formats: PDF, DOC, DOCX (Max 5MB)
          </p>
        </div>

        <!-- Selected File -->
        <div v-if="selectedFile" class="selected-file">
          <div class="file-info">
            <div class="file-icon">
              <i class="fas fa-file-pdf" v-if="selectedFile.type === 'application/pdf'"></i>
              <i class="fas fa-file-word" v-else></i>
            </div>
            <div class="file-details">
              <h4>{{ selectedFile.name }}</h4>
              <p>{{ formatFileSize(selectedFile.size) }}</p>
            </div>
          </div>
          <button @click="removeFile" class="btn-remove-file">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <!-- Upload Progress -->
        <div v-if="uploading" class="upload-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
          <p>{{ uploadProgress }}% uploaded</p>
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
        <button @click="closeModal" class="btn-cancel">
          Cancel
        </button>
        <button @click="uploadResume" class="btn-upload" :disabled="!selectedFile || uploading">
          <i class="fas fa-spinner fa-spin" v-if="uploading"></i>
          <i class="fas fa-upload" v-else></i>
          {{ uploading ? 'Uploading...' : 'Upload Resume' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue'
import axios from 'axios'

const emit = defineEmits(['close', 'resume-uploaded'])

// State
const selectedFile = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const errorMessage = ref('')
const successMessage = ref('')
const isDragOver = ref(false)
const fileInput = ref(null)

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

const formatFileSize = (bytes) => {
  const kb = bytes / 1024
  if (kb < 1024) return `${kb.toFixed(1)} KB`
  return `${(kb / 1024).toFixed(1)} MB`
}

const validateFile = (file) => {
  // Check file type
  const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  if (!allowedTypes.includes(file.type)) {
    errorMessage.value = 'Invalid file type. Please upload PDF, DOC, or DOCX files only.'
    return false
  }

  // Check file size (5MB max)
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    errorMessage.value = 'File size exceeds 5MB. Please upload a smaller file.'
    return false
  }

  return true
}

// File Handling
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file && validateFile(file)) {
    selectedFile.value = file
    errorMessage.value = ''
  }
}

const handleDrop = (event) => {
  isDragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file && validateFile(file)) {
    selectedFile.value = file
    errorMessage.value = ''
  }
}

const removeFile = () => {
  selectedFile.value = null
  errorMessage.value = ''
  successMessage.value = ''
}

// Upload Resume
const uploadResume = async () => {
  if (!selectedFile.value) return

  try {
    uploading.value = true
    errorMessage.value = ''
    successMessage.value = ''
    uploadProgress.value = 0

    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('category', 'resume')
    formData.append('description', 'Resume uploaded from profile')

    const response = await axios.post('/api/files/upload/resume', formData, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      }
    })

    if (response.data.success) {
      successMessage.value = 'Resume uploaded successfully!'
      closeModal()

      // Emit success event
      setTimeout(() => {
        emit('resume-uploaded', response.data.file)
      }, 1500)
    }
  } catch (error) {
    console.error('Upload failed:', error)
    errorMessage.value = error.response?.data?.error || 'Failed to upload resume. Please try again.'
  } finally {
    uploading.value = false
  }
}

const closeModal = () => {
  if (!uploading.value) {
    emit('close')
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
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 1px solid #ecf0f1;
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
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #ecf0f1;
  color: #e74c3c;
}

/* Modal Body */
.modal-body {
  padding: 30px;
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
  margin-top: 20px;
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

/* Modal Footer */
.modal-footer {
  padding: 20px 30px;
  border-top: 1px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.btn-cancel,
.btn-upload {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
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