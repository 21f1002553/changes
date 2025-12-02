<template>
  <DashboardLayout>
    <div class="vacancies-page">
      <!-- Header Section -->
      <div class="page-header">
        <div class="header-content">
          <h1><i class="fas fa-briefcase"></i> Available Vacancies</h1>
          <p>Browse all available teaching positions</p>
        </div>
        <div class="header-actions">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search by title, school, location..."
              @input="filterVacancies"
            />
          </div>
          <select v-model="filterLocation" @change="filterVacancies" class="filter-select">
            <option value="">All Locations</option>
            <option v-for="loc in locations" :key="loc" :value="loc">{{ loc }}</option>
          </select>
          <select v-model="filterLevel" @change="filterVacancies" class="filter-select">
            <option value="">All Levels</option>
            <option v-for="lvl in levels" :key="lvl" :value="lvl">{{ lvl }}</option>
          </select>
        </div>
      </div>

      <!-- Stats Overview -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon total">
            <i class="fas fa-briefcase"></i>
          </div>
          <div class="stat-info">
            <h3>{{ totalVacancies }}</h3>
            <p>Total Vacancies</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon applied">
            <i class="fas fa-paper-plane"></i>
          </div>
          <div class="stat-info">
            <h3>{{ appliedCount }}</h3>
            <p>Applied</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon filtered">
            <i class="fas fa-filter"></i>
          </div>
          <div class="stat-info">
            <h3>{{ filteredVacancies.length }}</h3>
            <p>Filtered Results</p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner">
          <i class="fas fa-spinner fa-spin"></i>
        </div>
        <p>Loading vacancies...</p>
      </div>

      <!-- Vacancies Grid -->
      <div v-else-if="filteredVacancies.length > 0" class="vacancies-grid">
        <div 
          v-for="vacancy in filteredVacancies" 
          :key="vacancy.id" 
          class="vacancy-card"
          :class="{ applied: isVacancyApplied(vacancy.id) }"
        >
          <!-- Vacancy Header -->
          <div class="vacancy-header">
            <div class="school-icon">
              <i class="fas fa-school"></i>
            </div>
            <div class="vacancy-title-section">
              <h3>{{ vacancy.title }}</h3>
              <p class="school-name">
                <i class="fas fa-building"></i>
                {{ vacancy.school || 'School Name' }}
              </p>
            </div>
          </div>

          <!-- Vacancy Details -->
          <div class="vacancy-details">
            <div class="detail-item">
              <i class="fas fa-map-marker-alt"></i>
              <span>{{ vacancy.location || 'Location not specified' }}</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-graduation-cap"></i>
              <span>{{ vacancy.level || 'All Levels' }}</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-briefcase"></i>
              <span>{{ vacancy.employment_type || 'Full-time' }}</span>
            </div>
            <div class="detail-item" v-if="vacancy.salary_range">
              <i class="fas fa-dollar-sign"></i>
              <span>{{ vacancy.salary_range }}</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-clock"></i>
              <span>Posted {{ getTimeAgo(vacancy.posted_at) }}</span>
            </div>
            <div class="detail-item" v-if="vacancy.department">
              <i class="fas fa-layer-group"></i>
              <span>{{ vacancy.department }}</span>
            </div>
          </div>

          <!-- Vacancy Description -->
          <div class="vacancy-description">
            <p>{{ truncateText(vacancy.description, 150) }}</p>
          </div>

          <!-- Requirements Preview -->
          <div class="vacancy-requirements" v-if="vacancy.requirements">
            <strong>Requirements:</strong>
            <p>{{ truncateText(vacancy.requirements, 100) }}</p>
          </div>

          <!-- Status Badge -->
          <div class="vacancy-status">
            <span 
              class="status-badge" 
              :class="vacancy.status"
            >
              <i :class="getStatusIcon(vacancy.status)"></i>
              {{ vacancy.status || 'Active' }}
            </span>
          </div>

          <!-- Action Buttons -->
          <div class="vacancy-actions">
            <button 
              @click="viewVacancyDetails(vacancy)" 
              class="btn-secondary"
            >
              <i class="fas fa-eye"></i>
              View Details
            </button>
            <button 
              v-if="!isVacancyApplied(vacancy.id)"
              @click="applyToVacancy(vacancy)" 
              class="btn-primary"
            >
              <i class="fas fa-paper-plane"></i>
              Apply Now
            </button>
            <button 
              v-else
              class="btn-applied"
              disabled
            >
              <i class="fas fa-check-circle"></i>
              Applied
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-search"></i>
        </div>
        <h3>No Vacancies Found</h3>
        <p v-if="searchQuery || filterLocation || filterLevel">
          No vacancies match your search criteria. Try different filters.
        </p>
        <p v-else>No vacancies are currently available. Please check back later.</p>
        <button @click="clearFilters" class="btn-primary" v-if="searchQuery || filterLocation || filterLevel">
          <i class="fas fa-times"></i>
          Clear Filters
        </button>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import DashboardLayout from './DashboardLayout.vue'
import axios from 'axios'

const router = useRouter()

// State
const loading = ref(false)
const allVacancies = ref([])
const appliedVacancies = ref([])
const locations = ref([])
const levels = ref([])
const searchQuery = ref('')
const filterLocation = ref('')
const filterLevel = ref('')

// Computed
const filteredVacancies = computed(() => {
  let vacancies = [...allVacancies.value]
  
  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    vacancies = vacancies.filter(vacancy => 
      vacancy.title?.toLowerCase().includes(query) ||
      vacancy.school?.toLowerCase().includes(query) ||
      vacancy.location?.toLowerCase().includes(query) ||
      vacancy.description?.toLowerCase().includes(query) ||
      vacancy.department?.toLowerCase().includes(query)
    )
  }
  
  // Filter by location
  if (filterLocation.value) {
    vacancies = vacancies.filter(v => v.location === filterLocation.value)
  }
  
  // Filter by level
  if (filterLevel.value) {
    vacancies = vacancies.filter(v => v.level === filterLevel.value)
  }
  
  return vacancies
})

const totalVacancies = computed(() => allVacancies.value?.length || 0)
const appliedCount = computed(() => appliedVacancies.value?.length || 0)

// Helper Functions
const getAuthToken = () => localStorage.getItem('access_token')

const isVacancyApplied = (vacancyId) => {
  if (!vacancyId || !appliedVacancies.value?.length) return false
  return appliedVacancies.value.some(app => app.vacancy_id === vacancyId)
}

const truncateText = (text, length) => {
  if (!text) return 'No description available'
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

const getTimeAgo = (dateString) => {
  if (!dateString) return 'Recently'
  
  const diffDays = Math.ceil((new Date() - new Date(dateString)) / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  return `${Math.floor(diffDays / 30)} months ago`
}

const getStatusIcon = (status) => {
  const iconMap = {
    'active': 'fas fa-check-circle',
    'inactive': 'fas fa-times-circle',
    'closed': 'fas fa-lock'
  }
  return iconMap[status?.toLowerCase()] || 'fas fa-circle'
}

// API Functions
const loadVacancies = async () => {
  try {
    loading.value = true
    
    const response = await axios.get('/api/vacancies/', {
      headers: { Authorization: `Bearer ${getAuthToken()}` },
      params: { status: 'active' }
    })
    
    console.log('Vacancies response:', response.data)
    allVacancies.value = Array.isArray(response.data) ? response.data : []
    
    console.log(`Loaded ${allVacancies.value.length} vacancies`)
  } catch (error) {
    console.error('Failed to load vacancies:', error)
    allVacancies.value = []
  } finally {
    loading.value = false
  }
}

const loadLocations = async () => {
  try {
    const response = await axios.get('/api/vacancies/locations', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    locations.value = response.data.locations || []
  } catch (error) {
    console.error('Failed to load locations:', error)
  }
}

const loadLevels = async () => {
  try {
    const response = await axios.get('/api/vacancies/levels', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    levels.value = response.data.levels || []
  } catch (error) {
    console.error('Failed to load levels:', error)
  }
}

const loadAppliedVacancies = async () => {
  try {
    const response = await axios.get('/api/applications/', {
      headers: { Authorization: `Bearer ${getAuthToken()}` }
    })
    
    appliedVacancies.value = response.data?.applications || []
  } catch (error) {
    console.error('Failed to load applied vacancies:', error)
    appliedVacancies.value = []
  }
}

// Action Functions
const filterVacancies = () => {
  // Filtering is handled by computed property
  console.log('Filtering vacancies...')
}

const clearFilters = () => {
  searchQuery.value = ''
  filterLocation.value = ''
  filterLevel.value = ''
}

const applyToVacancy = (vacancy) => {
  // Navigate to application form or open modal
  router.push(`/candidate/apply/${vacancy.id}`)
}

const viewVacancyDetails = (vacancy) => {
  router.push(`/candidate/vacancy/${vacancy.id}`)
}

// Load data on mount
onMounted(async () => {
  try {
    await Promise.all([
      loadVacancies(),
      loadLocations(),
      loadLevels(),
      loadAppliedVacancies()
    ])
  } catch (error) {
    console.error('Failed to load data:', error)
  }
})
</script>

<style scoped>
.vacancies-page {
  padding: 0;
}

/* Header Section */
.page-header {
  margin-bottom: 30px;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-content p {
  color: #7f8c8d;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 15px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 250px;
  position: relative;
}

.search-box i {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #7f8c8d;
}

.search-box input {
  width: 100%;
  padding: 12px 15px 12px 45px;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
}

.search-box input:focus {
  border-color: #3498db;
}

.filter-select {
  padding: 12px 20px;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
  cursor: pointer;
  background: white;
}

/* Stats Cards */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.applied {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.filtered {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-info h3 {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
  color: #2c3e50;
}

.stat-info p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* Loading & Empty States */
.loading-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  margin-bottom: 20px;
}

.loading-spinner i {
  font-size: 3rem;
  color: #3498db;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon i {
  font-size: 4rem;
  color: #bdc3c7;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 0 0 10px 0;
}

.empty-state p {
  color: #7f8c8d;
  margin: 0 0 25px 0;
}

/* Vacancies Grid */
.vacancies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

.vacancy-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.vacancy-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: #3498db;
}

.vacancy-card.applied {
  opacity: 0.7;
  background: #f8f9fa;
}

/* Vacancy Header */
.vacancy-header {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  margin-bottom: 20px;
}

.school-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.vacancy-title-section h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.school-name {
  color: #7f8c8d;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Vacancy Details */
.vacancy-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 15px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.detail-item i {
  color: #3498db;
  width: 16px;
}

/* Description & Requirements */
.vacancy-description,
.vacancy-requirements {
  margin-bottom: 15px;
}

.vacancy-description p,
.vacancy-requirements p {
  color: #7f8c8d;
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 5px 0 0 0;
}

.vacancy-requirements strong {
  color: #2c3e50;
  font-size: 0.9rem;
}

/* Status & Actions */
.vacancy-status {
  margin-bottom: 20px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive,
.status-badge.closed {
  background: #f8d7da;
  color: #721c24;
}

.vacancy-actions {
  display: flex;
  gap: 10px;
}

.vacancy-actions button {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #ecf0f1;
  color: #2c3e50;
}

.btn-secondary:hover {
  background: #d5dbdb;
}

.btn-applied {
  background: #27ae60;
  color: white;
  cursor: not-allowed;
  opacity: 0.7;
}

@media (max-width: 768px) {
  .vacancies-grid {
    grid-template-columns: 1fr;
  }
  
  .vacancy-details {
    grid-template-columns: 1fr;
  }
  
  .header-actions {
    flex-direction: column;
  }
  
  .search-box {
    width: 100%;
  }
}
</style>