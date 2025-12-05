<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-container test-results-modal" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <h3>
          <i class="fas fa-chart-line"></i>
          AI Test Results - {{ candidate?.name }}
        </h3>
        <button @click="$emit('close')" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <!-- Modal Body -->
      <div class="modal-body">
        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading test results...</p>
        </div>

        <!-- Test Results -->
        <div v-else class="test-results">
          <!-- Candidate & Test Info -->
          <div class="test-info-section">
            <div class="info-grid">
              <div class="info-item">
                <label>Candidate:</label>
                <span>{{ candidate.name }}</span>
              </div>
              <div class="info-item">
                <label>Position:</label>
                <span>{{ testResults.job_title }}</span>
              </div>
              <div class="info-item">
                <label>Test Duration:</label>
                <span>{{ testResults.duration_minutes }} minutes</span>
              </div>
              <div class="info-item">
                <label>Submitted:</label>
                <span>{{ formatDateTime(testResults.submitted_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Questions & Answers -->
          <div class="questions-section">
            <h4>
              <i class="fas fa-question-circle"></i>
              Test Questions & Answers
            </h4>
            
            <div v-for="(qa, index) in questionsAndAnswers" :key="index" class="question-item">
              <div class="question-header">
                <span class="question-number">Q{{ index + 1 }}</span>
                <span :class="getDifficultyClass(qa.difficulty)" class="difficulty-badge">
                  {{ qa.difficulty }}
                </span>
              </div>
              
              <div class="question-content">
                <h5>{{ qa.question }}</h5>
                <div class="answer-section">
                  <label>Candidate's Answer:</label>
                  <div class="answer-text">{{ qa.answer || 'No answer provided' }}</div>
                </div>
                
                <!-- Score Input -->
                <div class="score-input-section">
                  <label>Score (out of 10):</label>
                  <select 
                    v-model="qa.score" 
                    @change="updateTotalScore"
                    class="score-select"
                  >
                    <option value="">Select Score</option>
                    <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Overall Assessment -->
          <div class="assessment-section">
            <h4>
              <i class="fas fa-clipboard-check"></i>
              Overall Assessment
            </h4>
            
            <div class="assessment-grid">
              <div class="score-summary">
                <div class="total-score">
                  <label>Total Score:</label>
                  <span class="score-value">{{ totalScore }}/{{ maxScore }}</span>
                  <span class="score-percentage">({{ scorePercentage }}%)</span>
                </div>
                
                <div class="score-breakdown">
                  <div class="breakdown-item">
                    <span>Easy Questions ({{ easyQuestions.length }}):</span>
                    <span>{{ easyScore }}/{{ easyQuestions.length * 10 }}</span>
                  </div>
                  <div class="breakdown-item">
                    <span>Medium Questions ({{ mediumQuestions.length }}):</span>
                    <span>{{ mediumScore }}/{{ mediumQuestions.length * 10 }}</span>
                  </div>
                  <div class="breakdown-item">
                    <span>Hard Questions ({{ hardQuestions.length }}):</span>
                    <span>{{ hardScore }}/{{ hardQuestions.length * 10 }}</span>
                  </div>
                </div>
              </div>

              <div class="recommendation-section">
                <label>Recommendation:</label>
                <select v-model="assessment.recommendation" class="recommendation-select">
                  <option value="">Select Recommendation</option>
                  <option value="pass">Pass - Move to Next Stage</option>
                  <option value="fail">Fail - Reject Candidate</option>
                  <option value="borderline">Borderline - Requires Discussion</option>
                </select>
              </div>
            </div>

            <!-- Comments -->
            <div class="comments-section">
              <label>Comments & Feedback:</label>
              <textarea 
                v-model="assessment.comments"
                class="comments-textarea"
                placeholder="Provide detailed feedback on the candidate's performance..."
                rows="4"
              ></textarea>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Modal Footer -->
      <div class="modal-footer">
        <button @click="$emit('close')" type="button" class="btn-secondary" :disabled="submitting">
          Cancel
        </button>
        <button 
          @click="submitAssessment" 
          type="submit" 
          class="btn-primary" 
          :disabled="submitting || !canSubmit"
        >
          <i class="fas fa-spinner fa-spin" v-if="submitting"></i>
          <i class="fas fa-check" v-else></i>
          {{ submitting ? 'Submitting...' : 'Submit Assessment' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  candidate: {
    type: Object,
    required: true
  },
  testId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close', 'assessmentSubmitted'])

// State
const loading = ref(true)
const submitting = ref(false)
const testResults = ref({})
const questionsAndAnswers = ref([])
const assessment = ref({
  recommendation: '',
  comments: ''
})

// Computed
const totalScore = computed(() => {
  return questionsAndAnswers.value.reduce((sum, qa) => sum + (parseInt(qa.score) || 0), 0)
})

const maxScore = computed(() => {
  return questionsAndAnswers.value.length * 10
})

const scorePercentage = computed(() => {
  return maxScore.value > 0 ? Math.round((totalScore.value / maxScore.value) * 100) : 0
})

const easyQuestions = computed(() => questionsAndAnswers.value.filter(qa => qa.difficulty === 'easy'))
const mediumQuestions = computed(() => questionsAndAnswers.value.filter(qa => qa.difficulty === 'medium'))
const hardQuestions = computed(() => questionsAndAnswers.value.filter(qa => qa.difficulty === 'hard'))

const easyScore = computed(() => easyQuestions.value.reduce((sum, qa) => sum + (parseInt(qa.score) || 0), 0))
const mediumScore = computed(() => mediumQuestions.value.reduce((sum, qa) => sum + (parseInt(qa.score) || 0), 0))
const hardScore = computed(() => hardQuestions.value.reduce((sum, qa) => sum + (parseInt(qa.score) || 0), 0))

const canSubmit = computed(() => {
  return assessment.value.recommendation && 
         questionsAndAnswers.value.every(qa => qa.score !== '')
})

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

function getDifficultyClass(difficulty) {
  const classMap = {
    'easy': 'difficulty-easy',
    'medium': 'difficulty-medium',
    'hard': 'difficulty-hard'
  }
  return classMap[difficulty] || 'difficulty-default'
}

function updateTotalScore() {
  // This will trigger computed properties to recalculate
}

// API Functions
async function loadTestResults() {
  try {
    loading.value = true
    
    const response = await axios.get(`/api/ai/test-results/${props.testId}`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    
    if (response.data) {
      testResults.value = response.data
      
      // Parse questions and answers
      const questions = JSON.parse(response.data.questions || '[]')
      const answers = JSON.parse(response.data.answers || '[]')
      
      questionsAndAnswers.value = questions.map((q, index) => ({
        question: q.question,
        difficulty: q.difficulty,
        answer: answers[index] || '',
        score: ''
      }))
    }
  } catch (error) {
    console.error('Failed to load test results:', error)
  } finally {
    loading.value = false
  }
}

async function submitAssessment() {
  try {
    submitting.value = true
    
    const assessmentData = {
      test_id: props.testId,
      candidate_id: props.candidate.id,
      total_score: totalScore.value,
      max_score: maxScore.value,
      score_percentage: scorePercentage.value,
      recommendation: assessment.value.recommendation,
      comments: assessment.value.comments,
      question_scores: questionsAndAnswers.value.map((qa, index) => ({
        question_index: index,
        score: parseInt(qa.score),
        difficulty: qa.difficulty
      })),
      assessed_by: getCurrentUserId()
    }
    
    const response = await axios.post('/api/ai/submit-assessment', assessmentData, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    
    if (response.data) {
      emit('assessmentSubmitted', {
        candidate_id: props.candidate.id,
        total_score: totalScore.value,
        score_percentage: scorePercentage.value,
        recommendation: assessment.value.recommendation
      })
      
      alert('Assessment submitted successfully!')
      emit('close')
    }
  } catch (error) {
    console.error('Failed to submit assessment:', error)
    alert('Failed to submit assessment. Please try again.')
  } finally {
    submitting.value = false
  }
}

function getCurrentUserId() {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  return user.id || localStorage.getItem('user_id') || null
}

// Load data on mount
onMounted(() => {
  loadTestResults()
})
</script>

<style scoped>
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

.modal-container.test-results-modal {
  background: white;
  border-radius: 16px;
  max-width: 1000px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.modal-header {
  padding: 24px 28px;
  border-bottom: 2px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.close-btn {
  background: rgba(255,255,255,0.2);
  border: none;
  font-size: 1.5rem;
  color: white;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255,255,255,0.3);
}

.modal-body {
  padding: 28px;
  overflow-y: auto;
  flex: 1;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.loading-state i {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
  color: #3498db;
}

/* Test Info Section */
.test-info-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  border-left: 4px solid #3498db;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  font-size: 0.8rem;
  color: #7f8c8d;
  font-weight: 600;
  text-transform: uppercase;
}

.info-item span {
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 600;
}

/* Questions Section */
.questions-section {
  margin-bottom: 24px;
}

.questions-section h4 {
  color: #2c3e50;
  font-size: 1.2rem;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ecf0f1;
}

.question-item {
  background: white;
  border: 1px solid #ecf0f1;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.question-item:hover {
  border-color: #3498db;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.1);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.question-number {
  background: #3498db;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.difficulty-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.difficulty-easy {
  background: #d4edda;
  color: #155724;
}

.difficulty-medium {
  background: #fff3cd;
  color: #856404;
}

.difficulty-hard {
  background: #f8d7da;
  color: #721c24;
}

.question-content h5 {
  color: #2c3e50;
  margin: 0 0 16px 0;
  font-size: 1.1rem;
  line-height: 1.5;
}

.answer-section {
  margin-bottom: 16px;
}

.answer-section label {
  display: block;
  font-weight: 600;
  color: #7f8c8d;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.answer-text {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  color: #2c3e50;
  line-height: 1.6;
  min-height: 50px;
  border-left: 3px solid #e74c3c;
}

.score-input-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-input-section label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.score-select {
  padding: 8px 12px;
  border: 2px solid #ecf0f1;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-weight: 600;
}

.score-select:focus {
  outline: none;
  border-color: #3498db;
}

/* Assessment Section */
.assessment-section {
  background: #f8f9fa;
  padding: 24px;
  border-radius: 12px;
  border-left: 4px solid #27ae60;
}

.assessment-section h4 {
  color: #2c3e50;
  font-size: 1.2rem;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.assessment-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 20px;
}

.score-summary {
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #ecf0f1;
}

.total-score {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ecf0f1;
}

.total-score label {
  font-weight: 600;
  color: #7f8c8d;
}

.score-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: #2c3e50;
}

.score-percentage {
  font-size: 1.2rem;
  font-weight: 600;
  color: #27ae60;
}

.score-breakdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.breakdown-item span:first-child {
  color: #7f8c8d;
}

.breakdown-item span:last-child {
  font-weight: 600;
  color: #2c3e50;
}

.recommendation-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #ecf0f1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-section label {
  font-weight: 600;
  color: #2c3e50;
}

.recommendation-select {
  padding: 12px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 1rem;
}

.recommendation-select:focus {
  outline: none;
  border-color: #3498db;
}

.comments-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comments-section label {
  font-weight: 600;
  color: #2c3e50;
}

.comments-textarea {
  padding: 12px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  resize: vertical;
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.5;
}

.comments-textarea:focus {
  outline: none;
  border-color: #3498db;
}

/* Modal Footer */
.modal-footer {
  padding: 20px 28px;
  border-top: 2px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: #f8f9fa;
  border-radius: 0 0 16px 16px;
}

.btn-secondary,
.btn-primary {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-secondary:hover:not(:disabled) {
  background: #bdc3c7;
}

.btn-primary {
  background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(39, 174, 96, 0.4);
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Responsive */
@media (max-width: 768px) {
  .modal-container.test-results-modal {
    max-width: 95%;
    margin: 10px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .assessment-grid {
    grid-template-columns: 1fr;
  }

  .question-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .score-input-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .btn-secondary,
  .btn-primary {
    width: 100%;
    justify-content: center;
  }
}
</style>