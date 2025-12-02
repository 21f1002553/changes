<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="close-btn" @click="$emit('close')">&times;</button>
      <h3>Interview Scorecard</h3>
      <div class="candidate-info">
        <h4>{{ candidate.name }}</h4>
        <p>{{ candidate.job }}</p>
      </div>
      <div class="scorecard-details">
        <div class="detail-item">
          <strong>Stage:</strong>
          <span>{{ stage.title }}</span>
        </div>
        <div class="detail-item">
          <strong>Interviewer:</strong>
          <span>{{ candidate.interviewer || 'N/A' }}</span>
        </div>
        <div class="detail-item">
          <strong>Result:</strong>
          <span :class="['result-badge', result.result]">{{ result.result }}</span>
        </div>
      </div>
      <div class="scores-section">
        <h4>Scores</h4>
        <ul>
          <li v-for="(score, key) in result.scorecardData" :key="key">
            <template v-if="typeof score === 'number'">
              <strong>{{ key }}:</strong>
              <span class="score-value">{{ score }} / 5</span>
            </template>
          </li>
        </ul>
        <div class="comments">
          <strong>Comments:</strong>
          <p>{{ result.scorecardData.Comments }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  candidate: Object,
  stage: Object,
  result: Object,
});
defineEmits(['close']);
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background-color: #fff;
  padding: 30px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  position: relative;
}
.close-btn {
  position: absolute;
  top: 10px;
  right: 15px;
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #aaa;
}
h3 { margin-bottom: 20px; }
.candidate-info { margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px; }
.scorecard-details { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
.detail-item { display: flex; justify-content: space-between; }
.result-badge { padding: 3px 8px; border-radius: 12px; text-transform: capitalize; }
.result-badge.pass { background-color: #d4edda; color: #155724; }
.result-badge.fail { background-color: #f8d7da; color: #721c24; }
.scores-section ul { list-style: none; padding: 0; margin-bottom: 15px; }
.scores-section li { display: flex; justify-content: space-between; padding: 8px 0; }
.score-value { font-weight: 700; }
.comments p {
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 5px;
  margin-top: 5px;
  font-style: italic;
}
</style>