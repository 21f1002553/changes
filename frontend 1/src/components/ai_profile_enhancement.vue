<template>
  <DashboardLayout>
    <div class="resume-profile">
      <div class="header">
        <h1>My Resume Profile</h1>
        <p>Manage your resume and get AI-powered insights</p>
      </div>

      <div class="profile-grid">
        <!-- Resume Upload Section -->
        <div class="profile-card upload-section">
          <h3><i class="fas fa-upload"></i> Upload Resume</h3>

          <div v-if="!currentResume" class="upload-area" @click="$refs.fileInput.click()">
            <input ref="fileInput" type="file" @change="handleResumeUpload" accept=".pdf,.docx" style="display: none"
              :disabled="uploading" />
            <div class="upload-placeholder">
              <i class="fas fa-cloud-upload-alt"></i>
              <p>Click to upload your resume</p>
              <small>Supports PDF and DOCX (Max 10MB)</small>
            </div>
          </div>

          <div v-else class="resume-uploaded">
            <input ref="replaceFileInput" type="file" @change="handleResumeReplace" accept=".pdf,.docx"
              style="display: none" :disabled="uploading" />

            <div class="resume-info">
              <i class="fas fa-file-alt"></i>
              <div class="info-text">
                <h4>{{ currentResume.filename }}</h4>
                <p>Uploaded: {{ formatDate(currentResume.uploaded_at) }}</p>
              </div>
            </div>

            <div class="resume-actions">
              <button @click="downloadResume" class="btn-secondary">
                <i class="fas fa-download"></i> Download
              </button>
              <button @click="previewResume" class="btn-info" :disabled="loadingPreview">
                <i class="fas fa-eye"></i> {{ loadingPreview ? 'Loading...' : 'Preview' }}
              </button>
              <button @click="replaceResume" class="btn-primary" :disabled="uploading">
                <i class="fas fa-sync"></i> {{ uploading ? 'Replacing...' : 'Replace' }}
              </button>
              <button @click="deleteResume" class="btn-danger">
                <i class="fas fa-trash"></i> Delete
              </button>
            </div>
          </div>


          <div v-if="showPreview" class="preview-modal" @click="closePreview">
            <div class="preview-content" @click.stop>
              <div class="preview-header">
                <h3><i class="fas fa-eye"></i> Resume Preview</h3>
                <button @click="closePreview" class="close-btn">
                  <i class="fas fa-times"></i>
                </button>
              </div>

              <div class="preview-body">
                <div v-if="previewLoading" class="preview-loading">
                  <i class="fas fa-spinner fa-spin"></i>
                  <p>Loading preview...</p>
                </div>

                <div v-else-if="previewError" class="preview-error">
                  <i class="fas fa-exclamation-triangle"></i>
                  <p>{{ previewError }}</p>
                </div>

                <div v-else-if="previewData" class="preview-container">
                  <!-- File Info -->
                  <div class="file-info-header">
                    <div class="file-details">
                      <h4>{{ previewData.filename }}</h4>
                      <div class="file-meta">
                        <span class="file-size">{{ formatFileSize(previewData.file_size) }}</span>
                        <span class="file-type">{{ previewData.file_type.toUpperCase() }}</span>
                        <span class="upload-date">{{ formatDate(previewData.uploaded_at) }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- Preview Content -->
                  <div class="preview-text-content">
                    <div v-if="previewData.preview_type === 'text' && previewData.content">
                      <h5>Document Content:</h5>
                      <div class="text-preview">
                        <pre>{{ previewData.content }}</pre>
                        <div v-if="previewData.full_length > previewData.content.length" class="truncate-notice">
                          <p><i class="fas fa-info-circle"></i>
                            Showing first {{ previewData.content.length }} of {{ previewData.full_length }} characters.
                            Download for full content.</p>
                        </div>
                      </div>
                    </div>

                    <div v-else-if="previewData.preview_type === 'metadata'">
                      <div class="metadata-preview">
                        <i class="fas fa-file-pdf"></i>
                        <h5>{{ previewData.message || 'File preview not available' }}</h5>
                        <p>{{ previewData.error || 'Please download the file to view its contents.' }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="preview-footer">
                <button @click="downloadResume" class="btn-primary">
                  <i class="fas fa-download"></i> Download Full File
                </button>
                <button @click="closePreview" class="btn-secondary">
                  Close Preview
                </button>
              </div>
            </div>
          </div>

          <div v-if="uploading" class="upload-progress">
            <div class="progress-bar">
              <div class="progress-fill"></div>
            </div>
            <p>Uploading resume...</p>
          </div>

          <div v-if="uploadError" class="error">{{ uploadError }}</div>
        </div>

        <!-- Resume Details Section -->
        <div class="profile-card details-section">
          <h3><i class="fas fa-info-circle"></i> Resume Details</h3>

          <div v-if="currentResume" class="resume-details">
            <div class="detail-row">
              <label>File URL:</label>
              <span class="file-url">{{ currentResume.file_url }}</span>
            </div>

            <div class="detail-row">
              <label>Upload Date:</label>
              <span>{{ formatDate(currentResume.uploaded_at) }}</span>
            </div>

            <div class="detail-row">
              <label>File Size:</label>
              <span>{{ formatFileSize(currentResume.file_size) }}</span>
            </div>

            <div class="detail-row">
              <label>Status:</label>
              <span :class="['status', currentResume.status]">{{ currentResume.status || 'Active' }}</span>
            </div>

            <!-- Parsed Resume Data Preview -->
            <div v-if="currentResume.parsed_data" class="parsed-data">
              <h4>Parsed Information:</h4>
              <div class="parsed-content">
                <pre>{{ formatParsedData(currentResume.parsed_data) }}</pre>
              </div>
            </div>
          </div>

          <div v-else class="no-resume">
            <i class="fas fa-file-plus"></i>
            <p>No resume uploaded yet</p>
            <p>Upload your resume to see details here</p>
          </div>
        </div>

        <!-- AI Enhancement Section -->
        <div class="profile-card ai-section">
          <h3><i class="fas fa-brain"></i> AI Enhancement</h3>

          <div v-if="currentResume" class="ai-actions">
            <p>Get AI-powered suggestions to improve your resume</p>

            <div class="form-group">
              <label>Target Job or Carrer goals</label>
              <input v-model="targetJobTitle" type="text" placeholder="e.g., Goals or Job Description" />
            </div>

            <button @click="getEnhancementSuggestions" :disabled="loadingEnhancement" class="btn-primary full-width">
              {{ loadingEnhancement ? 'Analyzing...' : 'Get AI Suggestions' }}
            </button>

            <div v-if="enhancementSuggestions && enhancementSuggestions.length">
              <div v-for="(sec, idx) in enhancementSuggestions" :key="'sec-' + idx" class="enhancement-card">
                <h3 class="enhancement-title">{{ sec.section || ('Section ' + (idx + 1)) }}</h3>
                <div class="enhancement-grid" :style="{
                  gridTemplateColumns:
                    ((sec.mistakes && sec.mistakes.length > 0) && (sec.suggested_change && sec.suggested_change.length > 0))
                      ? '1fr 1fr'
                      : '1fr'
                }">
                  <!-- Issues column - only render if there are issues -->
                  <div v-if="sec.mistakes && sec.mistakes.length > 0" class="column column-issues">
                    <h4>Issues</h4>
                    <ul class="nice-list">
                      <li v-for="(m, i) in sec.mistakes" :key="i">{{ m }}</li>
                    </ul>
                  </div>

                  <!-- Suggested Changes column - only render if there are suggested changes -->
                  <div v-if="sec.suggested_change && sec.suggested_change.length > 0" class="column column-changes">
                    <h4>Suggested Changes</h4>
                    <ul class="nice-list">
                      <li v-for="(c, i) in sec.suggested_change" :key="i">{{ c }}</li>
                    </ul>
                  </div>

                </div>

                <!-- Reason (optional) -->
                <div v-if="sec.reason" class="enhancement-reason">
                  <strong>Reason:</strong> <span class="muted">{{ sec.reason }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="ai-disabled">
            <i class="fas fa-robot"></i>
            <p>Upload a resume to unlock AI enhancement features</p>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const API_BASE = 'http://localhost:5001/api'

// State
const currentResume = ref(null)
const uploading = ref(false)
const uploadError = ref(null)
const targetJobTitle = ref('')
const loadingEnhancement = ref(false)
const enhancementError = ref(null)
const enhancementSuggestions = ref(null)

// Load current resume
async function loadCurrentResume() {
  try {
    const response = await axios.get(`${API_BASE}/files`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    currentResume.value = response.data
  } catch (error) {
    if (error.response?.status !== 404) {
      console.error('Failed to load resume:', error)
    }
    // 404 is expected if user hasn't uploaded a resume yet
  }
}
function replaceResume() {
  uploadError.value = null
  enhancementSuggestions.value = null // Clear previous suggestions
  enhancementError.value = null
  // Trigger the hidden file input for replacing
  document.querySelector('input[ref="replaceFileInput"]') || $refs.replaceFileInput.click()
}
// Handle resume upload - UPDATED to use new endpoint
async function handleResumeUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  if (!validateFile(file)) return

  uploading.value = true
  uploadError.value = null

  try {
    const formData = new FormData()
    formData.append('file', file)

    // Use the new dedicated resume upload endpoint
    const response = await axios.post(`${API_BASE}/files/upload/resume`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    currentResume.value = response.data.resume

    // Clear any previous errors
    enhancementSuggestions.value = null
    enhancementError.value = null

  } catch (error) {
    console.error('Upload error:', error.response?.data || error)

    // Handle different error types
    if (error.response?.status === 422) {
      uploadError.value = 'Invalid request data. Please check your file and try again.'
    } else if (error.response?.status === 413) {
      uploadError.value = 'File size too large. Please upload a file smaller than 10MB.'
    } else if (error.response?.status === 400) {
      uploadError.value = error.response.data.error || 'Invalid file. Please upload a PDF or DOCX file.'
    } else {
      uploadError.value = error.response?.data?.error || 'Failed to upload resume. Please try again.'
    }
  } finally {
    uploading.value = false
    // Clear file input to allow re-uploading the same file
    if (event.target) {
      event.target.value = ''
    }
  }
}

// File validation - ENHANCED
function validateFile(file) {
  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  const allowedExtensions = ['pdf', 'docx']
  const maxSize = 10 * 1024 * 1024 // 10MB

  // Check file type by MIME type
  if (!allowedTypes.includes(file.type)) {
    // Fallback: check by file extension
    const fileExtension = file.name.split('.').pop()?.toLowerCase()
    if (!allowedExtensions.includes(fileExtension)) {
      uploadError.value = 'Please upload only PDF or DOCX files'
      return false
    }
  }

  // Check file size
  if (file.size > maxSize) {
    uploadError.value = 'File size should be less than 10MB'
    return false
  }

  // Check if file has content
  if (file.size === 0) {
    uploadError.value = 'The selected file is empty'
    return false
  }

  return true
}

// Replace resume - UPDATED
// Add these new state variables
const showPreview = ref(false)
const previewLoading = ref(false)
const previewError = ref(null)
const previewData = ref(null)
const loadingPreview = ref(false)

// Add the preview function
async function previewResume() {
  if (!currentResume.value?.file_id) {
    uploadError.value = 'Cannot preview: File reference not found'
    return
  }

  loadingPreview.value = true
  previewError.value = null
  previewData.value = null

  try {
    const response = await axios.get(
      `${API_BASE}/files/${currentResume.value.file_id}/preview`,
      {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }
    )

    previewData.value = response.data
    showPreview.value = true

  } catch (error) {
    console.error('Preview error:', error)
    previewError.value = error.response?.data?.error || 'Failed to load preview'
    uploadError.value = previewError.value
  } finally {
    loadingPreview.value = false
  }
}

// Add close preview function
function closePreview() {
  showPreview.value = false
  previewData.value = null
  previewError.value = null
}

// Keep the existing replaceResume function
// Replace resume - FIXE

// Handle resume replacement - NEW FUNCTION
async function handleResumeReplace(event) {
  const file = event.target.files[0]
  if (!file) return

  if (!validateFile(file)) return

  // Show confirmation dialog
  const confirmReplace = confirm(
    `Are you sure you want to replace "${currentResume.value.filename}" with "${file.name}"? This action cannot be undone.`
  )

  if (!confirmReplace) {
    // Clear the file input
    event.target.value = ''
    return
  }

  uploading.value = true
  uploadError.value = null

  try {
    const formData = new FormData()
    formData.append('file', file)

    // Use the same resume upload endpoint - it will replace the existing resume
    const response = await axios.post(`${API_BASE}/files/upload/resume`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })

    // Update current resume with new data
    currentResume.value = response.data.resume

    // Clear previous AI suggestions since we have a new resume
    enhancementSuggestions.value = null
    enhancementError.value = null

    // Show success message (optional)
    uploadError.value = null

  } catch (error) {
    console.error('Replace error:', error.response?.data || error)

    // Handle different error types
    if (error.response?.status === 422) {
      uploadError.value = 'Invalid request data. Please check your file and try again.'
    } else if (error.response?.status === 413) {
      uploadError.value = 'File size too large. Please upload a file smaller than 10MB.'
    } else if (error.response?.status === 400) {
      uploadError.value = error.response.data.error || 'Invalid file. Please upload a PDF or DOCX file.'
    } else {
      uploadError.value = error.response?.data?.error || 'Failed to replace resume. Please try again.'
    }
  } finally {
    uploading.value = false
    // Clear file input to allow re-uploading the same file
    if (event.target) {
      event.target.value = ''
    }
  }
}

// Download resume - UPDATED to use file_id
// Download resume - FIXED
async function downloadResume() {
  if (currentResume.value?.file_id) {
    try {
      const response = await axios.get(
        `${API_BASE}/files/${currentResume.value.file_id}/download`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
          responseType: 'blob' // Important for file downloads
        }
      )

      // Create blob URL and trigger download
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

      // Use the original filename from currentResume or response headers
      const filename = currentResume.value.filename || 'resume.pdf'
      link.setAttribute('download', filename)

      // Trigger download
      document.body.appendChild(link)
      link.click()

      // Cleanup
      link.remove()
      window.URL.revokeObjectURL(url)

    } catch (error) {
      console.error('Download error:', error)
      uploadError.value = error.response?.data?.error || 'Failed to download resume'
    }
  } else {
    uploadError.value = 'Cannot download: File reference not found'
  }
}

// Delete resume - ENHANCED with better error handling
async function deleteResume() {
  if (!confirm('Are you sure you want to delete your resume? This action cannot be undone.')) return

  try {
    // Delete the resume record (this should also handle file cleanup in backend)
    await axios.delete(`${API_BASE}/files/delete/${currentResume.value.file_id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })

    // Clear state
    currentResume.value = null
    enhancementSuggestions.value = null
    enhancementError.value = null
    uploadError.value = null

  } catch (error) {
    console.error('Delete error:', error)
    uploadError.value = error.response?.data?.error || 'Failed to delete resume'
  }
}

// Get AI enhancement suggestions - NO CHANGES NEEDED
async function getEnhancementSuggestions() {
  enhancementError.value = null
  enhancementSuggestions.value = null
  loadingEnhancement.value = true

  try {
    const payload = targetJobTitle.value ? { job_title: targetJobTitle.value } : {}

    const response = await axios.post(
      `${API_BASE}/ai/profile_enhancement/${currentResume.value.id}`,
      payload,
      {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }
    )

    enhancementSuggestions.value = response.data.profile_enhancement || response.data
  } catch (error) {
    console.error('Enhancement error:', error)
    enhancementError.value = error.response?.data?.error || 'Failed to get enhancement suggestions'
  } finally {
    loadingEnhancement.value = false
  }
}

// Utility functions remain the same
function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatFileSize(bytes) {
  if (!bytes) return 'N/A'
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 Byte'
  const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

function formatParsedData(data) {
  if (typeof data === 'string') return data
  return JSON.stringify(data, null, 2)
}

onMounted(() => {
  loadCurrentResume()
})
</script>

<style scoped>
/* Preview Modal */
.preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.preview-content {
  background: white;
  border-radius: 12px;
  max-width: 900px;
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 2px solid #ecf0f1;
  background: #f8f9fa;
  border-radius: 12px 12px 0 0;
}

.preview-header h3 {
  margin: 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
}

.close-btn {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: background-color 0.3s ease;
}

.close-btn:hover {
  background: #c0392b;
}

.preview-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  min-height: 300px;
}

.preview-loading,
.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #7f8c8d;
}

.preview-loading i {
  font-size: 2rem;
  margin-bottom: 10px;
}

.preview-error {
  color: #e74c3c;
}

.preview-error i {
  font-size: 2rem;
  margin-bottom: 10px;
}

.file-info-header {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.file-details h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.file-meta {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.file-meta span {
  background: #ecf0f1;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #2c3e50;
}

.text-preview {
  background: #f8f9fa;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
}

.text-preview pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  line-height: 1.6;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 0.9rem;
  color: #2c3e50;
}

.truncate-notice {
  margin-top: 15px;
  padding: 10px;
  background: #e8f4f8;
  border-left: 4px solid #3498db;
  border-radius: 0 4px 4px 0;
}

.truncate-notice p {
  margin: 0;
  color: #2c3e50;
  font-size: 0.9rem;
}

.metadata-preview {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.metadata-preview i {
  font-size: 4rem;
  margin-bottom: 20px;
  color: #e74c3c;
}

.metadata-preview h5 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.preview-footer {
  padding: 20px;
  border-top: 2px solid #ecf0f1;
  background: #f8f9fa;
  border-radius: 0 0 12px 12px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.preview-footer button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s ease;
}

.preview-footer button:hover {
  transform: translateY(-2px);
}

/* Button styles */
.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background: #138496;
}

.btn-info:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .preview-modal {
    padding: 10px;
  }

  .preview-content {
    max-height: 90vh;
  }

  .file-meta {
    flex-direction: column;
    gap: 8px;
  }

  .preview-footer {
    flex-direction: column;
  }

  .preview-footer button {
    width: 100%;
  }
}

.resume-profile {
  padding: 0;
  /* Remove padding since DashboardLayout handles it */
  max-width: 100%;
  /* Use full width */
  margin: 0;
  height: 100%;
  overflow: visible;
  /* Allow content to flow normally */
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 10px;
  word-break: break-word;
}

.header p {
  font-size: 1.2rem;
  color: #7f8c8d;
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 20px;
  width: 100%;
  box-sizing: border-box;
}

.profile-card {
  background: #fff;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.07);
  box-sizing: border-box;
  min-width: 0;
  /* Allow cards to shrink */
  overflow-wrap: break-word;
}

.profile-card h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  word-break: break-word;
}

.ai-section {
  grid-column: 1 / -1;
}

/* Upload Section */
.upload-area {
  border: 3px dashed #ecf0f1;
  border-radius: 12px;
  padding: 30px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: #3498db;
  background: #f8f9fa;
}

.upload-placeholder i {
  font-size: 3rem;
  color: #bdc3c7;
  margin-bottom: 15px;
  display: block;
}

.upload-placeholder p {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 10px;
  font-weight: 600;
  word-break: break-word;
}

.upload-placeholder small {
  color: #7f8c8d;
  display: block;
}


.resume-uploaded {
  text-align: left;
}

.resume-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.resume-info i {
  font-size: 2.5rem;
  color: #27ae60;
}

.info-text h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  word-break: break-word;
  font-size: 1rem;
}

.info-text p {
  margin: 2px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.resume-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.resume-actions button {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: transform 0.2s ease;
  white-space: nowrap;
  min-width: 0;
  flex: 1;
  max-width: 120px;
}


.resume-actions button:hover {
  transform: translateY(-2px);
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.full-width {
  width: 100%;
  padding: 12px;
  font-size: 1.1rem;
}

/* Details Section */
.resume-details .detail-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 10px 0;
  border-bottom: 1px solid #ecf0f1;
  gap: 10px;
}


.detail-row label {
  font-weight: 600;
  color: #2c3e50;
  flex-shrink: 0;
  min-width: 80px;
}

.file-url {
  font-family: monospace;
  font-size: 0.8rem;
  color: #7f8c8d;
  word-break: break-all;
  text-align: right;
  flex: 1;
}


.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status.active {
  background: #d5f4e6;
  color: #27ae60;
}

.parsed-data {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid #ecf0f1;
}

.parsed-content {
  background: #f8f9fa;
  border: 1px solid #ecf0f1;
  border-radius: 6px;
  padding: 15px;
  max-height: 200px;
  overflow-y: auto;
}

.parsed-content pre {
  margin: 0;
  font-size: 0.85rem;
  line-height: 1.4;
}

.no-resume,
.ai-disabled {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.no-resume i,
.ai-disabled i {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
}

/* AI Section */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2c3e50;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
}

.suggestions {
  margin-top: 25px;
  padding-top: 25px;
  border-top: 2px solid #ecf0f1;
}

.suggestions h4 {
  color: #27ae60;
  margin-bottom: 15px;
}

.suggestions-content {
  background: #f8f9fa;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  padding: 20px;
  max-height: 300px;
  overflow-y: auto;
}

.suggestions-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  line-height: 1.6;
}

.upload-progress {
  text-align: center;
  margin-top: 20px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #ecf0f1;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2980b9);
  animation: loading 2s ease-in-out infinite;
}

@keyframes loading {
  0% {
    width: 0%;
  }

  50% {
    width: 70%;
  }

  100% {
    width: 100%;
  }
}

.error {
  background: #e74c3c;
  color: white;
  padding: 15px;
  border-radius: 8px;
  margin-top: 15px;
}

@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }

  .resume-actions {
    justify-content: center;
  }
}

/* Enhancement suggestions card - improved styling */
/* Enhancement suggestions card - improved styling */
.enhancement-card {
  background: linear-gradient(180deg, #ffffff, #fbfdff);
  border: 1px solid #e6eef5;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 6px 20px rgba(18, 38, 63, 0.06);
  margin: 12px 0;
  overflow: hidden;
  word-wrap: break-word;
}

/* Title centered */
.enhancement-title {
  text-align: center;
  font-size: 1.3rem;
  margin: 4px 0 16px 0;
  color: #24324a;
  font-weight: 700;
  word-break: break-word;
}

.enhancement-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  align-items: start;
  margin-bottom: 14px;
}

/* Column headings */
.enhancement-card h4 {
  margin: 0 0 10px 0;
  color: #1f3a57;
  font-size: 1.02rem;
  font-weight: 600;
}

/* prettier list */
.nice-list {
  list-style: none;
  padding: 0;
  margin: 0;
  text-align: left;
}

.nice-list li {
  position: relative;
  padding-left: 28px;
  margin-bottom: 10px;
  line-height: 1.55;
  color: #334155;
  font-size: 0.98rem;
  text-align: left;
}

/* custom bullet */
.nice-list li::before {
  content: "";
  display: inline-block;
  width: 10px;
  height: 10px;
  background: #60a5fa;
  /* soft blue */
  border-radius: 50%;
  position: absolute;
  left: 8px;
  top: 8px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.06);
}

/* Reason line */
.enhancement-reason {
  border-top: 1px dashed #e6eef5;
  padding-top: 12px;
  color: #475569;
  font-size: 0.95rem;
}

/* small screens: stack columns */
@media (max-width: 800px) {
  .enhancement-grid {
    grid-template-columns: 1fr;
  }

  .nice-list li::before {
    left: 6px;
    top: 7px;
  }
}

@media (max-width: 320px) {
  .profile-card {
    padding: 10px;
  }

  .header {
    margin-bottom: 20px;
  }

  .resume-actions button {
    font-size: 0.75rem;
    padding: 5px 8px;
  }
}

/* Make lists wrap and be readable inside narrow container */
.enhancement-card .nice-list li {
  word-break: break-word;
}
</style>