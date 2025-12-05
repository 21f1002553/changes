<template>
  <DashboardLayout>
    <div class="candidate-profile-page">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-left">
          <h1><i class="fas fa-user-circle"></i> My Profile</h1>
          <p>Manage your personal information and professional details</p>
        </div>
        <div class="header-actions">
          <button @click="toggleEditMode" class="btn-edit" v-if="!isEditMode">
            <i class="fas fa-edit"></i>
            Edit Profile
          </button>
          <template v-else>
            <button @click="cancelEdit" class="btn-cancel">
              <i class="fas fa-times"></i>
              Cancel
            </button>
            <button @click="saveProfile" class="btn-save" :disabled="saving">
              <i class="fas fa-spinner fa-spin" v-if="saving"></i>
              <i class="fas fa-save" v-else></i>
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </template>
        </div>
      </div>

      <!-- Profile Content Grid -->
      <div class="profile-grid">
        <!-- Left Column -->
        <div class="profile-left">
          <!-- Profile Card -->
          <div class="profile-card">
            <div class="profile-avatar">
              <div class="avatar-circle">
                <i class="fas fa-user"></i>
              </div>
              <button class="change-avatar-btn" v-if="isEditMode">
                <i class="fas fa-camera"></i>
              </button>
            </div>

            <div class="profile-basic-info">
              <h2>{{ profileData.name || 'Your Name' }}</h2>
              <p class="role-badge">
                <i class="fas fa-briefcase"></i>
                {{ profileData.role_name || 'Candidate' }}
              </p>
              <p class="email">
                <i class="fas fa-envelope"></i>
                {{ profileData.email }}
              </p>
              <p class="member-since">
                <i class="fas fa-calendar"></i>
                Member since {{ formatDate(profileData.created_at) }}
              </p>
            </div>

            <div class="profile-stats">
              <div class="stat">
                <h3>{{ stats.applications }}</h3>
                <p>Applications</p>
              </div>
              <div class="stat">
                <h3>{{ stats.interviews }}</h3>
                <p>Interviews</p>
              </div>
              <div class="stat">
                <h3>{{ stats.views }}</h3>
                <p>Profile Views</p>
              </div>
            </div>
          </div>

          <!-- Resume Section -->
          <div class="resume-card">
            <div class="card-header">
              <h3><i class="fas fa-file-alt"></i> My Resume</h3>
              <button @click="openResumeUploadModal" class="btn-upload-resume">
                <i class="fas fa-upload"></i>
                Upload New
              </button>
            </div>

            <!-- Loading State -->
            <div v-if="resumeLoading" class="loading-state">
              <i class="fas fa-spinner fa-spin"></i>
              <p>Loading resume...</p>
            </div>

            <!-- Resume List -->
            <div v-else-if="resumes.length > 0" class="resume-list">
              <div v-for="resume in resumes" :key="resume.id" class="resume-item"
                :class="{ active: resume.id === selectedResumeId }">
                <div class="resume-icon">
                  <i class="fas fa-file-pdf" v-if="resume.file_type === 'pdf'"></i>
                  <i class="fas fa-file-word" v-else></i>
                </div>
                <div class="resume-info">
                  <h4>{{ resume.original_filename || resume.filename }}</h4>
                  <p class="resume-meta">
                    <span><i class="fas fa-calendar"></i> {{ formatDate(resume.uploaded_at) }}</span>
                    <span><i class="fas fa-hdd"></i> {{ formatFileSize(resume.file_size) }}</span>
                  </p>
                </div>
                <div class="resume-actions">
                  <button @click="downloadResume(resume)" class="btn-icon" title="Download">
                    <i class="fas fa-download"></i>
                  </button>
                  <button @click="viewResume(resume)" class="btn-icon" title="View">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button @click="deleteResume(resume.id)" class="btn-icon delete" title="Delete">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="empty-resume-state">
              <div class="empty-icon">
                <i class="fas fa-file-upload"></i>
              </div>
              <h4>No Resume Uploaded</h4>
              <p>Upload your resume to get personalized job recommendations</p>
              <button @click="openResumeUploadModal" class="btn-upload-primary">
                <i class="fas fa-upload"></i>
                Upload Your Resume
              </button>
            </div>
          </div>

          <!-- Quick Links -->
          <div class="quick-links-card">
            <h3><i class="fas fa-link"></i> Quick Links</h3>
            <div class="links-list">
              <a href="#" class="link-item">
                <i class="fas fa-briefcase"></i>
                <span>Job Recommendations</span>
                <i class="fas fa-chevron-right"></i>
              </a>
              <a href="#" class="link-item">
                <i class="fas fa-paper-plane"></i>
                <span>My Applications</span>
                <i class="fas fa-chevron-right"></i>
              </a>
              <a href="#" class="link-item">
                <i class="fas fa-brain"></i>
                <span>AI Enhancement</span>
                <i class="fas fa-chevron-right"></i>
              </a>
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="profile-right">
          <!-- Personal Information -->
          <div class="info-card">
            <h3><i class="fas fa-user"></i> Personal Information</h3>
            <div class="form-grid">
              <div class="form-group">
                <label>Full Name *</label>
                <input v-model="editData.name" type="text" :disabled="!isEditMode" placeholder="Enter your full name" />
              </div>

              <div class="form-group">
                <label>Email Address *</label>
                <input v-model="editData.email" type="email" :disabled="!isEditMode"
                  placeholder="your.email@example.com" />
              </div>

              <div class="form-group">
                <label>Phone Number</label>
                <input v-model="editData.phone" type="tel" :disabled="!isEditMode" placeholder="+91-99999999000" />
              </div>

              <div class="form-group">
                <label>Location</label>
                <input v-model="editData.location" type="text" :disabled="!isEditMode" placeholder="City, State" />
              </div>

              <div class="form-group full-width">
                <label>LinkedIn Profile</label>
                <input v-model="editData.linkedin" type="url" :disabled="!isEditMode"
                  placeholder="https://linkedin.com/in/yourprofile" />
              </div>

              <div class="form-group full-width">
                <label>Portfolio/Website</label>
                <input v-model="editData.portfolio" type="url" :disabled="!isEditMode"
                  placeholder="https://yourportfolio.com" />
              </div>
            </div>
          </div>

          <!-- Professional Summary -->
          <div class="info-card">
            <h3><i class="fas fa-file-alt"></i> Professional Summary</h3>
            <div class="form-group">
              <label>About Me</label>
              <textarea v-model="editData.summary" :disabled="!isEditMode" rows="6"
                placeholder="Write a brief professional summary about yourself..."></textarea>
              <p class="char-count" v-if="isEditMode">
                {{ editData.summary?.length || 0 }}/500 characters
              </p>
            </div>
          </div>

          <!-- Skills -->
          <div class="info-card">
            <h3><i class="fas fa-code"></i> Skills</h3>
            <div class="form-group">
              <label>Your Skills</label>
              <div class="skills-input" v-if="isEditMode">
                <input v-model="newSkill" type="text" placeholder="Add a skill and press Enter"
                  @keypress.enter.prevent="addSkill" />
                <button @click="addSkill" class="btn-add-skill">
                  <i class="fas fa-plus"></i>
                  Add
                </button>
              </div>

              <div class="skills-list">
                <div v-for="(skill, index) in editData.skills" :key="index" class="skill-tag">
                  <span>{{ skill }}</span>
                  <button v-if="isEditMode" @click="removeSkill(index)" class="remove-skill">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <p v-if="editData.skills.length === 0" class="no-skills">
                  No skills added yet
                </p>
              </div>
            </div>
          </div>

          <!-- Experience -->
          <div class="info-card">
            <div class="card-header-with-action">
              <h3><i class="fas fa-briefcase"></i> Work Experience</h3>
              <button v-if="isEditMode" @click="addExperience" class="btn-add">
                <i class="fas fa-plus"></i>
                Add Experience
              </button>
            </div>

            <div class="experience-list">
              <div v-for="(exp, index) in editData.experience" :key="index" class="experience-item">
                <div class="experience-header">
                  <div class="experience-icon">
                    <i class="fas fa-building"></i>
                  </div>
                  <div class="experience-details" v-if="!isEditMode">
                    <h4>{{ exp.title }}</h4>
                    <p class="company">{{ exp.company }}</p>
                    <p class="duration">
                      {{ exp.startDate }} - {{ exp.endDate || 'Present' }}
                    </p>
                    <p class="description">{{ exp.description }}</p>
                  </div>
                  <div class="experience-form" v-else>
                    <input v-model="exp.title" type="text" placeholder="Job Title" class="form-control" />
                    <input v-model="exp.company" type="text" placeholder="Company Name" class="form-control" />
                    <div class="date-range">
                      <input v-model="exp.startDate" type="month" placeholder="Start Date" class="form-control" />
                      <input v-model="exp.endDate" type="month" placeholder="End Date" class="form-control" />
                    </div>
                    <textarea v-model="exp.description" rows="3"
                      placeholder="Describe your responsibilities and achievements..." class="form-control"></textarea>
                    <button @click="removeExperience(index)" class="btn-remove">
                      <i class="fas fa-trash"></i>
                      Remove
                    </button>
                  </div>
                </div>
              </div>

              <p v-if="editData.experience.length === 0" class="no-experience">
                No work experience added yet
              </p>
            </div>
          </div>

          <!-- Education -->
          <div class="info-card">
            <div class="card-header-with-action">
              <h3><i class="fas fa-graduation-cap"></i> Education</h3>
              <button v-if="isEditMode" @click="addEducation" class="btn-add">
                <i class="fas fa-plus"></i>
                Add Education
              </button>
            </div>

            <div class="education-list">
              <div v-for="(edu, index) in editData.education" :key="index" class="education-item">
                <div class="education-icon">
                  <i class="fas fa-university"></i>
                </div>
                <div class="education-details" v-if="!isEditMode">
                  <h4>{{ edu.degree }}</h4>
                  <p class="school">{{ edu.school }}</p>
                  <p class="year">{{ edu.year }}</p>
                  <p class="gpa" v-if="edu.gpa">GPA: {{ edu.gpa }}</p>
                </div>
                <div class="education-form" v-else>
                  <input v-model="edu.degree" type="text" placeholder="Degree/Certification" class="form-control" />
                  <input v-model="edu.school" type="text" placeholder="School/University" class="form-control" />
                  <input v-model="edu.year" type="text" placeholder="Year (e.g., 2020-2024)" class="form-control" />
                  <input v-model="edu.gpa" type="text" placeholder="GPA (optional)" class="form-control" />
                  <button @click="removeEducation(index)" class="btn-remove">
                    <i class="fas fa-trash"></i>
                    Remove
                  </button>
                </div>
              </div>

              <p v-if="editData.education.length === 0" class="no-education">
                No education added yet
              </p>
            </div>
          </div>

          <!-- Preferences -->
          <div class="info-card">
            <h3><i class="fas fa-sliders-h"></i> Job Preferences</h3>
            <div class="form-grid">
              <div class="form-group">
                <label>Desired Job Title</label>
                <input v-model="editData.preferences.jobTitle" type="text" :disabled="!isEditMode"
                  placeholder="e.g., Software Engineer" />
              </div>

              <div class="form-group">
                <label>Expected Salary</label>
                <input v-model="editData.preferences.salary" type="text" :disabled="!isEditMode"
                  placeholder="e.g., $80,000 - $100,000" />
              </div>

              <div class="form-group">
                <label>Preferred Location</label>
                <input v-model="editData.preferences.location" type="text" :disabled="!isEditMode"
                  placeholder="e.g., Remote, New York" />
              </div>

              <div class="form-group">
                <label>Employment Type</label>
                <select v-model="editData.preferences.employmentType" :disabled="!isEditMode">
                  <option value="">Select type</option>
                  <option value="full-time">Full Time</option>
                  <option value="part-time">Part Time</option>
                  <option value="contract">Contract</option>
                  <option value="internship">Internship</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Resume Upload Modal -->
      <ResumeUploadModal v-if="showResumeUploadModal" @close="closeResumeUploadModal"
        @resume-uploaded="handleResumeUploaded" />

      <!-- Success/Error Messages -->
      <div v-if="successMessage" class="toast success">
        <i class="fas fa-check-circle"></i>
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="toast error">
        <i class="fas fa-exclamation-circle"></i>
        {{ errorMessage }}
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import DashboardLayout from './DashboardLayout.vue'
import ResumeUploadModal from './ResumeUploadModal.vue'
import axios from 'axios'

const router = useRouter()

// State
const isEditMode = ref(false)
const saving = ref(false)
const resumeLoading = ref(false)
const showResumeUploadModal = ref(false)
const selectedResumeId = ref(null)
const successMessage = ref('')
const errorMessage = ref('')
const newSkill = ref('')
const uploading = ref(false)
const uploadError = ref(null)

const profileData = ref({
  id: '',
  name: '',
  email: '',
  role_name: '',
  created_at: '',
  phone: '',
  location: '',
  linkedin: '',
  portfolio: ''
})

const editData = ref({
  name: '',
  email: '',
  phone: '',
  location: '',
  linkedin: '',
  portfolio: '',
  summary: '',
  skills: [],
  experience: [],
  education: [],
  preferences: {
    jobTitle: '',
    salary: '',
    location: '',
    employmentType: ''
  }
})

const resumes = ref([])

const stats = ref({
  applications: 0,
  interviews: 0,
  views: 0
})

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

const formatFileSize = (bytes) => {
  if (!bytes) return '0 KB'
  const kb = bytes / 1024
  if (kb < 1024) return `${kb.toFixed(1)} KB`
  return `${(kb / 1024).toFixed(1)} MB`
}

const showToast = (message, type = 'success') => {
  if (type === 'success') {
    successMessage.value = message
    setTimeout(() => successMessage.value = '', 3000)
  } else {
    errorMessage.value = message
    setTimeout(() => errorMessage.value = '', 3000)
  }
}

// API Functions
const loadUserProfile = async () => {
  try {
    const response = await axios.get('/api/users/', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      profileData.value = response.data

      // Initialize edit data
      editData.value = {
        name: response.data.name || '',
        email: response.data.email || '',
        phone: response.data.phone || '',
        location: response.data.location || '',
        linkedin: response.data.linkedin || '',
        portfolio: response.data.portfolio || '',
        summary: response.data.summary || '',
        skills: response.data.skills || [],
        experience: response.data.experience || [],
        education: response.data.education || [],
        preferences: response.data.preferences || {
          jobTitle: '',
          salary: '',
          location: '',
          employmentType: ''
        }
      }
    }
  } catch (error) {
    console.error('Failed to load profile:', error)
    showToast('Failed to load profile', 'error')
  }
}

const loadResumes = async () => {
  try {
    resumeLoading.value = true

    const response = await axios.get('/api/files/', {
      params: { category: 'resume' },
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data && response.data.data) {
      resumes.value = response.data.data

      // Set first resume as selected
      if (resumes.value.length > 0) {
        selectedResumeId.value = resumes.value[0].id
      }
    }
  } catch (error) {
    console.error('Failed to load resumes:', error)
    showToast('Failed to load resumes', 'error')
  } finally {
    resumeLoading.value = false
  }
}

const loadStats = async () => {
  try {
    // Load applications count
    const appsResponse = await axios.get('/api/applications/', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    stats.value.applications = appsResponse.data?.length || 0

    // You can add more stats loading here
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

// Edit Mode Functions
const toggleEditMode = () => {
  isEditMode.value = true
}

const cancelEdit = () => {
  isEditMode.value = false
  // Reset edit data to original
  loadUserProfile()
}

const saveProfile = async () => {
  try {
    saving.value = true

    const response = await axios.put(
      `/api/users/${profileData.value.id}`,
      editData.value,
      {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      }
    )

    if (response.data) {
      profileData.value = { ...profileData.value, ...editData.value }
      isEditMode.value = false
      showToast('Profile updated successfully!')
    }
  } catch (error) {
    console.error('Failed to save profile:', error)
    showToast('Failed to save profile', 'error')
  } finally {
    saving.value = false
  }
}

// Skills Functions
const addSkill = () => {
  const skill = newSkill.value.trim()
  if (skill && !editData.value.skills.includes(skill)) {
    editData.value.skills.push(skill)
    newSkill.value = ''
  }
}

const removeSkill = (index) => {
  editData.value.skills.splice(index, 1)
}

// Experience Functions
const addExperience = () => {
  editData.value.experience.push({
    title: '',
    company: '',
    startDate: '',
    endDate: '',
    description: ''
  })
}

const removeExperience = (index) => {
  editData.value.experience.splice(index, 1)
}

// Education Functions
const addEducation = () => {
  editData.value.education.push({
    degree: '',
    school: '',
    year: '',
    gpa: ''
  })
}

const removeEducation = (index) => {
  editData.value.education.splice(index, 1)
}

// Resume Functions
const openResumeUploadModal = () => {

  showResumeUploadModal.value = true
}

const closeResumeUploadModal = () => {
  showResumeUploadModal.value = false
}

const handleResumeUploaded = async (resumeData) => {
  showToast('Resume uploaded successfully!')
  await loadResumes()
  closeResumeUploadModal()
}

const downloadResume = async (resume) => {
  try {
    const response = await axios.get(`/api/files/${resume.id}/download`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` },
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', resume.original_filename || resume.filename)
    document.body.appendChild(link)
    link.click()
    link.remove()

    showToast('Resume downloaded!')
  } catch (error) {
    console.error('Failed to download resume:', error)
    showToast('Failed to download resume', 'error')
  }
}

const viewResume = (resume) => {
  window.open(resume.file_path, '_blank')
}

const deleteResume = async (resumeId) => {
  if (!confirm('Are you sure you want to delete this resume?')) return

  try {
    await axios.delete(`/api/files/delete/${resumeId}`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    showToast('Resume deleted successfully!')
    await loadResumes()
  } catch (error) {
    console.error('Failed to delete resume:', error)
    showToast('Failed to delete resume', 'error')
  }
}

// Load data on mount
onMounted(async () => {
  await Promise.all([
    loadUserProfile(),
    loadResumes(),
    loadStats()
  ])
})
</script>

<style scoped>
.candidate-profile-page {
  padding: 0;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-left h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left p {
  color: #7f8c8d;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-edit,
.btn-save,
.btn-cancel {
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

.btn-edit {
  background: #3498db;
  color: white;
}

.btn-save {
  background: #27ae60;
  color: white;
}

.btn-cancel {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-edit:hover {
  background: #2980b9;
}

.btn-save:hover:not(:disabled) {
  background: #229954;
}

.btn-cancel:hover {
  background: #d5dbdb;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Profile Grid */
.profile-grid {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 30px;
}

/* Profile Card */
.profile-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.profile-avatar {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.avatar-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 3rem;
}

.change-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #3498db;
  color: white;
  border: 3px solid white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-basic-info h2 {
  font-size: 1.5rem;
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.role-badge {
  background: #e8f4f8;
  color: #2980b9;
  padding: 6px 12px;
  border-radius: 20px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.profile-basic-info .email,
.profile-basic-info .member-since {
  color: #7f8c8d;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin: 5px 0;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.stat {
  text-align: center;
}

.stat h3 {
  font-size: 1.8rem;
  margin: 0;
  color: #3498db;
}

.stat p {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin: 5px 0 0 0;
}

/* Resume Card */
.resume-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-upload-resume {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.loading-state {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.loading-state i {
  font-size: 2rem;
  margin-bottom: 10px;
  display: block;
}

.resume-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resume-item {
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.resume-item.active {
  border-color: #3498db;
  background: #e8f4f8;
}

.resume-icon {
  width: 45px;
  height: 45px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #e74c3c;
}

.resume-info {
  flex: 1;
}

.resume-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 0.95rem;
}

.resume-meta {
  display: flex;
  gap: 15px;
  font-size: 0.8rem;
  color: #7f8c8d;
}

.resume-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.resume-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 35px;
  height: 35px;
  border: none;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7f8c8d;
  transition: all 0.3s ease;
}

.btn-icon:hover {
  background: #3498db;
  color: white;
}

.btn-icon.delete:hover {
  background: #e74c3c;
  color: white;
}

.empty-resume-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 3rem;
  color: #bdc3c7;
  margin-bottom: 15px;
}

.empty-resume-state h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.empty-resume-state p {
  color: #7f8c8d;
  margin: 0 0 20px 0;
}

.btn-upload-primary {
  background: #3498db;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

/* Quick Links */
.quick-links-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin-top: 20px;
}

.quick-links-card h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
}

.links-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  text-decoration: none;
  color: #2c3e50;
  transition: all 0.3s ease;
}

.link-item:hover {
  background: #e8f4f8;
  color: #3498db;
}

.link-item i:first-child {
  width: 20px;
  text-align: center;
}

.link-item span {
  flex: 1;
}

/* Info Cards */
.info-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.info-card h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
}

.card-header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header-with-action h3 {
  margin: 0;
}

.btn-add {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Form Elements */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px 15px;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
}

.form-group input:disabled,
.form-group select:disabled,
.form-group textarea:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.char-count {
  text-align: right;
  font-size: 0.85rem;
  color: #7f8c8d;
  margin: 0;
}

/* Skills */
.skills-input {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.skills-input input {
  flex: 1;
}

.btn-add-skill {
  background: #27ae60;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.skill-tag {
  background: #e8f4f8;
  color: #2980b9;
  padding: 8px 12px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
}

.remove-skill {
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  padding: 0;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.remove-skill:hover {
  background: rgba(231, 76, 60, 0.1);
}

.no-skills {
  color: #7f8c8d;
  font-style: italic;
}

/* Experience & Education */
.experience-list,
.education-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.experience-item,
.education-item {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.experience-header {
  display: flex;
  gap: 15px;
}

.experience-icon,
.education-icon {
  width: 45px;
  height: 45px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  color: #3498db;
  flex-shrink: 0;
}

.experience-details,
.education-details {
  flex: 1;
}

.experience-details h4,
.education-details h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.company,
.school {
  color: #7f8c8d;
  margin: 0 0 5px 0;
}

.duration,
.year {
  color: #95a5a6;
  font-size: 0.85rem;
  margin: 0 0 10px 0;
}

.description,
.gpa {
  color: #7f8c8d;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

.experience-form,
.education-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-control {
  padding: 10px 12px;
  border: 1px solid #ecf0f1;
  border-radius: 6px;
  font-size: 0.95rem;
}

.date-range {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.btn-remove {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  align-self: flex-start;
}

.no-experience,
.no-education {
  color: #7f8c8d;
  font-style: italic;
  text-align: center;
  padding: 30px;
}

/* Toast Messages */
.toast {
  position: fixed;
  bottom: 30px;
  right: 30px;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  z-index: 10000;
  animation: slideIn 0.3s ease;
}

.toast.success {
  background: #27ae60;
  color: white;
}

.toast.error {
  background: #e74c3c;
  color: white;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }

  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 1024px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-group.full-width {
    grid-column: 1;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .header-actions {
    width: 100%;
  }

  .btn-edit,
  .btn-save,
  .btn-cancel {
    flex: 1;
  }

  .profile-stats {
    grid-template-columns: 1fr;
  }
}
</style>