<template>
  <DashboardLayout>
    <div class="applications-page">
      <!-- Header Section -->
      <div class="page-header">
        <div class="header-content">
          <h1><i class="fas fa-paper-plane"></i> My Applications</h1>
          <p>Track and manage your job applications</p>
        </div>
        <div class="header-actions">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search applications..."
              @input="filterApplications"
            />
          </div>
          <select v-model="filterStatus" @change="filterApplications" class="filter-select">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="under review">Under Review</option>
            <option value="shortlisted">Shortlisted</option>
            <option value="interviewed">Interviewed</option>
            <option value="rejected">Rejected</option>
            <option value="accepted">Accepted</option>
          </select>
        </div>
      </div>

      <!-- Stats Overview -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon total">
            <i class="fas fa-paper-plane"></i>
          </div>
          <div class="stat-info">
            <h3>{{ totalApplications }}</h3>
            <p>Total Applications</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon pending">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-info">
            <h3>{{ pendingCount }}</h3>
            <p>Pending</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon shortlisted">
            <i class="fas fa-star"></i>
          </div>
          <div class="stat-info">
            <h3>{{ shortlistedCount }}</h3>
            <p>Shortlisted</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon interviewed">
            <i class="fas fa-calendar-check"></i>
          </div>
          <div class="stat-info">
            <h3>{{ interviewedCount }}</h3>
            <p>Interviewed</p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner">
          <i class="fas fa-spinner fa-spin"></i>
        </div>
        <p>Loading applications...</p>
      </div>

      <!-- Applications List -->
      <div v-else-if="filteredApplications.length > 0" class="applications-list">
        <div 
          v-for="app in filteredApplications" 
          :key="app.id" 
          class="application-card"
          :class="`status-${app.status?.toLowerCase().replace(' ', '-')}`"
        >
          <!-- Application Header -->
          <div class="application-header">
            <div class="job-icon">
              <i class="fas fa-briefcase"></i>
            </div>
            <div class="application-info">
              <h3>{{ app.job_title || 'Position Title' }}</h3>
              <p class="company">
                <i class="fas fa-building"></i>
                {{ app.company || 'Company Name' }}
              </p>
              <p class="applied-date">
                <i class="fas fa-calendar"></i>
                Applied on {{ formatDate(app.created_at) }}
              </p>
            </div>
            <div class="status-badge" :class="app.status?.toLowerCase().replace(' ', '-')">
              <i :class="getStatusIcon(app.status)"></i>
              {{ app.status || 'Pending' }}
            </div>
          </div>

          <!-- Application Details -->
          <div class="application-details">
            <div class="detail-row">
              <div class="detail-item" v-if="app.location">
                <i class="fas fa-map-marker-alt"></i>
                <span>{{ app.location }}</span>
              </div>
              <div class="detail-item" v-if="app.employment_type">
                <i class="fas fa-briefcase"></i>
                <span>{{ app.employment_type }}</span>
              </div>
              <div class="detail-item" v-if="app.salary">
                <i class="fas fa-dollar-sign"></i>
                <span>{{ formatSalary(app.salary) }}</span>
              </div>
            </div>
            
            <!-- Cover Letter Preview -->
            <div class="cover-letter-preview" v-if="app.cover_letter">
              <strong>Cover Letter:</strong>
              <p>{{ truncateText(app.cover_letter, 150) }}</p>
            </div>

            <!-- Resume Info -->
            <div class="resume-info" v-if="app.resume_file">
              <i class="fas fa-file-pdf"></i>
              <span>{{ app.resume_file }}</span>
            </div>
          </div>

          <!-- Pipeline Status (if available) -->
          <div class="pipeline-status" v-if="app.pipeline_stage">
            <div class="pipeline-header">
              <i class="fas fa-stream"></i>
              <strong>Application Pipeline</strong>
            </div>
            <div class="pipeline-stages">
              <div 
                v-for="stage in getPipelineStages(app)" 
                :key="stage.name"
                class="stage"
                :class="{ active: stage.active, completed: stage.completed }"
              >
                <div class="stage-icon">
                  <i :class="stage.completed ? 'fas fa-check-circle' : 'fas fa-circle'"></i>
                </div>
                <span>{{ stage.name }}</span>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="application-actions">
            <button @click="viewDetails(app)" class="btn-secondary">
              <i class="fas fa-eye"></i>
              View Details
            </button>
            <button 
              v-if="app.status === 'pending'" 
              @click="withdrawApplication(app)" 
              class="btn-danger"
            >
              <i class="fas fa-times"></i>
              Withdraw
            </button>
            <button 
              v-if="app.status === 'shortlisted'" 
              @click="scheduleInterview(app)" 
              class="btn-primary"
            >
              <i class="fas fa-calendar"></i>
              Schedule Interview
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-inbox"></i>
        </div>
        <h3>No Applications Found</h3>
        <p v-if="searchQuery || filterStatus">
          No applications match your filters.
        </p>
        <p v-else>
          You haven't submitted any applications yet.
        </p>
        <button @click="clearFilters" class="btn-primary" v-if="searchQuery || filterStatus">
          <i class="fas fa-times"></i>
          Clear Filters
        </button>
        <button @click="navigateToJobs" class="btn-primary" v-else>
          <i class="fas fa-search"></i>
          Browse Jobs
        </button>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import DashboardLayout from './DashboardLayout.vue'
import axios from 'axios'

const router = useRouter()

// State
const loading = ref(false)
const allApplications = ref([])
const searchQuery = ref('')
const filterStatus = ref('')

// Computed
const filteredApplications = computed(() => {
  let apps = [...allApplications.value]
  
  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    apps = apps.filter(app => 
      app.job_title?.toLowerCase().includes(query) ||
      app.company?.toLowerCase().includes(query) ||
      app.location?.toLowerCase().includes(query)
    )
  }
  
  // Filter by status
  if (filterStatus.value) {
    apps = apps.filter(app => 
      app.status?.toLowerCase() === filterStatus.value.toLowerCase()
    )
  }
  
  // Sort by date (newest first)
  return apps.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const totalApplications = computed(() => allApplications.value?.length || 0)

const pendingCount = computed(() => 
  allApplications.value.filter(app => app.status?.toLowerCase() === 'pending').length
)

const shortlistedCount = computed(() => 
  allApplications.value.filter(app => app.status?.toLowerCase() === 'shortlisted').length
)

const interviewedCount = computed(() => 
  allApplications.value.filter(app => app.status?.toLowerCase() === 'interviewed').length
)

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

const truncateText = (text, length) => {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatSalary = (salary) => {
  if (!salary) return null
  return `$${new Intl.NumberFormat('en-US').format(salary)}`
}

const getStatusIcon = (status) => {
  const iconMap = {
    'pending': 'fas fa-clock',
    'under review': 'fas fa-search',
    'shortlisted': 'fas fa-star',
    'interviewed': 'fas fa-calendar-check',
    'rejected': 'fas fa-times-circle',
    'accepted': 'fas fa-check-circle'
  }
  return iconMap[status?.toLowerCase()] || 'fas fa-circle'
}

const getPipelineStages = (application) => {
  // Define default pipeline stages
  const defaultStages = [
    { name: 'Applied', completed: true, active: false },
    { name: 'Screening', completed: false, active: false },
    { name: 'Interview', completed: false, active: false },
    { name: 'Offer', completed: false, active: false }
  ]
  
  // Update based on application status
  const status = application.status?.toLowerCase()
  
  if (status === 'under review' || status === 'shortlisted') {
    defaultStages[1].completed = true
  }
  if (status === 'interviewed') {
    defaultStages[1].completed = true
    defaultStages[2].completed = true
  }
  if (status === 'accepted') {
    defaultStages.forEach(stage => stage.completed = true)
  }
  
  // Mark current active stage
  const activeIndex = defaultStages.findIndex(stage => !stage.completed)
  if (activeIndex !== -1) {
    defaultStages[activeIndex].active = true
  }
  
  return defaultStages
}

// API Functions
const loadApplications = async () => {
  try {
    loading.value = true
    
    const response = await axios.get('/api/applications/', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    
    console.log('Applications response:', response.data)
    
    // Handle different response structures
    if (response.data?.applications) {
      allApplications.value = response.data.applications
    } else if (Array.isArray(response.data)) {
      allApplications.value = response.data
    } else {
      allApplications.value = []
    }
    
    console.log(`Loaded ${allApplications.value.length} applications`)
  } catch (error) {
    console.error('Failed to load applications:', error)
    allApplications.value = []
  } finally {
    loading.value = false
  }
}

// Action Functions
const filterApplications = () => {
  // Filtering is handled by computed property
  console.log('Filtering applications...')
}

const clearFilters = () => {
  searchQuery.value = ''
  filterStatus.value = ''
}

const viewDetails = (application) => {
  router.push(`/candidate/application/${application.id}`)
}

const withdrawApplication = async (application) => {
  if (!confirm('Are you sure you want to withdraw this application?')) return
  
  try {
    await axios.delete(`/api/applications/${application.id}`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    
    alert('Application withdrawn successfully')
    await loadApplications()
  } catch (error) {
    console.error('Failed to withdraw application:', error)
    alert('Failed to withdraw application')
  }
}

const scheduleInterview = (application) => {
  // Navigate to interview scheduling or open modal
  router.push(`/candidate/interview/schedule/${application.id}`)
}

const navigateToJobs = () => {
  router.push('/candidate/job-search')
}

// Load data on mount
onMounted(async () => {
  await loadApplications()
})
</script>

<style scoped>
.applications-page {
  padding: 0;
}

/* Header Section - Same as Vacancies */
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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
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

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.pending {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.shortlisted {
  background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
}

.stat-icon.interviewed {
  background: linear-gradient(135deg, #55efc4 0%, #00b894 100%);
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

/* Loading & Empty States */
.loading-container,
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner i,
.empty-icon i {
  font-size: 3rem;
  color: #3498db;
  margin-bottom: 20px;
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

/* Applications List */
.applications-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.application-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  border-left: 4px solid #3498db;
  transition: all 0.3s ease;
}

.application-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.application-card.status-pending {
  border-left-color: #f39c12;
}

.application-card.status-shortlisted {
  border-left-color: #f1c40f;
}

.application-card.status-interviewed {
  border-left-color: #2ecc71;
}

.application-card.status-rejected {
  border-left-color: #e74c3c;
}

.application-card.status-accepted {
  border-left-color: #27ae60;
}

/* Application Header */
.application-header {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ecf0f1;
}

.job-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.application-info {
  flex: 1;
}

.application-info h3 {
  font-size: 1.4rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.application-info p {
  margin: 4px 0;
  color: #7f8c8d;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.95rem;
}

.status-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.under-review {
  background: #cfe2ff;
  color: #084298;
}

.status-badge.shortlisted {
  background: #fff3cd;
  color: #664d03;
}

.status-badge.interviewed {
  background: #d1e7dd;
  color: #0f5132;
}

.status-badge.rejected {
  background: #f8d7da;
  color: #842029;
}

.status-badge.accepted {
  background: #d1e7dd;
  color: #0a3622;
}

/* Application Details */
.application-details {
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7f8c8d;
  font-size: 0.95rem;
}

.detail-item i {
  color: #3498db;
}

.cover-letter-preview {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.cover-letter-preview strong {
  color: #2c3e50;
  display: block;
  margin-bottom: 8px;
}

.cover-letter-preview p {
  margin: 0;
  color: #7f8c8d;
  line-height: 1.6;
}

.resume-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #3498db;
  font-size: 0.95rem;
}

/* Pipeline Status */
.pipeline-status {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.pipeline-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;
  color: #2c3e50;
}

.pipeline-stages {
  display: flex;
  justify-content: space-between;
  position: relative;
}

.pipeline-stages::before {
  content: '';
  position: absolute;
  top: 15px;
  left: 30px;
  right: 30px;
  height: 2px;
  background: #ecf0f1;
  z-index: 0;
}

.stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.stage-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: white;
  border: 2px solid #ecf0f1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bdc3c7;
}

.stage.completed .stage-icon {
  border-color: #27ae60;
  color: #27ae60;
  background: #d1e7dd;
}

.stage.active .stage-icon {
  border-color: #3498db;
  color: #3498db;
  background: #cfe2ff;
}

.stage span {
  font-size: 0.85rem;
  color: #7f8c8d;
  text-align: center;
}

.stage.active span {
  color: #3498db;
  font-weight: 600;
}

/* Action Buttons */
.application-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.application-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-secondary {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-secondary:hover {
  background: #d5dbdb;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

@media (max-width: 768px) {
  .application-header {
    flex-direction: column;
  }
  
  .pipeline-stages {
    flex-direction: column;
    gap: 15px;
  }
  
  .pipeline-stages::before {
    display: none;
  }
  
  .application-actions {
    flex-direction: column;
  }
  
  .application-actions button {
    width: 100%;
    justify-content: center;
  }
}
</style>