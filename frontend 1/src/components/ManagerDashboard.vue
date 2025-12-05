<template>
  <DashboardLayout>
    <div class="manager-dashboard">
      <!-- Header Section -->
      <div class="dashboard-header">
        <div class="welcome-section">
          <h1>Welcome back, {{ managerName || 'Manager' }}!</h1>
          <p>{{ getCurrentDateString() }}</p>
        </div>
        <div class="quick-actions">
          <button @click="navigate('team-overview')" class="quick-action-btn">
            <i class="fas fa-users"></i>
            Team Overview
          </button>
          <button @click="navigate('performance-review')" class="quick-action-btn">
            <i class="fas fa-chart-line"></i>
            Performance Reviews
          </button>
          <button @click="navigate('approvals')" class="quick-action-btn">
            <i class="fas fa-clipboard-check"></i>
            Pending Approvals
          </button>
        </div>
      </div>

      <!-- Stats Overview -->
      <div class="stats-grid">
        <div class="stat-card team-size">
          <div class="stat-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="stat-content">
            <h3>{{ teamStats.totalMembers || 0 }}</h3>
            <p>Team Members</p>
            <span class="stat-change positive" v-if="teamStats.newHires > 0">
              +{{ teamStats.newHires }} new this month
            </span>
          </div>
        </div>

        <div class="stat-card performance">
          <div class="stat-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="stat-content">
            <h3>{{ teamStats.avgPerformance || 0 }}%</h3>
            <p>Avg Performance</p>
            <span class="stat-change" :class="teamStats.performanceTrend >= 0 ? 'positive' : 'negative'">
              {{ teamStats.performanceTrend >= 0 ? '+' : '' }}{{ teamStats.performanceTrend || 0 }}%
            </span>
          </div>
        </div>

        <div class="stat-card pending-approvals">
          <div class="stat-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-content">
            <h3>{{ pendingApprovals.length || 0 }}</h3>
            <p>Pending Approvals</p>
            <span class="stat-change urgent" v-if="urgentApprovals > 0">
              {{ urgentApprovals }} urgent
            </span>
          </div>
        </div>

        <div class="stat-card budget">
          <div class="stat-icon">
            <i class="fas fa-dollar-sign"></i>
          </div>
          <div class="stat-content">
            <h3>${{ formatCurrency(teamStats.budgetUsed) }}</h3>
            <p>Budget Used</p>
            <span class="stat-change" :class="teamStats.budgetVariance >= 0 ? 'negative' : 'positive'">
              {{ teamStats.budgetUsage }}% of total
            </span>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="dashboard-grid">
        <!-- Team Performance -->
        <div class="dashboard-card team-performance">
          <div class="card-header">
            <h3><i class="fas fa-chart-bar"></i> Team Performance Overview</h3>
            <div class="card-actions">
              <select v-model="performancePeriod" @change="loadTeamPerformance">
                <option value="month">This Month</option>
                <option value="quarter">This Quarter</option>
                <option value="year">This Year</option>
              </select>
            </div>
          </div>
          
          <div v-if="performanceLoading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading performance data...</p>
          </div>
          
          <div v-else class="performance-grid">
            <div class="performance-metric">
              <h4>Team Productivity</h4>
              <div class="metric-value">
                <span class="value">{{ teamPerformance.productivity }}%</span>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: teamPerformance.productivity + '%' }"></div>
                </div>
              </div>
            </div>
            
            <div class="performance-metric">
              <h4>Goal Achievement</h4>
              <div class="metric-value">
                <span class="value">{{ teamPerformance.goalAchievement }}%</span>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: teamPerformance.goalAchievement + '%' }"></div>
                </div>
              </div>
            </div>
            
            <div class="performance-metric">
              <h4>Employee Satisfaction</h4>
              <div class="metric-value">
                <span class="value">{{ teamPerformance.satisfaction }}/5</span>
                <div class="star-rating">
                  <i v-for="n in 5" :key="n" 
                     class="fas fa-star" 
                     :class="{ active: n <= teamPerformance.satisfaction }">
                  </i>
                </div>
              </div>
            </div>
          </div>
          
          <button @click="navigate('team-analytics')" class="view-details-btn">
            View Detailed Analytics
          </button>
        </div>

        <!-- Pending Approvals -->
        <div class="dashboard-card pending-approvals-card">
          <div class="card-header">
            <h3><i class="fas fa-clipboard-check"></i> Pending Approvals</h3>
            <span class="badge" v-if="urgentApprovals > 0">{{ urgentApprovals }} Urgent</span>
          </div>
          
          <div v-if="approvalsLoading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading approvals...</p>
          </div>
          
          <div v-else-if="pendingApprovals.length > 0" class="approvals-list">
            <div v-for="approval in pendingApprovals.slice(0, 5)" :key="approval.id" class="approval-item">
              <div class="approval-info">
                <div class="approval-header">
                  <h4>{{ approval.title }}</h4>
                  <span class="approval-type" :class="approval.type">{{ approval.type }}</span>
                </div>
                <p>{{ approval.description }}</p>
                <div class="approval-meta">
                  <span><i class="fas fa-user"></i> {{ approval.requester }}</span>
                  <span><i class="fas fa-clock"></i> {{ formatDate(approval.submittedAt) }}</span>
                  <span v-if="approval.urgent" class="urgent-tag">
                    <i class="fas fa-exclamation-triangle"></i> Urgent
                  </span>
                </div>
              </div>
              <div class="approval-actions">
                <button @click="approveRequest(approval)" class="approve-btn" :disabled="processingApproval">
                  <i class="fas fa-check"></i> Approve
                </button>
                <button @click="rejectRequest(approval)" class="reject-btn" :disabled="processingApproval">
                  <i class="fas fa-times"></i> Reject
                </button>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-state">
            <i class="fas fa-check-circle"></i>
            <h4>All Caught Up!</h4>
            <p>No pending approvals at the moment.</p>
          </div>
          
          <button v-if="pendingApprovals.length > 5" @click="navigate('approvals')" class="view-all-btn">
            View All Approvals ({{ pendingApprovals.length }})
          </button>
        </div>

        <!-- Team Members -->
        <div class="dashboard-card team-members">
          <div class="card-header">
            <h3><i class="fas fa-users"></i> Team Members</h3>
            <button @click="navigate('team-management')" class="add-member-btn">
              <i class="fas fa-plus"></i> Manage Team
            </button>
          </div>
          
          <div v-if="teamLoading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading team data...</p>
          </div>
          
          <div v-else class="team-list">
            <div v-for="member in teamMembers.slice(0, 6)" :key="member.id" class="team-member-card">
              <div class="member-avatar">
                <img :src="member.avatar || '/default-avatar.png'" :alt="member.name" />
                <div class="status-indicator" :class="member.status"></div>
              </div>
              <div class="member-info">
                <h4>{{ member.name }}</h4>
                <p>{{ member.position }}</p>
                <div class="member-stats">
                  <span class="performance-score" :class="getPerformanceClass(member.performance)">
                    {{ member.performance }}%
                  </span>
                  <span class="attendance">{{ member.attendance }}% attendance</span>
                </div>
              </div>
              <div class="member-actions">
                <button @click="viewMemberDetails(member)" class="action-btn">
                  <i class="fas fa-eye"></i>
                </button>
                <button @click="messageMember(member)" class="action-btn">
                  <i class="fas fa-message"></i>
                </button>
              </div>
            </div>
          </div>
          
          <button @click="navigate('team-overview')" class="view-all-btn">
            View All Team Members
          </button>
        </div>

        <!-- Recent Activities -->
        <div class="dashboard-card recent-activities">
          <div class="card-header">
            <h3><i class="fas fa-history"></i> Recent Activities</h3>
            <div class="activity-filters">
              <button @click="filterActivities('all')" :class="{ active: activityFilter === 'all' }">All</button>
              <button @click="filterActivities('performance')" :class="{ active: activityFilter === 'performance' }">Performance</button>
              <button @click="filterActivities('approvals')" :class="{ active: activityFilter === 'approvals' }">Approvals</button>
            </div>
          </div>
          
          <div class="activities-list">
            <div v-for="activity in filteredActivities.slice(0, 6)" :key="activity.id" class="activity-item">
              <div class="activity-icon" :class="activity.type">
                <i :class="getActivityIcon(activity.type)"></i>
              </div>
              <div class="activity-content">
                <h4>{{ activity.title }}</h4>
                <p>{{ activity.description }}</p>
                <span class="activity-time">{{ formatDateTime(activity.timestamp) }}</span>
              </div>
            </div>
          </div>
          
          <button @click="navigate('activity-log')" class="view-all-btn">
            View All Activities
          </button>
        </div>

        <!-- Upcoming Tasks & Deadlines -->
        <div class="dashboard-card upcoming-tasks">
          <div class="card-header">
            <h3><i class="fas fa-calendar-check"></i> Upcoming Tasks & Deadlines</h3>
            <button @click="navigate('task-management')" class="add-task-btn">
              <i class="fas fa-plus"></i> Add Task
            </button>
          </div>
          
          <div class="tasks-list">
            <div v-for="task in upcomingTasks.slice(0, 5)" :key="task.id" class="task-item">
              <div class="task-info">
                <h4>{{ task.title }}</h4>
                <p>{{ task.description }}</p>
                <div class="task-meta">
                  <span class="assignee"><i class="fas fa-user"></i> {{ task.assignee }}</span>
                  <span class="due-date" :class="{ overdue: isOverdue(task.dueDate) }">
                    <i class="fas fa-calendar"></i> {{ formatDate(task.dueDate) }}
                  </span>
                </div>
              </div>
              <div class="task-priority" :class="task.priority">
                {{ task.priority }}
              </div>
            </div>
          </div>
          
          <button @click="navigate('tasks')" class="view-all-btn">
            View All Tasks
          </button>
        </div>

        <!-- Department Budget -->
        <div class="dashboard-card budget-overview">
          <div class="card-header">
            <h3><i class="fas fa-chart-pie"></i> Department Budget</h3>
            <select v-model="budgetPeriod" @change="loadBudgetData">
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
            </select>
          </div>
          
          <div class="budget-summary">
            <div class="budget-item">
              <span class="label">Total Budget</span>
              <span class="amount">${{ formatCurrency(budget.total) }}</span>
            </div>
            <div class="budget-item">
              <span class="label">Used</span>
              <span class="amount used">${{ formatCurrency(budget.used) }}</span>
            </div>
            <div class="budget-item">
              <span class="label">Remaining</span>
              <span class="amount remaining">${{ formatCurrency(budget.remaining) }}</span>
            </div>
          </div>
          
          <div class="budget-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: budget.usagePercentage + '%' }"></div>
            </div>
            <span class="usage-text">{{ budget.usagePercentage }}% used</span>
          </div>
          
          <button @click="navigate('budget-management')" class="view-details-btn">
            Manage Budget
          </button>
        </div>
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
const managerName = ref('')
const managerId = ref('')

// Team stats
const teamStats = ref({
  totalMembers: 0,
  newHires: 0,
  avgPerformance: 0,
  performanceTrend: 0,
  budgetUsed: 0,
  budgetUsage: 0,
  budgetVariance: 0
})

// Performance data
const teamPerformance = ref({
  productivity: 0,
  goalAchievement: 0,
  satisfaction: 0
})

const performancePeriod = ref('month')
const performanceLoading = ref(false)

// Approvals
const pendingApprovals = ref([])
const approvalsLoading = ref(false)
const processingApproval = ref(false)

// Team members
const teamMembers = ref([])
const teamLoading = ref(false)

// Activities
const recentActivities = ref([])
const activityFilter = ref('all')

// Tasks
const upcomingTasks = ref([])

// Budget
const budget = ref({
  total: 0,
  used: 0,
  remaining: 0,
  usagePercentage: 0
})
const budgetPeriod = ref('month')

// Loading states
const loading = ref(false)

// Computed
const urgentApprovals = computed(() => {
  return pendingApprovals.value.filter(approval => approval.urgent).length
})

const filteredActivities = computed(() => {
  if (activityFilter.value === 'all') {
    return recentActivities.value
  }
  return recentActivities.value.filter(activity => activity.type === activityFilter.value)
})

// Helper Functions
const getCurrentDateString = () => {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US').format(amount || 0)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const isOverdue = (dueDate) => {
  return new Date(dueDate) < new Date()
}

const getPerformanceClass = (performance) => {
  if (performance >= 90) return 'excellent'
  if (performance >= 80) return 'good'
  if (performance >= 70) return 'average'
  return 'poor'
}

const getActivityIcon = (type) => {
  const iconMap = {
    performance: 'fas fa-chart-line',
    approvals: 'fas fa-clipboard-check',
    team: 'fas fa-users',
    budget: 'fas fa-dollar-sign',
    task: 'fas fa-tasks'
  }
  return iconMap[type] || 'fas fa-info-circle'
}

// Navigation
const navigate = (page) => {
  const pageMap = {
    'team-overview': '/manager/team',
    'performance-review': '/manager/performance',
    'approvals': '/manager/approvals',
    'team-analytics': '/manager/analytics',
    'team-management': '/manager/team-management',
    'activity-log': '/manager/activities',
    'task-management': '/manager/tasks',
    'tasks': '/manager/tasks',
    'budget-management': '/manager/budget'
  }
  
  if (pageMap[page]) {
    router.push(pageMap[page])
  }
}

// API Functions
const loadManagerData = async () => {
  try {
    const response = await axios.get('/api/users/profile', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    
    if (response.data) {
      managerName.value = response.data.name
      managerId.value = response.data.id
    }
  } catch (error) {
    console.error('Failed to load manager data:', error)
  }
}

const loadTeamStats = async () => {
  try {
    const response = await axios.get('/api/manager/team-stats', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    
    if (response.data) {
      teamStats.value = response.data
    }
  } catch (error) {
    console.error('Failed to load team stats:', error)
    // Mock data for demo
    teamStats.value = {
      totalMembers: 12,
      newHires: 2,
      avgPerformance: 87,
      performanceTrend: 5,
      budgetUsed: 45000,
      budgetUsage: 75,
      budgetVariance: -2
    }
  }
}

const loadTeamPerformance = async () => {
  try {
    performanceLoading.value = true
    const response = await axios.get(`/api/manager/team-performance?period=${performancePeriod.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    
    if (response.data) {
      teamPerformance.value = response.data
    }
  } catch (error) {
    console.error('Failed to load team performance:', error)
    // Mock data
    teamPerformance.value = {
      productivity: 85,
      goalAchievement: 92,
      satisfaction: 4.2
    }
  } finally {
    performanceLoading.value = false
  }
}

const loadPendingApprovals = async () => {
  try {
    approvalsLoading.value = true
    const response = await axios.get('/api/manager/pending-approvals', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    
    if (response.data) {
      pendingApprovals.value = response.data
    }
  } catch (error) {
    console.error('Failed to load pending approvals:', error)
    // Mock data
    pendingApprovals.value = [
      {
        id: 1,
        title: 'Leave Request - John Doe',
        description: 'Annual leave for 3 days',
        type: 'leave',
        requester: 'John Doe',
        submittedAt: '2024-12-01',
        urgent: false
      },
      {
        id: 2,
        title: 'Budget Approval - Marketing Campaign',
        description: 'Additional budget for Q1 marketing',
        type: 'budget',
        requester: 'Sarah Smith',
        submittedAt: '2024-11-30',
        urgent: true
      }
    ]
  } finally {
    approvalsLoading.value = false
  }
}

const loadTeamMembers = async () => {
  try {
    teamLoading.value = true
    const response = await axios.get('/api/manager/team-members', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    
    if (response.data) {
      teamMembers.value = response.data
    }
  } catch (error) {
    console.error('Failed to load team members:', error)
    // Mock data
    teamMembers.value = [
      {
        id: 1,
        name: 'John Doe',
        position: 'Senior Developer',
        avatar: null,
        status: 'online',
        performance: 92,
        attendance: 98
      },
      {
        id: 2,
        name: 'Sarah Smith',
        position: 'Marketing Specialist',
        avatar: null,
        status: 'away',
        performance: 88,
        attendance: 95
      }
    ]
  } finally {
    teamLoading.value = false
  }
}

const loadRecentActivities = async () => {
  try {
    const response = await axios.get('/api/manager/recent-activities', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    
    if (response.data) {
      recentActivities.value = response.data
    }
  } catch (error) {
    console.error('Failed to load recent activities:', error)
    // Mock data
    recentActivities.value = [
      {
        id: 1,
        title: 'Performance Review Completed',
        description: 'John Doe - Q4 performance review',
        type: 'performance',
        timestamp: '2024-12-01T10:30:00'
      },
      {
        id: 2,
        title: 'Leave Request Approved',
        description: 'Sarah Smith - 2 days approved',
        type: 'approvals',
        timestamp: '2024-12-01T09:15:00'
      }
    ]
  }
}

const loadUpcomingTasks = async () => {
  try {
    const response = await axios.get('/api/manager/upcoming-tasks', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    
    if (response.data) {
      upcomingTasks.value = response.data
    }
  } catch (error) {
    console.error('Failed to load upcoming tasks:', error)
    // Mock data
    upcomingTasks.value = [
      {
        id: 1,
        title: 'Q4 Performance Reviews',
        description: 'Complete all team member reviews',
        assignee: 'Self',
        dueDate: '2024-12-15',
        priority: 'high'
      },
      {
        id: 2,
        title: 'Budget Planning 2025',
        description: 'Prepare department budget for next year',
        assignee: 'Self',
        dueDate: '2024-12-20',
        priority: 'medium'
      }
    ]
  }
}

const loadBudgetData = async () => {
  try {
    const response = await axios.get(`/api/manager/budget?period=${budgetPeriod.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    
    if (response.data) {
      budget.value = response.data
    }
  } catch (error) {
    console.error('Failed to load budget data:', error)
    // Mock data
    budget.value = {
      total: 60000,
      used: 45000,
      remaining: 15000,
      usagePercentage: 75
    }
  }
}

// Action Functions
const approveRequest = async (approval) => {
  try {
    processingApproval.value = true
    
    const response = await axios.post(`/api/manager/approve/${approval.id}`, {}, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    
    if (response.data.success) {
      // Remove from pending approvals
      const index = pendingApprovals.value.findIndex(a => a.id === approval.id)
      if (index > -1) {
        pendingApprovals.value.splice(index, 1)
      }
      
      alert(`${approval.title} has been approved successfully.`)
    }
  } catch (error) {
    console.error('Failed to approve request:', error)
    alert('Failed to approve request. Please try again.')
  } finally {
    processingApproval.value = false
  }
}

const rejectRequest = async (approval) => {
  try {
    processingApproval.value = true
    
    const response = await axios.post(`/api/manager/reject/${approval.id}`, {}, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    
    if (response.data.success) {
      // Remove from pending approvals
      const index = pendingApprovals.value.findIndex(a => a.id === approval.id)
      if (index > -1) {
        pendingApprovals.value.splice(index, 1)
      }
      
      alert(`${approval.title} has been rejected.`)
    }
  } catch (error) {
    console.error('Failed to reject request:', error)
    alert('Failed to reject request. Please try again.')
  } finally {
    processingApproval.value = false
  }
}

const viewMemberDetails = (member) => {
  router.push(`/manager/team/${member.id}`)
}

const messageMember = (member) => {
  // Implement messaging functionality
  alert(`Message feature for ${member.name} coming soon!`)
}

const filterActivities = (filter) => {
  activityFilter.value = filter
}

// Load all data on mount
onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      loadManagerData(),
      loadTeamStats(),
      loadTeamPerformance(),
      loadPendingApprovals(),
      loadTeamMembers(),
      loadRecentActivities(),
      loadUpcomingTasks(),
      loadBudgetData()
    ])
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.manager-dashboard {
  padding: 0;
  max-width: 100%;
}

/* Header Section */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  gap: 20px;
  flex-wrap: wrap;
}

.welcome-section h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 5px 0;
}

.welcome-section p {
  color: #7f8c8d;
  margin: 0;
  font-size: 1rem;
}

.quick-actions {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.quick-action-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.quick-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  color: white;
}

.stat-card.team-size .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.performance .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card.pending-approvals .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card.budget .stat-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content h3 {
  font-size: 2rem;
  font-weight: bold;
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.stat-content p {
  margin: 0 0 8px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.stat-change {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 12px;
  display: inline-block;
}

.stat-change.positive {
  background: #d4edda;
  color: #155724;
}

.stat-change.negative {
  background: #f8d7da;
  color: #721c24;
}

.stat-change.urgent {
  background: #fff3cd;
  color: #856404;
}

/* Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
}

/* Dashboard Cards */
.dashboard-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  transition: transform 0.3s ease;
}

.dashboard-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.card-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-actions select {
  padding: 6px 12px;
  border: 1px solid #ecf0f1;
  border-radius: 6px;
  outline: none;
  font-size: 0.9rem;
}

.badge {
  background: #e74c3c;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.loading-state i {
  font-size: 2rem;
  color: #3498db;
  margin-bottom: 10px;
  display: block;
}

/* Performance Grid */
.performance-grid {
  display: grid;
  gap: 20px;
}

.performance-metric h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 1rem;
}

.metric-value {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.metric-value .value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #3498db;
  min-width: 60px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3498db;
  transition: width 0.3s ease;
}

.star-rating {
  display: flex;
  gap: 2px;
}

.star-rating i {
  color: #ddd;
  transition: color 0.3s ease;
}

.star-rating i.active {
  color: #f39c12;
}

/* Approvals List */
.approvals-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.approval-item {
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  padding: 15px;
  transition: border-color 0.3s ease;
}

.approval-item:hover {
  border-color: #3498db;
}

.approval-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 10px;
}

.approval-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1rem;
}

.approval-type {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.approval-type.leave {
  background: #e8f4f8;
  color: #2980b9;
}

.approval-type.budget {
  background: #fff3cd;
  color: #856404;
}

.approval-type.performance {
  background: #d4edda;
  color: #155724;
}

.approval-info p {
  margin: 0 0 10px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.approval-meta {
  display: flex;
  gap: 15px;
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.approval-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.urgent-tag {
  color: #e74c3c !important;
  font-weight: 600;
}

.approval-actions {
  display: flex;
  gap: 10px;
}

.approve-btn, .reject-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s ease;
}

.approve-btn {
  background: #27ae60;
  color: white;
}

.approve-btn:hover:not(:disabled) {
  background: #229954;
}

.reject-btn {
  background: #e74c3c;
  color: white;
}

.reject-btn:hover:not(:disabled) {
  background: #c0392b;
}

.approve-btn:disabled, .reject-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Team List */
.team-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.team-member-card {
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: all 0.3s ease;
}

.team-member-card:hover {
  border-color: #3498db;
  transform: translateY(-2px);
}

.member-avatar {
  position: relative;
  flex-shrink: 0;
}

.member-avatar img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.status-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
}

.status-indicator.online {
  background: #27ae60;
}

.status-indicator.away {
  background: #f39c12;
}

.status-indicator.offline {
  background: #95a5a6;
}

.member-info {
  flex: 1;
}

.member-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 1rem;
}

.member-info p {
  margin: 0 0 8px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.member-stats {
  display: flex;
  gap: 15px;
  font-size: 0.8rem;
}

.performance-score {
  padding: 2px 6px;
  border-radius: 12px;
  font-weight: 600;
}

.performance-score.excellent {
  background: #d4edda;
  color: #155724;
}

.performance-score.good {
  background: #cce7ff;
  color: #004085;
}

.performance-score.average {
  background: #fff3cd;
  color: #856404;
}

.performance-score.poor {
  background: #f8d7da;
  color: #721c24;
}

.member-actions {
  display: flex;
  gap: 5px;
}

.action-btn {
  background: #ecf0f1;
  border: none;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  color: #7f8c8d;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: #3498db;
  color: white;
}

/* Activities List */
.activity-filters {
  display: flex;
  gap: 5px;
}

.activity-filters button {
  padding: 6px 12px;
  border: 1px solid #ecf0f1;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.activity-filters button.active,
.activity-filters button:hover {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.activity-icon.performance {
  background: #3498db;
}

.activity-icon.approvals {
  background: #27ae60;
}

.activity-icon.team {
  background: #9b59b6;
}

.activity-icon.budget {
  background: #f39c12;
}

.activity-icon.task {
  background: #e74c3c;
}

.activity-content {
  flex: 1;
}

.activity-content h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 0.95rem;
}

.activity-content p {
  margin: 0 0 5px 0;
  color: #7f8c8d;
  font-size: 0.85rem;
}

.activity-time {
  font-size: 0.75rem;
  color: #95a5a6;
}

/* Tasks List */
.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  gap: 15px;
}

.task-info {
  flex: 1;
}

.task-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 1rem;
}

.task-info p {
  margin: 0 0 10px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.task-meta {
  display: flex;
  gap: 15px;
  font-size: 0.85rem;
  color: #7f8c8d;
  flex-wrap: wrap;
}

.task-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.due-date.overdue {
  color: #e74c3c;
  font-weight: 600;
}

.task-priority {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.task-priority.high {
  background: #f8d7da;
  color: #721c24;
}

.task-priority.medium {
  background: #fff3cd;
  color: #856404;
}

.task-priority.low {
  background: #d4edda;
  color: #155724;
}

/* Budget Overview */
.budget-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.budget-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.budget-item .label {
  display: block;
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.budget-item .amount {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.budget-item .amount.used {
  color: #e74c3c;
}

.budget-item .amount.remaining {
  color: #27ae60;
}

.budget-progress {
  margin-bottom: 20px;
}

.usage-text {
  display: block;
  text-align: center;
  margin-top: 8px;
  font-size: 0.9rem;
  color: #7f8c8d;
}

/* Buttons */
.view-all-btn, .view-details-btn, .add-member-btn, .add-task-btn {
  width: 100%;
  padding: 12px;
  border: 1px solid #3498db;
  background: transparent;
  color: #3498db;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.view-all-btn:hover, .view-details-btn:hover, .add-member-btn:hover, .add-task-btn:hover {
  background: #3498db;
  color: white;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.empty-state i {
  font-size: 3rem;
  color: #bdc3c7;
  margin-bottom: 15px;
  display: block;
}

.empty-state h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.empty-state p {
  margin: 0;
  font-size: 0.9rem;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .quick-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .quick-action-btn {
    flex: 1;
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .budget-summary {
    grid-template-columns: 1fr;
  }
  
  .team-list {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .approval-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .approval-actions {
    width: 100%;
  }
  
  .approval-actions button {
    flex: 1;
  }
}

@media (max-width: 480px) {
  .dashboard-card {
    padding: 15px;
  }
  
  .stat-card {
    padding: 15px;
  }
  
  .quick-actions {
    flex-direction: column;
  }
  
  .task-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .task-priority {
    align-self: flex-start;
  }
}
</style>