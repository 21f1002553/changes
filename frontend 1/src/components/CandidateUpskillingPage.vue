<template>
  <DashboardLayout>
    <div class="upskilling-page">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-content">
          <h1>
            <i class="fas fa-graduation-cap"></i>
            Upskilling Path
          </h1>
          <p>Generate a tailored learning path for a selected job using your resume</p>
        </div>
      </div>

      <!-- Job Selection Section -->
      <div class="job-selection-section">
        <div class="form-group">
          <label for="job-select">
            <i class="fas fa-briefcase"></i>
            Select Job Position
          </label>
          <select id="job-select" v-model="selectedJobId" class="job-select">
            <option value="">-- Select a Job Position --</option>
            <option v-for="job in jobs" :key="job.id" :value="job.id">
              {{ job.title }} - {{ job.location || 'Remote' }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="resume-select">
            <i class="fas fa-file-alt"></i>
            Select Resume
          </label>
          <select id="resume-select" v-model="selectedResumeId" class="job-select">
            <option value="">-- Choose a resume --</option>
            <option v-for="r in resumes" :key="r.id" :value="r.id">{{ r.filename || r.id }}</option>
          </select>
          <p class="hint" v-if="resumes.length === 0">
            <i class="fas fa-info-circle"></i>
            No resumes found. Upload one in your profile to use this feature.
          </p>
        </div>

        <div class="form-actions">
          <button class="btn-primary" :disabled="generating || !selectedJobId || !selectedResumeId"
            @click="generatePath">
            <i class="fas" :class="generating ? 'fa-spinner fa-spin' : 'fa-magic'"></i>
            {{ generating ? 'Generating...' : 'Generate Upskilling Path' }}
          </button>
        </div>

        <div v-if="error" class="error-message">
          <i class="fas fa-exclamation-circle"></i>
          {{ error }}
        </div>
        <div v-if="info" class="info-message">
          <i class="fas fa-info-circle"></i>
          {{ info }}
        </div>
      </div>

      <!-- Results Section -->
      <div v-if="selectedJobId && selectedResumeId" class="results-section">
        <!-- Loading State -->
        <div v-if="generating" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Generating upskilling path — this may take a moment...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="!generating && (!upskillingPath || upskillingPath.length === 0)" class="empty-state">
          <i class="fas fa-inbox"></i>
          <h3>No Course Recommendations</h3>
          <p>Click "Generate Upskilling Path" to see recommended courses for the selected job.</p>
        </div>

        <!-- Results Table -->
        <div v-else class="table-container">
          <div class="section-header">
            <h3>
              <i class="fas fa-list"></i>
              Recommended Courses
            </h3>
            <div class="filter-stats">
              <span class="stat-badge total">Total: {{ upskillingPath.length }}</span>
            </div>
          </div>

          <!-- Missing Skills Tags -->
          <div v-if="missingSkills && missingSkills.length" class="missing-skills-section">
            <h4>
              <i class="fas fa-exclamation-triangle"></i>
              Skills Gap Analysis
            </h4>
            <div class="metrics-tags">
              <span class="metric-tag" v-for="(s, i) in missingSkills" :key="i">{{ s }}</span>
            </div>
          </div>

          <table class="candidates-table">
            <thead>
              <tr>
                <th>Step</th>
                <th>Course Title</th>
                <th>Estimated Time</th>
                <th>Reason</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="course in upskillingPath" :key="course.course_id">
                <td>
                  <div class="step-badge">
                    {{ course.step }}
                  </div>
                </td>
                <td>
                  <div class="course-info">
                    <span class="course-title">{{ course.course_title }}</span>
                  </div>
                </td>
                <td>
                  <div class="duration">
                    <i class="fas fa-clock"></i>
                    {{ course.estimated_time || 'N/A' }}
                  </div>
                </td>
                <td>
                  <div class="reason-text">{{ course.reason }}</div>
                </td>
                <td>
                  <div class="action-buttons">
                    <a v-if="course.content_url || course.contentUrl" :href="course.content_url || course.contentUrl"
                      target="_blank" class="btn-view-course">
                      <i class="fas fa-external-link-alt"></i>
                      View Course
                    </a>
                    <button v-else @click="$router.push('/candidate/courses')"
                      class="btn-action btn-primary full-width">
                      <i class="fas fa-play"></i>
                      Enroll Now
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- No Selection State -->
      <div v-else class="no-job-selected">
        <i class="fas fa-search"></i>
        <h3>Select Job and Resume</h3>
        <p>Choose a job position and your resume from the dropdowns above to generate your personalized upskilling path
        </p>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'

const jobs = ref([])
const resumes = ref([])
const selectedJobId = ref('')
const selectedResumeId = ref('')
const upskillingPath = ref([])
const missingSkills = ref([])
const generating = ref(false)
const error = ref('')
const info = ref('')

const getAuthToken = () => localStorage.getItem('access_token')

const loadJobs = async () => {
  try {
    const resp = await axios.get('/api/jobs/', { headers: { Authorization: `Bearer ${getAuthToken()}` } })
    jobs.value = Array.isArray(resp.data) ? resp.data : (resp.data.data || [])
  } catch (err) {
    console.error('Failed to load jobs', err)
    error.value = 'Failed to load jobs.'
  }
}

const loadResumes = async () => {
  try {
    const resp = await axios.get('/api/files/resume', { headers: { Authorization: `Bearer ${getAuthToken()}` } })
    console.log('Loading resumes')
    console.log('Resumes response:', resp.data)

    const data = resp.data
    if (Array.isArray(data)) {
      resumes.value = data
    } else if (data && Array.isArray(data.data)) {
      resumes.value = data.data
    } else if (data && Array.isArray(data.files)) {
      resumes.value = data.files
    } else if (data && (data.id || data.file_id)) {
      resumes.value = [data]
    } else {
      resumes.value = []
    }
    console.log('Parsed resumes count:', resumes.value.length)
  } catch (err) {
    console.error('Failed to load resumes', err)
    resumes.value = []
    error.value = 'Failed to load resumes.'
  }
}

const generatePath = async () => {
  error.value = ''
  info.value = ''
  upskillingPath.value = []

  if (!selectedJobId.value) { error.value = 'Please select a job.'; return }
  if (!selectedResumeId.value) { error.value = 'Please select a resume.'; return }

  const job = jobs.value.find(j => j.id === selectedJobId.value)
  if (!job) { error.value = 'Selected job not found.'; return }

  generating.value = true
  try {
    const payload = {
      job_title: job.title,
      job_description: job.description || ''
    }

    const maxAttempts = 3
    let attempt = 0
    let resp = null
    while (attempt < maxAttempts) {
      try {
        resp = await axios.post(`/api/ai/get_upskilling_path/${selectedResumeId.value}`, payload, {
          headers: { Authorization: `Bearer ${getAuthToken()}` }
        })
        console.log(resp.data)
        break
      } catch (e) {
        const status = e.response?.status
        if (status === 429 && attempt < maxAttempts - 1) {
          const waitMs = 1000 * Math.pow(2, attempt)
          console.warn(`Upskilling API rate limited (429). Retry #${attempt + 1} after ${waitMs}ms`)
          await new Promise(r => setTimeout(r, waitMs))
          attempt += 1
          continue
        }
        throw e
      }
    }

    if (resp && resp.data && resp.data.upskilling_path) {
      const payloadPath = resp.data.upskilling_path
      if (Array.isArray(payloadPath.course_upskilling_path)) {
        upskillingPath.value = payloadPath.course_upskilling_path
      } else if (Array.isArray(payloadPath)) {
        upskillingPath.value = payloadPath
      } else {
        upskillingPath.value = []
      }
      missingSkills.value = Array.isArray(payloadPath.missing_skill) ? payloadPath.missing_skill : []

      if (!upskillingPath.value || upskillingPath.value.length === 0) {
        info.value = 'No course recommendations generated for this resume/job.'
      }
    } else if (resp && resp.data) {
      error.value = resp.data?.error || 'Failed to generate upskilling path.'
    } else {
      error.value = 'Failed to generate upskilling path.'
    }
  } catch (err) {
    console.error('Error generating upskilling path', err)
    const remoteErr = err.response?.data?.error || err.message
    if (err.response?.status === 429) {
      error.value = `${remoteErr} — service is rate limited. Try again in a few seconds.`
    } else {
      error.value = remoteErr || 'Error generating upskilling path.'
    }
  } finally {
    generating.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadJobs(), loadResumes()])
})
</script>

<style scoped>
.upskilling-page {
  padding: 0;
  max-width: 100%;
}

/* Page Header */
.page-header {
  margin-bottom: 30px;
}

.header-content h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-content p {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

/* Job Selection Section */
.job-selection-section {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 1rem;
}

.job-select {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  color: #2c3e50;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.job-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.hint {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.form-actions {
  margin-top: 25px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  opacity: 0.6;
}

.error-message,
.info-message {
  margin-top: 15px;
  padding: 12px 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  border-left: 4px solid #c62828;
}

.info-message {
  background: #e3f2fd;
  color: #1976d2;
  border-left: 4px solid #1976d2;
}

/* Results Section */
.results-section {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

/* Section Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #ecf0f1;
}

.section-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-stats {
  display: flex;
  gap: 10px;
}

.stat-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.stat-badge.total {
  background: #3498db;
  color: white;
}

/* Missing Skills Section */
.missing-skills-section {
  background: #fff3e0;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 25px;
  border-left: 4px solid #f39c12;
}

.missing-skills-section h4 {
  color: #e67e22;
  font-size: 1.1rem;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.metrics-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.metric-tag {
  background: #f39c12;
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

/* Loading and Empty States */
.loading-state,
.empty-state,
.no-job-selected {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.loading-state i,
.empty-state i,
.no-job-selected i {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
  color: #bdc3c7;
}

.empty-state h3,
.no-job-selected h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.empty-state p,
.no-job-selected p {
  font-size: 1rem;
  line-height: 1.6;
}

/* Table */
.table-container {
  overflow-x: auto;
}

.candidates-table {
  width: 100%;
  border-collapse: collapse;
}

.candidates-table thead {
  background: #f8f9fa;
}

.candidates-table th {
  padding: 15px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #ecf0f1;
  white-space: nowrap;
}

.candidates-table td {
  padding: 15px;
  border-bottom: 1px solid #ecf0f1;
  vertical-align: middle;
}

.candidates-table tbody tr:hover {
  background: #f8f9fa;
}

/* Step Badge */
.step-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
}

/* Course Info */
.course-info {
  display: flex;
  flex-direction: column;
}

.course-title {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1rem;
  line-height: 1.4;
}

/* Duration */
.duration {
  color: #7f8c8d;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Reason Text */
.reason-text {
  color: #2c3e50;
  line-height: 1.6;
  font-size: 0.95rem;
  max-width: 400px;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.full-width {
  width: 100%;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-view-course {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-view-course:hover {
  background: #2980b9;
  transform: translateY(-1px);
}

.btn-action-disabled {
  background: #bdc3c7;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: not-allowed;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  opacity: 0.6;
}

/* Responsive */
@media (max-width: 1200px) {
  .candidates-table {
    font-size: 0.85rem;
  }

  .metric-tag {
    font-size: 0.75rem;
    padding: 5px 12px;
  }
}

@media (max-width: 768px) {
  .header-content h1 {
    font-size: 2rem;
  }

  .candidates-table {
    font-size: 0.9rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .filter-stats {
    width: 100%;
    justify-content: space-between;
  }

  .step-badge {
    width: 35px;
    height: 35px;
    font-size: 0.9rem;
  }
}
</style>