<template>
  <DashboardLayout>
    <div class="job-recommendations-page">
      <!-- Header Section -->
      <div class="page-header">
        <div class="header-content">
          <h1><i class="fas fa-briefcase"></i> Job Recommendations</h1>
          <p>AI-powered job matches based on your profile and resume</p>
        </div>
        <div class="header-actions">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input v-model="searchQuery" type="text" placeholder="Search jobs..." @input="filterJobs" />
          </div>
          <select v-model="filterStatus" @change="filterJobs" class="filter-select">
            <option value="all">All Jobs</option>
            <option value="active">Active</option>
            <option value="applied">Already Applied</option>
          </select>
        </div>
      </div>

      <!-- Stats Overview -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon recommended">
            <i class="fas fa-star"></i>
          </div>
          <div class="stat-info">
            <h3>{{ totalRecommendations }}</h3>
            <p>Recommended Jobs</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon applied">
            <i class="fas fa-paper-plane"></i>
          </div>
          <div class="stat-info">
            <h3>{{ appliedCount }}</h3>
            <p>Applications Sent</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon match">
            <i class="fas fa-percentage"></i>
          </div>
          <div class="stat-info">
            <h3>{{ avgMatchScore }}%</h3>
            <p>Avg Match Score</p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner">
          <i class="fas fa-spinner fa-spin"></i>
        </div>
        <p>Loading job recommendations...</p>
      </div>

      <!-- Jobs Grid -->
      <div v-else-if="filteredJobs.length > 0" class="jobs-grid">
        <div v-for="job in filteredJobs" :key="job.job_id" class="job-card"
          :class="{ applied: isJobApplied(job.job_id) }">
          <!-- Match Score Badge -->
          <div class="match-badge" v-if="job.matchScore">
            <i class="fas fa-chart-line"></i>
            {{ job.matchScore }}% Match
          </div>

          <!-- Job Header -->
          <div class="job-header">
            <div class="company-logo">
              <img :src="job.companyLogo || '/default-company-logo.png'" :alt="job.company" />
            </div>
            <div class="job-title-section">
              <h3>{{ job.title }}</h3>
              <p class="company-name">
                <i class="fas fa-building"></i>
                {{ job.company || 'Company Name' }}
              </p>
            </div>
          </div>

          <!-- Job Details -->
          <div class="job-details">
            <div class="detail-item">
              <i class="fas fa-map-marker-alt"></i>
              <span>{{ job.location || job.requirements || 'Location not specified' }}</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-briefcase"></i>
              <span>{{ job.employment_type || 'Full-time' }}</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-dollar-sign"></i>
              <span>{{ formatSalary(job.salary) || 'Salary not disclosed' }}</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-clock"></i>
              <span>Posted {{ getTimeAgo(job.created_at) }}</span>
            </div>
          </div>

          <!-- Job Description Preview -->
          <div class="job-description">
            <p>{{ truncateText(job.description, 150) }}</p>
          </div>

          <!-- Skills/Tags -->
          <div class="job-tags" v-if="job.required_skills || job.tags">
            <span v-for="(skill, index) in getSkills(job)" :key="index" class="tag">
              {{ skill }}
            </span>
          </div>

          <!-- Status Badge -->
          <div class="job-status">
            <span class="status-badge" :class="job.status">
              <i :class="getStatusIcon(job.status)"></i>
              {{ job.status || 'Active' }}
            </span>
          </div>

          <!-- Action Buttons -->
          <div class="job-actions">
            <button @click="viewJobDetails(job)" class="btn-secondary">
              <i class="fas fa-eye"></i>
              View Details
            </button>
            <button v-if="!isJobApplied(job.job_id)" @click="openApplyModal(job)" class="btn-primary">
              <i class="fas fa-paper-plane"></i>
              Apply Now
            </button>
            <button v-else class="btn-applied" disabled>
              <i class="fas fa-check-circle"></i>
              Applied
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-search"></i>
        </div>
        <h3>No Job Recommendations Found</h3>
        <p>We couldn't find any job recommendations matching your criteria.</p>
        <button @click="refreshRecommendations" class="btn-primary">
          <i class="fas fa-sync-alt"></i>
          Refresh Recommendations
        </button>
      </div>
      <!-- job details modal -->
      <JobDetailsModal v-if="showDetailsModal && selectedJob" :job-id="selectedJob.job_id" :user-id="user_id"
        @close="closeDetailsModal" @apply="handleDetailsApply" />
      <!-- Application Modal -->
      <JobApplicationModal v-if="showApplyModal" :job="selectedJob" :userId="user_id" @close="closeApplyModal"
        @application-submitted="handleApplicationSubmitted" />
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import DashboardLayout from './DashboardLayout.vue'
import JobApplicationModal from './JobApplicationModal.vue'
import JobDetailsModal from './JobDetailsModal.vue'
import axios from 'axios'

const router = useRouter()

// State
const user_id = ref('')
const loading = ref(false)
const recommendedJobs = ref([])
const appliedJobs = ref([])
const searchQuery = ref('')
const filterStatus = ref('all')
const showApplyModal = ref(false)
const selectedJob = ref(null)
const showDetailsModal = ref(false)
// Computed
const filteredJobs = computed(() => {
  let jobs = [...recommendedJobs.value]

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    jobs = jobs.filter(job =>
      job.title.toLowerCase().includes(query) ||
      (job.company && job.company.toLowerCase().includes(query)) ||
      (job.description && job.description.toLowerCase().includes(query))
    )
  }

  // Filter by status
  if (filterStatus.value === 'active') {
    jobs = jobs.filter(job => !isJobApplied(job.job_id))
  } else if (filterStatus.value === 'applied') {
    jobs = jobs.filter(job => isJobApplied(job.job_id))
  }

  return jobs
})

const totalRecommendations = computed(() => recommendedJobs?.value.length)

const appliedCount = computed(() => appliedJobs?.value.length)



const avgMatchScore = computed(() => {
  if (recommendedJobs?.value.length === 0) return 0
  const total = recommendedJobs.value.reduce((sum, job) => sum + (job.matchScore || 0), 0)
  return Math.round(total / recommendedJobs.value.length)
})

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

const isJobApplied = (jobId) => {
  // Return false if no applied jobs or invalid jobId
  // if (!jobId || !appliedJobs.value?.length) return false

  // Check if any application matches this job
  // console.log(jobId)
  if (!jobId || !appliedJobs.value?.length) return false

  // Check if any application matches this job
  return appliedJobs.value.some(app => {
    const appJobId = app?.job_id || app?.job?.id
    return appJobId === jobId

  })
}
const truncateText = (text, length) => {
  if (!text) return 'No description available'
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

const formatSalary = (salary) => {
  if (!salary) return null
  return `$${new Intl.NumberFormat('en-US').format(salary)}`
}

const getTimeAgo = (dateString) => {
  if (!dateString) return 'Recently'

  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  return `${Math.floor(diffDays / 30)} months ago`
}

const getSkills = (job) => {
  if (job.required_skills) {
    return typeof job.required_skills === 'string'
      ? job.required_skills.split(',').map(s => s.trim()).slice(0, 5)
      : job.required_skills.slice(0, 5)
  }
  if (job.tags) {
    return typeof job.tags === 'string'
      ? job.tags.split(',').map(s => s.trim()).slice(0, 5)
      : job.tags.slice(0, 5)
  }
  return []
}

const getStatusIcon = (status) => {
  const iconMap = {
    'active': 'fas fa-check-circle',
    'inactive': 'fas fa-times-circle',
    'closed': 'fas fa-lock'
  }
  return iconMap[status?.toLowerCase()] || 'fas fa-circle'
}



// API Functions
const loadUserData = async () => {
  try {
    const response = await axios.get('/api/users/', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      user_id.value = response.data.id
      console.log(user_id?.value)
    }
  } catch (error) {
    console.error('Failed to load user data:', error)
  }
}

const loadRecommendedJobs = async () => {
  try {
    loading.value = true

    // Get user's resume
    const resumeResponse = await axios.get('/api/files/resume', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    console.log('Resume response:', resumeResponse.data)

    if (!resumeResponse.data || resumeResponse.data.length === 0) {
      console.log('No resume found')
      // Fallback to regular jobs
      await loadAllJobs()
      return
    }

    // Get the latest resume based on uploaded_at timestamp
    let latestResume
    if (Array.isArray(resumeResponse.data)) {
      // Sort by uploaded_at descending and get the first one
      latestResume = resumeResponse.data.sort((a, b) => 
        new Date(b.uploaded_at) - new Date(a.uploaded_at)
      )[0]
    } else {
      latestResume = resumeResponse.data
    }

    const resumeId = latestResume.id
    console.log('Using latest resume ID:', resumeId, 'uploaded at:', latestResume.uploaded_at)

    // Get AI recommendations
    const jobsResponse = await axios.get(`/api/ai/get_job_posts/${resumeId}`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (jobsResponse.data && jobsResponse.data.job_post) {
      recommendedJobs.value = jobsResponse.data.job_post.meta_data || []

      // Add match scores (you can get this from AI response)
      recommendedJobs.value = recommendedJobs.value.map((job, index) => ({
        ...job,
        matchScore: Math.round((95 - (Math.round(jobsResponse.data.job_post.distance[index]) * 10)).toFixed(2)),
      }))
      console.log('Recommended jobs:', recommendedJobs?.value)
    } else {
      await loadAllJobs()
    }
  } catch (error) {
    console.error('Failed to load recommended jobs:', error)
    await loadAllJobs()
  } finally {
    loading.value = false
  }
}

const loadAllJobs = async () => {
  try {
    const response = await axios.get('/api/jobs/', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      recommendedJobs.value = response.data
    }
  } catch (error) {
    console.error('Failed to load jobs:', error)
    recommendedJobs.value = []
  }
}

const loadAppliedJobs = async () => {
  try {
    const response = await axios.get('/api/applications/', {
      params: { candidate_id: user_id?.value },
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    console.log('Applied jobs response:', response.data)

    if (response.data) {
      appliedJobs.value = response.data.applications
    }
    else {
      console.warn('Unexpected applications response structure:', response.data)
      appliedJobs.value = []
    }

  } catch (error) {
    console.error('Failed to load applied jobs:', error)
    appliedJobs.value = []
  }
}
// Action Functions
const filterJobs = () => {
  // Filtering is handled by computed property
  //   return filteredJobs.value = recommendedJobs.value.filter(job => job.status === 'active')
}

const refreshRecommendations = async () => {
  await loadRecommendedJobs()
}

const openApplyModal = (job) => {
  // Open modal
  console.log('Opening apply modal for job:', job)
  console.log('User ID:', user_id?.value)
  if (!user_id?.value) {
    console.error('User ID not found')
  }
  selectedJob.value = job
  showApplyModal.value = true
}

const closeApplyModal = () => {
  showApplyModal.value = false
  selectedJob.value = null
}

const handleApplicationSubmitted = (applicationData) => {
  // Add to applied jobs
  appliedJobs.value.push(applicationData)

  // Close modal
  closeApplyModal()

  // Show success message
  alert(`Successfully applied to ${applicationData.job_title}!`)
}

const viewJobDetails = (job) => {
  selectedJob.value = job
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedJob.value = null
}
const handleDetailsApply = (job) => {
  // Close details modal and open apply modal
  closeDetailsModal()
  selectedJob.value = job
  showApplyModal.value = true
}


// Load data on mount
onMounted(async () => {
  try {
    await loadUserData()
    console.log('User ID:', user_id?.value)
    await Promise.all([
      loadRecommendedJobs(),
      loadAppliedJobs()
    ])
  }
  catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
})
</script>

<style scoped>
.job-recommendations-page {
  padding: 0;
}

/* Header Section */
.page-header {
  margin-bottom: 30px;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-content p {
  color: #7f8c8d;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 15px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 250px;
  position: relative;
}

.search-box i {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #7f8c8d;
}

.search-box input {
  width: 100%;
  padding: 12px 15px 12px 45px;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
}

.search-box input:focus {
  border-color: #3498db;
}

.filter-select {
  padding: 12px 20px;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
  cursor: pointer;
  background: white;
}

/* Stats Cards */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.stat-icon.recommended {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.applied {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.match {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-info h3 {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
  color: #2c3e50;
}

.stat-info p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* Loading State */
.loading-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  margin-bottom: 20px;
}

.loading-spinner i {
  font-size: 3rem;
  color: #3498db;
}

.loading-container p {
  color: #7f8c8d;
  font-size: 1rem;
}

/* Jobs Grid */
.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

.job-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
  border: 2px solid transparent;
}

.job-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: #3498db;
}

.job-card.applied {
  opacity: 0.7;
  background: #f8f9fa;
}

/* Match Badge */
.match-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
}

/* Job Header */
.job-header {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  margin-bottom: 20px;
}

.company-logo {
  width: 60px;
  height: 60px;
  flex-shrink: 0;
}

.company-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
  border: 1px solid #ecf0f1;
}

.job-title-section h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.company-name {
  color: #7f8c8d;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.95rem;
}

/* Job Details */
.job-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 15px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.detail-item i {
  color: #3498db;
  width: 16px;
  flex-shrink: 0;
}

/* Job Description */
.job-description {
  margin-bottom: 15px;
}

.job-description p {
  color: #7f8c8d;
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0;
}

/* Job Tags */
.job-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.tag {
  background: #ecf0f1;
  color: #2c3e50;
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
}

/* Job Status */
.job-status {
  margin-bottom: 20px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 0.85rem;
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

/* Job Actions */
.job-actions {
  display: flex;
  gap: 10px;
}

.job-actions button {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-secondary:hover {
  background: #d5dbdb;
}

.btn-applied {
  background: #27ae60;
  color: white;
  cursor: not-allowed;
  opacity: 0.7;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  margin-bottom: 20px;
}

.empty-icon i {
  font-size: 4rem;
  color: #bdc3c7;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 0 0 10px 0;
}

.empty-state p {
  color: #7f8c8d;
  margin: 0 0 25px 0;
}

.empty-state .btn-primary {
  display: inline-flex;
  padding: 12px 24px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .jobs-grid {
    grid-template-columns: 1fr;
  }

  .job-details {
    grid-template-columns: 1fr;
  }

  .header-actions {
    flex-direction: column;
  }

  .search-box {
    width: 100%;
  }

  .job-actions {
    flex-direction: column;
  }
}
</style>