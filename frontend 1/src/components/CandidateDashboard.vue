<template>
  <div>
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
                  <h4>{{ job.title || "Untitled Position" }}</h4>
                  <p>{{ job.company || "Unknown Company" }}</p>
                  <div class="job-meta">
                    <span><i class="fas fa-map-marker-alt"></i>
                      {{
                        job.location || job.requirements || "Location notspecified"
                      }}</span>
                    <span class="jobStatus" :style="{ backgroundColor: getStatusColor(job.status) }">
                      {{ job.status || "Unknown Status" }}
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
              <p>
                Upload your resume to get personalized job recommendations powered by AI
              </p>
              <button @click="navigate('candidate-profile')" class="upload-resume-btn">
                <i class="fas fa-upload"></i>
                Upload Resume
              </button>
            </div>

            <!-- View All Button (only show when there are jobs) -->
            <button v-if="recommendedJobs && recommendedJobs.length > 0" @click="navigate('job-recommend')"
              class="view-all-btn">
              View All Recommendations
            </button>
          </div>

          <!-- Profile Completeness -->
          <div class="dashboard-card technical-tests">
            <h3>
              <i class="fas fa-laptop-code"></i>
              Technical Tests
            </h3>

            <!-- Loading State -->
            <div v-if="testsLoading" class="loading-state">
              <i class="fas fa-spinner fa-spin"></i>
              <p>Loading tests...</p>
            </div>

            <!-- Tests List -->
            <div v-else-if="technicalTests && technicalTests.length > 0" class="tests-list">
              <div v-for="test in technicalTests" :key="test.id" class="test-item"
                :class="getTestStatusClass(test.status)">
                <div class="test-header">
                  <div class="test-info">
                    <h4>{{ test.job_title }}</h4>
                    <span class="test-type">
                      <i class="fas fa-magic"></i>
                      AI Technical Test
                    </span>
                  </div>
                  <div class="test-status-badge" :class="test.status">
                    {{ formatTestStatus(test.status) }}
                  </div>
                </div>

                <div class="test-details">
                  <div class="test-meta">
                    <span class="meta-item">
                      <i class="fas fa-clock"></i>
                      {{ test.duration_minutes }} mins
                    </span>
                    <span class="meta-item">
                      <i class="fas fa-calendar"></i>
                      Due: {{ formatDate(test.deadline) }}
                    </span>
                  </div>

                  <!-- Deadline Warning -->
                  <div v-if="isDeadlineNear(test.deadline) && test.status === 'scheduled'" class="deadline-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    Deadline approaching!
                  </div>
                </div>

                <!-- Action Buttons -->
                <div class="test-actions">
                  <button v-if="test.status === 'scheduled'" @click="attemptTest(test)" class="btn-attempt-test">
                    <i class="fas fa-play-circle"></i>
                    Attempt Test
                  </button>

                  <button v-else-if="test.status === 'submitted'" class="btn-test-submitted" disabled>
                    <i class="fas fa-check-circle"></i>
                    Submitted - Awaiting Results
                  </button>

                  <button v-else-if="test.status === 'evaluated'" @click="viewTestResults(test)"
                    class="btn-view-results">
                    <i class="fas fa-chart-bar"></i>
                    View Results
                  </button>
                </div>

                <!-- Test Results (if evaluated) -->
                <div v-if="test.assessment" class="test-results">
                  <div class="score-display">
                    <span class="score-label">Score:</span>
                    <span class="score-value" :class="getScoreClass(test.assessment.score_percentage)">
                      {{ test.assessment.score_percentage }}%
                    </span>
                  </div>
                  <div class="recommendation" :class="test.assessment.recommendation">
                    {{ formatRecommendation(test.assessment.recommendation) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="empty-state">
              <div class="empty-icon">
                <i class="fas fa-clipboard-list"></i>
              </div>
              <h4>No Technical Tests</h4>
              <p>You don't have any pending technical tests at the moment.</p>
            </div>
          </div>

          <!-- Upcoming Interviews -->
          <!-- Upcoming Interviews -->
<div class="dashboard-card upcoming-interviews">
  <h3><i class="fas fa-calendar-alt"></i> Upcoming Interviews</h3>
  
  <div v-if="upcomingInterviews.length" class="interview-list">
    <div v-for="interview in upcomingInterviews" :key="interview.id" class="interview-item">
      <div class="interview-time">
        <span class="time">{{ formatTime(interview.scheduledTime) }}</span>
        <span class="duration">{{ interview.duration }}min</span>
      </div>
      
      <div class="interview-info">
        <h4>{{ interview.jobTitle }}</h4>
        <p>{{ interview.company }}</p>
        <div class="interview-meta">
          <span class="interviewer">
            <i class="fas fa-user-tie"></i>
            {{ interview.interviewer || 'Interviewer TBA' }}
          </span>
          <span 
            class="interview-type-badge"
            :style="{ 
              backgroundColor: getInterviewTypeColor(interview.type),
              color: 'white'
            }"
          >
            {{ formatInterviewType(interview.type) }}
          </span>
        </div>
      </div>
      
      <div class="interview-actions">
        <button 
          class="btn-join" 
          @click="joinInterview(interview)"
          :disabled="!interview.meeting_link"
          :title="interview.meeting_link ? 'Join Meeting' : 'No meeting link available'"
        >
          <i class="fas fa-video"></i>
          Join
        </button>
      </div>
    </div>
  </div>
  
  <div v-else class="no-interviews">
    <i class="fas fa-calendar-times"></i>
    <p>No upcoming interviews</p>
  </div>
</div>

          <!-- Offer Letters -->
          <div class="dashboard-card offer-letters">
            <h3>
              <i class="fas fa-file-contract"></i>
              Offer Letters
            </h3>

            <!-- Loading State -->
            <div v-if="offersLoading" class="loading-state">
              <i class="fas fa-spinner fa-spin"></i>
              <p>Loading offers...</p>
            </div>

            <!-- Offers List -->
            <div v-else-if="myOffers && myOffers.length > 0" class="offers-list">
              <div v-for="offer in myOffers" :key="offer.id" class="offer-item"
                :class="`status-${offer.acceptance_status}`">
                <div class="offer-header">
                  <div class="offer-info">
                    <h4>{{ offer.job_title }}</h4>
                    <p class="offer-date">Sent {{ formatDate(offer.created_at) }}</p>
                  </div>
                  <div class="offer-status-badge" :class="offer.acceptance_status">
                    <i :class="{
                      'fas fa-clock': offer.acceptance_status === 'pending',
                      'fas fa-check-circle': offer.acceptance_status === 'accepted',
                      'fas fa-times-circle': offer.acceptance_status === 'rejected'
                    }"></i>
                    {{ formatOfferStatus(offer.acceptance_status) }}
                  </div>
                </div>

                <!-- View Offer Letter Button -->
                <div class="offer-view-section">
                  <button @click="viewOfferLetter(offer)" class="btn-view-offer">
                    <i class="fas fa-file-pdf"></i>
                    View Offer Letter
                  </button>
                </div>

                <!-- Offer Actions -->
                <div v-if="offer.acceptance_status === 'pending'" class="offer-actions">
                  <button @click="acceptOffer(offer)" class="btn-accept-offer"
                    :disabled="processingOffer === offer.id">
                    <i class="fas fa-check"></i>
                    Accept Offer
                  </button>
                  <button @click="rejectOffer(offer)" class="btn-reject-offer"
                    :disabled="processingOffer === offer.id">
                    <i class="fas fa-times"></i>
                    Decline
                  </button>
                </div>

                <!-- Accepted/Rejected State -->
                <div v-else class="offer-result">
                  <p v-if="offer.acceptance_status === 'accepted'" class="accepted-text">
                    <i class="fas fa-check-circle"></i>
                    You accepted this offer on {{ formatDate(offer.accepted_at) }}
                  </p>
                  <p v-else class="rejected-text">
                    <i class="fas fa-times-circle"></i>
                    You declined this offer on {{ formatDate(offer.accepted_at) }}
                  </p>
                </div>

                <!-- Processing Indicator -->
                <div v-if="processingOffer === offer.id" class="processing-indicator">
                  <i class="fas fa-spinner fa-spin"></i>
                  Processing...
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="empty-state">
              <i class="fas fa-inbox"></i>
              <p>No offer letters yet</p>
            </div>
          </div>

          <!-- AI Insights -->
          <div class="dashboard-card ai-insights">
            <h3><i class="fas fa-lightbulb"></i> AI Insights</h3>
            <div class="insight-list">\n              <div v-for="insight in aiInsights" :key="insight.id" class="insight-item">
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
      <div class="dashboard-card task-board">\n        <h3>
          <i class="fas fa-tasks"></i>
          Today's Tasks
        </h3>

        <!-- Loading State -->
        <div v-if="tasksLoading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading tasks...</p>
        </div>

        <!-- Tasks List -->
        <div v-else-if="todayTasks && todayTasks.length > 0" class="tasks-list">
          <div v-for="task in todayTasks" :key="task.id" class="task-card" :class="getTaskPriorityClass(task.priority)">
            <!-- Task Header -->
            <div class="task-header">
              <div class="task-title-section">
                <h4>{{ task.title }}</h4>
                <span class="priority-badge" :class="task.priority">
                  <i class="fas fa-flag"></i>
                  {{ formatPriority(task.priority) }}
                </span>
              </div>
              <div class="task-status-badge" :class="task.status">
                {{ formatTaskStatus(task.status) }}
              </div>
            </div>

            <!-- Task Description -->
            <div class="task-description">
              <p>{{ task.description }}</p>
            </div>

            <!-- Task Meta -->
            <div class="task-meta">
              <div class="meta-item">
                <i class="fas fa-user-tie"></i>
                <span>Assigned by: {{ task.assigned_by_name }}</span>
              </div>
              <div class="meta-item" :class="{ 'deadline-warning': isDeadlineNear(task.deadline) }">
                <i class="fas fa-clock"></i>
                <span>Deadline: {{ formatDateTime(task.deadline) }}</span>
              </div>
            </div>

            <!-- Reviews Section -->
            <div v-if="task.employee_review || task.manager_review" class="reviews-section">
              <!-- Employee Review -->
              <div v-if="task.employee_review" class="review-item employee-review">
                <div class="review-header">
                  <i class="fas fa-user"></i>
                  <strong>Your Review</strong>
                  <small>{{ formatDate(task.employee_reviewed_at) }}</small>
                </div>
                <div class="review-text">{{ task.employee_review }}</div>
              </div>

              <!-- Manager Review -->
              <div v-if="task.manager_review" class="review-item manager-review">
                <div class="review-header">
                  <i class="fas fa-user-tie"></i>
                  <strong>Manager's Feedback</strong>
                  <small>{{ formatDate(task.manager_reviewed_at) }}</small>
                </div>
                <div class="review-text">{{ task.manager_review }}</div>
              </div>

              <!-- AI Summary -->
              <div v-if="task.ai_summary" class="review-item ai-summary">
                <div class="review-header">
                  <i class="fas fa-robot"></i>
                  <strong>AI Performance Summary</strong>
                  <small>{{ formatDate(task.ai_summary_generated_at) }}</small>
                </div>
                <div class="review-text ai-text">
                  {{ formatAISummary(task.ai_summary) }}
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="task-actions">
              <!-- Submit Self Review -->
              <button v-if="!task.employee_review && task.status !== 'pending'" @click="openReviewModal(task)"
                class="btn-submit-review">
                <i class="fas fa-pencil-alt"></i>
                Submit Your Review
              </button>

              <!-- Generate AI Summary -->
              <button v-if="task.employee_review && task.manager_review && !task.ai_summary"
                @click="generateAISummary(task)" class="btn-generate-summary" :disabled="generatingSummary">
                <i class="fas fa-magic"></i>
                {{ generatingSummary ? 'Generating...' : 'Generate AI Summary' }}
              </button>

              <!-- Mark as In Progress -->
              <button v-if="task.status === 'pending'" @click="updateTaskStatus(task, 'in_progress')"
                class="btn-start-task">
                <i class="fas fa-play"></i>
                Start Task
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-clipboard-check"></i>
          </div>
          <h4>No Tasks for Today</h4>
          <p>You're all caught up! Check back later for new assignments.</p>
        </div>
      </div>

      <!-- Review Modal -->
      <div v-if="showReviewModal" class="modal-overlay" @click="closeReviewModal">
        <div class="modal-container review-modal" @click.stop>
          <div class="modal-header">
            <h3>
              <i class="fas fa-pencil-alt"></i>
              Submit Task Review
            </h3>
            <button @click="closeReviewModal" class="close-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <div class="task-info-box">
              <h4>{{ selectedTask?.title }}</h4>
              <p>{{ selectedTask?.description }}</p>
            </div>

            <div class="form-group">
              <label for="task-review">
                <i class="fas fa-comment-dots"></i>
                Describe what you accomplished and any challenges faced:
              </label>
              <textarea id="task-review" v-model="employeeReview" placeholder="Write your review here..." rows="8"
                class="review-textarea"></textarea>
              <div class="character-count">
                {{ employeeReview.length }} characters
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="closeReviewModal" class="btn-cancel">
              Cancel
            </button>
            <button @click="submitEmployeeReview" class="btn-submit"
              :disabled="!employeeReview.trim() || submittingReview">
              <i class="fas fa-paper-plane"></i>
              {{ submittingReview ? 'Submitting...' : 'Submit Review' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Chatbot Widget -->\n      <div class="chatbot-widget">
        <!-- Chat Toggle Button -->
        <button 
          v-if="!showChatbot" 
          @click="toggleChatbot" 
          class="chatbot-toggle"
          title="Chat with HR Assistant"
        >
          <i class="fas fa-comments"></i>
          <span class="chat-badge" v-if="unreadMessages > 0">{{ unreadMessages }}</span>
        </button>

        <!-- Chatbot Window -->
        <div v-if="showChatbot" class="chatbot-window">
          <!-- Header -->
          <div class="chatbot-header">
            <div class="chatbot-header-info">
              <i class="fas fa-robot"></i>
              <div>
                <h4>HR Support Assistant</h4>
                <span class="chatbot-status">Online</span>
              </div>
            </div>
            <button @click="toggleChatbot" class="chatbot-close">
              <i class="fas fa-times"></i>
            </button>
          </div>

          <!-- Messages -->
          <div class="chatbot-messages" ref="chatMessagesContainer">
            <div v-if="chatMessages.length === 0" class="chatbot-welcome">
              <i class="fas fa-hand-wave"></i>
              <h4>Welcome to HR Support!</h4>
              <p>Ask me anything about company policies, leave requests, benefits, or general HR questions.</p>
              <div class="quick-questions">
                <button 
                  v-for="(question, index) in quickQuestions" 
                  :key="index"
                  @click="sendQuickQuestion(question)"
                  class="quick-question-btn"
                >
                  {{ question }}
                </button>
              </div>
            </div>

            <div 
              v-for="(message, index) in chatMessages" 
              :key="index" 
              class="chat-message"
              :class="message.sender"
            >
              <div class="message-avatar">
                <i :class="message.sender === 'user' ? 'fas fa-user' : 'fas fa-robot'"></i>
              </div>
              <div class="message-content">
                <div class="message-text">{{ message.text }}</div>
                <div class="message-time">{{ formatMessageTime(message.timestamp) }}</div>
              </div>
            </div>

            <div v-if="chatLoading" class="chat-message bot">
              <div class="message-avatar">
                <i class="fas fa-robot"></i>
              </div>
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>

          <!-- Input -->
          <div class="chatbot-input">
            <textarea
              v-model="chatInput"
              @keydown.enter.prevent="sendMessage"
              placeholder="Type your question here..."
              rows="1"
              class="chat-textarea"
            ></textarea>
            <button 
              @click="sendMessage" 
              :disabled="!chatInput.trim() || chatLoading"
              class="chat-send-btn"
            >
              <i class="fas fa-paper-plane"></i>
            </button>
          </div>
        </div>
      </div>
    </DashboardLayout>
    <JobApplicationModal v-if="showApplyModal" :job="selectedJob" :userId="user_id" @close="closeApplyModal"
      @application-submitted="handleApplicationSubmitted" />
  </div>
</template>

<script setup>
import { ref, onMounted, TrackOpTypes } from "vue";
import { computed } from "vue";
import { useRouter } from "vue-router";
import DashboardLayout from "./DashboardLayout.vue";
import axios from "axios";
import JobApplicationModal from "./JobApplicationModal.vue";


const technicalTests = ref([]);
const testsLoading = ref(false);


const showApplyModal = ref(false);
const selectedJob = ref(null);



const todayTasks = ref([])
const tasksLoading = ref(false)
const showReviewModal = ref(false)
const selectedTask = ref(null)
const employeeReview = ref('')
const submittingReview = ref(false)
const generatingSummary = ref(false)

// Chatbot state
const showChatbot = ref(false)
const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)
const unreadMessages = ref(0)
const chatMessagesContainer = ref(null)

// Offer Letters state
const myOffers = ref([])
const offersLoading = ref(false)
const processingOffer = ref(null)

const quickQuestions = ref([
  'How do I apply for leave?',
  'What are the company benefits?',
  'How do I update my profile?',
  'What is the interview process?'
])


// Add function to open modal
function applyToJob(job) {
  selectedJob.value = job;
  showApplyModal.value = true;
}

function closeApplyModal() {
  showApplyModal.value = false;
  selectedJob.value = null;
}

function handleApplicationSubmitted(applicationData) {
  // Refresh applications list
  loadApplications();

  // Close modal
  closeApplyModal();

  // Show success message
  alert(`Successfully applied to ${applicationData.job_title}!`);
}

const router = useRouter();

// State
const userName = ref(null); // Get from auth
const user_id = ref("");
const jobsLoading = ref(false);

const recentApplications = ref([]);
const recommendedJobs = ref([]);
const profileCompletion = ref(75);
const completionItems = ref([
  { name: "Resume Uploaded", completed: false },
  { name: "Skills Added", completed: false },
  { name: "Experience Details", completed: true },
  { name: "Portfolio Links", completed: false },
  { name: "Preferences Set", completed: false },
]);

const upcomingInterviews = ref([]);

const aiInsights = ref([
  {
    id: 1,
    type: "tip",
    icon: "fas fa-lightbulb",
    title: "Improve Your Resume",
    description:
      "Add more quantified achievements to increase your profile strength by 23%",
  },
  {
    id: 2,
    type: "warning",
    icon: "fas fa-exclamation-triangle",
    title: "Skills Gap Detected",
    description:
      "Consider learning TypeScript - it appears in 68% of your target job postings",
  },
]);

const applicationCount = computed(() => {
  return recentApplications.value?.length;
});

const interviewCount = computed(() => {
  return upcomingInterviews.value?.length || 0;
});

const profileView = computed(() => {
  return 45;
});

// Functions
function navigate(page) {
  const pageMap = {
    "candidate-profile": "/candidate/candidate-profile",
    "job-search": "/candidate/job-search",
    "ai-enhancement": "/candidate/ai-enhancement",
    applications: "/candidate/applications",
    "job-recommend": "/candidate/job-recommend",
  };

  if (pageMap[page]) {
    router.push(pageMap[page]);
  }
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

function attemptTest(test) {
  // Navigate to test taking interface
  router.push({
    path: '/candidate/take-test',
    query: { test_id: test.id }
  });
}

function viewTestResults(test) {
  // Navigate to test results page
  router.push({
    path: '/candidate/test-results',
    query: { test_id: test.id }
  });
}

function formatTestStatus(status) {
  const statusMap = {
    'scheduled': 'Pending',
    'in_progress': 'In Progress',
    'submitted': 'Submitted',
    'evaluated': 'Completed'
  };
  return statusMap[status] || status;
}

function getTestStatusClass(status) {
  return `status-${status.toLowerCase().replace('_', '-')}`;
}

function isDeadlineNear(deadline) {
  const now = new Date();
  const deadlineDate = new Date(deadline);
  const hoursUntilDeadline = (deadlineDate - now) / (1000 * 60 * 60);
  return hoursUntilDeadline <= 24 && hoursUntilDeadline > 0;
}

function getScoreClass(score) {
  if (score >= 80) return 'excellent';
  if (score >= 60) return 'good';
  if (score >= 40) return 'average';
  return 'poor';
}

function formatRecommendation(recommendation) {
  const recMap = {
    'pass': 'Passed',
    'fail': 'Not Passed',
    'borderline': 'Under Review'
  };
  return recMap[recommendation] || recommendation;
}


// Add these helper functions after your existing functions

function formatTime(dateString) {
  if (!dateString) return 'N/A'
  
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

function formatInterviewType(type) {
  const typeMap = {
    'technical_interview': 'Technical Interview',
    'behavioral_interview': 'Behavioral Interview',
    'communication_interview': 'Communication Interview',
    'final_interview': 'General Interview',
        'general': 'General Interview'
  }
  return typeMap[type] || type
}

function getInterviewTypeColor(type) {
  const colorMap = {
    'technical_interview': '#9b59b6',
    'behavioral_interview': '#e67e22',
    'communication_interview': '#27ae60',
    'final_interview': '#f39c12',
    'general': '#f39c12'
  }
  return colorMap[type] || '#95a5a6'
}

function joinInterview(interview) {
  if (interview?.meeting_link) {
    // Open meeting link in new tab
    window.open(interview.meeting_link, '_blank')
  } else {
    alert('No meeting link available for this interview. Please contact HR.')
  }
}

async function loadUpcomingInterviews() {
  try {
    const response = await axios.get(
      `/api/screening/candidates/${user_id.value}/interviews`,
      {
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
        params: { upcoming_only: "true", limit: 5 },
      }
    );
    console.log("Upcoming Interviews API Response:", response.data);
    if (response.data.success && response.data) {
      upcomingInterviews.value = response.data.interviews.map((interview) => ({
        id: interview.id,
        jobTitle: interview.job_details?.title || "Interview",
        company: interview.job_details?.company || "Company",
        scheduledTime: interview.scheduled_at,
        type: interview.interview_type || "Interview",
        interviewer: interview.interviewer_details?.name,
        meeting_link: interview.meeting_link,
        duration: interview.duration_minutes,
        status: interview.status,
      }));
    }
  } catch (error) {
    console.log("Failed to load upcoming interviews:", error);
  }
}
async function jobRecommendationService() {
  try {
    jobsLoading.value = true; // Start loading

    // 1. Get user's resume files
    const UserResumeInfo = await axios.get(`/api/files/resume`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
    });

    console.log("Resume files response:", UserResumeInfo.data);

    // 2. Check if user has any resume files
    if (!UserResumeInfo.data || UserResumeInfo.data.length === 0) {
      console.log("No resume found for user");
      recommendedJobs.value = [];
      return;
    }

    // 3. Get the first resume's ID
    const UserResumeId = UserResumeInfo.data.id;
    console.log("Using resume ID:", UserResumeId);

    // 4. Get job recommendations based on resume
    const topJobsResponse = await axios.get(`/api/get_job_posts/${UserResumeId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
    });

    console.log("Job recommendations response:", topJobsResponse.data.job_post.meta_data);

    // 5. Extract job data correctly
    if (topJobsResponse.data && topJobsResponse.data.job_post) {
      recommendedJobs.value = topJobsResponse.data.job_post.meta_data || [];
    } else {
      console.log("No job recommendations found");
      recommendedJobs.value = [];
    }
  } catch (error) {
    console.error("Error in jobRecommendationService:", error);

    if (error.response) {
      console.error("API Error:", error.response.status, error.response.data);

      if (error.response.status === 404) {
        console.log("Resume not found or no job posts available");
        // Try loading regular jobs as fallback
        await loadJobs();
      }
    }

    recommendedJobs.value = [];
  } finally {
    jobsLoading.value = false; // Stop loading
  }
}
async function loadRecentApplications() {
  try {
    console.log("🔄 Loading applications...");

    const response = await axios.get(`/api/applications/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
    });

    console.log("📋 Applications API Response:", response.data);

    recentApplications.value = response.data.applications;

    // Verify the structure
    console.log("✅ Applications stored:", recentApplications.value);
    console.log("✅ Total count:", recentApplications.value.length);
  } catch (error) {
    console.error("❌ Failed to load recent applications:", error);
    // Set default structure on error
    recentApplications.value = { applications: [] };
  }
}

async function loadTechnicalTests() {
  try {
    testsLoading.value = true;

    const response = await axios.get('/api/ai/candidate-tests', {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
    });

    console.log('Technical tests loaded:', response.data);

    if (response.data && response.data.tests) {
      technicalTests.value = response.data.tests.map(test => ({
        id: test.id,
        job_id: test.job_id,
        job_title: test.job_title,
        test_type: test.test_type,
        duration_minutes: test.duration_minutes,
        deadline: test.deadline,
        status: test.status,
        questions: test.questions,
        submitted_at: test.submitted_at,
        assessment: test.assessment || null
      }));
    }
  } catch (error) {
    console.error('Failed to load technical tests:', error);
    technicalTests.value = [];
  } finally {
    testsLoading.value = false;
  }
}


function getStatusColor(status) {
  const statusMap = {
    active: "#27ae60",
    inactive: "#e74c3c",
    closed: "#95a5a6",
    pending: "#f39c12",
  };
  return statusMap[status?.toLowerCase()] || "#7f8c8d";
}

async function loadJobs() {
  try {
    const response = await axios.get(`/api/jobs/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
    });
    if (!recommendedJobs.value) {
      recommendedJobs.value = response.data;
      console.log("job are loaded", recommendedJobs.value);
    }
  } catch (error) {
    console.error("Failed to load jobs:", error);
  }
}



// Task Board Functions
async function loadTodayTasks() {
  try {
    tasksLoading.value = true

    const response = await axios.get('/api/tasks/today', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })

    if (response.data && response.data.tasks) {
      todayTasks.value = response.data.tasks
    }

    console.log('✅ Today tasks loaded:', todayTasks.value.length)
  } catch (error) {
    console.error('❌ Failed to load today tasks:', error)
    todayTasks.value = []
  } finally {
    tasksLoading.value = false
  }
}

function getTaskPriorityClass(priority) {
  return `priority-${priority}`
}

function formatPriority(priority) {
  const priorityMap = {
    'low': 'Low',
    'medium': 'Medium',
    'high': 'High'
  }
  return priorityMap[priority] || priority
}

function formatTaskStatus(status) {
  const statusMap = {
    'pending': 'Pending',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'reviewed': 'Reviewed'
  }
  return statusMap[status] || status
}

function openReviewModal(task) {
  selectedTask.value = task
  employeeReview.value = ''
  showReviewModal.value = true
}

function closeReviewModal() {
  showReviewModal.value = false
  selectedTask.value = null
  employeeReview.value = ''
}

async function submitEmployeeReview() {
  try {
    submittingReview.value = true

    await axios.post(
      `/api/tasks/${selectedTask.value.id}/employee-review`,
      {
        review: employeeReview.value
      },
      {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }
    )

    alert('Review submitted successfully!')
    closeReviewModal()
    await loadTodayTasks()
  } catch (error) {
    console.error('Failed to submit review:', error)
    alert('Failed to submit review. Please try again.')
  } finally {
    submittingReview.value = false
  }
}

async function generateAISummary(task) {
  try {
    generatingSummary.value = true

    const response = await axios.post(
      `/api/tasks/${task.id}/generate-ai-summary`,
      {},
      {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }
    )

    alert('AI summary generated successfully!')
    await loadTodayTasks()
  } catch (error) {
    console.error('Failed to generate AI summary:', error)
    alert('Failed to generate AI summary. Please try again.')
  } finally {
    generatingSummary.value = false
  }
}

async function updateTaskStatus(task, newStatus) {
  try {
    await axios.put(
      `/api/tasks/${task.id}`,
      { status: newStatus },
      {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }
    )

    await loadTodayTasks()
  } catch (error) {
    console.error('Failed to update task status:', error)
    alert('Failed to update task status.')
  }
}

function formatAISummary(summary) {
  try {
    const parsed = JSON.parse(summary)
    // Format the AI summary nicely
    return typeof parsed === 'string' ? parsed : JSON.stringify(parsed, null, 2)
  } catch {
    return summary
  }
}

// Chatbot Functions
function toggleChatbot() {
  showChatbot.value = !showChatbot.value
  if (showChatbot.value) {
    unreadMessages.value = 0
    // Scroll to bottom when opening
    setTimeout(scrollToBottom, 100)
  }
}

function scrollToBottom() {
  if (chatMessagesContainer.value) {
    chatMessagesContainer.value.scrollTop = chatMessagesContainer.value.scrollHeight
  }
}

function formatMessageTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function sendQuickQuestion(question) {
  chatInput.value = question
  sendMessage()
}

async function sendMessage() {
  if (!chatInput.value.trim() || chatLoading.value) return

  const userMessage = {
    sender: 'user',
    text: chatInput.value,
    timestamp: new Date()
  }

  chatMessages.value.push(userMessage)
  const question = chatInput.value
  chatInput.value = ''

  // Scroll to bottom
  setTimeout(scrollToBottom, 100)

  try {
    chatLoading.value = true

    // Use a default school_id or get it from user context
    const schoolId = 1

    const response = await axios.post(
      `/api/ai/chatbot/${schoolId}`,
      { question },
      {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      }
    )

    if (response.data.success) {
      const botMessage = {
        sender: 'bot',
        text: response.data.answer,
        timestamp: new Date()
      }

      chatMessages.value.push(botMessage)

      // If chatbot is closed, increment unread count
      if (!showChatbot.value) {
        unreadMessages.value++
      }
    } else {
      throw new Error(response.data.error || 'Failed to get response')
    }
  } catch (error) {
    console.error('Chatbot error:', error)

    const errorMessage = {
      sender: 'bot',
      text: 'Sorry, I encountered an error. Please try again or contact HR directly.',
      timestamp: new Date()
    }

    chatMessages.value.push(errorMessage)
  } finally {
    chatLoading.value = false
    setTimeout(scrollToBottom, 100)
  }
}

// Offer Letter Functions
async function loadMyOffers() {
  try {
    offersLoading.value = true
    const token = localStorage.getItem('access_token')

    const response = await axios.get('/api/pipeline/my-offers', {
      headers: { Authorization: `Bearer ${token}` }
    })

    myOffers.value = response.data.offers || []
    console.log('Offers loaded:',myOffers.value)
  } catch (error) {
    console.error('Error loading offers:', error)
    myOffers.value = []
  } finally {
    offersLoading.value = false
  }
}

function formatOfferStatus(status) {
  const statusMap = {
    'pending': 'Pending',
    'accepted': 'Accepted',
    'rejected': 'Declined'
  }
  return statusMap[status] || status
}

async function acceptOffer(offer) {
  if (!confirm(`Are you sure you want to accept the offer for ${offer.job_title}?`)) {
    return
  }

  try {
    processingOffer.value = offer.id
    const token = localStorage.getItem('access_token')

    await axios.put(
      `/api/pipeline/accept-offer/${offer.id}`,
      { acceptance: 'accepted' },
      { headers: { Authorization: `Bearer ${token}` } }
    )

    alert('Congratulations! You have accepted the offer.')
    await loadMyOffers()
  } catch (error) {
    console.error('Error accepting offer:', error)
    alert(error.response?.data?.error || 'Failed to accept offer. Please try again.')
  } finally {
    processingOffer.value = null
  }
}

async function rejectOffer(offer) {
  if (!confirm(`Are you sure you want to decline the offer for ${offer.job_title}?`)) {
    return
  }

  try {
    processingOffer.value = offer.id
    const token = localStorage.getItem('access_token')

    await axios.put(
      `/api/pipeline/accept-offer/${offer.id}`,
      { acceptance: 'rejected' },
      { headers: { Authorization: `Bearer ${token}` } }
    )

    alert('You have declined the offer.')
    await loadMyOffers()
  } catch (error) {
    console.error('Error declining offer:', error)
    alert(error.response?.data?.error || 'Failed to decline offer. Please try again.')
  } finally {
    processingOffer.value = null
  }
}

async function viewOfferLetter(offer) {
  try {
    const token = localStorage.getItem('access_token')
    
    // Download the offer letter file
    const response = await axios.get(
      `/api/files/preview-offer-letter`,
      {
        params: { file_path: offer.file_path },
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      }
    )

    // Create a blob URL and open in new tab
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
    const url = window.URL.createObjectURL(blob)
    window.open(url, '_blank')
    
    // Clean up
    setTimeout(() => window.URL.revokeObjectURL(url), 100)
  } catch (error) {
    console.error('Error viewing offer letter:', error)
    alert('Failed to open offer letter. Please try again.')
  }
}

async function loadDashboardData() {
  // Load user stats, applications, recommendations, etc.
  // This would typically come from API calls
  try {
    const userData = await axios.get(`/api/users/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
    });

    userName.value = userData.data.name;
    user_id.value = userData.data.id;
    console.log(user_id?.value);
  } catch (error) {
    console.error("Failed to load user data:", error);
  }
}

onMounted(async () => {
  try {
    console.log("🚀 Starting dashboard data load...");

    // Load user data first
    await loadDashboardData();
    console.log("✅ User data loaded");

    // Load applications BEFORE everything else
    await loadRecentApplications();
    console.log("✅ Applications loaded, count:", applicationCount.value);

    // Load recommended jobs
    await jobRecommendationService();
    console.log("✅ Job recommendations processed");

    await loadUpcomingInterviews();
    console.log("✅ Upcoming Interviews loaded");

    await loadTechnicalTests();
    console.log("✅ Technical tests loaded");

    await loadTodayTasks();
    console.log("✅ Today tasks loaded");

    await loadMyOffers();
    console.log("✅ Offer letters loaded");

    // Load regular jobs as fallback
    if (
      (!recommendedJobs.value || recommendedJobs.value.length === 0) &&
      !jobsLoading.value
    ) {
      await loadJobs();
      console.log("✅ Fallback jobs loaded");
    }

    console.log("🎉 Dashboard data load complete");
  } catch (error) {
    console.error("❌ Failed to load dashboard data:", error);
  }
});

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

.interview-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
  border: 1px solid #ecf0f1;
}
.application-item,
.job-item{
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

.jobStatus {
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
  background: conic-gradient(#3498db 0deg,
      #3498db calc(var(--progress) * 3.6deg),
      #ecf0f1 calc(var(--progress) * 3.6deg));
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.circle::before {
  content: "";
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

/* technical test */

.dashboard-card.technical-tests {
  border-left: 4px solid #9b59b6;
}

.tests-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 15px;
}

.test-item {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.test-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.test-item.status-scheduled {
  border-left-color: #f39c12;
  background: #fff9f0;
}

.test-item.status-submitted {
  border-left-color: #3498db;
  background: #f0f8ff;
}

.test-item.status-evaluated {
  border-left-color: #27ae60;
  background: #f0fff4;
}

.test-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.test-info h4 {
  margin: 0 0 6px 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.test-type {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.test-status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.test-status-badge.scheduled {
  background: #fff3cd;
  color: #856404;
}

.test-status-badge.submitted {
  background: #d1ecf1;
  color: #0c5460;
}

.test-status-badge.evaluated {
  background: #d4edda;
  color: #155724;
}

.test-details {
  margin-bottom: 12px;
}

.test-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #7f8c8d;
  font-size: 0.85rem;
}

.meta-item i {
  color: #9b59b6;
}

.deadline-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff3cd;
  color: #856404;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}

.deadline-warning i {
  color: #f39c12;
}

.test-actions {
  display: flex;
  gap: 8px;
}

.btn-attempt-test,
.btn-test-submitted,
.btn-view-results {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.btn-attempt-test {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-attempt-test:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-test-submitted {
  background: #d1ecf1;
  color: #0c5460;
  cursor: not-allowed;
}

.btn-view-results {
  background: #27ae60;
  color: white;
}

.btn-view-results:hover {
  background: #229954;
  transform: translateY(-2px);
}

.test-results {
  margin-top: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-label {
  color: #7f8c8d;
  font-weight: 600;
  font-size: 0.9rem;
}

.score-value {
  font-size: 1.3rem;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 8px;
}

.score-value.excellent {
  background: #d4edda;
  color: #155724;
}

.score-value.good {
  background: #d1ecf1;
  color: #0c5460;
}

.score-value.average {
  background: #fff3cd;
  color: #856404;
}

.score-value.poor {
  background: #f8d7da;
  color: #721c24;
}

.recommendation {
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.recommendation.pass {
  background: #d4edda;
  color: #155724;
}

.recommendation.fail {
  background: #f8d7da;
  color: #721c24;
}

.recommendation.borderline {
  background: #fff3cd;
  color: #856404;
}

/* Upcoming Interviews */
.interview-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 15px;
}

.interview-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
  border: 1px solid #ecf0f1;
}

.interview-item:hover {
  background: #e3f2fd;
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #3498db;
}

.interview-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
  padding: 10px;
  background: white;
  border-radius: 8px;
  border-left: 3px solid #3498db;
}

.interview-time .time {
  font-weight: 700;
  color: #2c3e50;
  font-size: 1rem;
  margin-bottom: 4px;
}

.interview-time .duration {
  font-size: 0.75rem;
  color: #7f8c8d;
  background: #ecf0f1;
  padding: 2px 8px;
  border-radius: 10px;
}

.interview-info {
  flex: 1;
  min-width: 0;
}

.interview-info h4 {
  margin: 0 0 4px 0;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
}

.interview-info p {
  margin: 0 0 8px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.interview-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.interviewer {
  font-size: 0.8rem;
  color: #7f8c8d;
  display: flex;
  align-items: center;
  gap: 4px;
}

.interviewer i {
  color: #3498db;
}

.interview-type-badge {
  font-size: 0.7rem;
  padding: 3px 8px;
  border-radius: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.interview-actions {
  display: flex;
  gap: 8px;
}

.btn-join {
  background: #27ae60;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.btn-join:hover:not(:disabled) {
  background: #229954;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.btn-join:disabled {
  background: #95a5a6;
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-join:disabled:hover {
  transform: none;
  box-shadow: none;
}

.no-interviews {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.no-interviews i {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
  color: #bdc3c7;
}

.no-interviews p {
  margin: 0;
  font-size: 1.1rem;
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

/* Upload Resume Button */
.upload-resume-btn {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  margin-top: 15px;
}

.upload-resume-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.upload-resume-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.2);
}

.upload-resume-btn i {
  font-size: 1.1rem;
}


/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.empty-state .empty-icon {
  font-size: 3rem;
  margin-bottom: 15px;
  opacity: 0.5;
  color: #9b59b6;
}

.empty-state h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.empty-state p {
  margin: 0;
  font-size: 0.9rem;
}

/* Task Board */
.dashboard-card.task-board {
  border-left: 4px solid #e74c3c;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.task-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  border-left: 4px solid transparent;
  transition: all 0.3s ease;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.task-card.priority-high {
  border-left-color: #e74c3c;
  background: #fff5f5;
}

.task-card.priority-medium {
  border-left-color: #f39c12;
  background: #fffbf0;
}

.task-card.priority-low {
  border-left-color: #3498db;
  background: #f0f8ff;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.task-title-section {
  flex: 1;
}

.task-title-section h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.priority-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.priority-badge.high {
  background: #fee;
  color: #e74c3c;
}

.priority-badge.medium {
  background: #fff3cd;
  color: #f39c12;
}

.priority-badge.low {
  background: #d1ecf1;
  color: #3498db;
}

.task-status-badge {
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

.task-status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.task-status-badge.in_progress {
  background: #d1ecf1;
  color: #0c5460;
}

.task-status-badge.completed {
  background: #d4edda;
  color: #155724;
}

.task-status-badge.reviewed {
  background: #e7e7ff;
  color: #4a4aff;
}

.task-description {
  margin-bottom: 15px;
}

.task-description p {
  margin: 0;
  color: #555;
  line-height: 1.6;
}

.task-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.meta-item i {
  color: #95a5a6;
}

.meta-item.deadline-warning {
  color: #e74c3c;
  font-weight: 600;
}

.meta-item.deadline-warning i {
  color: #e74c3c;
}

/* Reviews Section */
.reviews-section {
  margin: 20px 0;
  padding: 15px;
  background: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.review-item {
  padding: 12px;
  border-radius: 8px;
  border-left: 3px solid;
}

.review-item.employee-review {
  background: #e3f2fd;
  border-left-color: #2196f3;
}

.review-item.manager-review {
  background: #fff3e0;
  border-left-color: #ff9800;
}

.review-item.ai-summary {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-left-color: #667eea;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.review-header i {
  font-size: 1.1rem;
}

.review-header strong {
  flex: 1;
  color: #2c3e50;
}

.review-header small {
  color: #7f8c8d;
  font-size: 0.85rem;
}

.review-text {
  color: #2c3e50;
  line-height: 1.6;
  white-space: pre-wrap;
}

.review-text.ai-text {
  font-style: italic;
}

/* Task Actions */
.task-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-submit-review,
.btn-generate-summary,
.btn-start-task {
  padding: 10px 18px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.btn-submit-review {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-submit-review:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-generate-summary {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.btn-generate-summary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(240, 147, 251, 0.4);
}

.btn-generate-summary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-start-task {
  background: #27ae60;
  color: white;
}

.btn-start-task:hover {
  background: #229954;
  transform: translateY(-2px);
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

.modal-container {
  background: white;
  border-radius: 12px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.modal-container.review-modal {
  max-width: 600px;
  width: 100%;
}

.modal-header {
  padding: 24px 28px;
  border-bottom: 2px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 12px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #7f8c8d;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #ecf0f1;
  color: #2c3e50;
}

.modal-body {
  padding: 28px;
  overflow-y: auto;
}

.task-info-box {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #667eea;
}

.task-info-box h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.task-info-box p {
  margin: 0;
  color: #7f8c8d;
  line-height: 1.5;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2c3e50;
  font-weight: 600;
  margin-bottom: 10px;
}

.review-textarea {
  width: 100%;
  padding: 15px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.review-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.character-count {
  text-align: right;
  color: #7f8c8d;
  font-size: 0.85rem;
  margin-top: 6px;
}

.modal-footer {
  padding: 20px 28px;
  border-top: 2px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel,
.btn-submit {
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

.btn-cancel:hover {
  background: #bdc3c7;
}

.btn-submit {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Responsive Media Queries */
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
  .job-item {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .test-header {
    flex-direction: column;
    gap: 10px;
  }

  .test-meta {
    flex-direction: column;
    gap: 8px;
  }

  .test-actions {
    flex-direction: column;
  }

  .btn-attempt-test,
  .btn-test-submitted,
  .btn-view-results {
    width: 100%;
  }

  .test-results {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  /* Interview Responsive */
  .interview-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .interview-time {
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
  }

  .interview-actions {
    width: 100%;
  }

  .btn-join {
    width: 100%;
    justify-content: center;
  }

  /* Task Responsive */
  .task-header {
    flex-direction: column;
    gap: 12px;
  }

  .task-meta {
    flex-direction: column;
    gap: 8px;
  }

  .task-actions {
    flex-direction: column;
  }

  .btn-submit-review,
  .btn-generate-summary,
  .btn-start-task {
    width: 100%;
    justify-content: center;
  }

  .reviews-section {
    padding: 12px;
  }
}

/* Chatbot Widget */
.chatbot-widget {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
}

.chatbot-toggle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  position: relative;
}

.chatbot-toggle:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 30px rgba(102, 126, 234, 0.6);
}

.chat-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #e74c3c;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: bold;
}

.chatbot-window {
  width: 380px;
  height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chatbot-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chatbot-header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chatbot-header-info i {
  font-size: 1.8rem;
}

.chatbot-header-info h4 {
  margin: 0;
  font-size: 1.1rem;
}

.chatbot-status {
  font-size: 0.75rem;
  opacity: 0.9;
}

.chatbot-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.chatbot-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.chatbot-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f8f9fa;
}

.chatbot-welcome {
  text-align: center;
  padding: 40px 20px;
}

.chatbot-welcome i {
  font-size: 3rem;
  color: #667eea;
  margin-bottom: 15px;
}

.chatbot-welcome h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.chatbot-welcome p {
  color: #7f8c8d;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.quick-questions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 15px;
}

.quick-question-btn {
  background: white;
  border: 1px solid #ecf0f1;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  color: #2c3e50;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  text-align: left;
}

.quick-question-btn:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
  transform: translateX(5px);
}

.chat-message {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.chat-message.user .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.chat-message.bot .message-avatar {
  background: #ecf0f1;
  color: #7f8c8d;
}

.message-content {
  max-width: 70%;
}

.message-text {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  color: #2c3e50;
  line-height: 1.5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-message.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-time {
  font-size: 0.7rem;
  color: #95a5a6;
  margin-top: 4px;
  padding: 0 8px;
}

.typing-indicator {
  background: white;
  padding: 12px 20px;
  border-radius: 12px;
  display: flex;
  gap: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #95a5a6;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

.chatbot-input {
  padding: 15px;
  background: white;
  border-top: 1px solid #ecf0f1;
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.chat-textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  font-size: 0.95rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  resize: none;
  max-height: 100px;
  min-height: 40px;
}

.chat-textarea:focus {
  outline: none;
  border-color: #667eea;
}

.chat-send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.chat-send-btn:hover:not(:disabled) {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.chat-send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Chatbot Mobile Responsive */
@media (max-width: 768px) {
  .chatbot-widget {
    bottom: 20px;
    right: 20px;
  }

  .chatbot-window {
    width: calc(100vw - 40px);
    height: calc(100vh - 100px);
    max-width: 100%;
  }
}

/* Offer Letters */
.dashboard-card.offer-letters {
  grid-column: span 1;
}

.offers-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: 400px;
  overflow-y: auto;
}

.offer-item {
  background: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
}

.offer-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.offer-item.status-accepted {
  border-color: #28a745;
  background: #f0fff4;
}

.offer-item.status-rejected {
  border-color: #dc3545;
  background: #fff5f5;
}

.offer-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.offer-info h4 {
  margin: 0 0 4px 0;
  color: #2d3748;
  font-size: 1.1rem;
}

.offer-date {
  font-size: 0.85rem;
  color: #718096;
  margin: 0;
}

.offer-status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}

.offer-status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.offer-status-badge.accepted {
  background: #d4edda;
  color: #155724;
}

.offer-status-badge.rejected {
  background: #f8d7da;
  color: #721c24;
}

.offer-view-section {
  margin: 12px 0;
}

.btn-view-offer {
  width: 100%;
  padding: 10px 16px;
  border: 2px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-view-offer:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-view-offer i {
  font-size: 1.1rem;
}

.offer-actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.btn-accept-offer,
.btn-reject-offer {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-accept-offer {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
}

.btn-accept-offer:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
}

.btn-reject-offer {
  background: #f8f9fa;
  color: #dc3545;
  border: 2px solid #dc3545;
}

.btn-reject-offer:hover:not(:disabled) {
  background: #dc3545;
  color: white;
}

.btn-accept-offer:disabled,
.btn-reject-offer:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.offer-result {
  margin-top: 12px;
  padding: 12px;
  border-radius: 8px;
}

.accepted-text,
.rejected-text {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-weight: 600;
}

.accepted-text {
  color: #155724;
}

.accepted-text i {
  color: #28a745;
  font-size: 1.2rem;
}

.rejected-text {
  color: #721c24;
}

.rejected-text i {
  color: #dc3545;
  font-size: 1.2rem;
}

.processing-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  color: #667eea;
  font-weight: 600;
}

.processing-indicator i {
  font-size: 1.2rem;
}
</style>
