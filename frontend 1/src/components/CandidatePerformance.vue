<template>
  <DashboardLayout>
    <div class="performance-page">
      <div class="page-header">
        <h1><i class="fas fa-chart-line"></i> My Performance</h1>
        <p>Track your technical test results and interview feedback</p>
      </div>

      <!-- Tab Navigation -->
      <div class="tabs">
        <button 
          :class="['tab-btn', { active: activeTab === 'tests' }]"
          @click="activeTab = 'tests'"
        >
          <i class="fas fa-code"></i>
          Technical Tests
          <span class="badge">{{ technicalTests.length }}</span>
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'interviews' }]"
          @click="activeTab = 'interviews'"
        >
          <i class="fas fa-comments"></i>
          Interviews
          <span class="badge">{{ interviews.length }}</span>
        </button>
      </div>

      <!-- Technical Tests Tab -->
      <div v-if="activeTab === 'tests'" class="tab-content">
        <div v-if="testsLoading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading your test results...</p>
        </div>

        <div v-else-if="technicalTests.length === 0" class="empty-state">
          <i class="fas fa-clipboard-list"></i>
          <h3>No Test Results Yet</h3>
          <p>You haven't completed any technical tests. Check your dashboard for available tests.</p>
        </div>

        <div v-else class="results-grid">
          <div 
            v-for="test in technicalTests" 
            :key="test.id"
            class="result-card test-card"
          >
            <div class="card-header">
              <div class="header-left">
                <h3>{{ test.test_type || 'Technical Test' }}</h3>
                <p class="job-title" v-if="test.job_details">
                  <i class="fas fa-briefcase"></i>
                  {{ test.job_details.title }}
                </p>
              </div>
              <div class="status-badge" :class="getTestStatusClass(test.status)">
                {{ formatTestStatus(test.status) }}
              </div>
            </div>

            <div class="card-body">
              <div class="test-meta">
                <div class="meta-item">
                  <i class="fas fa-calendar"></i>
                  <span>Assigned: {{ formatDate(test.created_at) }}</span>
                </div>
                <div class="meta-item" v-if="test.deadline">
                  <i class="fas fa-clock"></i>
                  <span>Deadline: {{ formatDate(test.deadline) }}</span>
                </div>
              </div>

              <!-- Test Results/Assessment -->
              <div v-if="test.assessment" class="test-assessment">
                <div class="score-section">
                  <div class="score-circle" :class="getScoreClass(test.assessment.score)">
                    <span class="score-value">{{ test.assessment.score }}</span>
                    <span class="score-label">Score</span>
                  </div>
                  <div class="recommendation-badge" :class="test.assessment.recommendation">
                    {{ formatRecommendation(test.assessment.recommendation) }}
                  </div>
                </div>

                <div class="feedback-section">
                  <div class="feedback-item" v-if="test.assessment.feedback">
                    <h4><i class="fas fa-comment-dots"></i> Feedback</h4>
                    <p>{{ test.assessment.feedback }}</p>
                  </div>

                  <div class="strengths-weaknesses">
                    <div class="strength-item" v-if="test.assessment.strengths">
                      <h4><i class="fas fa-check-circle"></i> Strengths</h4>
                      <p>{{ test.assessment.strengths }}</p>
                    </div>
                    <div class="weakness-item" v-if="test.assessment.weaknesses">
                      <h4><i class="fas fa-exclamation-circle"></i> Areas for Improvement</h4>
                      <p>{{ test.assessment.weaknesses }}</p>
                    </div>
                  </div>

                  <div class="evaluated-date" v-if="test.assessment.evaluated_at">
                    <i class="fas fa-calendar-check"></i>
                    Evaluated on {{ formatDate(test.assessment.evaluated_at) }}
                  </div>
                </div>
              </div>

              <!-- Pending Evaluation -->
              <div v-else-if="test.status === 'submitted'" class="pending-evaluation">
                <i class="fas fa-hourglass-half"></i>
                <p>Your test has been submitted and is awaiting evaluation.</p>
              </div>

              <!-- Not Submitted -->
              <div v-else-if="test.status === 'scheduled'" class="not-submitted">
                <i class="fas fa-info-circle"></i>
                <p>This test is available for you to take. Please complete it before the deadline.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Interviews Tab -->
      <div v-if="activeTab === 'interviews'" class="tab-content">
        <!-- Interview Type Filter -->
        <div class="filter-section">
          <label for="interview-type-filter">
            <i class="fas fa-filter"></i> Filter by Interview Type:
          </label>
          <select 
            id="interview-type-filter"
            v-model="selectedInterviewType" 
            @change="loadInterviews"
            class="filter-select"
          >
            <option value="">All Types</option>
            <option value="technical">Technical</option>
            <option value="hr">HR</option>
            <option value="behavioral">Behavioral</option>
            <option value="panel">Panel</option>
            <option value="final">Final Round</option>
          </select>
        </div>

        <div v-if="interviewsLoading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading your interview results...</p>
        </div>

        <div v-else-if="interviews.length === 0" class="empty-state">
          <i class="fas fa-user-tie"></i>
          <h3>No Interview Results</h3>
          <p>{{ selectedInterviewType ? `No ${selectedInterviewType} interviews found.` : 'You haven\'t attended any interviews yet.' }}</p>
        </div>

        <div v-else class="results-grid">
          <div 
            v-for="interview in interviews" 
            :key="interview.id"
            class="result-card interview-card"
          >
            <div class="card-header">
              <div class="header-left">
                <h3>{{ formatInterviewType(interview.interview_type) }}</h3>
                <p class="job-title" v-if="interview.job_details">
                  <i class="fas fa-briefcase"></i>
                  {{ interview.job_details.title }}
                </p>
                <p class="interviewer" v-if="interview.interviewer_details">
                  <i class="fas fa-user"></i>
                  Interviewer: {{ interview.interviewer_details.name }}
                </p>
              </div>
              <div class="status-badge" :class="interview.status">
                {{ formatStatus(interview.status) }}
              </div>
            </div>

            <div class="card-body">
              <div class="interview-meta">
                <div class="meta-item">
                  <i class="fas fa-calendar"></i>
                  <span>{{ formatDateTime(interview.scheduled_at) }}</span>
                </div>
                <div class="meta-item" v-if="interview.duration_minutes">
                  <i class="fas fa-clock"></i>
                  <span>{{ interview.duration_minutes }} minutes</span>
                </div>
              </div>

              <!-- Interview Scorecard -->
              <div v-if="interview.scorecard" class="interview-scorecard">
                <div class="scores-grid">
                  <div class="score-item overall">
                    <span class="score-label">Overall Score</span>
                    <span class="score-value" :class="getScoreClass(interview.scorecard.overall_score)">
                      {{ interview.scorecard.overall_score || 'N/A' }}
                    </span>
                  </div>
                  <div class="score-item" v-if="interview.scorecard.technical_score">
                    <span class="score-label">Technical</span>
                    <span class="score-value">{{ interview.scorecard.technical_score }}</span>
                  </div>
                  <div class="score-item" v-if="interview.scorecard.communication_score">
                    <span class="score-label">Communication</span>
                    <span class="score-value">{{ interview.scorecard.communication_score }}</span>
                  </div>
                  <div class="score-item" v-if="interview.scorecard.problem_solving_score">
                    <span class="score-label">Problem Solving</span>
                    <span class="score-value">{{ interview.scorecard.problem_solving_score }}</span>
                  </div>
                  <div class="score-item" v-if="interview.scorecard.cultural_fit_score">
                    <span class="score-label">Cultural Fit</span>
                    <span class="score-value">{{ interview.scorecard.cultural_fit_score }}</span>
                  </div>
                </div>

                <div class="recommendation-section" v-if="interview.scorecard.recommendation">
                  <div class="recommendation-badge" :class="interview.scorecard.recommendation">
                    <i class="fas fa-thumbs-up"></i>
                    {{ formatRecommendation(interview.scorecard.recommendation) }}
                  </div>
                </div>

                <div class="feedback-section">
                  <div class="feedback-item" v-if="interview.scorecard.strengths">
                    <h4><i class="fas fa-check-circle"></i> Strengths</h4>
                    <p>{{ interview.scorecard.strengths }}</p>
                  </div>
                  <div class="feedback-item" v-if="interview.scorecard.weaknesses">
                    <h4><i class="fas fa-exclamation-circle"></i> Areas for Improvement</h4>
                    <p>{{ interview.scorecard.weaknesses }}</p>
                  </div>
                  <div class="feedback-item" v-if="interview.scorecard.feedback_notes">
                    <h4><i class="fas fa-comment-dots"></i> Additional Feedback</h4>
                    <p>{{ interview.scorecard.feedback_notes }}</p>
                  </div>
                </div>

                <div class="submitted-date" v-if="interview.scorecard.submitted_at">
                  <i class="fas fa-calendar-check"></i>
                  Feedback submitted on {{ formatDate(interview.scorecard.submitted_at) }}
                </div>
              </div>

              <!-- Pending Feedback -->
              <div v-else-if="interview.status === 'completed'" class="pending-feedback">
                <i class="fas fa-hourglass-half"></i>
                <p>Interview completed. Feedback is being prepared.</p>
              </div>

              <!-- Scheduled Interview -->
              <div v-else-if="interview.status === 'scheduled'" class="scheduled-info">
                <i class="fas fa-info-circle"></i>
                <p>This interview is scheduled. Join on time and prepare well!</p>
                <a v-if="interview.meeting_link" :href="interview.meeting_link" target="_blank" class="meeting-link">
                  <i class="fas fa-video"></i> Join Meeting
                </a>
              </div>
            </div>
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

// State
const activeTab = ref('tests')
const technicalTests = ref([])
const interviews = ref([])
const testsLoading = ref(false)
const interviewsLoading = ref(false)
const selectedInterviewType = ref('')

// Load Technical Tests
async function loadTechnicalTests() {
  testsLoading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get('/api/screening/my-performance/technical-tests', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (response.data.success) {
      technicalTests.value = response.data.tests
    }
  } catch (error) {
    console.error('Error loading technical tests:', error)
    alert('Failed to load technical test results')
  } finally {
    testsLoading.value = false
  }
}

// Load Interviews
async function loadInterviews() {
  interviewsLoading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const params = {}
    if (selectedInterviewType.value) {
      params.interview_type = selectedInterviewType.value
    }
    
    const response = await axios.get('/api/screening/my-performance/interviews', {
      headers: { Authorization: `Bearer ${token}` },
      params
    })
    
    if (response.data.success) {
      interviews.value = response.data.interviews
    }
  } catch (error) {
    console.error('Error loading interviews:', error)
    alert('Failed to load interview results')
  } finally {
    interviewsLoading.value = false
  }
}

// Utility Functions
function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatTestStatus(status) {
  const statusMap = {
    'scheduled': 'Available',
    'submitted': 'Submitted',
    'evaluated': 'Evaluated',
    'expired': 'Expired'
  }
  return statusMap[status] || status
}

function getTestStatusClass(status) {
  return status ? status.toLowerCase() : ''
}

function formatStatus(status) {
  if (!status) return 'N/A'
  return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')
}

function formatInterviewType(type) {
  if (!type) return 'Interview'
  return type.charAt(0).toUpperCase() + type.slice(1) + ' Interview'
}

function getScoreClass(score) {
  if (!score) return ''
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'average'
  return 'poor'
}

function formatRecommendation(recommendation) {
  const recMap = {
    'hire': 'Recommended for Hire',
    'strong_hire': 'Strongly Recommended',
    'no_hire': 'Not Recommended',
    'maybe': 'Under Consideration',
    'borderline': 'Borderline',
    'pass': 'Pass',
    'fail': 'Needs Improvement'
  }
  return recMap[recommendation] || recommendation
}

// Load data on mount
onMounted(() => {
  loadTechnicalTests()
  loadInterviews()
})
</script>

<style scoped>
.performance-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-header h1 i {
  color: #667eea;
}

.page-header p {
  color: #7f8c8d;
  font-size: 1rem;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 2px solid #ecf0f1;
}

.tab-btn {
  padding: 12px 24px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  color: #7f8c8d;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  color: #667eea;
  background-color: #f8f9fa;
}

.tab-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.tab-btn .badge {
  background: #667eea;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.tab-btn.active .badge {
  background: #764ba2;
}

/* Filter Section */
.filter-section {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-section label {
  font-weight: 500;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-select {
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  background: white;
  transition: border-color 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
}

/* Loading and Empty States */
.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.loading-state i,
.empty-state i {
  font-size: 4rem;
  color: #bdc3c7;
  margin-bottom: 20px;
}

.loading-state i {
  color: #667eea;
}

.empty-state h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

/* Results Grid */
.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 24px;
}

.result-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.result-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.card-header {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left h3 {
  margin: 0 0 8px 0;
  font-size: 1.3rem;
}

.job-title,
.interviewer {
  margin: 6px 0;
  opacity: 0.95;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.status-badge.scheduled,
.status-badge.available {
  background: #3498db;
}

.status-badge.submitted {
  background: #f39c12;
}

.status-badge.evaluated,
.status-badge.completed {
  background: #27ae60;
}

.status-badge.expired,
.status-badge.cancelled {
  background: #e74c3c;
}

.card-body {
  padding: 20px;
}

/* Meta Info */
.test-meta,
.interview-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ecf0f1;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.meta-item i {
  color: #667eea;
}

/* Score Section */
.score-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 10px;
}

.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  border: 4px solid;
}

.score-circle.excellent {
  border-color: #27ae60;
  background: rgba(39, 174, 96, 0.1);
  color: #27ae60;
}

.score-circle.good {
  border-color: #3498db;
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.score-circle.average {
  border-color: #f39c12;
  background: rgba(243, 156, 18, 0.1);
  color: #f39c12;
}

.score-circle.poor {
  border-color: #e74c3c;
  background: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
}

.score-value {
  font-size: 2rem;
}

.score-label {
  font-size: 0.85rem;
  text-transform: uppercase;
  opacity: 0.8;
}

.recommendation-badge {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  text-align: center;
  flex: 1;
}

.recommendation-badge.hire,
.recommendation-badge.strong_hire,
.recommendation-badge.pass {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.recommendation-badge.no_hire,
.recommendation-badge.fail {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.recommendation-badge.maybe,
.recommendation-badge.borderline {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

/* Feedback Section */
.feedback-section {
  margin-top: 20px;
}

.feedback-item {
  margin-bottom: 20px;
}

.feedback-item h4 {
  color: #2c3e50;
  font-size: 1rem;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.feedback-item p {
  color: #555;
  line-height: 1.6;
  padding-left: 24px;
}

.strengths-weaknesses {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.strength-item h4 i {
  color: #27ae60;
}

.weakness-item h4 i {
  color: #e74c3c;
}

/* Interview Scorecard */
.scores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.score-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 10px;
  text-align: center;
}

.score-item.overall {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  grid-column: span 2;
}

.score-item .score-label {
  display: block;
  font-size: 0.85rem;
  margin-bottom: 8px;
  opacity: 0.8;
  text-transform: uppercase;
}

.score-item .score-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #667eea;
}

.score-item.overall .score-value {
  color: white;
}

.recommendation-section {
  margin-bottom: 20px;
}

/* Pending/Info States */
.pending-evaluation,
.not-submitted,
.pending-feedback,
.scheduled-info {
  padding: 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f8f9fa;
  color: #7f8c8d;
}

.pending-evaluation i,
.pending-feedback i {
  font-size: 1.5rem;
  color: #f39c12;
}

.not-submitted i,
.scheduled-info i {
  font-size: 1.5rem;
  color: #3498db;
}

.scheduled-info {
  flex-direction: column;
  align-items: flex-start;
}

.meeting-link {
  margin-top: 10px;
  padding: 10px 20px;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: background 0.3s ease;
}

.meeting-link:hover {
  background: #764ba2;
}

/* Dates */
.evaluated-date,
.submitted-date {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ecf0f1;
  color: #7f8c8d;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Responsive */
@media (max-width: 768px) {
  .results-grid {
    grid-template-columns: 1fr;
  }

  .strengths-weaknesses {
    grid-template-columns: 1fr;
  }

  .scores-grid {
    grid-template-columns: 1fr 1fr;
  }

  .score-item.overall {
    grid-column: span 2;
  }
}
</style>
