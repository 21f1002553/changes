<template>
  <DashboardLayout>
    <div class="screening-page">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>
            <i class="fas fa-user-check"></i>
            Resume Screening
          </h1>
          <p>Review and screen candidate applications for open positions</p>
        </div>
      </div>

      <!-- Job Selection Section -->
      <div class="job-selection-section">
        <div class="form-group">
          <label for="job-select">
            <i class="fas fa-briefcase"></i>
            Select Job Position
          </label>
          <select id="job-select" v-model="selectedJobId" @change="loadCandidatesForJob" class="job-select">
            <option value="">-- Select a Job Position --</option>
            <option v-for="job in jobs" :key="job.id" :value="job.id">
              {{ job.title }} - {{ job.location }} ({{ job.level }})
            </option>
          </select>
        </div>

        <!-- Job Details Card (shows when job is selected) -->
        <div v-if="selectedJob" class="job-details-card">
          <div class="job-details-header">
            <h3>{{ selectedJob.title }}</h3>
            <span class="job-status">{{ selectedJob.status }}</span>
          </div>
          <div class="job-details-body">
            <div class="detail-item">
              <i class="fas fa-map-marker-alt"></i>
              <span>{{ selectedJob.location }}</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-layer-group"></i>
              <span>{{ selectedJob.level }}</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-users"></i>
              <span>{{ candidates.length }} Applications</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Candidates Table -->
      <div v-if="selectedJobId" class="candidates-section">
        <div class="section-header">
          <h3>
            <i class="fas fa-list"></i>
            Candidate Applications
          </h3>
          <div class="filter-stats">
            <span class="stat-badge total">Total: {{ candidates.length }}</span>
            <span class="stat-badge pending">Pending: {{ pendingCount }}</span>
            <span class="stat-badge screened">Screened: {{ screenedCount }}</span>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading candidates...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="candidates.length === 0" class="empty-state">
          <i class="fas fa-inbox"></i>
          <h3>No Applications Found</h3>
          <p>There are no candidate applications for this position yet.</p>
        </div>

        <!-- Candidates Table -->
        <div v-else class="table-container">
          <table class="candidates-table">
            <thead>
              <tr>
                <th>Candidate Name</th>
                <th>Email</th>
                <th>Applied Date</th>
                <th>View Resume</th>
                <th>Match Score</th>
                <th>Key Metrics</th>
                <th>AI Analysis</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="candidate in candidates" :key="candidate.id">
                <td>
                  <div class="candidate-info">
                    <div class="candidate-avatar">
                      {{ getInitials(candidate.candidate_name) }}
                    </div>
                    <span class="candidate-name">{{ candidate.candidate_name }}</span>
                  </div>
                </td>
                <td>{{ candidate.candidate_email || 'N/A' }}</td>
                <td>{{ formatDate(candidate.applied_at) }}</td>
                <td>
                  <button @click="viewResume(candidate)" class="btn-view-resume" :disabled="!candidate.resume_id">
                    <i class="fas fa-file-alt"></i>
                    View Resume
                  </button>
                </td>
                <td>
                  <div class="score-container">
                    <span :class="getScoreClass(candidate.score)" class="score-value">
                      {{ candidate.score !== null && candidate.score !== undefined ? candidate.score : 'N/A' }}
                    </span>
                    <span v-if="candidate.score !== null && candidate.score !== undefined" class="score-label">
                      /100
                    </span>
                  </div>
                </td>
                <td>
                  <div class="metrics-container">
                    <div v-if="candidate.key_metrics && candidate.key_metrics.length > 0" class="metrics-tags">
                      <span v-for="(metric, index) in candidate.key_metrics.slice(0, 3)" :key="index" class="metric-tag"
                        :title="metric">
                        {{ metric }}
                      </span>
                    </div>
                    <span v-else class="no-metrics">No metrics</span>
                  </div>
                </td>
                <td>
                  <div class="ai-analysis-cell">
                    <button v-if="candidate.reason" @click="showAnalysis(candidate)" class="btn-view-analysis"
                      title="View AI Analysis">
                      <i class="fas fa-robot"></i>
                      View Analysis
                    </button>
                    <span v-else class="no-analysis">N/A</span>
                  </div>
                </td>
                <td>
                  <span :class="getStatusClass(candidate.status)" class="status-badge">
                    {{ formatStatus(candidate.status) }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button @click="shortlistCandidate(candidate)" class="btn-action shortlist"
                      :disabled="candidate.status === 'screening' || candidate.status === 'selected'">
                      <i class="fas fa-check"></i>
                      Shortlist
                    </button>
                    <button @click="rejectCandidate(candidate)" class="btn-action reject"
                      :disabled="candidate.status === 'rejected'">
                      <i class="fas fa-times"></i>
                      Reject
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Empty Selection State -->
      <div v-else class="no-job-selected">
        <i class="fas fa-search"></i>
        <h3>Select a Job Position</h3>
        <p>Choose a job position from the dropdown above to view candidate applications</p>
      </div>
    </div>

    <!-- Resume Viewer Modal -->
    <div v-if="showResumeModal" class="modal-overlay" @click="closeResumeModal">
      <div class="modal-container resume-modal" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="fas fa-file-alt"></i>
            Resume - {{ selectedCandidate?.candidate_name }}
          </h3>
          <button @click="closeResumeModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div v-if="loadingResume" class="loading-resume">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading resume...</p>
          </div>
          <div v-else-if="resumeData" class="resume-content">
            <!-- Resume Details -->
            <div class="resume-section">
              <h4>Personal Information</h4>
              <div class="resume-info-grid">
                <div class="info-item">
                  <strong>Name:</strong>
                  <span>{{ resumeData.name || selectedCandidate?.candidate_name }}</span>
                </div>
                <div class="info-item">
                  <strong>Email:</strong>
                  <span>{{ resumeData.email || selectedCandidate?.candidate_email }}</span>
                </div>
                <div class="info-item">
                  <strong>Phone:</strong>
                  <span>{{ resumeData.phone || 'N/A' }}</span>
                </div>
                <div class="info-item">
                  <strong>Location:</strong>
                  <span>{{ resumeData.location || 'N/A' }}</span>
                </div>
              </div>
            </div>

            <!-- Skills -->
            <div v-if="resumeData.skills && resumeData.skills.length > 0" class="resume-section">
              <h4>Skills</h4>
              <div class="skills-tags">
                <span v-for="skill in resumeData.skills" :key="skill" class="skill-tag">
                  {{ skill }}
                </span>
              </div>
            </div>

            <!-- Experience -->
            <div v-if="resumeData.experience && resumeData.experience.length > 0" class="resume-section">
              <h4>Work Experience</h4>
              <div v-for="(exp, index) in resumeData.experience" :key="index" class="experience-item">
                <h5>{{ exp.title || exp.position }}</h5>
                <p class="company">{{ exp.company }}</p>
                <p class="duration">{{ exp.duration || exp.period }}</p>
                <p class="description">{{ exp.description }}</p>
              </div>
            </div>

            <!-- Education -->
            <div v-if="resumeData.education && resumeData.education.length > 0" class="resume-section">
              <h4>Education</h4>
              <div v-for="(edu, index) in resumeData.education" :key="index" class="education-item">
                <h5>{{ edu.degree }}</h5>
                <p class="institution">{{ edu.institution }}</p>
                <p class="duration">{{ edu.year || edu.period }}</p>
              </div>
            </div>

            <!-- Additional Info -->
            <div v-if="resumeData.summary" class="resume-section">
              <h4>Summary</h4>
              <p>{{ resumeData.summary }}</p>
            </div>
          </div>
          <div v-else class="resume-error">
            <i class="fas fa-exclamation-circle"></i>
            <p>Unable to load resume details</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeResumeModal" class="btn-secondary">Close</button>
          <button @click="downloadResume" class="btn-primary">
            <i class="fas fa-download"></i>
            Download Resume
          </button>
        </div>
      </div>
    </div>

    <div v-if="showAnalysisModal" class="modal-overlay" @click="closeAnalysisModal">
      <div class="modal-container analysis-modal" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="fas fa-robot"></i>
            AI Resume Analysis - {{ selectedCandidateForAnalysis?.candidate_name }}
          </h3>
          <button @click="closeAnalysisModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="analysis-content">
            <!-- Match Score -->
            <div class="analysis-section score-section">
              <h4>Match Score</h4>
              <div class="score-display">
                <span :class="getScoreClass(selectedCandidateForAnalysis?.score)" class="large-score">
                  {{ selectedCandidateForAnalysis?.score }}
                </span>
                <span class="score-max">/100</span>
              </div>
            </div>

            <!-- Key Metrics -->
            <div class="analysis-section">
              <h4><i class="fas fa-chart-line"></i> Key Metrics</h4>
              <div class="key-metrics-list">
                <div v-for="(metric, index) in selectedCandidateForAnalysis?.key_metrics" :key="index"
                  class="metric-item">
                  <i class="fas fa-check-circle"></i>
                  <span>{{ metric }}</span>
                </div>
              </div>
            </div>

            <!-- AI Analysis Reason -->
            <div class="analysis-section">
              <h4><i class="fas fa-brain"></i> AI Analysis</h4>
              <div class="reason-text">
                {{ selectedCandidateForAnalysis?.reason }}
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeAnalysisModal" class="btn-secondary">Close</button>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const router = useRouter()

// State
const jobs = ref([])
const selectedJobId = ref('')
const candidates = ref([])
const loading = ref(false)
const showResumeModal = ref(false)
const selectedCandidate = ref(null)
const resumeData = ref(null)
const loadingResume = ref(false)
const user_id = ref('');

const showAnalysisModal = ref(false)
const selectedCandidateForAnalysis = ref(null)


// Computed
const selectedJob = computed(() => {
  return jobs.value.find(job => job.id === selectedJobId.value)
})

const pendingCount = computed(() => {
  return candidates.value.filter(c => c.status === 'applied').length
})

const screenedCount = computed(() => {
  return candidates.value.filter(c => c.status === 'screening' || c.status === 'interviewed').length
})


function showAnalysis(candidate) {
  selectedCandidateForAnalysis.value = candidate
  showAnalysisModal.value = true
}

function closeAnalysisModal() {
  showAnalysisModal.value = false
  selectedCandidateForAnalysis.value = null
}

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

function getInitials(name) {
  if (!name) return '?'
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function formatStatus(status) {
  const statusMap = {
    'applied': 'Applied',
    'under_review': 'Under Review',
    'screening': 'Shortlisted',
    'interviewed': 'Interviewed',
    'selected': 'Selected',
    'rejected': 'Rejected',
    'withdrawn': 'Withdrawn',
    'on_hold': 'On Hold'
  }
  return statusMap[status] || status
}

function getStatusClass(status) {
  const classMap = {
    'applied': 'status-new',
    'under_review': 'status-review',
    'screening': 'status-screening',
    'interviewed': 'status-interview',
    'selected': 'status-selected',
    'rejected': 'status-rejected',
    'withdrawn': 'status-withdrawn',
    'on_hold': 'status-hold'
  }
  return classMap[status] || 'status-default'
}

function getScoreClass(score) {
  if (!score) return 'score-na'
  if (score >= 90) return 'score-excellent'
  if (score >= 75) return 'score-good'
  if (score >= 60) return 'score-average'
  return 'score-poor'
}

function getKeyMetrics(candidate) {
  // Return AI-generated key metrics if available
  if (candidate.key_metrics && candidate.key_metrics.length > 0) {
    return candidate.key_metrics.slice(0, 3) // Show first 3 metrics
  }

  // Fallback metrics based on score
  const metrics = []

  if (candidate.score) {
    if (candidate.score >= 90) {
      metrics.push('Top Match')
    } else if (candidate.score >= 75) {
      metrics.push('Good Fit')
    } else if (candidate.score >= 60) {
      metrics.push('Average Match')
    } else {
      metrics.push('Low Match')
    }
  }

  if (candidate.status === 'screening') {
    metrics.push('Shortlisted')
  }

  return metrics.length > 0 ? metrics : ['Pending Review']
}

// API Functions
async function loadJobs() {
  try {
    loading.value = true
    const response = await axios.get('/api/jobs/', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      // Filter only active jobs
      jobs.value = response.data.filter(job => job.status === 'active')
      console.log('Loaded jobs:', jobs.value.length)
    }
  } catch (error) {
    console.error('Failed to load jobs:', error)
    jobs.value = []
  } finally {
    loading.value = false
  }
}

async function loadCandidatesForJob() {
  if (!selectedJobId.value) {
    candidates.value = []
    return
  }

  try {
    loading.value = true
    console.log('Loading candidates for job:', selectedJobId.value)

    const response = await axios.get('/api/applications/', {
      params: {
        job_id: selectedJobId.value
      },
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data && response.data.applications) {
      candidates.value = response.data.applications.map(app => ({
        id: app.id,
        candidate_id: app.candidate_id,
        candidate_name: app.candidate_name || 'Unknown',
        candidate_email: app.candidate_email,
        resume_id: app.resume_id,
        score: app.score || null,
        status: app.status,
        applied_at: app.applied_at,
        application_data: app
      }))

      console.log('Loaded candidates:', candidates.value.length)

      await loadResumeScores()
    } else {
      candidates.value = []
    }
  } catch (error) {
    console.error('Failed to load candidates:', error)
    candidates.value = []
  } finally {
    loading.value = false
  }
}

async function viewResume(candidate) {
  if (!candidate.resume_id) {
    alert('No resume found for this candidate')
    return
  }

  try {
    selectedCandidate.value = candidate
    showResumeModal.value = true
    loadingResume.value = true

    console.log('🔄 Loading resume for candidate:', candidate.candidate_name)
    console.log('📄 Resume ID:', candidate.resume_id)

    // Step 1: Get resume record to get file_id
    const resumeResponse = await axios.get(`/api/screening/resumes/${candidate.resume_id}`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    console.log('Resume data:', resumeResponse.data)

    if (!resumeResponse.data) {
      throw new Error('Resume data not found')
    }

    const resume = resumeResponse.data
    const fileId = resume.file_id || resume.id

    console.log('📎 File ID:', fileId)

    // Step 2: Get file preview/metadata
    const fileResponse = await axios.get(`/api/files/${fileId}/preview`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    console.log('File preview data:', fileResponse.data)

    // Step 3: Parse resume data
    if (fileResponse.data) {
      // If parsed_data exists in resume, use it
      if (resume.parsed_data) {
        resumeData.value = typeof resume.parsed_data === 'string'
          ? JSON.parse(resume.parsed_data)
          : resume.parsed_data
      } else {
        // Otherwise use file metadata
        resumeData.value = {
          name: candidate.candidate_name,
          email: candidate.candidate_email,
          filename: fileResponse.data.filename,
          file_size: fileResponse.data.file_size,
          uploaded_at: fileResponse.data.uploaded_at,
          // Add placeholder data since parsing isn't available
          skills: [],
          experience: [],
          education: [],
          summary: fileResponse.data.description || 'No summary available'
        }
      }

      // Store file_id for download
      selectedCandidate.value.file_id = fileId

      console.log('Resume loaded successfully')
    }
  } catch (error) {
    console.error('Failed to load resume:', error)

    // Show error message
    if (error.response?.status === 403) {
      alert('Access denied. You do not have permission to view this resume.')
    } else if (error.response?.status === 404) {
      alert('Resume file not found.')
    } else {
      alert('Failed to load resume. Please try again.')
    }

    resumeData.value = null
  } finally {
    loadingResume.value = false
  }
}


async function downloadResume() {
  if (!selectedCandidate.value?.file_id && !selectedCandidate.value?.resume_id) {
    alert('Cannot download: Resume file not found')
    return
  }

  try {
    console.log('📥 Downloading resume...')

    const fileId = selectedCandidate.value.file_id || selectedCandidate.value.resume_id

    const response = await axios.get(`/api/files/${fileId}/download`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` },
      responseType: 'blob'
    })

    // Create download link
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url

    // Generate filename
    const candidateName = selectedCandidate.value.candidate_name.replace(/\s+/g, '_')
    const timestamp = new Date().toISOString().split('T')[0]
    const filename = `Resume_${candidateName}_${timestamp}.pdf`

    link.setAttribute('download', filename)

    // Trigger download
    document.body.appendChild(link)
    link.click()

    // Cleanup
    link.remove()
    window.URL.revokeObjectURL(url)

    console.log('Resume downloaded successfully')
  } catch (error) {
    console.error('Failed to download resume:', error)

    if (error.response?.status === 403) {
      alert('Access denied. You do not have permission to download this resume.')
    } else if (error.response?.status === 404) {
      alert('Resume file not found on server.')
    } else {
      alert('Failed to download resume. Please try again.')
    }
  }
}

function closeResumeModal() {
  showResumeModal.value = false
  selectedCandidate.value = null
  resumeData.value = null
}


async function shortlistCandidate(candidate) {
  try {
    console.log('Shortlisting candidate:', candidate.candidate_name)

    // First get the pipeline stages to find the Shortlisted stage ID
    const stagesResponse = await axios.get('/api/pipeline/stages', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    let shortlistedStage = null
    if (stagesResponse.data && stagesResponse.data.stages) {
      shortlistedStage = stagesResponse.data.stages.find(stage =>
        stage.name.toLowerCase().includes('shortlist')
      )
    }

    if (!shortlistedStage) {
      console.warn('Shortlisted stage not found, updating application status only')
      // Fallback to just updating application status
      const response = await axios.put(
        `/api/applications/${candidate.id}/status`,
        {
          status: 'shortlisted',
          notes: 'Shortlisted by HR for further screening'
        },
        {
          headers: { Authorization: `Bearer ${getAuthToken()}` }
        }
      )
    } else {
      // Move candidate to Shortlisted pipeline stage
      const response = await axios.put(
        `/api/pipeline/candidates/${candidate.candidate_id}/move`,
        {
          stage_id: shortlistedStage.id,
          job_id: candidate.job_id || selectedJobId.value,
          notes: 'Shortlisted by HR for further screening',
          moved_by_id: user_id?.value
        },
        {
          headers: { Authorization: `Bearer ${getAuthToken()}` }
        }
      )

      // Also update application status
      await axios.put(
        `/api/applications/${candidate.id}/status`,
        {
          status: 'screening',
          notes: 'Moved to shortlisted pipeline stage'
        },
        {
          headers: { Authorization: `Bearer ${getAuthToken()}` }
        }
      )
    }

    // Update local state
    const index = candidates.value.findIndex(c => c.id === candidate.id)
    if (index !== -1) {
      candidates.value[index].status = 'screening'
    }

    alert(`${candidate.candidate_name} has been shortlisted and moved to pipeline!`)
    console.log('Candidate shortlisted and moved to pipeline')

  } catch (error) {
    console.error('Failed to shortlist candidate:', error)
    alert('Failed to shortlist candidate. Please try again.')
  }
}

async function rejectCandidate(candidate) {
  if (!confirm(`Are you sure you want to reject ${candidate.candidate_name}?`)) {
    return
  }

  try {
    console.log('Rejecting candidate:', candidate.candidate_name)

    const response = await axios.put(
      `/api/applications/${candidate.id}/status`,
      {
        status: 'rejected',
        notes: 'Rejected during initial screening'
      },
      {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      }
    )

    if (response.data) {
      // Update local state
      const index = candidates.value.findIndex(c => c.id === candidate.id)
      if (index !== -1) {
        candidates.value[index].status = 'rejected'
      }

      alert(`${candidate.candidate_name} has been rejected.`)
      console.log('Candidate rejected')
    }
  } catch (error) {
    console.error('Failed to reject candidate:', error)
    alert('Failed to reject candidate. Please try again.')
  }
}

async function loadResumeScores() {
  if (!selectedJobId.value) {
    console.log('No job selected, skipping resume score loading')
    return
  }

  try {
    console.log('Loading resume scores for job:', selectedJobId.value)

    const response = await axios.get(`/api/ai/get_resume_score/${selectedJobId.value}`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    console.log('Resume scores response:', response.data)

    if (response.data && response.data.resume_score) {
      console.log('Resume scores loaded:', response.data.resume_score)

      // Update candidates array with AI resume scores
      candidates.value = candidates.value.map(candidate => {
        const scoreDatas = response.data.resume_score

        // Match by resume_id or user_id
        if(scoreDatas.length > 1) {
        for (let scoreData of scoreDatas) {
          if (scoreData.resume_id === candidate.resume_id ||
            scoreData.user_id === candidate.candidate_id) {
            return {
              ...candidate,
              score: scoreData.score,
              key_metrics: scoreData.key_metrics || [],
              reason: scoreData.reason || 'No analysis available'
            }
          }
        }
      } else{
          if (scoreDatas.resume_id = candidate.resume_id || scoreDatas.user_id === candidate.candidate_id){
            return {
              ...candidate,
              score: scoreDatas.score,
              key_metrics: scoreDatas.key_metrics || [],
              reason: scoreDatas.reason || 'No analysis available'
            }
          }
        }
      
    
    
        return candidate
      })

      console.log('Candidates updated with resume scores')
    }
  } catch (error) {
    console.error('Failed to load resume scores:', error)

  }
}

async function loadUserdata() {
  try {
    const response = await axios.get('/api/users/', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      user_id.value = response.data.id
    }
  } catch (error) {
    console.error('Failed to load user data:', error)
  }
}

// Load jobs on mount
onMounted(async () => {
  await loadUserdata()
  await loadJobs()

})
</script>

<style scoped>
.screening-page {
  padding: 0;
  max-width: 100%;
}

/* Page Header */
.page-header {
  margin-bottom: 30px;
}

.header-content h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-content p {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

/* Job Selection Section */
.job-selection-section {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 1rem;
}

.job-select {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  color: #2c3e50;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.job-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* Job Details Card */
.job-details-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 10px;
  color: white;
}

.job-details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.job-details-header h3 {
  margin: 0;
  font-size: 1.4rem;
}

.job-status {
  background: rgba(255, 255, 255, 0.2);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  text-transform: uppercase;
  font-weight: 600;
}

.job-details-body {
  display: flex;
  gap: 25px;
  flex-wrap: wrap;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
}

/* Candidates Section */
.candidates-section {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #ecf0f1;
}

.section-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-stats {
  display: flex;
  gap: 10px;
}

.stat-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.stat-badge.total {
  background: #3498db;
  color: white;
}

.stat-badge.pending {
  background: #f39c12;
  color: white;
}

.stat-badge.screened {
  background: #27ae60;
  color: white;
}

/* Loading and Empty States */
.loading-state,
.empty-state,
.no-job-selected {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.loading-state i,
.empty-state i,
.no-job-selected i {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
}

.empty-state h3,
.no-job-selected h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

/* Table */
.table-container {
  overflow-x: auto;
}

.candidates-table {
  width: 100%;
  border-collapse: collapse;
}

.candidates-table thead {
  background: #f8f9fa;
}

.candidates-table th {
  padding: 15px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #ecf0f1;
  white-space: nowrap;
}

.candidates-table td {
  padding: 15px;
  border-bottom: 1px solid #ecf0f1;
  vertical-align: middle;
}

.candidates-table tbody tr:hover {
  background: #f8f9fa;
}

/* Candidate Info */
.candidate-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.candidate-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
}

.candidate-name {
  font-weight: 600;
  color: #2c3e50;
}

/* Buttons */
.btn-view-resume {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-view-resume:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-1px);
}

.btn-view-resume:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}


.modal-container.analysis-modal {
  background: white;
  border-radius: 12px;
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.analysis-content {
  padding: 10px 0;
}

/* Analysis Modal */
.analysis-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ecf0f1;
}

.analysis-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.analysis-section h4 {
  color: #2c3e50;
  font-size: 1.1rem;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Score Classes */
.score-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  color: white;
  border: none;
}

.score-section h4 {
  color: white;
  margin-bottom: 10px;
}

.score-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
}

.large-score {
  font-size: 3rem;
  font-weight: 700;
}

.score-max {
  font-size: 1.5rem;
  opacity: 0.8;
}

.score-container {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.score-value {
  font-weight: 700;
  font-size: 1.2rem;
}

.score-label {
  color: #95a5a6;
  font-size: 0.9rem;
}

.score-excellent {
  color: #27ae60;
  font-weight: 700;
  font-size: 1.1rem;
}

.score-good {
  color: #2ecc71;
  font-weight: 700;
  font-size: 1.1rem;
}

.score-average {
  color: #f39c12;
  font-weight: 700;
  font-size: 1.1rem;
}

.score-poor {
  color: #e74c3c;
  font-weight: 700;
  font-size: 1.1rem;
}

.score-na {
  color: #95a5a6;
  font-style: italic;
}

/* Metrics Tags */

.metrics-container {
  max-width: 300px;
}

.metrics-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.metric-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}


/* Status Badges */
.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-block;
}

.status-new {
  background: #e3f2fd;
  color: #1976d2;
}

.status-review {
  background: #fff3e0;
  color: #f57c00;
}

.status-screening {
  background: #e8f5e9;
  color: #388e3c;
}

.status-interview {
  background: #f3e5f5;
  color: #7b1fa2;
}

.status-selected {
  background: #c8e6c9;
  color: #2e7d32;
}

.status-rejected {
  background: #ffebee;
  color: #c62828;
}

.status-withdrawn {
  background: #f5f5f5;
  color: #616161;
}

.status-hold {
  background: #fff9c4;
  color: #f57f17;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-action {
  padding: 8px 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.3s ease;
  color: white;
}

.btn-action.shortlist {
  background: #27ae60;
}

.btn-action.shortlist:hover:not(:disabled) {
  background: #229954;
  transform: translateY(-1px);
}

.btn-action.reject {
  background: #e74c3c;
}

.btn-action.reject:hover:not(:disabled) {
  background: #c0392b;
  transform: translateY(-1px);
}

.btn-action:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  opacity: 0.6;
}



/* AI Analysis Cell */
.ai-analysis-cell {
  min-width: 120px;
}

.btn-view-analysis {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-view-analysis:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.no-analysis {
  color: #95a5a6;
  font-size: 0.85rem;
  font-style: italic;
}


/* Key Metrics List */
.key-metrics-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-item {
  display: flex;
  align-items: start;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #3498db;
}

.metric-item i {
  color: #27ae60;
  margin-top: 2px;
  flex-shrink: 0;
}

.metric-item span {
  color: #2c3e50;
  line-height: 1.5;
  font-size: 0.95rem;
}

/* Reason Text */
.reason-text {
  background: #fff3e0;
  padding: 20px;
  border-radius: 8px;
  color: #2c3e50;
  line-height: 1.7;
  font-size: 0.95rem;
  border-left: 4px solid #f39c12;
}


/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container.resume-modal {
  background: white;
  border-radius: 12px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 20px 25px;
  border-bottom: 2px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #7f8c8d;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #ecf0f1;
  color: #2c3e50;
}

.modal-body {
  padding: 25px;
  overflow-y: auto;
  flex: 1;
}

.loading-resume,
.resume-error {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.loading-resume i {
  font-size: 2rem;
  margin-bottom: 10px;
  display: block;
}

.resume-content {
  max-width: 800px;
  margin: 0 auto;
}

.resume-section {
  margin-bottom: 30px;
}

.resume-section h4 {
  color: #2c3e50;
  font-size: 1.2rem;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #3498db;
}

.resume-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-item strong {
  color: #7f8c8d;
  font-size: 0.85rem;
  text-transform: uppercase;
}

.info-item span {
  color: #2c3e50;
  font-size: 1rem;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.skill-tag {
  background: #3498db;
  color: white;
  padding: 8px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.experience-item,
.education-item {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 15px;
  border-left: 4px solid #3498db;
}

.experience-item h5,
.education-item h5 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.company,
.institution {
  color: #7f8c8d;
  font-weight: 600;
  margin: 0 0 5px 0;
}

.duration {
  color: #95a5a6;
  font-size: 0.9rem;
  margin: 0 0 10px 0;
}

.description {
  color: #2c3e50;
  line-height: 1.6;
  margin: 0;
}

.modal-footer {
  padding: 20px 25px;
  border-top: 2px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.btn-secondary,
.btn-primary {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-secondary:hover {
  background: #bdc3c7;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
  transform: translateY(-1px);
}

/* Responsive */
@media (max-width: 1200px) {
  .candidates-table {
    font-size: 0.85rem;
  }

  .metric-tag {
    font-size: 0.7rem;
    padding: 3px 8px;
  }
}


@media (max-width: 768px) {
  .candidates-table {
    font-size: 0.9rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .filter-stats {
    width: 100%;
    justify-content: space-between;
  }

  .metrics-container {
    max-width: 200px;
  }

  .metric-tag {
    max-width: 100px;
  }

  .large-score {
    font-size: 2rem;
  }

  .score-max {
    font-size: 1.2rem;
  }

}
</style>