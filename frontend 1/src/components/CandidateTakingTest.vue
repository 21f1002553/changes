<template>
  <div>
    <DashboardLayout>
      <div class="test-container">
        <!-- Test Header -->
        <div class="test-header">
          <div class="test-info">
            <h1>
              <i class="fas fa-magic"></i>
              {{ testData.job_title }} - AI Technical Test
            </h1>
            <p class="test-description">{{ testData.instructions }}</p>
          </div>
          
          <div class="test-meta">
            <div class="meta-item">
              <i class="fas fa-clock"></i>
              <span>Duration: {{ testData.duration_minutes }} minutes</span>
            </div>
            <div class="meta-item deadline">
              <i class="fas fa-calendar"></i>
              <span>Deadline: {{ formatDeadline(testData.deadline) }}</span>
            </div>
            <div class="meta-item timer" :class="{ warning: timeRemaining < 300 }">
              <i class="fas fa-hourglass-half"></i>
              <span>Time Remaining: {{ formatTime(timeRemaining) }}</span>
            </div>
          </div>
        </div>

        <!-- Test Status Bar -->
        <div class="status-bar">
          <div class="progress-info">
            <span>Progress: {{ answeredCount }} / {{ questions.length }} questions answered</span>
            <div class="progress-bar-container">
              <div 
                class="progress-bar-fill" 
                :style="{ width: progressPercentage + '%' }"
              ></div>
            </div>
          </div>
          <div class="auto-save-status" v-if="autoSaving">
            <i class="fas fa-spinner fa-spin"></i>
            <span>Saving...</span>
          </div>
          <div class="auto-save-status saved" v-else-if="lastSaved">
            <i class="fas fa-check"></i>
            <span>Saved at {{ lastSaved }}</span>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-container">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading test questions...</p>
        </div>

        <!-- Test Not Started -->
        <div v-else-if="!testStarted" class="test-intro">
          <div class="intro-content">
            <div class="intro-icon">
              <i class="fas fa-info-circle"></i>
            </div>
            <h2>Test Instructions</h2>
            <div class="instructions-list">
              <div class="instruction-item">
                <i class="fas fa-check-circle"></i>
                <span>This is a subjective test with {{ questions.length }} questions</span>
              </div>
              <div class="instruction-item">
                <i class="fas fa-check-circle"></i>
                <span>You have {{ testData.duration_minutes }} minutes to complete the test</span>
              </div>
              <div class="instruction-item">
                <i class="fas fa-check-circle"></i>
                <span>Your answers will be auto-saved every 30 seconds</span>
              </div>
              <div class="instruction-item">
                <i class="fas fa-check-circle"></i>
                <span>You can navigate between questions using Previous/Next buttons</span>
              </div>
              <div class="instruction-item">
                <i class="fas fa-check-circle"></i>
                <span>Make sure to submit the test before the deadline</span>
              </div>
              <div class="instruction-item warning">
                <i class="fas fa-exclamation-triangle"></i>
                <span>Once submitted, you cannot modify your answers</span>
              </div>
            </div>
            <button @click="startTest" class="btn-start-test">
              <i class="fas fa-play-circle"></i>
              Start Test
            </button>
          </div>
        </div>

        <!-- Test Questions -->
        <div v-else-if="testStarted && !submitted" class="test-content">
          <!-- Question Navigation -->
          <div class="question-nav">
            <div class="nav-header">
              <h3>Questions</h3>
              <span class="answered-count">{{ answeredCount }} / {{ questions.length }}</span>
            </div>
            <div class="question-grid">
              <button
                v-for="(question, index) in questions"
                :key="index"
                @click="currentQuestionIndex = index"
                class="question-nav-btn"
                :class="{
                  active: currentQuestionIndex === index,
                  answered: answers[index] && answers[index].trim() !== ''
                }"
              >
                {{ index + 1 }}
              </button>
            </div>
          </div>

          <!-- Current Question Display -->
          <div class="question-display">
            <div class="question-header">
              <div class="question-number">
                <span class="label">Question {{ currentQuestionIndex + 1 }}</span>
                <span class="total">of {{ questions.length }}</span>
              </div>
              <div class="question-difficulty" :class="currentQuestion.difficulty">
                <i class="fas fa-signal"></i>
                {{ currentQuestion.difficulty }}
              </div>
            </div>

            <div class="question-content">
              <h3 class="question-text">{{ currentQuestion.question }}</h3>
              
              <!-- Answer Input -->
            <div class="answer-section">
                <label class="answer-label">
                    <i class="fas fa-pencil-alt"></i>
                    Your Answer
                </label>
                <textarea
                    v-model="answers[currentQuestionIndex]"
                    @input="handleAnswerChange"
                    class="answer-textarea"
                    :placeholder="`Write your answer for Question ${currentQuestionIndex + 1} here...`"
                    rows="12"
                ></textarea>
                <div class="character-count">
                    {{ (answers[currentQuestionIndex] || '').length }} characters
                </div>
                </div>
            </div>

            <!-- Navigation Buttons -->
            <div class="question-controls">
              <button
                @click="previousQuestion"
                :disabled="currentQuestionIndex === 0"
                class="btn-nav btn-previous"
              >
                <i class="fas fa-chevron-left"></i>
                Previous
              </button>

              <button
                @click="saveProgress"
                class="btn-save"
                :disabled="autoSaving"
              >
                <i class="fas fa-save"></i>
                Save Progress
              </button>

              <button
                v-if="currentQuestionIndex < questions.length - 1"
                @click="nextQuestion"
                class="btn-nav btn-next"
              >
                Next
                <i class="fas fa-chevron-right"></i>
              </button>

              <button
                v-else
                @click="showSubmitConfirmation = true"
                class="btn-submit-test"
              >
                <i class="fas fa-check-circle"></i>
                Submit Test
              </button>
            </div>
          </div>
        </div>

        <!-- Test Submitted -->
        <div v-else-if="submitted" class="test-completed">
          <div class="completion-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <h2>Test Submitted Successfully!</h2>
          <p>Your test has been submitted for evaluation.</p>
          <p class="info-text">You will be notified once the results are available.</p>
          <button @click="goToDashboard" class="btn-dashboard">
            <i class="fas fa-home"></i>
            Back to Dashboard
          </button>
        </div>

        <!-- Submit Confirmation Modal -->
        <div v-if="showSubmitConfirmation" class="modal-overlay" @click="showSubmitConfirmation = false">
          <div class="modal-container" @click.stop>
            <div class="modal-header">
              <h3>
                <i class="fas fa-exclamation-triangle"></i>
                Confirm Submission
              </h3>
            </div>
            <div class="modal-body">
              <p>Are you sure you want to submit your test?</p>
              <div class="submission-summary">
                <div class="summary-item">
                  <span class="label">Total Questions:</span>
                  <span class="value">{{ questions.length }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">Answered:</span>
                  <span class="value">{{ answeredCount }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">Unanswered:</span>
                  <span class="value unanswered">{{ questions.length - answeredCount }}</span>
                </div>
              </div>
              <p class="warning-text">
                <i class="fas fa-exclamation-circle"></i>
                Once submitted, you cannot modify your answers.
              </p>
            </div>
            <div class="modal-footer">
              <button @click="showSubmitConfirmation = false" class="btn-cancel">
                Cancel
              </button>
              <button @click="submitTest" class="btn-confirm-submit" :disabled="submitting">
                <i class="fas fa-spinner fa-spin" v-if="submitting"></i>
                <i class="fas fa-check" v-else></i>
                {{ submitting ? 'Submitting...' : 'Yes, Submit Test' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const router = useRouter()
const route = useRoute()

// State
const loading = ref(true)
const testStarted = ref(false)
const submitted = ref(false)
const submitting = ref(false)
const autoSaving = ref(false)
const showSubmitConfirmation = ref(false)

const testData = ref({
  id: null,
  job_title: '',
  duration_minutes: 60,
  deadline: null,
  instructions: ''
})

const questions = ref([])
const answers = ref([])
const currentQuestionIndex = ref(0)
const timeRemaining = ref(0)
const lastSaved = ref(null)

let timerInterval = null
let autoSaveInterval = null

// Computed
const currentQuestion = computed(() => {
  return questions.value[currentQuestionIndex.value] || {}
})

const answeredCount = computed(() => {
  return answers.value.filter(answer => answer && answer.trim() !== '').length
})

const progressPercentage = computed(() => {
  return (answeredCount.value / questions.value.length) * 100
})

// Functions
const getAuthToken = () => localStorage.getItem('access_token')

async function loadTestData() {
  try {
    loading.value = true
    const testId = route.query.test_id

    if (!testId) {
      alert('Invalid test ID')
      router.push('/candidateDashboard')
      return
    }

    const response = await axios.get(`/api/ai/test/${testId}`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      testData.value = {
        id: response.data.id,
        job_title: response.data.job_title,
        duration_minutes: response.data.duration_minutes,
        deadline: response.data.deadline,
        instructions: response.data.instructions || 'Complete all questions to the best of your ability.',
        status: response.data.status
      }

      // Check if test is already submitted
      if (testData.value.status === 'submitted' || testData.value.status === 'evaluated') {
        submitted.value = true
        loading.value = false
        return
      }

      // Parse questions with flexible key handling
      let rawQuestions = response.data.questions
      
      // Handle double JSON encoding
      if (typeof rawQuestions === 'string') {
        rawQuestions = JSON.parse(rawQuestions)
      }
      if (typeof rawQuestions === 'string') {
        rawQuestions = JSON.parse(rawQuestions)
      }

      let allQuestions = []

      // If it's already an array, use it directly
      if (Array.isArray(rawQuestions)) {
        allQuestions = rawQuestions.map(q => ({
          ...q,
          difficulty: q.difficulty || 'medium' // Default to medium if not specified
        }))
      } 
      // If it's an object with difficulty levels
      else if (typeof rawQuestions === 'object' && rawQuestions !== null) {
        // Define all possible key variations for each difficulty level
        const difficultyKeyMap = {
          easy: ['easy', 'easy_questions', 'easy_question', 'Easy', 'EASY'],
          medium: ['medium', 'medium_questions', 'medium_question', 'Medium', 'MEDIUM'],
          hard: ['hard', 'hard_questions', 'hard_question', 'Hard', 'HARD', 'difficult', 'difficult_questions']
        }

        // Process each difficulty level
        Object.entries(difficultyKeyMap).forEach(([level, possibleKeys]) => {
          // Find which key exists in the response
          const foundKey = possibleKeys.find(key => rawQuestions[key])
          
          if (foundKey && Array.isArray(rawQuestions[foundKey])) {
            const levelQuestions = rawQuestions[foundKey].map(q => ({
              ...q,
              difficulty: level // Normalize to lowercase: easy, medium, hard
            }))
            allQuestions = [...allQuestions, ...levelQuestions]
          }
        })

        // Fallback: if no standard keys found, try to extract any array properties
        if (allQuestions.length === 0) {
          Object.entries(rawQuestions).forEach(([key, value]) => {
            if (Array.isArray(value)) {
              // Try to infer difficulty from key name
              let inferredDifficulty = 'medium'
              const keyLower = key.toLowerCase()
              
              if (keyLower.includes('easy')) {
                inferredDifficulty = 'easy'
              } else if (keyLower.includes('hard') || keyLower.includes('difficult')) {
                inferredDifficulty = 'hard'
              } else if (keyLower.includes('medium')) {
                inferredDifficulty = 'medium'
              }

              const levelQuestions = value.map(q => ({
                ...q,
                difficulty: inferredDifficulty
              }))
              allQuestions = [...allQuestions, ...levelQuestions]
            }
          })
        }
      }

      console.log('✅ Parsed Questions Array:', allQuestions)
      questions.value = allQuestions

      // Handle answers
      if (response.data.answers) {
        let parsedAnswers = response.data.answers
        
        // Handle double JSON encoding
        if (typeof parsedAnswers === 'string') {
          parsedAnswers = JSON.parse(parsedAnswers)
        }
        if (typeof parsedAnswers === 'string') {
          parsedAnswers = JSON.parse(parsedAnswers)
        }
        
        answers.value = Array.isArray(parsedAnswers) 
          ? parsedAnswers 
          : new Array(questions.value.length).fill('')
      } else {
        // Create empty slots for new test
        answers.value = new Array(questions.value.length).fill('')
      }

      // Set time remaining based on duration
      timeRemaining.value = testData.value.duration_minutes * 60

      console.log('✅ Test data loaded:', testData.value)
      console.log('✅ Questions loaded:', questions.value.length)
      console.log('✅ Question difficulties:', 
        allQuestions.reduce((acc, q) => {
          acc[q.difficulty] = (acc[q.difficulty] || 0) + 1
          return acc
        }, {})
      )
      
      loading.value = false
    }
  } catch (error) {
    console.error('❌ Full Error Object:', error)
    
    // If it's a network response error (404, 500)
    if (error.response) {
      alert(`Server Error: ${error.response.status} - ${JSON.stringify(error.response.data)}`)
    } 
    // If it's a code logic error (JSON parse)
    else {
      alert(`Logic Error: ${error.message}`) 
    }
    
    loading.value = false
    router.push('/candidateDashboard')
  }
}

function startTest() {
  testStarted.value = true
  startTimer()
  startAutoSave()
}

function startTimer() {
  timerInterval = setInterval(() => {
    if (timeRemaining.value > 0) {
      timeRemaining.value--
    } else {
      // Auto-submit when time runs out
      clearInterval(timerInterval)
      alert('Time is up! Your test will be submitted automatically.')
      submitTest()
    }
  }, 1000)
}

function startAutoSave() {
  // Auto-save every 30 seconds
  autoSaveInterval = setInterval(() => {
    saveProgress()
  }, 30000)
}

function formatTime(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  }
  return `${minutes}:${String(secs).padStart(2, '0')}`
}

function formatDeadline(deadline) {
  if (!deadline) return 'N/A'
  return new Date(deadline).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}


let debounceTimer = null
function handleAnswerChange() {

  if (debounceTimer) clearTimeout(debounceTimer)

  debounceTimer = setTimeout(() => {
    saveProgress()
  }, 1500)
}
async function saveProgress() {
  try {
    autoSaving.value = true

    await axios.post(`/api/ai/save-test-progress/${testData.value.id}`, {
      answers: answers.value
    }, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    const now = new Date()
    lastSaved.value = now.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })

    console.log('✅ Progress saved')
  } catch (error) {
    console.error('❌ Failed to save progress:', error)
  } finally {
    autoSaving.value = false
  }
}

async function submitTest() {
  try {
    submitting.value = true

    await axios.post(`/api/ai/submit-test/${testData.value.id}`, {
      answers: answers.value
    }, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    // Clear intervals
    if (timerInterval) clearInterval(timerInterval)
    if (autoSaveInterval) clearInterval(autoSaveInterval)

    submitted.value = true
    showSubmitConfirmation.value = false

    console.log('✅ Test submitted successfully')
  } catch (error) {
    console.error('❌ Failed to submit test:', error)
    alert('Failed to submit test. Please try again.')
  } finally {
    submitting.value = false
  }
}

function nextQuestion() {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
  }
}

function previousQuestion() {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}

function goToDashboard() {
  router.push('/candidateDashboard')
}

// Lifecycle
onMounted(async () => {
  await loadTestData()
})

onBeforeUnmount(() => {
  // Clear intervals when component is destroyed
  if (timerInterval) clearInterval(timerInterval)
  if (autoSaveInterval) clearInterval(autoSaveInterval)
})

// Prevent accidental page close
window.addEventListener('beforeunload', (e) => {
  if (testStarted.value && !submitted.value) {
    e.preventDefault()
    e.returnValue = ''
  }
})
</script>

<style scoped>
.test-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

/* Test Header */
.test-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.test-info h1 {
  margin: 0 0 10px 0;
  font-size: 1.8rem;
  display: flex;
  align-items: center;
  gap: 12px;
}

.test-description {
  margin: 0;
  opacity: 0.9;
  font-size: 1.05rem;
}

.test-meta {
  display: flex;
  gap: 30px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.95rem;
}

.meta-item.timer.warning {
  background: #e74c3c;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Status Bar */
.status-bar {
  background: white;
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.progress-info {
  flex: 1;
  max-width: 400px;
}

.progress-bar-container {
  background: #ecf0f1;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 8px;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.auto-save-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.auto-save-status.saved {
  color: #27ae60;
}

/* Loading */
.loading-container {
  text-align: center;
  padding: 80px 20px;
  color: #7f8c8d;
}

.loading-container i {
  font-size: 3rem;
  margin-bottom: 20px;
  display: block;
  color: #667eea;
}

/* Test Intro */
.test-intro {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.intro-content {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.intro-icon {
  font-size: 4rem;
  color: #667eea;
  margin-bottom: 20px;
}

.intro-content h2 {
  color: #2c3e50;
  margin-bottom: 30px;
}

.instructions-list {
  text-align: left;
  margin: 30px 0;
}

.instruction-item {
  display: flex;
  align-items: start;
  gap: 12px;
  margin-bottom: 15px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.instruction-item i {
  color: #27ae60;
  margin-top: 2px;
}

.instruction-item.warning i {
  color: #e74c3c;
}

.btn-start-test {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 15px 40px;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 30px auto 0;
  transition: all 0.3s ease;
}

.btn-start-test:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

/* Test Content */
.test-content {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 20px;
}

/* Question Navigation */
.question-nav {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  height: fit-content;
  position: sticky;
  top: 20px;
}

.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 2px solid #ecf0f1;
}

.nav-header h3 {
  margin: 0;
  color: #2c3e50;
}

.answered-count {
  background: #667eea;
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.question-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.question-nav-btn {
  aspect-ratio: 1;
  border: 2px solid #ecf0f1;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  color: #7f8c8d;
  transition: all 0.2s ease;
}

.question-nav-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.question-nav-btn.active {
  background: #667eea;
  border-color: #667eea;
  color: white;
}

.question-nav-btn.answered {
  background: #27ae60;
  border-color: #27ae60;
  color: white;
}

.question-nav-btn.answered.active {
  background: #667eea;
  border-color: #667eea;
}

/* Question Display */
.question-display {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 2px solid #ecf0f1;
}

.question-number {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.question-number .label {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2c3e50;
}

.question-number .total {
  color: #7f8c8d;
  font-size: 1rem;
}

.question-difficulty {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: capitalize;
}

.question-difficulty.easy {
  background: #d4edda;
  color: #155724;
}

.question-difficulty.medium {
  background: #fff3cd;
  color: #856404;
}

.question-difficulty.hard {
  background: #f8d7da;
  color: #721c24;
}

.question-text {
  color: #2c3e50;
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: 25px;
}

/* Answer Section */
.answer-section {
  margin: 25px 0;
}

.answer-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2c3e50;
  font-weight: 600;
  margin-bottom: 12px;
  font-size: 1.05rem;
}

.answer-textarea {
  width: 100%;
  padding: 15px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.answer-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.character-count {
  text-align: right;
  color: #7f8c8d;
  font-size: 0.85rem;
  margin-top: 8px;
}

/* Question Controls */
.question-controls {
  display: flex;
  gap: 12px;
  margin-top: 30px;
  padding-top: 25px;
  border-top: 2px solid #ecf0f1;
}

.btn-nav,
.btn-save,
.btn-submit-test {
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

.btn-nav {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-nav:hover:not(:disabled) {
  background: #bdc3c7;
  transform: translateY(-1px);
}

.btn-nav:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-save {
  background: #3498db;
  color: white;
  margin-left: auto;
}

.btn-save:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-1px);
}

.btn-submit-test {
  background: linear-gradient(135deg, #27ae60, #229954);
  color: white;
  margin-left: auto;
}

.btn-submit-test:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(39, 174, 96, 0.4);
}

/* Test Completed */
.test-completed {
  background: white;
  border-radius: 12px;
  padding: 60px 40px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.completion-icon {
  font-size: 5rem;
  color: #27ae60;
  margin-bottom: 20px;
}

.test-completed h2 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.test-completed p {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin-bottom: 10px;
}

.info-text {
  color: #3498db;
  font-weight: 600;
}

.btn-dashboard {
  background: #667eea;
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-top: 30px;
  transition: all 0.3s ease;
}

.btn-dashboard:hover {
  background: #5568d3;
  transform: translateY(-2px);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.modal-header {
  padding: 24px 28px;
  border-bottom: 2px solid #ecf0f1;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 12px;
}

.modal-header h3 i {
  color: #f39c12;
}

.modal-body {
  padding: 28px;
}

.modal-body > p {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 1.05rem;
}

.submission-summary {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.summary-item:last-child {
  margin-bottom: 0;
}

.summary-item .label {
  color: #7f8c8d;
  font-weight: 600;
}

.summary-item .value {
  color: #2c3e50;
  font-weight: 700;
}

.summary-item .value.unanswered {
  color: #e74c3c;
}

.warning-text {
  background: #fff3cd;
  color: #856404;
  padding: 12px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 20px 0 0 0;
  font-weight: 600;
}

.modal-footer {
  padding: 20px 28px;
  border-top: 2px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel,
.btn-confirm-submit {
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

.btn-confirm-submit {
  background: linear-gradient(135deg, #27ae60, #229954);
  color: white;
}

.btn-confirm-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.4);
}

.btn-confirm-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 1024px) {
  .test-content {
    grid-template-columns: 1fr;
  }

  .question-nav {
    position: static;
  }

  .question-grid {
    grid-template-columns: repeat(8, 1fr);
  }
}

@media (max-width: 768px) {
  .test-header {
    padding: 20px;
  }

  .test-info h1 {
    font-size: 1.4rem;
  }

  .test-meta {
    flex-direction: column;
    gap: 10px;
  }

  .status-bar {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }

  .question-grid {
    grid-template-columns: repeat(5, 1fr);
  }

  .question-display {
    padding: 20px;
  }

  .question-controls {
    flex-direction: column;
  }

  .btn-save,
  .btn-submit-test {
    margin-left: 0;
    width: 100%;
    justify-content: center;
  }
}
</style>