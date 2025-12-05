<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-container resume-modal" @click.stop>
      <div class="modal-header">
        <h3>
          <i class="fas fa-file-alt"></i>
          Resume - {{ candidate?.name }}
        </h3>
        <button @click="$emit('close')" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <div v-if="loadingResume" class="loading-resume">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading resume...</p>
        </div>
        
        <div v-else-if="resumeData" class="resume-content">
          <!-- Personal Information -->
          <div class="resume-section">
            <h4>Personal Information</h4>
            <div class="resume-info-grid">
              <div class="info-item">
                <strong>Name:</strong>
                <span>{{ resumeData.name || candidate?.name }}</span>
              </div>
              <div class="info-item">
                <strong>Email:</strong>
                <span>{{ resumeData.email || candidate?.email }}</span>
              </div>
              <div class="info-item">
                <strong>Phone:</strong>
                <span>{{ resumeData.phone || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <strong>Location:</strong>
                <span>{{ resumeData.location || 'N/A' }}</span>
              </div>
            </div>
          </div>

          <!-- Skills -->
          <div v-if="resumeData.skills && resumeData.skills.length > 0" class="resume-section">
            <h4>Skills</h4>
            <div class="skills-tags">
              <span v-for="skill in resumeData.skills" :key="skill" class="skill-tag">
                {{ skill }}
              </span>
            </div>
          </div>

          <!-- Experience -->
          <div v-if="resumeData.experience && resumeData.experience.length > 0" class="resume-section">
            <h4>Work Experience</h4>
            <div v-for="(exp, index) in resumeData.experience" :key="index" class="experience-item">
              <h5>{{ exp.title || exp.position }}</h5>
              <p class="company">{{ exp.company }}</p>
              <p class="duration">{{ exp.duration || exp.period }}</p>
              <p class="description">{{ exp.description }}</p>
            </div>
          </div>

          <!-- Education -->
          <div v-if="resumeData.education && resumeData.education.length > 0" class="resume-section">
            <h4>Education</h4>
            <div v-for="(edu, index) in resumeData.education" :key="index" class="education-item">
              <h5>{{ edu.degree }}</h5>
              <p class="institution">{{ edu.institution }}</p>
              <p class="duration">{{ edu.year || edu.period }}</p>
            </div>
          </div>

          <!-- Summary -->
          <div v-if="resumeData.summary" class="resume-section">
            <h4>Summary</h4>
            <p>{{ resumeData.summary }}</p>
          </div>
        </div>
        
        <div v-else class="resume-error">
          <i class="fas fa-exclamation-circle"></i>
          <p>Unable to load resume details</p>
        </div>
      </div>
      
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn-secondary">Close</button>
        <button @click="downloadResume" class="btn-primary">
          <i class="fas fa-download"></i>
          Download Resume
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  candidate: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

// State
const loadingResume = ref(false)
const resumeData = ref(null)

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

// Load resume data
async function loadResumeData() {
  if (!props.candidate?.resume_id) return

  try {
    loadingResume.value = true
    
    const response = await axios.get(`/api/screening/resumes/${props.candidate.resume_id}`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })

    if (response.data) {
      const resume = response.data
      
      if (resume.parsed_data) {
        resumeData.value = typeof resume.parsed_data === 'string' 
          ? JSON.parse(resume.parsed_data) 
          : resume.parsed_data
      } else {
        resumeData.value = {
          name: props.candidate.name,
          email: props.candidate.email,
          skills: [],
          experience: [],
          education: [],
          summary: 'Resume data not parsed yet'
        }
      }
    }
  } catch (error) {
    console.error('❌ Failed to load resume:', error)
    resumeData.value = null
  } finally {
    loadingResume.value = false
  }
}

// Download resume
async function downloadResume() {
  if (!props.candidate?.resume_id) return

  try {
    const response = await axios.get(`/api/files/${props.candidate.resume_id}/download`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` },
      responseType: 'blob'
    })

    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    const candidateName = props.candidate.name.replace(/\s+/g, '_')
    link.setAttribute('download', `Resume_${candidateName}.pdf`)
    
    document.body.appendChild(link)
    link.click()
    
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('❌ Failed to download resume:', error)
    alert('Failed to download resume')
  }
}

// Load data on mount
onMounted(() => {
  loadResumeData()
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

.modal-container.resume-modal {
  background: white;
  border-radius: 12px;
  max-width: 900px;
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
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #7f8c8d;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #ecf0f1;
  color: #2c3e50;
}

.modal-body {
  padding: 25px;
  overflow-y: auto;
  flex: 1;
}

.loading-resume,
.resume-error {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.loading-resume i {
  font-size: 2rem;
  margin-bottom: 10px;
  display: block;
}

.resume-content {
  max-width: 800px;
  margin: 0 auto;
}

.resume-section {
  margin-bottom: 30px;
}

.resume-section h4 {
  color: #2c3e50;
  font-size: 1.2rem;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #3498db;
}

.resume-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-item strong {
  color: #7f8c8d;
  font-size: 0.85rem;
  text-transform: uppercase;
}

.info-item span {
  color: #2c3e50;
  font-size: 1rem;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.skill-tag {
  background: #3498db;
  color: white;
  padding: 8px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.experience-item,
.education-item {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 15px;
  border-left: 4px solid #3498db;
}

.experience-item h5,
.education-item h5 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.company,
.institution {
  color: #7f8c8d;
  font-weight: 600;
  margin: 0 0 5px 0;
}

.duration {
  color: #95a5a6;
  font-size: 0.9rem;
  margin: 0 0 10px 0;
}

.description {
  color: #2c3e50;
  line-height: 1.6;
  margin: 0;
}

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
</style>