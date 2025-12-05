<template>
  <DashboardLayout>
    <div class="course-page">
      <!-- Header Section -->
      <div class="page-header">
        <h1><i class="fas fa-graduation-cap"></i> Training Courses</h1>
        <p>Enhance your skills with our comprehensive training modules</p>
      </div>

      <!-- Stats Overview -->
      <div class="stats-overview">
        <div class="stat-card">
          <i class="fas fa-book-open"></i>
          <div class="stat-info">
            <h3>{{ availableCourses.length }}</h3>
            <p>Available Courses</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-user-graduate"></i>
          <div class="stat-info">
            <h3>{{ enrolledCourses.length }}</h3>
            <p>Enrolled Courses</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-trophy"></i>
          <div class="stat-info">
            <h3>{{ completedCoursesCount }}</h3>
            <p>Completed</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-clock"></i>
          <div class="stat-info">
            <h3>{{ totalLearningHours }}h</h3>
            <p>Learning Hours</p>
          </div>
        </div>
      </div>

      <!-- Course Sections -->
      <div class="course-sections">
        <!-- Enrolled Courses Section -->
        <div class="course-section" v-if="enrolledCourses.length > 0">
          <div class="section-header">
            <h2><i class="fas fa-user-graduate"></i> My Enrolled Courses</h2>
            <span class="course-count">{{ enrolledCourses.length }} courses</span>
          </div>
          
          <div class="course-grid">
            <div 
              v-for="enrollment in enrolledCourses" 
              :key="`enrolled-${enrollment.course_id}`"
              class="course-card enrolled-card"
            >
              <div class="course-header">
                <div class="course-title">
                  <h3>{{ enrollment.course.title }}</h3>
                  <span class="training-badge" v-if="enrollment.course.training_title">
                    {{ enrollment.course.training_title }}
                  </span>
                </div>
                <div class="course-status" :class="enrollment.status">
                  {{ enrollment.status }}
                </div>
              </div>
              
              <div class="course-content">
                <div class="course-info">
                  <p><i class="fas fa-clock"></i> {{ enrollment.course.duration_mins }} minutes</p>
                  <p><i class="fas fa-calendar-alt"></i> Enrolled {{ formatDate(enrollment.enrolled_at) }}</p>
                </div>
                
                <!-- Progress Bar -->
                <div class="progress-section">
                  <div class="progress-header">
                    <span>Progress</span>
                    <span class="progress-text">{{ Math.round(enrollment.progress) }}%</span>
                  </div>
                  <div class="progress-bar">
                    <div 
                      class="progress-fill" 
                      :style="{ width: enrollment.progress + '%' }"
                      :class="{ 'completed': enrollment.progress >= 100 }"
                    ></div>
                  </div>
                </div>
              </div>
              
              <div class="course-actions">
                <button 
                  @click="openCourse(enrollment.course)"
                  class="btn-primary"
                  :disabled="loading"
                >
                  <i class="fas fa-play"></i> 
                  {{ enrollment.progress >= 100 ? 'Review' : 'Continue' }}
                </button>
                
                <button 
                  v-if="enrollment.progress < 100"
                  @click="updateProgress(enrollment.course.id, 100)"
                  class="btn-success"
                  :disabled="loading"
                >
                  <i class="fas fa-check"></i> Mark Complete
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Available Courses Section -->
        <div class="course-section">
          <div class="section-header">
            <h2><i class="fas fa-book"></i> Available Courses</h2>
            <div class="section-actions">
              <div class="search-box">
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Search courses..."
                  class="search-input"
                >
                <i class="fas fa-search"></i>
              </div>
              <select v-model="trainingFilter" class="filter-select">
                <option value="">All Categories</option>
                <option v-for="training in trainingCategories" :key="training.id" :value="training.id">
                  {{ training.title }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="course-grid" v-if="filteredAvailableCourses.length > 0">
            <div 
              v-for="course in filteredAvailableCourses" 
              :key="`available-${course.id}`"
              class="course-card"
            >
              <div class="course-header">
                <div class="course-title">
                  <h3>{{ course.title }}</h3>
                  <span class="training-badge" v-if="course.training_title">
                    {{ course.training_title }}
                  </span>
                </div>
                <div class="course-difficulty">
                  <i class="fas fa-signal"></i>
                  <span>Beginner</span>
                </div>
              </div>
              
              <div class="course-content">
                <div class="course-info">
                  <p><i class="fas fa-clock"></i> {{ course.duration_mins }} minutes</p>
                  <p><i class="fas fa-users"></i> {{ getEnrollmentCount(course.id) }} enrolled</p>
                  <p><i class="fas fa-star"></i> 4.5 rating</p>
                </div>
              </div>
              
              <div class="course-actions">
                <button 
                  @click="showEnrollmentModal(course)"
                  class="btn-primary full-width"
                  :disabled="loading"
                >
                  <i class="fas fa-plus"></i> Enroll Now
                </button>
              </div>
            </div>
          </div>
          
          <div v-else class="no-courses">
            <i class="fas fa-search"></i>
            <h3>No courses found</h3>
            <p>Try adjusting your search or filter criteria</p>
          </div>
        </div>
      </div>

      <!-- Enrollment Modal -->
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3><i class="fas fa-graduation-cap"></i> Enroll in Course</h3>
            <button @click="closeModal" class="close-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="modal-body" v-if="selectedCourse">
            <div class="course-preview">
              <h4>{{ selectedCourse.title }}</h4>
              <p class="training-category" v-if="selectedCourse.training_title">
                <i class="fas fa-tag"></i> {{ selectedCourse.training_title }}
              </p>
              
              <div class="course-details">
                <div class="detail-item">
                  <i class="fas fa-clock"></i>
                  <span><strong>Duration:</strong> {{ selectedCourse.duration_mins }} minutes</span>
                </div>
                <div class="detail-item" v-if="selectedCourse.content_url">
                  <i class="fas fa-link"></i>
                  <span><strong>Content Type:</strong> Online Module</span>
                </div>
                <div class="detail-item">
                  <i class="fas fa-certificate"></i>
                  <span><strong>Certificate:</strong> Yes, upon completion</span>
                </div>
              </div>
              
              <div class="enrollment-benefits">
                <h5><i class="fas fa-check-circle"></i> What you'll gain:</h5>
                <ul>
                  <li>Professional certificate of completion</li>
                  <li>Progress tracking and analytics</li>
                  <li>Access to course materials anytime</li>
                  <li>Skills enhancement for career growth</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <button @click="closeModal" class="btn-secondary">Cancel</button>
            <button 
              @click="enrollInCourse" 
              class="btn-primary"
              :disabled="enrolling"
            >
              <i class="fas fa-spinner fa-spin" v-if="enrolling"></i>
              <i class="fas fa-graduation-cap" v-else></i>
              {{ enrolling ? 'Enrolling...' : 'Confirm Enrollment' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import DashboardLayout from './DashboardLayout.vue'


// State
const availableCourses = ref([])
const enrolledCourses = ref([])
const trainingCategories = ref([])
const showModal = ref(false)
const selectedCourse = ref(null)
const loading = ref(false)
const enrolling = ref(false)
const searchQuery = ref('')
const trainingFilter = ref('')
const user_id = ref('');
const username = ref('');


// Helper function to get auth token
const getAuthToken = () => {
  return localStorage.getItem('access_token');
}



// Helper function to get current user ID
async function fetchUserData() {
    const userData = await axios.get('/api/users/', { headers: { Authorization: `Bearer ${getAuthToken()}` } });
    
    user_id.value=userData.data.id;
    username.value=userData.data.name;

}

// Computed properties
const completedCoursesCount = computed(() => {
  return enrolledCourses.value.filter(e => e.status === 'completed').length
})

const totalLearningHours = computed(() => {
  return Math.round(enrolledCourses.value.reduce((total, e) => {
    return total + (e.course.duration_mins || 0)
  }, 0) / 60)
})

const filteredAvailableCourses = computed(() => {
  let filtered = [...availableCourses.value]
  
  // Filter out already enrolled courses
  const enrolledCourseIds = enrolledCourses.value.map(e => e.course_id)
  filtered = filtered.filter(course => !enrolledCourseIds.includes(course.id))
  
  // Search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(course => 
      course.title.toLowerCase().includes(query) ||
      (course.training_title && course.training_title.toLowerCase().includes(query))
    )
  }
  
  // Training category filter
  if (trainingFilter.value) {
    filtered = filtered.filter(course => course.training_id == trainingFilter.value)
  }
  
  return filtered
})

// Functions
async function fetchAvailableCourses() {
  try {
    loading.value = true
    const response = await axios.get('/api/training/modules', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    
    if (response.data.success) {
      availableCourses.value = response.data.data
      
      // Extract unique training categories
      const trainings = {}
      response.data.data.forEach(course => {
        if (course.training_id && course.training_title) {
          trainings[course.training_id] = {
            id: course.training_id,
            title: course.training_title
          }
        }
      })
      trainingCategories.value = Object.values(trainings)
    }
  } catch (error) {
    console.error('Failed to fetch available courses:', error)
  } finally {
    loading.value = false
  }
}

async function fetchEnrolledCourses() {
  try {

    
    // This would need a specific endpoint for user enrollments
    // For now, we'll simulate with the existing data
    const response = await axios.get(`/api/training/modules`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    
    if (response.data.success) {
      // Filter courses with enrollments (you'd get this from a proper endpoint)
      const enrolledData = []
      for (let course of response.data.data) {
        try {
          const enrollmentResponse = await axios.get(
            `/api/training/modules/${course.id}`, 
            {
              headers: { Authorization: `Bearer ${getAuthToken()}` },
              params: { user_id: user_id?.value }
            }
          )
          
          if (enrollmentResponse.data.success && enrollmentResponse.data.data.enrollment) {
            enrolledData.push({
              ...enrollmentResponse.data.data.enrollment,
              course: course,
            })
          }
        } catch (error) {
          // Course not enrolled, skip`
          continue
        }
      }
      enrolledCourses.value = enrolledData
      console.log(enrolledCourses)
    }
  } catch (error) {
    console.error('Failed to fetch enrolled courses:', error)
  }
}

function showEnrollmentModal(course) {
  selectedCourse.value = course
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedCourse.value = null
  enrolling.value = false
}

async function enrollInCourse() {
  if (!selectedCourse.value) return
  
  try {
    enrolling.value = true

    
    // Create enrollment by setting initial progress
    await axios.put(
      `/api/training/modules/${selectedCourse.value.id}/progress`,
      {
        user_id: user_id?.value ?? user_id,
        progress: 0
      },
      {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      }
    )
    
    // Add to enrolled courses
    enrolledCourses.value.push({
      user_id: user_id,
      course_id: selectedCourse.value.id,
      course: selectedCourse.value,
      progress: 0,
      status: 'enrolled'
    })
    
    closeModal()
    
    // Show success message (you can add a toast notification here)
    alert(`Successfully enrolled in "${selectedCourse.value}"!`)
    
  } catch (error) {
    console.error('Failed to enroll in course:', error)
    alert('Failed to enroll in course. Please try again.')
  } finally {
    enrolling.value = false
  }
}

async function updateProgress(courseId, progress) {
  try {
    loading.value = true
    
    await axios.put(
      `/api/training/modules/${courseId}/progress`,
      {
        user_id: user_id?.value,
        progress: progress
      },
      {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      }
    )
    
    // Update local state
    const enrollment = enrolledCourses.value.find(e => e.course_id === courseId)
    if (enrollment) {
      enrollment.progress = progress
      if (progress >= 100) {
        enrollment.status = 'completed'
      }
    }
    
  } catch (error) {
    console.error('Failed to update progress:', error)
    alert('Failed to update progress. Please try again.')
  } finally {
    loading.value = false
  }
}

async function completeModule(courseId) {
  try {
    
    await axios.post(
      `/api/training/modules/${courseId}/complete`,
      { user_id: user_id },
      {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      }
    )
    
    // Update local state
    const enrollment = enrolledCourses.value.find(e => e.course_id === courseId)
    if (enrollment) {
      enrollment.progress = 100
      enrollment.status = 'completed'
    }
    
  } catch (error) {
    console.error('Failed to complete module:', error)
  }
}

function openCourse(course) {
  if (course.content_url) {
    window.open(course.content_url, '_blank')
  } else {
    alert('Course content is not available yet.')
  }
}

function getEnrollmentCount(courseId) {
  // This would come from the API in a real implementation
  return Math.floor(Math.random() * 150) + 10
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Load data on mount
onMounted(async () => {
    try{
        await fetchUserData();
    
        await Promise.all([
        
            fetchEnrolledCourses(),
            fetchAvailableCourses(),
        ])
    }
    catch(error){
        console.log(error)
    }

})
</script>

<style scoped>
.course-page {
  padding: 0;
  max-width: 100%;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.page-header p {
  font-size: 1.2rem;
  color: #7f8c8d;
  margin: 0;
}

/* Stats Overview */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 25px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.stat-card i {
  font-size: 2.5rem;
  opacity: 0.8;
}

.stat-info h3 {
  font-size: 2rem;
  margin: 0 0 5px 0;
  font-weight: bold;
}

.stat-info p {
  margin: 0;
  opacity: 0.9;
  font-size: 1rem;
}

/* Course Sections */
.course-sections {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-header h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.course-count {
  background: #ecf0f1;
  color: #7f8c8d;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.section-actions {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
}

.search-input {
  padding: 10px 40px 10px 15px;
  border: 2px solid #ecf0f1;
  border-radius: 25px;
  outline: none;
  font-size: 0.9rem;
  width: 250px;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  border-color: #3498db;
}

.search-box i {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #7f8c8d;
}

.filter-select {
  padding: 10px 15px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  outline: none;
  font-size: 0.9rem;
  background: white;
  cursor: pointer;
}

/* Course Grid */
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

.course-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  border: 1px solid #ecf0f1;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  height: fit-content;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}

.enrolled-card {
  border-left: 4px solid #3498db;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 15px;
}

.course-title h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.training-badge {
  background: #e8f4f8;
  color: #2980b9;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.course-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.course-status.enrolled {
  background: #fff3cd;
  color: #856404;
}

.course-status.completed {
  background: #d4edda;
  color: #155724;
}

.course-status.in-progress {
  background: #cce7ff;
  color: #004085;
}

.course-difficulty {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #27ae60;
  font-size: 0.85rem;
  font-weight: 600;
}

.course-content {
  flex: 1;
  margin-bottom: 20px;
}

.course-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.course-info p {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.course-info i {
  width: 16px;
  color: #3498db;
}

/* Progress Section */
.progress-section {
  margin-top: 15px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-header span {
  font-size: 0.9rem;
  font-weight: 600;
  color: #2c3e50;
}

.progress-text {
  color: #3498db !important;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3498db;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-fill.completed {
  background: #27ae60;
}

/* Course Actions */
.course-actions {
  display: flex;
  gap: 10px;
  margin-top: auto;
}

.course-actions button {
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex: 1;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-2px);
}

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #229954;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.full-width {
  width: 100%;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* No Courses State */
.no-courses {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.no-courses i {
  font-size: 4rem;
  margin-bottom: 20px;
  display: block;
}

.no-courses h3 {
  font-size: 1.5rem;
  margin: 0 0 10px 0;
  color: #2c3e50;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
  box-sizing: border-box;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 25px 0 25px;
  border-bottom: 1px solid #ecf0f1;
  margin-bottom: 20px;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
  padding: 5px;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.close-btn:hover {
  background: #f8f9fa;
  color: #e74c3c;
}

.modal-body {
  padding: 0 25px 20px 25px;
}

.course-preview h4 {
  font-size: 1.4rem;
  color: #2c3e50;
  margin: 0 0 10px 0;
}

.training-category {
  color: #7f8c8d;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.course-details {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-item i {
  color: #3498db;
  width: 20px;
}

.enrollment-benefits {
  margin-top: 25px;
}

.enrollment-benefits h5 {
  color: #2c3e50;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.enrollment-benefits ul {
  margin: 0;
  padding-left: 25px;
}

.enrollment-benefits li {
  margin-bottom: 8px;
  color: #7f8c8d;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 20px 25px 25px 25px;
  border-top: 1px solid #ecf0f1;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
    flex-direction: column;
    gap: 10px;
  }
  
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
  
  .stat-card {
    padding: 20px;
    gap: 15px;
  }
  
  .stat-card i {
    font-size: 2rem;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .section-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .search-input {
    width: 200px;
  }
  
  .course-grid {
    grid-template-columns: 1fr;
  }
  
  .course-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .course-actions {
    flex-direction: column;
  }
  
  .modal-content {
    margin: 10px;
    max-height: 95vh;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding-left: 20px;
    padding-right: 20px;
  }
  
  .modal-footer {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .section-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    width: 100%;
  }
  
  .course-card {
    padding: 20px;
  }
}
</style>