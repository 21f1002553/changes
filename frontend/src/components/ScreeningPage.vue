<template>
  <div class="screening-container">
    <div class="screening-content">
      <!-- Input Section -->
      <div class="input-section">
        <div class="form-group">
          <label for="job-vacancy">Select Job Vacancy</label>
          <select id="job-vacancy">
            <option value="">-- Select Job --</option>
            <option value="robotics-instructor-level-one">Robotics Instructor Level 1</option>
            <option value="robotics-instructor-level-two">Robotics Instructor Level 2</option>
            <option value="academic-coordinator">Academic Coordinator</option>
            <option value="manager">Manager</option>
            <option value="bda">BDA</option>
            <option value="library-teacher">Library Teacher</option>
          </select>
        </div>
        <div class="resume-sourcing">
          <div class="drag-drop-area">
            <p>Drag & Drop Resumes Here</p>
            <span>or</span>
            <label for="file-upload" class="file-upload-label">Browse Files</label>
            <input type="file" id="file-upload" multiple />
          </div>
          <button class="import-db-btn">Import from Database</button>
        </div>
      </div>

      <!-- Analysis Section -->
      <div class="analysis-section">
        <h3>Screening & Score Checker</h3>
        <div class="filters">
          <button @click="setActiveFilter('new')" :class="{ active: activeFilter === 'new' }" class="filter-btn">New</button>
          <button @click="setActiveFilter('shortlisted')" :class="{ active: activeFilter === 'shortlisted' }" class="filter-btn">Shortlisted</button>
          <button @click="setActiveFilter('rejected')" :class="{ active: activeFilter === 'rejected' }" class="filter-btn">Rejected</button>
        </div>
        <table class="resume-table">
          <thead>
            <tr>
              <th>Candidate Name</th>
              <th>Match Score</th>
              <th>Key Metrics</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody v-if="filteredCandidates.length > 0">
            <tr v-for="candidate in filteredCandidates" :key="candidate.id">
              <td>{{ candidate.name }}</td>
              <td><span :class="getScoreClass(candidate.score)">{{ candidate.score }}%</span></td>
              <td>
                <span v-for="metric in candidate.metrics" :key="metric" class="metric-tag">{{ metric }}</span>
              </td>
              <td v-if="activeFilter === 'new'">
                <button @click="shortlistCandidate(candidate.id)" class="action-btn shortlist">Shortlist</button>
                <button @click="rejectCandidate(candidate.id)" class="action-btn reject">Reject</button>
                <button class="action-btn hold">Hold</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRecruitmentStore } from '@/stores/recruitment';

const store = useRecruitmentStore();

const activeFilter = ref('new');

const filteredCandidates = computed(() => {
  switch (activeFilter.value) {
    case 'shortlisted':
      return store.shortlistedCandidates;
    case 'rejected':
      return store.rejectedCandidates;
    default:
      return store.newCandidates;
  }
});

const setActiveFilter = (filter) => {
  activeFilter.value = filter;
};

const shortlistCandidate = (candidateId) => {
  store.shortlistCandidate(candidateId);
};

const rejectCandidate = (candidateId) => {
  store.rejectCandidate(candidateId);
};

const getScoreClass = (score) => {
  if (score >= 90) {
    return 'score-green';
  } else if (score >= 60) {
    return 'score-yellow';
  } else {
    return 'score-red';
  }
};
</script>

<style scoped>
.screening-container {
  padding: 20px;
  background-color: #f8f9fa;
}

.screening-content {
  background-color: #ffffff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid #bdc3c7;
  border-radius: 5px;
}

.resume-sourcing {
  display: flex;
  gap: 20px;
  align-items: center;
}

.drag-drop-area {
  flex-grow: 1;
  border: 2px dashed #bdc3c7;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  color: #7f8c8d;
}

.file-upload-label {
  cursor: pointer;
  color: #3498db;
  font-weight: 600;
}

input[type="file"] {
  display: none;
}

.import-db-btn {
  padding: 12px 20px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.analysis-section h3 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.filters {
  margin-bottom: 20px;
}

.filter-btn {
  margin-right: 10px;
  padding: 8px 15px;
  border: 1px solid #bdc3c7;
  background-color: transparent;
  border-radius: 5px;
  cursor: pointer;
}

.filter-btn.active {
  background-color: #3498db;
  color: white;
  border-color: #3498db;
}

.resume-table {
  width: 100%;
  border-collapse: collapse;
}

.resume-table th, .resume-table td {
  padding: 15px;
  border-bottom: 1px solid #ecf0f1;
  text-align: left;
}

.score-green { color: #27ae60; font-weight: 700; }
.score-yellow { color: #f39c12; font-weight: 700; }
.score-red { color: #e74c3c; font-weight: 700; }

.metric-tag {
  background-color: #ecf0f1;
  color: #7f8c8d;
  padding: 5px 8px;
  border-radius: 3px;
  margin-right: 5px;
  font-size: 0.8rem;
}

.action-btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  margin-right: 5px;
  color: white;
}

.shortlist { background-color: #27ae60; }
.reject { background-color: #e74c3c; }
.hold { background-color: #f39c12; }
</style>
