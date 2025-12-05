<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-container scorecard-modal" @click.stop>
      <div class="modal-header">
        <h3>
          <i class="fas fa-chart-bar"></i>
          Interview Scorecard - {{ candidate?.name }}
        </h3>
        <button @click="$emit('close')" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <div v-if="scorecard" class="scorecard-content">
          <!-- Overall Score Summary -->
          <div class="scorecard-summary">
            <div class="overall-score">
              <div class="score-circle" :class="getOverallScoreClass(scorecard.overall_score)">
                <span class="score-value">{{ scorecard.overall_score }}/5</span>
                <span class="score-label">Overall</span>
              </div>
            </div>
            <div class="recommendation-badge" :class="scorecard.recommendation">
              <i class="fas fa-thumbs-up"></i>
              {{ formatRecommendation(scorecard.recommendation) }}
            </div>
          </div>

          <!-- Interview Details -->
          <div class="interview-details">
            <div class="detail-grid">
              <div class="detail-item">
                <label>Interview Type:</label>
                <span>{{ formatInterviewType(scorecard.interview_type) }}</span>
              </div>
              <div class="detail-item">
                <label>Interviewer:</label>
                <span>{{ scorecard.interviewer_name }}</span>
              </div>
              <div class="detail-item">
                <label>Date:</label>
                <span>{{ formatDate(scorecard.interview_date) }}</span>
              </div>
              <div class="detail-item">
                <label>Duration:</label>
                <span>{{ scorecard.duration || 'N/A' }} minutes</span>
              </div>
            </div>
          </div>

          <!-- Individual Scores -->
          <div class="scores-section">
            <h4>Individual Scores</h4>
            <div class="scores-grid">
              <div v-for="score in individualScores" :key="score.criteria" class="score-item">
                <div class="score-header">
                  <span class="criteria-name">{{ score.criteria }}</span>
                  <span class="score-value" :class="getScoreClass(score.value)">
                    {{ score.value }}/5
                  </span>
                </div>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: (score.value / 5) * 100 + '%' }"></div>
                </div>
                <p v-if="score.notes" class="score-notes">{{ score.notes }}</p>
              </div>
            </div>
          </div>

          <!-- Strengths & Weaknesses -->
          <div class="feedback-section">
            <div class="feedback-grid">
              <div class="strengths">
                <h4><i class="fas fa-plus-circle"></i> Strengths</h4>
                <ul v-if="scorecard.strengths && scorecard.strengths.length > 0">
                  <li v-for="strength in scorecard.strengths" :key="strength">
                    {{ strength }}
                  </li>
                </ul>
                <p v-else class="no-data">No strengths noted</p>
              </div>
              
              <div class="weaknesses">
                <h4><i class="fas fa-minus-circle"></i> Areas for Improvement</h4>
                <ul v-if="scorecard.weaknesses && scorecard.weaknesses.length > 0">
                  <li v-for="weakness in scorecard.weaknesses" :key="weakness">
                    {{ weakness }}
                  </li>
                </ul>
                <p v-else class="no-data">No areas for improvement noted</p>
              </div>
            </div>
          </div>

          <!-- Comments -->
          <div v-if="scorecard.comments" class="comments-section">
            <h4>Additional Comments</h4>
            <div class="comments-box">
              <p>{{ scorecard.comments }}</p>
            </div>
          </div>

          <!-- Follow-up Actions -->
          <div v-if="scorecard.follow_up_actions && scorecard.follow_up_actions.length > 0" class="followup-section">
            <h4>Follow-up Actions</h4>
            <ul class="followup-list">
              <li v-for="action in scorecard.follow_up_actions" :key="action">
                <i class="fas fa-arrow-right"></i>
                {{ action }}
              </li>
            </ul>
          </div>
        </div>
        
        <div v-else class="no-scorecard">
          <i class="fas fa-chart-bar"></i>
          <h4>No Scorecard Available</h4>
          <p>The interview scorecard has not been completed yet.</p>
        </div>
      </div>
      
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn-secondary">Close</button>
        <button v-if="scorecard" @click="printScorecard" class="btn-primary">
          <i class="fas fa-print"></i>
          Print Scorecard
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  candidate: {
    type: Object,
    required: true
  },
  scorecard: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

// Computed properties
const individualScores = computed(() => {
  if (!props.scorecard?.individual_scores) return []
  
  return Object.entries(props.scorecard.individual_scores).map(([criteria, data]) => ({
    criteria: criteria.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value: data.score || data,
    notes: data.notes || null
  }))
})

// Helper functions
function formatRecommendation(recommendation) {
  const recMap = {
    'strong_hire': 'Strong Hire',
    'hire': 'Hire',
    'maybe': 'Maybe',
    'no_hire': 'No Hire'
  }
  return recMap[recommendation] || recommendation
}

function formatInterviewType(type) {
  const typeMap = {
    'technical_assessment': 'Technical Assessment',
    'technical_interview': 'Technical Interview',
    'behavioral_interview': 'Behavioral Interview',
    'communication_interview': 'Communication Interview'
  }
  return typeMap[type] || type
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function getOverallScoreClass(score) {
  if (score >= 4.5) return 'excellent'
  if (score >= 3.5) return 'good'
  if (score >= 2.5) return 'average'
  return 'poor'
}

function getScoreClass(score) {
  if (score >= 4.5) return 'score-excellent'
  if (score >= 3.5) return 'score-good'
  if (score >= 2.5) return 'score-average'
  return 'score-poor'
}

function printScorecard() {
  window.print()
}
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

.modal-container.scorecard-modal {
  background: white;
  border-radius: 12px;
  max-width: 1000px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.modal-header {
  padding: 20px 25px;
  border-bottom: 2px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  gap: 10px;
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
  padding: 25px;
  overflow-y: auto;
  flex: 1;
}

/* Scorecard Summary */
.scorecard-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 25px;
}

.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  position: relative;
  border: 5px solid transparent;
}

.score-circle.excellent {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  border-color: #27ae60;
}

.score-circle.good {
  background: linear-gradient(135deg, #3498db, #5dade2);
  border-color: #3498db;
}

.score-circle.average {
  background: linear-gradient(135deg, #f39c12, #f4d03f);
  border-color: #f39c12;
}

.score-circle.poor {
  background: linear-gradient(135deg, #e74c3c, #ec7063);
  border-color: #e74c3c;
}

.score-value {
  font-size: 1.8rem;
  line-height: 1;
}

.score-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.recommendation-badge {
  padding: 12px 25px;
  border-radius: 25px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
}

.recommendation-badge.strong_hire {
  background: #c8e6c9;
  color: #2e7d32;
}

.recommendation-badge.hire {
  background: #e8f5e9;
  color: #388e3c;
}

.recommendation-badge.maybe {
  background: #fff3e0;
  color: #f57c00;
}

.recommendation-badge.no_hire {
  background: #ffebee;
  color: #c62828;
}

/* Interview Details */
.interview-details {
  margin-bottom: 25px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  padding: 20px;
  background: white;
  border: 2px solid #ecf0f1;
  border-radius: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-item label {
  font-weight: 600;
  color: #7f8c8d;
  font-size: 0.9rem;
  text-transform: uppercase;
}

.detail-item span {
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 500;
}

/* Scores Section */
.scores-section {
  margin-bottom: 25px;
}

.scores-section h4 {
  color: #2c3e50;
  font-size: 1.2rem;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #3498db;
}

.scores-grid {
  display: grid;
  gap: 20px;
}

.score-item {
  padding: 20px;
  background: white;
  border: 2px solid #ecf0f1;
  border-radius: 12px;
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.criteria-name {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1rem;
}

.score-value {
  font-weight: 700;
  font-size: 1.1rem;
  padding: 4px 12px;
  border-radius: 20px;
}

.score-value.score-excellent {
  background: #c8e6c9;
  color: #2e7d32;
}

.score-value.score-good {
  background: #e3f2fd;
  color: #1976d2;
}

.score-value.score-average {
  background: #fff3e0;
  color: #f57c00;
}

.score-value.score-poor {
  background: #ffebee;
  color: #c62828;
}

.score-bar {
  width: 100%;
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.score-fill {
  height: 100%;
  background: linear-gradient(135deg, #3498db, #2980b9);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.score-notes {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
  font-style: italic;
}

/* Feedback Section */
.feedback-section {
  margin-bottom: 25px;
}

.feedback-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
}

.strengths,
.weaknesses {
  padding: 20px;
  border-radius: 12px;
}

.strengths {
  background: #e8f5e9;
  border-left: 4px solid #4caf50;
}

.weaknesses {
  background: #fff3e0;
  border-left: 4px solid #ff9800;
}

.strengths h4,
.weaknesses h4 {
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
}

.strengths h4 {
  color: #2e7d32;
}

.weaknesses h4 {
  color: #f57c00;
}

.strengths ul,
.weaknesses ul {
  margin: 0;
  padding-left: 20px;
  list-style-type: disc;
}

.strengths li,
.weaknesses li {
  margin-bottom: 8px;
  color: #2c3e50;
  line-height: 1.5;
}

.no-data {
  color: #7f8c8d;
  font-style: italic;
  margin: 0;
}

/* Comments Section */
.comments-section {
  margin-bottom: 25px;
}

.comments-section h4 {
  color: #2c3e50;
  font-size: 1.2rem;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #3498db;
}

.comments-box {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #3498db;
}

.comments-box p {
  margin: 0;
  color: #2c3e50;
  line-height: 1.6;
}

/* Follow-up Section */
.followup-section h4 {
  color: #2c3e50;
  font-size: 1.2rem;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #3498db;
}

.followup-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.followup-list li {
  padding: 10px 15px;
  background: #e3f2fd;
  border-radius: 8px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2c3e50;
}

.followup-list i {
  color: #3498db;
}

/* No Scorecard */
.no-scorecard {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.no-scorecard i {
  font-size: 4rem;
  margin-bottom: 20px;
  display: block;
  color: #bdc3c7;
}

.no-scorecard h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

/* Modal Footer */
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
@media (max-width: 768px) {
  .scorecard-summary {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .feedback-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
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