<template>
  <div class="hiring-pipeline-board">
    <ScorecardModal v-if="viewingScorecard" :candidate="viewingScorecard.candidate" :stage="viewingScorecard.stage" :result="viewingScorecard.result" @close="viewingScorecard = null" />
    <div v-for="stage in pipelineStages" :key="stage.id" class="pipeline-stage">
      <div class="stage-header-flex"> 

        <h3>{{ stage.title }} <span class="candidate-count">{{ store.getCandidatesByStage(stage.id).length }}</span></h3>
        <a v-if="stage.id === 'technical-test'" href="#" class="action-btn generate-test-btn">AI: Generate Test</a>
      </div>
      <div class="candidate-cards">
        <div v-for="candidate in store.getCandidatesByStage(stage.id)" :key="candidate.id" class="candidate-card">
          <h4>{{ candidate.name }}</h4>
          <p>{{ candidate.job }}</p>
          <div class="match-score">
            <span>Match Score:</span>
            <span class="score">{{ candidate.score }}%</span>
          </div>
          <div class="time-in-stage">
            <span>In stage for:</span>
            <span>{{ candidate.timeInStage }} days</span>
          </div>
          <div class="card-actions">
            <!-- Left Side: Interviewer Info -->
            <div v-if="candidate.interviewer" class="interviewer-badge">
              <i class="fas fa-user-tie"></i>
              <span>{{ candidate.interviewer }}</span>
            </div>
            <div v-else class="assign-interviewer-wrapper">
              <button @click="toggleAssigner(candidate.id)" class="action-btn assign-interviewer">Assign Interviewer</button>
              <div v-if="assigningToCandidateId === candidate.id" class="interviewer-list">
                <div class="list-header">Select Interviewer</div>
                <ul>
                  <li v-for="ho in store.hos" :key="ho.id" @click="selectInterviewer(candidate.id, ho.name)">
                    {{ ho.name }} <span class="ho-designation">{{ ho.designation }}</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Right Side: Action Buttons -->
            <div class="right-actions">
              <div v-if="isInterviewStage(stage.id) && candidate.interviewer" class="interview-result-actions">
                <div v-if="candidate.interviewResults && candidate.interviewResults[stage.id] && candidate.interviewResults[stage.id].result === 'fail'" class="result-badge fail">
                  Failed
                </div>
                <div v-else class="pass-fail-buttons">
                  <button @click="store.setInterviewResult(candidate.id, stage.id, 'pass')" class="action-btn icon-btn pass" title="Mark as Pass">P</button>
                  <button @click="store.setInterviewResult(candidate.id, stage.id, 'fail')" class="action-btn icon-btn fail" title="Mark as Fail">F</button>
                </div>
              </div>
              <button @click="viewScorecardForStage(candidate, stage)" :disabled="!isScorecardAvailable(candidate, stage)" class="action-btn view-scorecard">View Scorecard</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useRecruitmentStore } from '@/stores/recruitment';
import ScorecardModal from './ScorecardModal.vue';

const store = useRecruitmentStore();
const { pipelineStages } = storeToRefs(store);
const assigningToCandidateId = ref(null);
const viewingScorecard = ref(null);

const toggleAssigner = (candidateId) => {
  if (assigningToCandidateId.value === candidateId) {
    assigningToCandidateId.value = null; // Close if already open
  } else {
    assigningToCandidateId.value = candidateId; // Open for this candidate
  }
};

const selectInterviewer = (candidateId, interviewerName) => {
  store.assignInterviewer(candidateId, interviewerName);
  assigningToCandidateId.value = null; // Close the dropdown
};

const isInterviewStage = (stageId) => {
  const interviewStages = ['technical-test', 'technical-interview', 'behavioral-interview', 'communication-interview', 'demo'];
  return interviewStages.includes(stageId);
};

const isScorecardAvailable = (candidate, stage) => {
  return candidate.interviewResults && candidate.interviewResults[stage.id];
};

const viewScorecardForStage = (candidate, stage) => {
  if (isScorecardAvailable(candidate, stage)) {
    viewingScorecard.value = {
      candidate,
      stage,
      result: candidate.interviewResults[stage.id]
    };
  }
};
</script>

<style scoped>
.hiring-pipeline-board {
  display: flex;
  overflow-x: auto;
  padding: 25px;
  background-color: #f8f9fd; /* Softer background */
  min-height: 100vh;
  gap: 20px; /* Space between columns */
}

.pipeline-stage {
  flex: 1;
  min-width: 300px;
  max-width: 320px;
  padding: 15px;
  background-color: #ffffff; /* White columns */
  border-radius: 8px;
  border: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  height: fit-content;
}

.pipeline-stage h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #343a40;
  display: flex;
  align-items: center;
  gap: 8px;
}
.stage-header-flex {
    /* 1. Set the display mode */
    display: flex;
    
    /* 2. Push elements to opposite ends */
    justify-content: space-between;
    
    /* 3. Align them vertically in the middle */
    align-items: center;
    
    /* Optional: Remove default margin from the title */
    margin-bottom: 10px; /* Space before candidate cards */
}

.stage-header-flex h3 {
    /* Reset default browser margins for better alignment */
    margin: 0; 
}

.candidate-cards {
  display: flex;
  flex-direction: column;
  gap: 15px; /* Space between cards */
}

.candidate-count {
  font-size: 0.85rem;
  font-weight: 700;
  background-color: #e9ecef;
  color: #6c757d;
  padding: 3px 8px;
  border-radius: 20px;
}

.candidate-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.candidate-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.candidate-card h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 5px;
}

.candidate-card p {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 10px;
}

.match-score {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
  font-size: 0.9rem;
}

.match-score .score {
  font-weight: 600;
  color: #28a745;
}

.time-in-stage {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: #888;
  margin-bottom: 15px;
}

.card-actions {
  display: flex;
  justify-content: space-between; /* Align buttons */
  align-items: center;
  gap: 10px; /* Added space between buttons */
}

.action-btn {
  padding: 8px 12px;
  border: none;
  border-radius: 5px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
  text-decoration: none;
  text-align: center;

}

.assign-interviewer-wrapper {
  position: relative;
  /* flex-grow: 1; Allow wrapper to take space */
}

.assign-interviewer {
  background-color: #5e72e4; /* A more modern blue */
  color: #fff;
}

.assign-interviewer:hover {
  background-color: #475bd9;
}

.interviewer-list {
  position: absolute;
  bottom: 100%; /* Position above the button */
  left: 0;
  width: 100%;
  background-color: #fff;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.15);
  z-index: 10;
  margin-bottom: 8px;
  overflow: hidden;
}

.interviewer-list .list-header {
  padding: 10px 12px;
  font-weight: 600;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  font-size: 0.9rem;
}

.interviewer-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 150px;
  overflow-y: auto;
}

.interviewer-list li {
  padding: 10px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 0.85rem;
  display: flex;
  justify-content: space-between;
}

.interviewer-list li:hover {
  background-color: #f1f3f5;
}

.ho-designation {
  color: #868e96;
  font-style: italic;
}

.view-scorecard {
  background-color: transparent;
  color: #525f7f;
  border: 1px solid #dee2e6;
}

.view-scorecard:hover {
  background-color: #f8f9fa;
  border-color: #ced4da;
}

.view-scorecard:disabled {
  background-color: #f8f9fa;
  color: #adb5bd;
  cursor: not-allowed;
}

.generate-test-btn {
  background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
  color: #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.generate-test-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.interviewer-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #e9ecef;
  color: #495057;
  padding: 8px 12px;
  border-radius: 5px;
  font-size: 0.8rem;
  font-weight: 600;
  /* flex-grow: 1; */
  justify-content: flex-start;
}

.right-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.interview-result-actions {
  display: flex;
  align-items: center;
}

.pass-fail-buttons {
  display: flex;
  gap: 6px;
}

.action-btn.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.9rem;
}

.action-btn.pass { background-color: #eaf6ec; color: #28a745; }
.action-btn.pass:hover { background-color: #d4edda; }
.action-btn.fail { background-color: #fceeee; color: #dc3545; }
.action-btn.fail:hover { background-color: #f8d7da; }

.result-badge {
  text-align: center;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.75rem;
}
.result-badge.fail { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
</style>
