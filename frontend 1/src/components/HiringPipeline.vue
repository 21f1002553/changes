<template>
  <DashboardLayout>
    <div class="hiring-pipeline-page">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>
            <i class="fas fa-stream"></i>
            Hiring Pipeline
          </h1>
          <p>Manage candidates through the recruitment process</p>
        </div>
        <div class="header-actions">
          <select v-model="selectedJobId" @change="loadPipelineData" class="job-filter">
            <option value="">All Jobs</option>
            <option v-for="job in jobs" :key="job.id" :value="job.id">
              {{ job.title }} - {{ job.location }}
            </option>
          </select>
          <button @click="refreshPipeline" class="btn-refresh" :disabled="loading">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
            Refresh
          </button>
        </div>
      </div>

      <!-- Pipeline Board -->
      <div class="hiring-pipeline-board">
        <div v-for="stage in pipelineStages" :key="stage.id" class="pipeline-stage"
          :class="{ 'stage-loading': loading }">
          <!-- Stage Header -->
          <div class="stage-header">
            <div class="stage-info">
              <h3>{{ stage.name }}</h3>
              <span class="candidate-count">{{ getCandidatesInStage(stage.id).length }}</span>
            </div>
            <div class="stage-actions">
              <button v-if="stage.name === 'Technical Test'" @click="generateTechnicalTest"
                class="action-btn generate-test-btn">
                <i class="fas fa-magic"></i>
                AI Test
              </button>
            </div>
          </div>

          <!-- Candidates in Stage -->
          <div class="candidate-cards" v-if="!loading">
            <div v-for="candidate in getCandidatesInStage(stage.id)" :key="candidate.id" class="candidate-card"
              :class="{ 'has-interview': candidate.interview_assignments }">
              <!-- Candidate Basic Info -->
              <div class="candidate-header">
                <div class="candidate-avatar">
                  {{ getInitials(candidate.name) }}
                </div>
                <div class="candidate-info">
                  <h4>{{ candidate.name }}</h4>
                  <p>{{ candidate.job_title }}</p>
                </div>
              </div>

              <!-- Candidate Metrics -->
              <div class="candidate-metrics">
                <div class="metric-item">
                  <span class="metric-label">Match Score:</span>
                  <span class="metric-value score" :class="getScoreClass(candidate.score)">
                    {{ candidate.score || 'N/A' }}%
                  </span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">In stage:</span>
                  <span class="metric-value">{{ getDaysInStage(candidate.entered_at) }} days</span>
                </div>
              </div>

              <!-- Offer Letter Section (for Offer Stage) -->
              <div v-if="isOfferStage(stage)" class="offer-section">
                <!-- Offer Letter Sent -->
                <div v-if="candidate.offer_letter" class="offer-status">
                  <div class="offer-info">
                    <i class="fas fa-file-contract"></i>
                    <span>Offer Letter Sent</span>
                  </div>
                  <div class="acceptance-status" :class="candidate.offer_letter.acceptance_status">
                    <i :class="{
                      'fas fa-clock': candidate.offer_letter.acceptance_status === 'pending',
                      'fas fa-check-circle': candidate.offer_letter.acceptance_status === 'accepted',
                      'fas fa-times-circle': candidate.offer_letter.acceptance_status === 'rejected'
                    }"></i>
                    {{ formatOfferStatus(candidate.offer_letter.acceptance_status) }}
                  </div>
                  <div v-if="candidate.offer_letter.accepted_at" class="offer-date">
                    {{ candidate.offer_letter.acceptance_status === 'accepted' ? 'Accepted' : 'Rejected' }} on: {{ formatDate(candidate.offer_letter.accepted_at) }}
                  </div>
                </div>

                <!-- Send Offer Button -->
                <div v-else class="send-offer-section">
                  <button @click="sendOfferLetter(candidate)" class="action-btn send-offer-btn"
                    :disabled="processingCandidate === candidate.id">
                    <i class="fas fa-paper-plane"></i>
                    Send Offer Letter
                  </button>
                </div>
              </div>

              <!-- Interview Assignment Section -->
              <div v-if="isInterviewStage(stage)" class="interview-section">
                <!-- Show Assigned Interviewer -->
                <div v-if="findInterviewAssignment(candidate.interview_assignments, stage.name)"
                  class="interviewer-assigned" @click="viewInterviewDetails(candidate, stage)" style="cursor:pointer;">
                  <div class="interviewer-info">
                    <i class="fas fa-user-tie"></i>
                    <span>{{ findInterviewName(candidate.interview_assignments, stage.name) }}</span>
                    <span class="interview-type">{{
                      formatInterviewType(findInterviewAssignment(candidate.interview_assignments,
                      stage.name).interview_type) }}</span>
                  </div>
                  <div class="interview-status" :class="candidate.interview_assignments.status">
                    {{ formatInterviewStatus(findInterviewAssignment(candidate.interview_assignments,
                    stage.name).status) }}
                  </div>
                  <div class="view-details-hint">
                    <i class="fas fa-eye"></i> Click to view details
                  </div>
                </div>

                <!-- Assign Interviewer Button -->
                <div v-else class="assign-interviewer-section">
                  <button @click="openAssignmentModal(candidate, stage)" class="action-btn assign-interviewer">
                    <i class="fas fa-plus"></i>
                    Assign Interviewer
                  </button>

                  <!-- Interviewer Selection Dropdown -->
                  <div v-if="assigningToCandidateId === candidate.id" class="interviewer-dropdown">
                    <div class="dropdown-header">Select Interviewer</div>
                    <div class="interviewer-list">
                      <div v-for="interviewer in getInterviewersForStage(stage)" :key="interviewer.id"
                        @click="assignInterviewer(candidate.id, interviewer, stage)" class="interviewer-option">
                        <div class="interviewer-details">
                          <span class="interviewer-name">{{ interviewer.name }}</span>
                          <span class="interviewer-role">{{ interviewer.role_name }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Interview Results & Actions -->
              <div v-if="candidate.scorecard" class="interview-results">
                <div class="scorecard-summary">
                  <div class="overall-score">
                    <span>Overall: {{ candidate.scorecard.overall_score }}/5</span>
                  </div>
                  <div class="recommendation" :class="candidate.scorecard.recommendation">
                    {{ formatRecommendation(candidate.scorecard.recommendation) }}
                  </div>
                </div>
              </div>

              <!-- Card Actions -->
              <div class="card-actions">
                <!-- View Scorecard Button -->
                <button v-if="candidate.scorecard" @click="viewScorecard(candidate)" class="action-btn view-scorecard">
                  <i class="fas fa-chart-bar"></i>
                  Scorecard
                </button>

                <!-- View Resume Button -->
                <button @click="viewResume(candidate)" class="action-btn view-resume">
                  <i class="fas fa-file-alt"></i>
                  Resume
                </button>

                <!-- Stage Actions -->
                <div class="stage-actions">
                  <!-- Pass/Fail for Interview Stages -->
                  <div v-if="isInterviewStage(stage) && candidate.scorecard" class="pass-fail-actions">
                    <button @click="moveToNextStage(candidate, 'pass')" class="action-btn pass-btn"
                      :disabled="processingCandidate === candidate.id">
                      <i class="fas fa-check"></i>
                      Pass
                    </button>
                    <button @click="rejectCandidate(candidate)" class="action-btn fail-btn"
                      :disabled="processingCandidate === candidate.id">
                      <i class="fas fa-times"></i>
                      Reject
                    </button>
                  </div>

                  <!-- Next Stage Button for Other Stages (except Hired stage) -->
                  <div v-else-if="!isHiredStage(stage)" class="next-stage-actions">
                    <div class="action-row">
                      <button v-if="!isLastStage(stage)" @click="moveToNextStage(candidate, 'proceed')" class="action-btn next-stage-btn"
                        :disabled="processingCandidate === candidate.id">
                        <i class="fas fa-arrow-right"></i>
                        {{ isOfferStage(stage) ? 'Hire' : 'Next Stage' }}
                      </button>
                      <button v-else-if="isOfferStage(stage)" @click="hireCandidate(candidate)" class="action-btn hire-btn"
                        :disabled="processingCandidate === candidate.id">
                        <i class="fas fa-user-plus"></i>
                        Hire
                      </button>
                      
                      <!-- Reject Button for All Stages (except Hired) -->
                      <button @click="rejectCandidate(candidate)" class="action-btn reject-btn"
                        :disabled="processingCandidate === candidate.id">
                        <i class="fas fa-times"></i>
                        Reject
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Processing Indicator -->
              <div v-if="processingCandidate === candidate.id" class="processing-indicator">
                <i class="fas fa-spinner fa-spin"></i>
                Processing...
              </div>
            </div>

            <!-- Empty Stage Message -->
            <div v-if="getCandidatesInStage(stage.id).length === 0" class="empty-stage">
              <i class="fas fa-inbox"></i>
              <p>No candidates in this stage</p>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="stage-loading-indicator">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading candidates...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Scorecard Modal -->
    <ScorecardModal v-if="showScorecardModal" :candidate="selectedCandidate" :scorecard="selectedScorecard"
      @close="closeScorecardModal" />

    <!-- Resume Modal -->
  <ResumeModal v-if="showResumeModal" :candidate="selectedCandidate" @close="closeResumeModal" />
  </DashboardLayout>
  <InterviewAssignmentModal v-if="showAssignmentModal" :candidate="selectedCandidate" :stage="selectedStage" :assigner="userData"
    :availableInterviewers="getInterviewersForStage(selectedStage)" @close="closeAssignmentModal"
    @assigned="handleInterviewAssigned" />
  <InterviewDetailsModal v-if="showInterviewDetailsModal" :candidate="selectedCandidate" :stage="selectedStage"
    :interviewAssignment="selectedInterviewAssignment" @close="closeInterviewDetailsModal" @viewResume="viewResume"
    @viewScorecard="viewScorecard" @reschedule="handleReschedule" @edit="handleEditInterview" />

  <AITestModal
    v-if="showAITestModal"
    :candidate="selectedCandidate"
    :jobDetails="selectedJobDetails"
    @close="closeAITestModal"
    @testGenerated="handleTestGenerated"
  />

  <TestResultsModal
    v-if="showTestResultsModal"
    :candidate="selectedCandidate"
    :testId="selectedTestId"
    @close="closeTestResultsModal"
    @assessmentSubmitted="handleAssessmentSubmitted"
  />
  
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'
import ScorecardModal from './ScorecardModal.vue'
import ResumeModal from './ResumeModal.vue'
import InterviewAssignmentModal from './InterviewAssignmentModal.vue'
import InterviewDetailsModal from './InterviewDetailsModal.vue'
import AITestModal from './AITestModal.vue'
import TestResultsModal from './TestResultsModal.vue'

const router = useRouter()

// State
const userData = ref([])
const jobs = ref([])
const selectedJobId = ref('')
const pipelineStages = ref([])
const candidatesInPipeline = ref([])
const HRinterviewers = ref([])
const BDAinterviewers = ref([])
const Managers = ref([])
const loading = ref(false)
const processingCandidate = ref(null)
const assigningToCandidateId = ref(null)

// Modal States
const showScorecardModal = ref(false)
const showResumeModal = ref(false)
const selectedCandidate = ref(null)
const selectedScorecard = ref(null)

const showAssignmentModal = ref(false)
const selectedStage = ref(null)

const showInterviewDetailsModal = ref(false)
const selectedInterviewAssignment = ref(null)


const showAITestModal = ref(false)
const showTestResultsModal = ref(false)
const selectedJobDetails = ref(null)
const selectedTestId = ref(null)


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

function getDaysInStage(enteredAt) {
  if (!enteredAt) return 0
  const entered = new Date(enteredAt)
  const now = new Date()
  const diffTime = Math.abs(now - entered)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

function getScoreClass(score) {
  if (!score) return 'score-na'
  if (score >= 90) return 'score-excellent'
  if (score >= 75) return 'score-good'
  if (score >= 60) return 'score-average'
  return 'score-poor'
}

function isInterviewStage(stage) {
  const interviewStages = ['Technical Test', 'Technical Interview', 'Behavioral Interview', 'Final Interview']
  return interviewStages.includes(stage.name)
}

function isLastStage(stage) {
  return stage.name === 'Offer' || stage.order_index === Math.max(...pipelineStages.value.map(s => s.order_index))
}

function isHiredStage(stage) {
  return stage.name === 'Hired'
}

function isOfferStage(stage) {
  return stage.name === 'Offer'
}

function checkInterviewType(type) {
  const interviewTypeMap = {
    'Technical Test': 'technical_test',
    'Technical Interview': 'technical_interview',
    'Behavioral Interview': 'behavioral_interview',
    'Final Interview': 'final_interview'
  }
  return interviewTypeMap[type]
}

function findInterviewAssignment(interviews, stageName) {
  if (!interviews || !Array.isArray(interviews)) return null
  
  const interviewType = checkInterviewType(stageName)
  
  // Filter interviews by type
  const matchingInterviews = interviews.filter(
    interview => interview.interview_type === interviewType
  )
  
  // If no matches, return null
  if (matchingInterviews.length === 0) return null
  
  // Sort by assigned_at date (most recent first)
  const sortedInterviews = matchingInterviews.sort((a, b) => {
    const dateA = new Date(a.assigned_at)
    const dateB = new Date(b.assigned_at)
    return dateB - dateA
  })
  
  // Return the most recent one
  return sortedInterviews[0]
}
function findInterviewName(interviews, stageName) {
  const assignment = findInterviewAssignment(interviews, stageName)
  return assignment ? assignment.interviewer_name : null
}


function formatInterviewType(type) {
  const typeMap = {
    'technical_test': 'Technical Test',
    'technical_interview': 'Technical',
    'behavioral_interview': 'Behavioral',
    'final_interview': 'Final'
  }
  return typeMap[type] || type
}

function formatInterviewStatus(status) {
  const statusMap = {
    'scheduled': 'Scheduled',
    'completed': 'Completed',
    'cancelled': 'Cancelled',
    'rescheduled': 'Rescheduled'
  }
  return statusMap[status] || status
}

function formatRecommendation(recommendation) {
  const recMap = {
    'strong_hire': 'Strong Hire',
    'hire': 'Hire',
    'maybe': 'Maybe',
    'no_hire': 'No Hire'
  }
  return recMap[recommendation] || recommendation
}

function formatOfferStatus(status) {
  const statusMap = {
    'pending': 'Pending Acceptance',
    'accepted': 'Accepted',
    'rejected': 'Rejected'
  }
  return statusMap[status] || status
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

function formatDateTime(dateString) {
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}


function getCandidatesInStage(stageId) {
  return candidatesInPipeline.value.filter(candidate => candidate.current_stage_id === stageId)
}

function getInterviewersForStage(stage) {
  // Return appropriate interviewers based on stage
  const stageInterviewerMap = {
    'Technical Test': Managers.value,
    'Technical Interview': Managers.value,
    'Behavioral Interview': [...HRinterviewers.value, ...BDAinterviewers.value],
    'Final Interview': HRinterviewers.value
  }

  return stageInterviewerMap[stage.name] || HRinterviewers.value
}


function closeAssignmentModal() {
  showAssignmentModal.value = false
  selectedCandidate.value = null
  selectedStage.value = null
}


function viewInterviewDetails(candidate, stage) {
  const assignment = findInterviewAssignment(candidate.interview_assignments, stage.name)
  if (assignment) {
    selectedCandidate.value = candidate
    selectedStage.value = stage
    selectedInterviewAssignment.value = assignment
    showInterviewDetailsModal.value = true
  }
}

function closeInterviewDetailsModal() {
  showInterviewDetailsModal.value = false
  selectedCandidate.value = null
  selectedStage.value = null
  selectedInterviewAssignment.value = null
}

function handleReschedule(assignment) {
  // Implement reschedule logic
  console.log('Reschedule interview:', assignment)
  closeInterviewDetailsModal()
  // Open assignment modal for rescheduling
  openAssignmentModal(selectedCandidate.value, selectedStage.value)
}

function handleEditInterview(assignment) {
  // Implement edit logic
  console.log('Edit interview:', assignment)
  closeInterviewDetailsModal()
  // Open assignment modal for editing
  openAssignmentModal(selectedCandidate.value, selectedStage.value)
}


function handleInterviewAssigned(assignmentData) {
  // Update candidate with assignment
  const candidate = candidatesInPipeline.value.find(c => c.id === assignmentData.candidate_id)
  if (candidate) {
    if (!Array.isArray(candidate.interview_assignments)) {
      candidate.interview_assignments = []
    }
    candidate.interview_assignments.push({
      id: assignmentData.id,
      interviewer_id: assignmentData.interviewer_id,
      interviewer_name: assignmentData.interviewer_name,
      interview_type: assignmentData.interview_type,
      status: assignmentData.status || 'scheduled',
      scheduled_at: assignmentData.scheduled_at,
      duration: assignmentData.duration_minutes,
      meeting_link: assignmentData.meeting_link
    })
  }

  alert(`Interview assigned successfully to ${assignmentData.interviewer_name}!`)
}


// API Functions
async function loadJobs() {
  try {
    const response = await axios.get('/api/jobs/', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      jobs.value = response.data.filter(job => job.status === 'active')
    }
  } catch (error) {
    console.error('Failed to load jobs:', error)
  }
}

async function loadPipelineStages() {
  try {
    const response = await axios.get('/api/pipeline/stages', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data?.stages) {
      pipelineStages.value = response.data.stages
        .filter(stage => stage.is_active)
        .sort((a, b) => a.order_index - b.order_index)
    }
  } catch (error) {
    console.error('Failed to load pipeline stages:', error)
  }
}

async function loadManagerInterviewers() {
  try {
    const response = await axios.get('/api/users/role/manager', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      Managers.value = response.data
    }
  } catch (error) {
    console.error('Failed to load interviewers:', error)
  }
}

async function loadBDAInterviewers() {
  try {
    const response = await axios.get('/api/users/role/bda', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      BDAinterviewers.value = response.data
    }
  } catch (error) {
    console.error('Failed to load interviewers:', error)
  }
}

async function loadHRInterviewers() {
  try {
    const response = await axios.get('/api/users/role/hr', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      HRinterviewers.value = response.data
    }
  } catch (error) {
    console.error('Failed to load interviewers:', error)
  }
}

// async function loadPipelineData() {
//   await Promise.all([
//     loadPipelineStages(),
//     loadInterviewers(),
//     loadPipelineCandidatesForAllStages()
//   ])
// }

// Action Functions
function openAssignmentModal(candidate, stage) {
  selectedCandidate.value = candidate
  selectedStage.value = stage
  showAssignmentModal.value = true
}

function closeAITestModal() {
  showAITestModal.value = false
  selectedCandidate.value = null
  selectedJobDetails.value = null
}


function handleTestGenerated(testData) {
  console.log('Test generated:', testData)
  alert(`AI test generated successfully! Test scheduled for ${selectedCandidate.value.name}`)
  
  // Refresh pipeline data to show test assignment
  loadPipelineData()
}

function openTestResults(candidate, testId) {
  selectedCandidate.value = candidate
  selectedTestId.value = testId
  showTestResultsModal.value = true
}

function closeTestResultsModal() {
  showTestResultsModal.value = false
  selectedCandidate.value = null
  selectedTestId.value = null
}

function handleAssessmentSubmitted(assessmentData) {
  console.log('Assessment submitted:', assessmentData)
  
  // Update candidate with test score
  const candidate = candidatesInPipeline.value.find(c => c.id === assessmentData.candidate_id)
  if (candidate) {
    candidate.test_score = assessmentData.score_percentage
    candidate.test_recommendation = assessmentData.recommendation
  }
  
  // Refresh pipeline data
  loadPipelineData()
}



async function loadPipelineCandidates() {
  try {
    loading.value = true

    const params = {}
    if (selectedJobId.value) {
      params.job_id = selectedJobId.value
    }


    const response = await axios.get('/api/pipeline/candidates', {
      params,
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data?.candidates) {
      candidatesInPipeline.value = response.data.candidates.map(candidate => ({
        id: candidate.candidate_details?.id || candidate.candidate_id,
        name: candidate.candidate_details?.name || 'Unknown',
        email: candidate.candidate_details?.email || '',
        job_id: candidate.application_details?.job_id || candidate.job_id,
        job_title: candidate.application_details?.job_title || 'N/A',
        score: candidate.application_details?.score || null,
        application_id: candidate.application_details?.id,
        current_stage_id: candidate.stage_info?.id || candidate.stage_id,
        stage_name: candidate.stage_info?.name || 'Unknown',
        entered_at: candidate.entered_at,
        // Initialize empty - will be loaded separately
        interview_assignments: [],
        scorecard: null,
        offer_letter: null
      }))
    console.log(candidatesInPipeline.value)
      // Load interview assignments and scorecards for each candidate individually
      await loadInterviewAssignments()
      await loadScorecards()
      await loadOfferStatuses()
    }

  } catch (error) {
    console.error('❌ Failed to load pipeline candidates:', error)
    candidatesInPipeline.value = []
  } finally {
    loading.value = false
  }
}

// Load interview assignments for all candidates (one by one)
async function loadInterviewAssignments() {
  try {
    for (const candidate of candidatesInPipeline.value) {
      try {
        const response = await axios.get('/api/pipeline/interview-assignments', {
          params: {
            candidate_id: candidate.id,
            job_id: candidate.job_id
          },
          headers: { Authorization: `Bearer ${getAuthToken()}` }
        })

        if (response.data?.interview_assignments && response.data.interview_assignments.length > 0) {

          const sortedAssignments = response.data.interview_assignments.sort((a, b) => {
            const dateA = new Date(a.scheduled_at);
            const dateB = new Date(b.scheduled_at);
            return dateB - dateA;
          })

          // Get the most recent assignment
        
        candidate.interview_assignments = sortedAssignments.map(assignment => ({
            id: assignment.id,
            interviewer_id: assignment.interviewer_id,
            interviewer_name: assignment.interviewer_name || 'Unknown',
            interview_type: assignment.interview_type,
            status: assignment.status,
            job_id: assignment.job_id,
            job_title: assignment.job_title,
            scheduled_at: assignment.scheduled_at,
            duration: assignment.duration_minutes,
            meeting_link: assignment.meeting_link,
            assigned_at: assignment.assigned_at
        }))
        console.log(`✅ Loaded ${candidate.interview_assignments.length} interview assignments for ${candidate.name}`)
        } else {
          candidate.interview_assignments = []
        }
        console.log(`assignments`, candidate.interview_assignments)
      } catch (error) {
        console.error(`❌ Failed to load interview assignment for candidate ${candidate.id}:`, error)
      }
    }
  } catch (error) {
    console.error('❌ Failed to load interview assignments:', error)
  }
}



async function assignInterviewer(candidateId, interviewer, stage) {
  try {
    processingCandidate.value = candidateId

    const candidate = candidatesInPipeline.value.find(c => c.id === candidateId)
    if (!candidate) {
      throw new Error('Candidate not found')
    }

    const interviewTypeMap = {
      'Technical Test': 'technical_test',
      'Technical Interview': 'technical_interview',
      'Behavioral Interview': 'behavioral_interview',
      'Final Interview': 'final_interview'
    }

    // Use your exact backend endpoint structure
    const response = await axios.post('/api/pipeline/assign-interviewer', {
      candidate_id: candidateId,
      job_id: selectedJobId.value || candidate.job_id,
      interviewer_id: interviewer.id,
      interview_type: interviewTypeMap[stage.name],
      duration_minutes: 60,
      assigned_by_id: getCurrentUserId(),
      scheduled_at: null // as of now
    }, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data?.assignment) {
      // Update local state
      candidate.interview_assignment = {
        id: response.data.assignment.id,
        interviewer_id: interviewer.id,
        interviewer_name: interviewer.name,
        interview_type: interviewTypeMap[stage.name],
        status: response.data.assignment.status || 'scheduled'
      }

      assigningToCandidateId.value = null
      alert(`Interviewer ${interviewer.name} assigned successfully!`)
    }

  } catch (error) {
    console.error('❌ Failed to assign interviewer:', error)

    alert('Failed to assign interviewer. Please try again.')
  } finally {
    processingCandidate.value = null
  }
}

// Updated moveToNextStage function to match your backend
async function moveToNextStage(candidate, action) {
  if (!confirm(`Move ${candidate.name} to the next stage?`)) return

  try {
    processingCandidate.value = candidate.id

    // Find next stage
    const currentStageIndex = pipelineStages.value.findIndex(s => s.id === candidate.current_stage_id)
    const nextStage = pipelineStages.value[currentStageIndex + 1]

    if (!nextStage) {
      throw new Error('No next stage available')
    }

    // Use your exact backend endpoint
    const response = await axios.put(`/api/pipeline/candidates/${candidate.id}/move`, {
      stage_id: nextStage.id,
      job_id: selectedJobId.value || candidate.job_id,
      notes: `Moved by HR - ${action}`,
      moved_by_id: getCurrentUserId()
    }, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      // Refresh candidates data
      await loadPipelineCandidates()
      alert(`${candidate.name} moved to ${nextStage.name} successfully!`)
    }

  } catch (error) {
    console.error('❌ Failed to move candidate:', error)
    alert('Failed to move candidate. Please try again.')
  } finally {
    processingCandidate.value = null
  }
}

// Updated hire candidate function
async function hireCandidate(candidate) {
  if (!confirm(`Hire ${candidate.name}? This will update their application status.`)) return

  try {
    processingCandidate.value = candidate.id

    // Update application status to hired
    const response = await axios.put(`/api/applications/${candidate.application_id}`, {
      status: 'hired',
      notes: 'Hired through pipeline process'
    }, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      // Remove from pipeline view
      candidatesInPipeline.value = candidatesInPipeline.value.filter(c => c.id !== candidate.id)
      alert(`${candidate.name} has been hired! Application status updated.`)
    }

  } catch (error) {
    console.error('❌ Failed to hire candidate:', error)
    alert('Failed to hire candidate. Please try again.')
  } finally {
    processingCandidate.value = null
  }
}


async function generateTechnicalTest() {
  try {
    // Get job details for the selected job or first candidate's job
    let jobId = selectedJobId.value
    
    if (!jobId && candidatesInPipeline.value.length > 0) {
      jobId = candidatesInPipeline.value[0].job_id
    }
    
    if (!jobId) {
      alert('Please select a job first')
      return
    }

    // Load job details
    const jobResponse = await axios.get(`/api/jobs/${jobId}`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (jobResponse.data) {
      selectedJobDetails.value = jobResponse.data
      
      // Find a candidate in Technical Assessment stage
      const technicalStage = pipelineStages.value.find(s => s.name === 'Technical Test')
      if (!technicalStage) {
        alert('Technical Test stage not found')
        return
      }
      
      const candidatesInTechnicalStage = getCandidatesInStage(technicalStage.id)
      if (candidatesInTechnicalStage.length === 0) {
        alert('No candidates in Technical Assessment stage')
        return
      }
      
      // For demo, select first candidate. In real app, you might want a selection UI
      selectedCandidate.value = candidatesInTechnicalStage[0]
      showAITestModal.value = true
    }
  } catch (error) {
    console.error('Failed to load job details:', error)
    alert('Failed to load job details')
  }
}

// Simplified loadPipelineData function
async function loadPipelineData() {
  await loadPipelineStages()
  await loadHRInterviewers()
  await loadBDAInterviewers()
  await loadManagerInterviewers()


  // Only load candidates after stages are loaded
  if (pipelineStages.value.length > 0) {
    await loadPipelineCandidates()
  }
}

// Add helper function to get current user ID
function getCurrentUserId() {
  // Implement this based on how you store user info
  return localStorage.getItem('user_id') || null
}


async function rejectCandidate(candidate) {
  if (!confirm(`Are you sure you want to reject ${candidate.name}?`)) return

  try {
    processingCandidate.value = candidate.id

    const response = await axios.put(`/api/applications/${candidate.application_id}/status`, {
      status: 'rejected',
      notes: 'Rejected by HR during pipeline review'
    }, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      // Remove from pipeline
      candidatesInPipeline.value = candidatesInPipeline.value.filter(c => c.id !== candidate.id)
      alert(`${candidate.name} has been rejected.`)
    }

  } catch (error) {
    console.error('❌ Failed to reject candidate:', error)
    alert('Failed to reject candidate. Please try again.')
  } finally {
    processingCandidate.value = null
  }
}

// Offer Letter Functions
async function loadOfferStatuses() {
  try {
    const offerStage = pipelineStages.value.find(s => s.name === 'Offer')
    if (!offerStage) return

    const candidatesInOfferStage = candidatesInPipeline.value.filter(
      c => c.current_stage_id === offerStage.id
    )

    for (const candidate of candidatesInOfferStage) {
      try {
        const response = await axios.get(
          `/api/pipeline/offer-status/${candidate.id}/${candidate.job_id}`,
          { headers: { Authorization: `Bearer ${getAuthToken()}` } }
        )

        if (response.data.has_offer) {
          candidate.offer_letter = response.data.offer
        }
      } catch (error) {
        console.error(`Error loading offer status for candidate ${candidate.id}:`, error)
      }
    }
  } catch (error) {
    console.error('Error loading offer statuses:', error)
  }
}

async function sendOfferLetter(candidate) {
  const salary = prompt(`Enter salary offer for ${candidate.name}:`, '50000')
  
  if (!salary) return

  try {
    processingCandidate.value = candidate.id

    const response = await axios.post(
      '/api/pipeline/send-offer',
      {
        candidate_id: candidate.id,
        job_id: candidate.job_id,
        salary: salary
      },
      { headers: { Authorization: `Bearer ${getAuthToken()}` } }
    )

    candidate.offer_letter = response.data.offer
    alert('Offer letter sent successfully!')
    await refreshPipeline()
  } catch (error) {
    console.error('Error sending offer letter:', error)
    alert(error.response?.data?.error || 'Failed to send offer letter. Please try again.')
  } finally {
    processingCandidate.value = null
  }
}

// Load scorecards for all candidates (one by one)
async function loadScorecards() {
  try {
    for (const candidate of candidatesInPipeline.value) {
      try {
        const response = await axios.get('/api/pipeline/scorecards', {
          params: {
            candidate_id: candidate.id,
            job_id: candidate.job_id
          },
          headers: { Authorization: `Bearer ${getAuthToken()}` }
        })

        if (response.data?.scorecards && response.data.scorecards.length > 0) {
          // Get the most recent scorecard
          const scorecard = response.data.scorecards[0]
          candidate.scorecard = {
            id: scorecard.id,
            overall_score: scorecard.overall_score,
            recommendation: scorecard.recommendation,
            technical_score: scorecard.technical_score,
            communication_score: scorecard.communication_score,
            problem_solving_score: scorecard.problem_solving_score,
            cultural_fit_score: scorecard.cultural_fit_score,
            strengths: scorecard.strengths,
            weaknesses: scorecard.weaknesses,
            feedback_notes: scorecard.feedback_notes,
            interview_type: scorecard.interview_type,
            interviewer_name: scorecard.interviewer?.name || 'Unknown',
            interview_date: scorecard.submitted_at
          }
        }
      } catch (error) {
        console.error(`❌ Failed to load scorecard for candidate ${candidate.id}:`, error)
      }
    }
  } catch (error) {
    console.error('❌ Failed to load scorecards:', error)
  }
}


async function refreshPipeline() {
  await loadPipelineData()
}

// Modal Functions
function viewScorecard(candidate) {
  selectedCandidate.value = candidate
  selectedScorecard.value = candidate.scorecard
  showScorecardModal.value = true
}

function closeScorecardModal() {
  showScorecardModal.value = false
  selectedCandidate.value = null
  selectedScorecard.value = null
}

function viewResume(candidate) {
  selectedCandidate.value = candidate
  showResumeModal.value = true
}

function closeResumeModal() {
  showResumeModal.value = false
  selectedCandidate.value = null
}

async function loadHRData() {
  // Load HR dashboard data
  try{
    const response = await axios.get('/api/users/', {
    headers: { Authorization: `Bearer ${getAuthToken()}` }
  })

  if (response.data) {
    userData.value = response.data
    }
  }
  catch(error) {
    console.error('Failed to load HR data:', error)
  }
}


// Load data on mount
onMounted(async () => {
  await loadHRData()
  await loadJobs()
  await loadPipelineData()
})
</script>

<style scoped>
.hiring-pipeline-page {
  padding: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  background: white;
  border-bottom: 2px solid #ecf0f1;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  font-size: 2.2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-content p {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.job-filter {
  padding: 10px 15px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  background: white;
  color: #2c3e50;
  cursor: pointer;
  min-width: 200px;
  font-size: 0.95rem;
}

.btn-refresh {
  padding: 10px 20px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.btn-refresh:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-1px);
}

/* Pipeline Board */
.hiring-pipeline-board {
  display: flex;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  gap: 20px;
  flex: 1;
  min-height: 0;
  /* Custom Scrollbar */
  scrollbar-width: thin;
  scrollbar-color: #bdc3c7 #ecf0f1;
}

.hiring-pipeline-board::-webkit-scrollbar {
  height: 8px;
}

.hiring-pipeline-board::-webkit-scrollbar-track {
  background: #ecf0f1;
  border-radius: 4px;
}

.hiring-pipeline-board::-webkit-scrollbar-thumb {
  background: #bdc3c7;
  border-radius: 4px;
}

.hiring-pipeline-board::-webkit-scrollbar-thumb:hover {
  background: #95a5a6;
}

/* Pipeline Stage Columns */
.pipeline-stage {
  flex-shrink: 0;
  width: 320px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 200px);
  border: 1px solid #ecf0f1;
  transition: all 0.3s ease;
}

.pipeline-stage:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}



/* Stage Header */
.stage-header {
  padding: 20px;
  border-bottom: 2px solid #ecf0f1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  flex-shrink: 0;
}

.stage-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.stage-info h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
}


.candidate-count {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.generate-test-btn {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.generate-test-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

/* Candidate Cards Container */
.candidate-cards {
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
  /* Custom Scrollbar for cards */
  scrollbar-width: thin;
  scrollbar-color: #bdc3c7 transparent;
}

.candidate-cards::-webkit-scrollbar {
  width: 6px;
}

.candidate-cards::-webkit-scrollbar-track {
  background: transparent;
}

.candidate-cards::-webkit-scrollbar-thumb {
  background: #bdc3c7;
  border-radius: 3px;
}

.candidate-card {
  background: #ffffff;
  border: 2px solid #ecf0f1;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
}

.candidate-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #3498db;
}

.candidate-card.has-interview {
  border-left: 4px solid #27ae60;
}


/* Candidate Header */
.candidate-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.candidate-avatar {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
  flex-shrink: 0;
}

.candidate-info {
  flex: 1;
  min-width: 0;
}


.candidate-info h4 {
  margin: 0 0 4px 0;
  color: #2c3e50;
  font-size: 1.1rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.candidate-info p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.85rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}


/* Candidate Metrics */

/* Candidate Metrics */
.candidate-metrics {
  margin-bottom: 12px;
  background: #f8f9fa;
  padding: 10px;
  border-radius: 8px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-size: 0.85rem;
}

.metric-item:last-child {
  margin-bottom: 0;
}

.metric-label {
  color: #7f8c8d;
  font-weight: 600;
}

.metric-value {
  color: #2c3e50;
  font-weight: 600;
}

.metric-value.score.score-excellent {
  color: #27ae60;
  background: #e8f5e9;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.metric-value.score.score-good {
  color: #2ecc71;
  background: #e8f5e9;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.metric-value.score.score-average {
  color: #f39c12;
  background: #fdf2e9;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.metric-value.score.score-poor {
  color: #e74c3c;
  background: #fdedec;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.metric-value.score.score-na {
  color: #95a5a6;
  font-style: italic;
}


/* Interview Section */

/* Offer Section */
.offer-section {
  margin-bottom: 12px;
  padding: 12px;
  background: #f0f8ff;
  border-radius: 8px;
  border-left: 3px solid #667eea;
}

.offer-status {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.offer-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #2d3748;
}

.offer-info i {
  color: #667eea;
  font-size: 1.1rem;
}

.acceptance-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
}

.acceptance-status.pending {
  background: #fff3cd;
  color: #856404;
}

.acceptance-status.accepted {
  background: #d4edda;
  color: #155724;
}

.acceptance-status.rejected {
  background: #f8d7da;
  color: #721c24;
}

.acceptance-status i {
  font-size: 1.1rem;
}

.offer-date {
  font-size: 0.85rem;
  color: #6c757d;
  font-style: italic;
}

.send-offer-section {
  display: flex;
  justify-content: center;
}

.send-offer-btn {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  padding: 10px 16px;
  transition: all 0.3s ease;
}

.send-offer-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-offer-btn i {
  margin-right: 6px;
}

/* Interview Section */
.interview-section {
  margin-bottom: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #3498db;
}

.interviewer-assigned {
  transition: all 0.3s ease;
  border-radius: 8px;
  padding: 12px;
  background: #f8f9fa;
}

.interviewer-assigned:hover {
  background: #e3f2fd;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.view-details-hint {
  margin-top: 8px;
  text-align: center;
  font-size: 0.75rem;
  color: #667eea;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.interviewer-assigned:hover .view-details-hint {
  opacity: 1;
}

.interviewer-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #2c3e50;
  font-size: 0.85rem;
  font-weight: 600;
}

.interview-type {
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.7rem;
  margin-left: auto;
}

.interview-status {
  padding: 4px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  text-align: center;
}

.interview-status.scheduled {
  background: #fff3e0;
  color: #f57c00;
}

.interview-status.completed {
  background: #e8f5e9;
  color: #388e3c;
}

.assign-interviewer-section {
  position: relative;
}

.assign-interviewer {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  width: 100%;
  justify-content: center;
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.assign-interviewer:hover {
  background: #2980b9;
}

.interviewer-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  z-index: 20;
  margin-top: 4px;
  max-height: 150px;
}

.dropdown-header {
  padding: 8px 12px;
  background: #f8f9fa;
  border-bottom: 1px solid #ecf0f1;
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.8rem;
}

.interviewer-list {
  max-height: 120px;
  overflow-y: auto;
}

.interviewer-option {
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.2s ease;
  border-bottom: 1px solid #f8f9fa;
  font-size: 0.85rem;
}

.interviewer-option:hover {
  background: #f8f9fa;
}

.interviewer-option:last-child {
  border-bottom: none;
}

.interviewer-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.interviewer-name {
  font-weight: 600;
  color: #2c3e50;
}

.interviewer-role {
  font-size: 0.75rem;
  color: #7f8c8d;
  font-style: italic;
}

/* Interview Results */

/* Interview Results */
.interview-results {
  margin-bottom: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #27ae60;
}

.scorecard-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.overall-score {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.85rem;
}

.recommendation {
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  text-align: center;
}

.recommendation.strong_hire {
  background: #c8e6c9;
  color: #2e7d32;
}

.recommendation.hire {
  background: #e8f5e9;
  color: #388e3c;
}

.recommendation.maybe {
  background: #fff3e0;
  color: #f57c00;
}

.recommendation.no_hire {
  background: #ffebee;
  color: #c62828;
}

/* Card Actions */

/* Card Actions */
.card-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-btn {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s ease;
  font-size: 0.8rem;
}

.view-scorecard {
  background: #e3f2fd;
  color: #1976d2;
}

.view-resume {
  background: #f3e5f5;
  color: #7b1fa2;
}

.pass-fail-actions,
.next-stage-actions,
.hire-actions {
  display: flex;
  gap: 6px;
}

.action-row {
  display: flex;
  gap: 8px;
  width: 100%;
  flex-direction: row;
}

.pass-btn {
  background: #4caf50;
  color: white;
  flex: 1;
}

.fail-btn {
  background: #f44336;
  color: white;
  flex: 1;
}

.next-stage-btn {
  background: #ff9800;
  color: white;
  width: 100%;
}

.hire-btn {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  color: white;
  width: 100%;
}

.reject-btn {
  background: #f44336;
  color: white;
  width: 100%;
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.processing-indicator {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: #3498db;
  font-weight: 600;
  z-index: 10;
}

/* Empty Stage */
.empty-stage {
  text-align: center;
  padding: 30px 15px;
  color: #7f8c8d;
}

.empty-stage i {
  font-size: 2.5rem;
  margin-bottom: 12px;
  display: block;
  opacity: 0.5;
}

.empty-stage p {
  margin: 0;
  font-size: 0.9rem;
}

/* Loading States */
.stage-loading-indicator {
  padding: 40px 20px;
  text-align: center;
  color: #7f8c8d;
}

.stage-loading-indicator i {
  font-size: 2rem;
  margin-bottom: 15px;
  display: block;
  color: #3498db;
}

/* Responsive */

/* Responsive Design */
@media (max-width: 1200px) {
  .pipeline-stage {
    width: 280px;
  }
}

@media (max-width: 768px) {
  .hiring-pipeline-board {
    padding: 15px;
    gap: 15px;
  }

  .pipeline-stage {
    width: 260px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
    padding: 15px 20px;
  }

  .header-actions {
    width: 100%;
    justify-content: space-between;
  }

  .job-filter {
    min-width: 150px;
  }

  .candidate-card {
    padding: 12px;
  }

  .candidate-header {
    gap: 10px;
  }

  .candidate-avatar {
    width: 40px;
    height: 40px;
    font-size: 0.9rem;
  }
}


@media (max-width: 480px) {
  .hiring-pipeline-board {
    padding: 10px;
  }

  .pipeline-stage {
    width: 240px;
  }

  .page-header {
    padding: 12px 15px;
  }

  .header-content h1 {
    font-size: 1.8rem;
  }
}

/* Additional Polish */
.pipeline-stage:first-child {
  margin-left: 0;
}

.pipeline-stage:last-child {
  margin-right: 20px;
}

/* Smooth animations for card interactions */
.candidate-card {
  animation: slideInUp 0.3s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Custom focus styles for accessibility */
.action-btn:focus,
.assign-interviewer:focus,
.job-filter:focus,
.btn-refresh:focus {
  outline: 2px solid #3498db;
  outline-offset: 2px;
}
</style>