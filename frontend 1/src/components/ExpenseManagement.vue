<template>
  <div class="expense-management-page">
    <!-- View Switcher -->
    <div class="view-switcher">
      <button @click="currentView = 'employee'" :class="{ active: currentView === 'employee' }">
        <i class="fas fa-user"></i> Employee View
      </button>
      <button @click="currentView = 'manager'" :class="{ active: currentView === 'manager' }">
        <i class="fas fa-user-tie"></i> Manager View
      </button>
    </div>

    <!-- ========================== -->
    <!--      EMPLOYEE VIEW         -->
    <!-- ========================== -->
    <div v-if="currentView === 'employee'" class="employee-view">
      <div class="grid-container">
        <!-- Real-Time Submission Form -->
        <div class="card submission-form">
          <h2><i class="fas fa-paper-plane"></i> Submit an Expense</h2>
          <form @submit.prevent="submitExpense">
            <div class="form-group">
              <label for="tripId">Trip Identifier</label>
              <input id="tripId" type="text" placeholder="e.g., Q4-Client-Summit" v-model="newExpense.tripId" required>
            </div>
            <div class="form-group">
              <label>Category</label>
              <div class="category-select">
                <button type="button" @click="newExpense.category = 'Travel'" :class="{active: newExpense.category === 'Travel'}"><i class="fas fa-plane"></i> Travel</button>
                <button type="button" @click="newExpense.category = 'Food'" :class="{active: newExpense.category === 'Food'}"><i class="fas fa-utensils"></i> Food</button>
                <button type="button" @click="newExpense.category = 'Supplies'" :class="{active: newExpense.category === 'Supplies'}"><i class="fas fa-pencil-alt"></i> Supplies</button>
              </div>
            </div>
            <div class="form-group">
              <label for="amount">Amount</label>
              <input id="amount" type="number" placeholder="$0.00" v-model.number="newExpense.amount" required>
            </div>
            <div class="form-group">
              <label for="description">Short Description</label>
              <textarea id="description" v-model="newExpense.description" placeholder="e.g., Dinner with client" rows="2"></textarea>
            </div>
            <div class="form-group">
              <label for="receipt-upload" class="receipt-upload-label">
                <i class="fas fa-camera"></i> Capture or Upload Receipt
              </label>
              <input type="file" id="receipt-upload" @change="handleReceiptUpload" accept="image/*" style="display: none;">
               <span v-if="newExpense.receipt" class="filename">{{ newExpense.receipt.name }}</span>
            </div>
            <button type="submit" class="submit-btn">Submit for Verification</button>
          </form>
        </div>

        <!-- Real-Time Summary Panel -->
        <div class="card summary-panel">
          <h2><i class="fas fa-chart-line"></i> Real-Time Summary</h2>
          <div class="summary-metric">
            <span>Today's Total Expenses</span>
            <strong class="value">${{ summary.todayTotal }}</strong>
          </div>
          <div class="summary-metric">
            <span>Trip Total ({{ newExpense.tripId || 'N/A' }})</span>
            <strong class="value">${{ summary.tripTotal }}</strong>
          </div>
          <div class="summary-metric">
            <span>Remaining Expense Limit</span>
            <strong class="value" :class="{ exceeded: summary.remainingLimit < 0 }">
              ${{ Math.abs(summary.remainingLimit) }}
              <span v-if="summary.remainingLimit < 0" class="exceeded-label">(Exceeded)</span>
            </strong>
          </div>
        </div>
      </div>

      <!-- Expense History -->
      <div class="card expense-history">
        <h2><i class="fas fa-history"></i> Your Recent Expenses</h2>
        <div class="table-responsive">
          <table class="expense-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Description</th>
                <th>Amount</th>
                <th>AI Status</th>
                <th>Approval Status</th>
                <th>Receipt</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(expense, index) in recentExpenses" :key="expense.id" :class="{ 'alt-row': index % 2 !== 0 }">
                <td><strong class="category-name">{{ expense.category }}</strong></td>
                <td>{{ expense.description }}</td>
                <td><strong class="amount">${{ expense.amount }}</strong></td>
                <td>
                  <span class="tag" :class="getAIStatusClass(expense.aiStatus)">
                    <i :class="getAIStatusIcon(expense.aiStatus)"></i> {{ expense.aiStatus }}
                  </span>
                </td>
                <td>
                  <span class="tag" :class="`status-${expense.status.toLowerCase()}`">{{ expense.status }}</span>
                </td>
                <td class="receipt-action">
                  <i class="fas fa-eye" @click="openDetailModal(expense)"></i>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ========================== -->
    <!--   MANAGER/HR/FINANCE VIEW  -->
    <!-- ========================== -->
    <div v-if="currentView === 'manager'" class="manager-view">
        <!-- Approval Queue -->
        <div class="card approval-queue">
            <h2><i class="fas fa-inbox"></i> Approval Queue</h2>
            <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Employee</th>
                            <th>Date</th>
                            <th>Category</th>
                            <th>Amount</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="expense in pendingExpenses" :key="expense.id" @click="openDetailModal(expense)">
                            <td>{{ expense.employee }}</td>
                            <td>{{ expense.date }}</td>
                            <td>{{ expense.category }}</td>
                            <td>${{ expense.amount }}</td>
                            <td>
                                <span class="status-badge" :class="`status-${expense.status.toLowerCase()}`">
                                    <i v-if="expense.policyFlag" class="fas fa-flag policy-flag" title="Policy Violation"></i>
                                    {{ expense.status }}
                                </span>
                            </td>
                            <td class="actions">
                                <button class="approve-btn"><i class="fas fa-check"></i> Approve</button>
                                <button class="reject-btn"><i class="fas fa-times"></i> Reject</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Audit & Reporting -->
        <div class="card audit-reporting">
            <h2><i class="fas fa-chart-pie"></i> Audit & Reporting</h2>
            <div class="filter-panel">
                <input type="date" v-model="filters.startDate">
                <input type="date" v-model="filters.endDate">
                <input type="text" placeholder="Employee Name" v-model="filters.employee">
                <button class="export-btn"><i class="fas fa-download"></i> Export Report</button>
            </div>
            <div class="reporting-grid">
                <div class="kpi-card">
                    <h4>Total Expenses (Month)</h4>
                    <p>$12,450</p>
                </div>
                 <div class="kpi-card">
                    <h4>Policy Violations</h4>
                    <p>3</p>
                </div>
                <div class="budget-graph">
                    <Bar :data="chartData" :options="chartOptions" />
                </div>
            </div>
        </div>
    </div>

    <!-- ========================== -->
    <!--      DETAIL MODAL          -->
    <!-- ========================== -->
    <div v-if="showDetailModal" class="modal-overlay" @click.self="showDetailModal = false">
        <div class="modal-content">
            <button class="close-modal" @click="showDetailModal = false">&times;</button>
            <h3>Expense Details</h3>
            <div v-if="selectedExpense">
                <p><strong>Employee:</strong> {{ selectedExpense.employee || 'N/A' }}</p>
                <p><strong>Amount:</strong> <span class="modal-amount">${{ selectedExpense.amount }}</span></p>
                <p><strong>Category:</strong> {{ selectedExpense.category }}</p>
                <p><strong>Date:</strong> {{ selectedExpense.date || new Date().toLocaleDateString() }}</p>
                <hr>
                <p><strong>AI Verification:</strong>
                    <span class="tag" :class="getAIStatusClass(selectedExpense.aiStatus)">
                        <i :class="getAIStatusIcon(selectedExpense.aiStatus)"></i> {{ selectedExpense.aiStatus }}
                    </span>
                    <span v-if="selectedExpense.policyFlag" class="tag status-rejected">
                        <i class="fas fa-flag"></i> Policy Violation
                    </span>
                </p>
                 <div class="receipt-image">
                    <p><strong>Receipt:</strong></p>
                    <img src="https://i.imgur.com/4q1wzHT.jpeg" alt="Receipt" />
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

// --- STATE MANAGEMENT ---
const currentView = ref('employee');
const showDetailModal = ref(false);
const selectedExpense = ref(null);

// --- EMPLOYEE VIEW STATE ---
const newExpense = ref({
  tripId: '',
  category: 'Travel',
  amount: null,
  description: '',
  receipt: null
});

const recentExpenses = ref([
    { id: 1, tripId: 'Q4-Client-Summit', category: 'Food', amount: 55, description: 'Team Lunch', status: 'Pending', aiStatus: 'Verified', receipt: 'receipt1.jpg' },
    { id: 2, tripId: 'Q4-Client-Summit', category: 'Travel', amount: 300, description: 'Flight Ticket', status: 'Pending', aiStatus: 'Processing', receipt: 'receipt2.jpg' },
    { id: 3, tripId: 'Internal-Training', category: 'Supplies', amount: 120, description: 'Whiteboard Markers', status: 'Approved', aiStatus: 'Verified', receipt: 'receipt3.jpg' },
]);

// --- MANAGER VIEW STATE ---
const allExpenses = ref([
  { id: 1, employee: 'John Doe', date: '2024-07-28', category: 'Food', amount: 55, status: 'Pending', policyFlag: false, aiStatus: 'Verified' },
  { id: 2, employee: 'Jane Smith', date: '2024-07-28', category: 'Travel', amount: 850, status: 'Pending', policyFlag: true, aiStatus: 'Flagged' },
  { id: 3, employee: 'John Doe', date: '2024-07-27', category: 'Supplies', amount: 75, status: 'Approved', policyFlag: false, aiStatus: 'Verified' },
  { id: 4, employee: 'Peter Jones', date: '2024-07-26', category: 'Food', amount: 150, status: 'Rejected', policyFlag: true, aiStatus: 'Flagged' },
]);
const filters = ref({ startDate: '', endDate: '', employee: '' });


// --- COMPUTED PROPERTIES ---
const summary = computed(() => {
  const today = new Date().toLocaleDateString();
  const todayTotal = recentExpenses.value
    .filter(exp => new Date().toLocaleDateString() === today)
    .reduce((total, exp) => total + exp.amount, 0);

  const tripTotal = newExpense.value.tripId
    ? recentExpenses.value
        .filter(exp => exp.tripId === newExpense.value.tripId)
        .reduce((total, exp) => total + exp.amount, 0)
    : 0;

  const budget = 2500; // Mock budget
  return {
    todayTotal,
    tripTotal,
    remainingLimit: budget - tripTotal
  };
});

const pendingExpenses = computed(() => allExpenses.value.filter(exp => exp.status === 'Pending'));


// --- METHODS ---
const handleReceiptUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    newExpense.value.receipt = file;
  }
};

const submitExpense = () => {
  if (!newExpense.value.category || !newExpense.value.amount) return;
  const submittedExpense = {
    ...newExpense.value,
    id: Date.now(),
    status: 'Pending',
    aiStatus: 'Processing'
  };
  recentExpenses.value.unshift(submittedExpense);
  // Reset form
  newExpense.value = { tripId: newExpense.value.tripId, category: 'Travel', amount: null, description: '', receipt: null };
};

const openDetailModal = (expense) => {
  selectedExpense.value = expense;
  showDetailModal.value = true;
};

const getAIStatusClass = (status) => {
    switch (status) {
        case 'Verified': return 'ai-verified';
        case 'Processing': return 'ai-processing';
        case 'Flagged': return 'ai-flagged';
        default: return '';
    }
};

const getAIStatusIcon = (status) => {
    switch (status) {
        case 'Verified': return 'fas fa-check-circle';
        case 'Processing': return 'fas fa-spinner fa-spin';
        case 'Flagged': return 'fas fa-exclamation-triangle';
        default: return 'fas fa-question-circle';
    }
};

// --- CHART.JS CONFIG ---
const chartData = ref({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
  datasets: [{
    label: 'Budget Usage',
    backgroundColor: 'rgba(0, 123, 255, 0.6)',
    borderColor: 'rgba(0, 123, 255, 1)',
    borderRadius: 4,
    data: [6500, 5900, 8000, 8100, 5600, 7200, 4000]
  }]
});
const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { beginAtZero: true },
    x: { grid: { display: false } }
  }
});

</script>

<style scoped>
/* ========================= */
/*      GENERAL & SETUP      */
/* ========================= */
:root {
  --primary-color: #007bff;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  --light-gray: #f0f2f5;
  --dark-gray: #6c757d;
  --text-color: #333;
  --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.expense-management-page {
  padding: 20px;
  background-color: var(--light-gray);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: var(--text-color);
}

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  padding: 25px;
  margin-bottom: 25px;
}

h2 {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--primary-color);
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
}

/* ========================= */
/*      VIEW SWITCHER        */
/* ========================= */
.view-switcher {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  background: #fff;
  padding: 8px;
  border-radius: 50px;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
}

.view-switcher button {
  padding: 12px 25px;
  border: none;
  background: transparent;
  color: var(--dark-gray);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 50px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.view-switcher button.active {
  background: var(--primary-color);
  color: rgb(5, 0, 0);
  box-shadow: 0 3px 8px rgba(0, 123, 255, 0.3);
}

/* ========================= */
/*      EMPLOYEE VIEW        */
/* ========================= */
.grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
}

.submission-form .form-group {
  margin-bottom: 20px;
}
.submission-form label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
}
.submission-form input, .submission-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
  transition: border-color 0.2s;
}
.submission-form input:focus, .submission-form textarea:focus {
  border-color: var(--primary-color);
  outline: none;
}

.category-select {
  display: flex;
  gap: 10px;
}
.category-select button {
  flex-grow: 1;
  padding: 12px;
  border: 1px solid #ccc;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.category-select button.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}
.receipt-upload-label {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  padding: 20px;
  border: 2px dashed #ccc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.receipt-upload-label:hover {
  background: #f8f9fa;
  border-color: var(--primary-color);
}

.submit-btn {
  width: 100%;
  padding: 15px;
  font-size: 1.1rem;
  font-weight: 700;
  background-color: var(--success-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.submit-btn:hover { background-color: #218838; }

.summary-panel .summary-metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 0;
  border-bottom: 1px solid #eee;
}
.summary-panel .summary-metric:last-child { border-bottom: none; }
.summary-panel .value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--primary-color);
}
.summary-panel .value.exceeded {
  color: var(--danger-color);
}
.exceeded-label {
  font-size: 0.8rem;
  font-weight: 600;
  vertical-align: middle;
}

.expense-table {
  width: 100%;
  border-collapse: collapse;
}
.expense-table th, .expense-table td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}
.expense-table th {
  background-color: #f7f9fc;
  font-weight: 700;
}
.expense-table .alt-row {
  background-color: #f7f9fc;
}
.category-name, .amount {
  font-weight: bold;
}
.receipt-action i {
  cursor: pointer;
  color: var(--primary-color);
  font-size: 1.2rem;
}

/* ========================= */
/*       MANAGER VIEW        */
/* ========================= */
.data-table {
    width: 100%;
    border-collapse: collapse;
}
.data-table th, .data-table td {
    padding: 12px 15px;
    border-bottom: 1px solid #e0e0e0;
    text-align: left;
}
.data-table tbody tr {
    cursor: pointer;
    transition: background-color 0.2s;
}
.data-table tbody tr:hover {
    background-color: #f7f9fc;
}
.policy-flag {
    color: var(--danger-color);
    margin-right: 5px;
}
.actions button {
    margin-right: 8px;
    padding: 6px 12px;
    border: none;
    border-radius: 5px;
    color: white;
    cursor: pointer;
    font-weight: 600;
}
.actions .approve-btn { background-color: var(--success-color); }
.actions .reject-btn { background-color: var(--danger-color); }

.filter-panel, .reporting-grid {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}
.filter-panel input { padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
.export-btn {
    background-color: #17a2b8;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    font-weight: 600;
}
.kpi-card {
    flex: 1;
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
}
.kpi-card p {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary-color);
}
.budget-graph {
    flex-basis: 100%;
    min-height: 250px;
}

/* ========================= */
/*      TAGS & STATUSES      */
/* ========================= */
.tag, .status-badge {
    padding: 5px 12px;
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: capitalize;
}
.tag i, .status-badge i {
    margin-right: 5px;
}

/* AI Status */
.ai-verified { background-color: #d4edda; color: #155724; }
.ai-processing { background-color: #e2e3e5; color: #383d41; }
.ai-flagged { background-color: #f8d7da; color: #721c24; }

/* Approval Status */
.status-pending, .status-needs-review { background-color: #fff3cd; color: #856404; }
.status-approved { background-color: #d4edda; color: #155724; }
.status-rejected { background-color: #f8d7da; color: #721c24; }


/* ========================= */
/*          MODAL            */
/* ========================= */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}
.modal-content {
    background: white;
    padding: 30px;
    border-radius: 12px;
    width: 90%;
    max-width: 550px;
    position: relative;
}
.close-modal {
    position: absolute;
    top: 15px;
    right: 15px;
    background: none;
    border: none;
    font-size: 1.8rem;
    cursor: pointer;
    color: #999;
}
.modal-amount {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-color);
}
.receipt-image img {
    width: 100%;
    border-radius: 8px;
    margin-top: 15px;
    border: 1px solid #ddd;
}

/* ========================= */
/*      RESPONSIVENESS       */
/* ========================= */
@media (max-width: 992px) {
  .grid-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .view-switcher {
    border-radius: 10px;
    flex-direction: column;
  }
  .view-switcher button {
    border-radius: 10px;
  }
  .filter-panel {
    flex-direction: column;
  }
}
</style>
