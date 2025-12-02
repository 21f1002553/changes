import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useRecruitmentStore = defineStore('recruitment', () => {
  // State
  const candidates = ref([
    // Initial candidates for screening
    { id: 1, name: 'Harish sharma', score: 92, metrics: ['5+ YoE(T)', 'Python', 'M.Sc.'], status: 'new', job: 'Robotics Instructor Level1', timeInStage: 2, interviewer: null, interviewResults: {} },
    { id: 2, name: 'Nikhil chabra', score: 75, metrics: ['3 YoE(O)', 'Java', 'B.Sc.'], status: 'new', job: 'Robotics Instructor Level2', timeInStage: 3, interviewer: null, interviewResults: {} },
    { id: 3, name: 'seema aggarwal', score: 48, metrics: ['1 YoE(T)', 'HTML', 'Diploma'], status: 'new', job: 'Robotics instructor Level1', timeInStage: 1, interviewer: null, interviewResults: {} },
    // Candidates already in the pipeline
    { id: 4, name: 'Ananya Gupta', score: 85, metrics: ['2 YoE(O)', 'Salesforce', 'MBA'], status: 'behavioral-interview', job: 'BDA', timeInStage: 4, interviewer: 'Sunita Sharma', interviewResults: { 'behavioral-interview': 'pass' } },
    { id: 5, name: 'Aditya Kumar', score: 82, metrics: ['4 YoE(O)', 'Recruitment', 'MBA-HR'], status: 'communication-interview', job: 'HR', timeInStage: 2, interviewer: null, interviewResults: {} },
    { id: 6, name: 'Isha Verma', score: 80, metrics: ['3 YoE(O)', 'Vue.js', 'B.Tech'], status: 'demo', job: 'Product Developer', timeInStage: 5, interviewer: 'Amit Patel', interviewResults: { 'demo': 'fail' } },
    { id: 7, name: 'Rohan Mehta', score: 78, metrics: ['5+ YoE(T)', 'Management', 'M.Lib'], status: 'hired', job: 'Library teacher', timeInStage: 1, interviewer: null, interviewResults: {} },
    { id: 8, name: 'Priya Singh', score: 91, metrics: ['4 YoE(T)', 'Arduino', 'M.Tech'], status: 'technical-test', job: 'Robotics Instructor Level2', timeInStage: 2, interviewer: null, interviewResults: {} },
    { id: 9, name: 'Karan Malhotra', score: 88, metrics: ['3 YoE(T)', 'EdTech', 'M.A.'], status: 'technical-test', job: 'Academic Coordinator', timeInStage: 1, interviewer: null, interviewResults: {} },
    { id: 10, name: 'Sneha Reddy', score: 90, metrics: ['5 YoE(T)', 'Python', 'M.Sc.'], status: 'technical-interview', job: 'Robotics Instructor Level1', timeInStage: 3, interviewer: 'Rajesh Kumar', interviewResults: {} },
    { id: 11, name: 'Vikram Rathod', score: 86, metrics: ['8+ YoE(O)', 'PMP', 'B.E.'], status: 'technical-interview', job: 'Manager', timeInStage: 4, interviewer: null, interviewResults: {} },
  ]);

  const hos = ref([
    { id: 'HO-001', name: 'Rajesh Kumar', employeeId: 'E1001', designation: 'Regional Head', region: 'North' },
    { id: 'HO-002', name: 'Sunita Sharma', employeeId: 'E1002', designation: 'Regional Manager', region: 'North' },
    { id: 'HO-003', name: 'Amit Patel', employeeId: 'E2001', designation: 'Regional Head', region: 'Middle' },
    { id: 'HO-004', name: 'Priya Verma', employeeId: 'E2002', designation: 'Operations Lead', region: 'Middle' },
    { id: 'HO-005', name: 'Suresh Menon', employeeId: 'E3001', designation: 'Regional Head', region: 'South' },
    { id: 'HO-006', name: 'Deepa Iyer', employeeId: 'E3002', designation: 'Regional Coordinator', region: 'South' },
  ]);

  const pipelineStages = ref([
    { id: 'shortlisted', title: 'Shortlisted' },
    { id: 'technical-test', title: 'Technical Test' },
    { id: 'technical-interview', title: 'Technical Interview' },
    { id: 'behavioral-interview', title: 'Behavioral Interview' },
    { id: 'communication-interview', title: 'Communication Interview' },
    { id: 'demo', title: 'Demo' },
    { id: 'hired', title: 'Offer/Hired' },
  ]);

  // Getters (Computed)
  const newCandidates = computed(() => candidates.value.filter(c => c.status === 'new'));
  const shortlistedCandidates = computed(() => candidates.value.filter(c => c.status === 'shortlisted'));
  const rejectedCandidates = computed(() => candidates.value.filter(c => c.status === 'rejected'));

  const getCandidatesByStage = computed(() => {
    return (stageId) => candidates.value.filter(candidate => candidate.status === stageId);
  });

  // Actions
  function shortlistCandidate(candidateId) {
    const candidate = candidates.value.find(c => c.id === candidateId);
    if (candidate) {
      candidate.status = 'shortlisted';
    }
  }

  function rejectCandidate(candidateId) {
    const candidate = candidates.value.find(c => c.id === candidateId);
    if (candidate) {
      candidate.status = 'rejected';
    }
  }

  function assignInterviewer(candidateId, interviewerName) {
    const candidate = candidates.value.find(c => c.id === candidateId);
    if (candidate) {
      candidate.interviewer = interviewerName;
    }
  }

  function setInterviewResult(candidateId, stageId, result) {
    const candidateIndex = candidates.value.findIndex(c => c.id === candidateId);
    if (candidateIndex !== -1 && (result === 'pass' || result === 'fail')) {
      // Create a deep copy to avoid direct mutation
      const updatedCandidate = JSON.parse(JSON.stringify(candidates.value[candidateIndex]));

      // Ensure the results object exists
      if (!updatedCandidate.interviewResults) {
        updatedCandidate.interviewResults = {};
      }

      // Set the result for the specific stage
      updatedCandidate.interviewResults[stageId] = {
        result: result,
        scorecardData: {
          'Technical Skill': Math.floor(Math.random() * 3) + 3,
          'Problem Solving': Math.floor(Math.random() * 3) + 3,
          'Communication': Math.floor(Math.random() * 3) + 3,
          'Comments': result === 'pass' ? 'Strong candidate, good fit for the role.' : 'Did not meet the technical requirements.',
        }
      };

      // If passed, move to the next stage
      if (result === 'pass') {
        const currentStageIndex = pipelineStages.value.findIndex(stage => stage.id === stageId);
        if (currentStageIndex !== -1 && currentStageIndex < pipelineStages.value.length - 1) {
          const nextStage = pipelineStages.value[currentStageIndex + 1];
          updatedCandidate.status = nextStage.id;
          updatedCandidate.interviewer = null; // Reset interviewer for the new stage
        }
      }

      // Replace the old candidate object with the updated one
      candidates.value[candidateIndex] = updatedCandidate;
    }
  }

  return {
    candidates,
    hos,
    newCandidates,
    pipelineStages,
    shortlistedCandidates,
    rejectedCandidates,
    getCandidatesByStage,
    shortlistCandidate,
    rejectCandidate,
    assignInterviewer,
    setInterviewResult,
  };
});