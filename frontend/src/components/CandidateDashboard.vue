<template>
  <DashboardLayout>
    <div class="candidate-dashboard">
      <div class="welcome-section">
        <div class="welcome-text">
          <h1>Welcome back, {{ userName }}!</h1>
          <p>Here's what's happening with your job search today</p>
        </div>
        <div class="quick-stats">
          <div class="stat-card applications">
            <i class="fas fa-file-alt"></i>
            <div class="stat-info">
              <h3>{{ applicationCount }}</h3>
              <p>Applications</p>
            </div>
          </div>
          <div class="stat-card interviews">
            <i class="fas fa-calendar-check"></i>
            <div class="stat-info">
              <h3>{{ interviewCount }}</h3>
              <p>Interviews</p>
            </div>
          </div>
          <div class="stat-card profile-views">
            <i class="fas fa-eye"></i>
            <div class="stat-info">
              <h3>{{ profileView }}</h3>
              <p>Profile Views</p>
            </div>
          </div>
        </div>
      </div>

      <div class="dashboard-grid">
        <!-- Quick Actions -->
        <div class="dashboard-card quick-actions">
          <h3><i class="fas fa-bolt"></i> Quick Actions</h3>
          <div class="action-buttons">
            <button @click="navigate('candidate-profile')" class="action-btn primary">
              <i class="fas fa-user-edit"></i>
              Update Profile
            </button>
            <button @click="navigate('job-search')" class="action-btn secondary">
              <i class="fas fa-search"></i>
              Search Jobs
            </button>
            <button @click="navigate('ai-enhancement')" class="action-btn tertiary">
              <i class="fas fa-brain"></i>
              AI Enhancement
            </button>
          </div>
        </div>

        <!-- Recent Applications -->
        <div class="dashboard-card recent-applications">
          <h3><i class="fas fa-clock"></i> Recent Applications</h3>
          <div class="application-list">
            <div v-for="app in recentApplications" :key="app.id" class="application-item">
              <div class="app-info">
                <h4>{{ app.job_title }}</h4>
                <p>{{ app.company }}</p>
                <small>Applied {{ formatDate(app.applied_at) }}</small>
              </div>
              <div class="app-status" :class="app.status.toLowerCase()">
                {{ app.status }}
              </div>
            </div>
          </div>
          <button @click="navigate('applications')" class="view-all-btn">
            View All Applications
          </button>
        </div>

        <!-- Job Recommendations -->
      <div class="dashboard-card job-recommendations">
        <h3><i class="fas fa-briefcase"></i> Recommended Jobs</h3>
        
        <!-- Loading State -->
        <div v-if="jobsLoading" class="loading-state">
          <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
          </div>
          <p>Finding perfect jobs for you...</p>
        </div>
        
        <!-- Jobs List -->
        <div v-else-if="recommendedJobs && recommendedJobs.length > 0" class="job-list">
          <div v-for="job in recommendedJobs" :key="job.id" class="job-item">
            <div class="job-info">
              <h4>{{ job.title || 'Untitled Position' }}</h4>
              <p>{{ job.company || 'Unknown Company' }}</p>
              <div class="job-meta">
                <span><i class="fas fa-map-marker-alt"></i> {{ job.location || job.requirements || 'Location not specified' }}</span>
                <span class="jobStatus" :style="{ backgroundColor: getStatusColor(job.status) }">
                {{ job.status || 'Unknown Status' }}
                </span>
              </div>
            </div>
            <button @click="applyToJob(job)" class="apply-btn">Apply</button>
          </div>
        </div>
        
        <!-- Empty State -->
        <div v-else class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-briefcase"></i>
          </div>
          <h4>No Recommendations Yet</h4>
          <p>Upload your resume to get personalized job recommendations powered by AI</p>
          <button @click="navigate('candidate-profile')" class="upload-resume-btn">
            <i class="fas fa-upload"></i>
            Upload Resume
          </button>
        </div>
        
        <!-- View All Button (only show when there are jobs) -->
        <button 
          v-if="recommendedJobs && recommendedJobs.length > 0" 
          @click="navigate('job-recommend')" 
          class="view-all-btn"
        >
          View All Recommendations
        </button>
      </div>

        <!-- Profile Completeness -->
        <div class="dashboard-card profile-completion">
          <h3><i class="fas fa-chart-pie"></i>Get AI-powered Suggestions</h3>
          <div class="completion-circle">
            <div class="circle" :style="{ '--progress': profileCompletion + '%' }">
              <span>{{ profileCompletion }}%</span>
            </div>
          </div>
          <div class="completion-items">
            <div v-for="item in completionItems" :key="item.name" class="completion-item">
              <i
                :class="[item.completed ? 'fas fa-check-circle' : 'fas fa-circle', item.completed ? 'completed' : '']"></i>
              <span>{{ item.name }}</span>
            </div>
          </div>
          <button @click="navigate('candidate-profile')" class="complete-btn">
            Tailor Your Resume
          </button>
        </div>

        <!-- Upcoming Interviews -->
        <div class="dashboard-card upcoming-interviews">
          <h3><i class="fas fa-calendar-alt"></i> Upcoming Interviews</h3>
          <div v-if="upcomingInterviews.length" class="interview-list">
            <div v-for="interview in upcomingInterviews" :key="interview.id" class="interview-item">
              <div class="interview-info">
                <h4>{{ interview.jobTitle }}</h4>
                <p>{{ interview.company }}</p>
                <div class="interview-time">
                  <i class="fas fa-clock"></i>
                  {{ formatDateTime(interview.scheduledTime) }}
                </div>
              </div>
              <div class="interview-type">
                {{ interview.type }}
              </div>
            </div>
          </div>
          <div v-else class="no-interviews">
            <i class="fas fa-calendar-times"></i>
            <p>No upcoming interviews</p>
          </div>
        </div>

        <!-- AI Insights -->
        <div class="dashboard-card ai-insights">
          <h3><i class="fas fa-lightbulb"></i> AI Insights</h3>
          <div class="insight-list">
            <div v-for="insight in aiInsights" :key="insight.id" class="insight-item">
              <div class="insight-icon" :class="insight.type">
                <i :class="insight.icon"></i>
              </div>
              <div class="insight-content">
                <h4>{{ insight.title }}</h4>
                <p>{{ insight.description }}</p>
              </div>
            </div>
          </div>
          <button @click="navigate('ai-enhancement')" class="view-all-btn">
            Get More Insights
          </button>
        </div>
      </div>
    </div>
  </DashboardLayout>
  <JobApplicationModal
    v-if="showApplyModal"
    :job="selectedJob"
    :userId="user_id"
    @close="closeApplyModal"
    @application-submitted="handleApplicationSubmitted"
  />
</template>

<script setup>
import { ref, onMounted, TrackOpTypes } from 'vue'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import DashboardLayout from './DashboardLayout.vue'
import axios from 'axios'
import JobApplicationModal from './JobApplicationModal.vue'

const showApplyModal = ref(false)
const selectedJob = ref(null)

// Add function to open modal
function applyToJob(job) {
  selectedJob.value = job
  showApplyModal.value = true
}

function closeApplyModal() {
  showApplyModal.value = false
  selectedJob.value = null
}

function handleApplicationSubmitted(applicationData) {
  // Refresh applications list
  loadApplications()
  
  // Close modal
  closeApplyModal()
  
  // Show success message
  alert(`Successfully applied to ${applicationData.job_title}!`)
}

const router = useRouter()

// State
const userName = ref(null) // Get from auth
const user_id = ref('');
const jobsLoading = ref(false)

const recentApplications = ref([])
const recommendedJobs = ref([])
const profileCompletion = ref(75)
const completionItems = ref([
  { name: 'Resume Uploaded', completed: false },
  { name: 'Skills Added', completed: false },
  { name: 'Experience Details', completed: true },
  { name: 'Portfolio Links', completed: false },
  { name: 'Preferences Set', completed: false }
])

const upcomingInterviews = ref([])

const aiInsights = ref([
  {
    id: 1,
    type: 'tip',
    icon: 'fas fa-lightbulb',
    title: 'Improve Your Resume',
    description: 'Add more quantified achievements to increase your profile strength by 23%'
  },
  {
    id: 2,
    type: 'warning',
    icon: 'fas fa-exclamation-triangle',
    title: 'Skills Gap Detected',
    description: 'Consider learning TypeScript - it appears in 68% of your target job postings'
  }
])

const applicationCount = computed(() => {
  return recentApplications.value?.length
})

const interviewCount = computed(() => {
  return upcomingInterviews.value?.length || 0
})

const profileView = computed(() => {
  return 45 
})

// Functions
function navigate(page) {
  const pageMap = {
    'candidate-profile': '/candidate/candidate-profile',
    'job-search': '/candidate/job-search',
    'ai-enhancement': '/candidate/ai-enhancement',
    'applications': '/candidate/applications',
    'job-recommend': '/candidate/job-recommend'
  }

  if (pageMap[page]) {
    router.push(pageMap[page])
  }
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}

function formatDateTime(dateString) {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
async function loadUpcomingInterviews(){
  try{
    const response = await axios.get(`/api/screening/candidates/${user_id.value}/interviews`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      params: { upcoming_only: 'true' , limit: 5 }
    });
    console.log('Upcoming Interviews API Response:', response.data);
    if (response.data.success && response.data) {
        upcomingInterviews.value = response.data.interviews.map(interview => ({
        id: interview.id,
        jobTitle: interview.job_details?.title || 'Interview',
        company: interview.job_details?.company || 'Company',
        scheduledTime: interview.scheduled_at,
        type: interview.interview_type || 'Interview',
        interviewer: interview.interviewer_details?.name,
        meeting_link: interview.meeting_link,
        duration: interview.duration_minutes,
        status: interview.status
        }))
    }
  }
  catch(error){
    console.log('Failed to load upcoming interviews:', error)
  }
}
async function jobRecommendationService(){
try{
    jobsLoading.value = true // Start loading
    
    // 1. Get user's resume files
    const UserResumeInfo = await axios.get(`/api/files/resume`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });

    console.log('Resume files response:', UserResumeInfo.data);

    // 2. Check if user has any resume files
    if (!UserResumeInfo.data || UserResumeInfo.data.length === 0) {
      console.log('No resume found for user');
      recommendedJobs.value = [];
      return;
    }

    // 3. Get the first resume's ID
    const UserResumeId = UserResumeInfo.data.id;
    console.log('Using resume ID:', UserResumeId);

    // 4. Get job recommendations based on resume
    const topJobsResponse = await axios.get(`/api/get_job_posts/${UserResumeId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });

    console.log('Job recommendations response:', topJobsResponse.data.job_post.meta_data);

    // 5. Extract job data correctly
    if (topJobsResponse.data && topJobsResponse.data.job_post) {
      recommendedJobs.value = topJobsResponse.data.job_post.meta_data || [];

    } else {
      console.log('No job recommendations found');
      recommendedJobs.value = [];
    }

  } catch(error) {
    console.error('Error in jobRecommendationService:', error);
    
    if (error.response) {
      console.error('API Error:', error.response.status, error.response.data);
      
      if (error.response.status === 404) {
        console.log('Resume not found or no job posts available');
        // Try loading regular jobs as fallback
        await loadJobs();
      }
    }
    
    recommendedJobs.value = [];
  } finally {
    jobsLoading.value = false // Stop loading
  }
}
async function loadRecentApplications() {
  try {
    console.log('🔄 Loading applications...')
    
    const response = await axios.get(`/api/applications/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    
    console.log('📋 Applications API Response:', response.data)
    
    recentApplications.value = response.data.applications
    
    
    // Verify the structure
    console.log('✅ Applications stored:', recentApplications.value)
    console.log('✅ Total count:', recentApplications.value.length)
    
  } catch(error) {
    console.error('❌ Failed to load recent applications:', error)
    // Set default structure on error
    recentApplications.value = { applications: [] }
  }
}

function getStatusColor(status) {
  const statusMap = {
    'active': '#27ae60',
    'inactive': '#e74c3c', 
    'closed': '#95a5a6',
    'pending': '#f39c12'
  };
  return statusMap[status?.toLowerCase()] || '#7f8c8d';
}

async function loadJobs() {
  try {
    const response = await axios.get(`/api/jobs/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
    if(!recommendedJobs.value){
      recommendedJobs.value = response.data;
      console.log('job are loaded', recommendedJobs.value)
    }
  } catch (error) {
    console.error('Failed to load jobs:', error)

  }
}


onMounted(async () => {
  try {
    console.log('🚀 Starting dashboard data load...')
    
    // Load user data first
    await loadDashboardData()
    console.log('✅ User data loaded')
    
    // Load applications BEFORE everything else
    await loadRecentApplications()
    console.log('✅ Applications loaded, count:', applicationCount.value)
    
    // Load recommended jobs
    await jobRecommendationService()
    console.log('✅ Job recommendations processed')

    await loadUpcomingInterviews();
    console.log('✅ Upcoming Interviews loaded')

    // Load regular jobs as fallback
    if ((!recommendedJobs.value || recommendedJobs.value.length === 0) && !jobsLoading.value) {
      await loadJobs()
      console.log('✅ Fallback jobs loaded')
    }
    
    console.log('🎉 Dashboard data load complete')
  } catch (error) {
    console.error('❌ Failed to load dashboard data:', error)
  }
})


async function loadDashboardData() {
  // Load user stats, applications, recommendations, etc.
  // This would typically come from API calls
  try {
  const userData = await axios.get(`/api/users/`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  });
  
  userName.value = userData.data.name
  user_id.value = userData.data.id
  console.log(user_id?.value)
}
catch (error) {
  console.error('Failed to load user data:', error)
}
}
</script>

<style scoped>
.candidate-dashboard {
  padding: 0;
}

.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px;
  border-radius: 12px;
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-text h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;
}

.welcome-text p {
  font-size: 1.2rem;
  opacity: 0.9;
}

.quick-stats {
  display: flex;
  gap: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  min-width: 140px;
}

.stat-card i {
  font-size: 2rem;
  opacity: 0.8;
}

.stat-info h3 {
  font-size: 1.8rem;
  margin: 0;
  font-weight: bold;
}

.stat-info p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
}

.dashboard-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dashboard-card h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
}

/* Quick Actions */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: transform 0.2s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.action-btn.primary {
  background: #3498db;
  color: white;
}

.action-btn.secondary {
  background: #2ecc71;
  color: white;
}

.action-btn.tertiary {
  background: #f39c12;
  color: white;
}

/* Applications & Jobs */
.application-list,
.job-list,
.interview-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 15px;
}

.application-item,
.job-item,
.interview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.app-info h4,
.job-info h4,
.interview-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.app-info p,
.job-info p,
.interview-info p {
  margin: 0 0 3px 0;
  color: #7f8c8d;
}
.jobStatus{
  color: #ffffff;
  border: 1px solid #7f8c8d;
  height: 20px;
  border-radius: 8px;
  padding: 2px 8px;
  
}

.app-status {
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.app-status.applied {
  background: #e8f4f8;
  color: #2980b9;
}

.app-status.shortlisted {
  background: #e8f8f0;
  color: #27ae60;
}

.app-status.under.review {
  background: #fff3cd;
  color: #856404;
}

.job-meta {
  display: flex;
  gap: 15px;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.apply-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.view-all-btn,
.complete-btn {
  width: 100%;
  background: #ecf0f1;
  color: #2c3e50;
  border: none;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

/* Profile Completion */
.completion-circle {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: conic-gradient(#3498db 0deg, #3498db calc(var(--progress) * 3.6deg), #ecf0f1 calc(var(--progress) * 3.6deg));
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.circle::before {
  content: '';
  width: 90px;
  height: 90px;
  background: white;
  border-radius: 50%;
  position: absolute;
}

.circle span {
  position: relative;
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.completion-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 15px 0;
}

.completion-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.completion-item i.completed {
  color: #27ae60;
}

.completion-item i:not(.completed) {
  color: #bdc3c7;
}

/* Interviews */
.no-interviews {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.no-interviews i {
  font-size: 3rem;
  margin-bottom: 10px;
  display: block;
}

.interview-time {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
  color: #7f8c8d;
}

/* AI Insights */
.insight-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 15px;
}

.insight-item {
  display: flex;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.insight-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.insight-icon.tip {
  background: #e8f4f8;
  color: #2980b9;
}

.insight-icon.warning {
  background: #fff3cd;
  color: #856404;
}

.insight-content h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.insight-content p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }

  .quick-stats {
    justify-content: center;
    flex-wrap: wrap;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .application-item,
  .job-item,
  .interview-item {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
}
</style>