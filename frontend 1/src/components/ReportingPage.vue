<template>
  <div class="reporting-page">
    <header class="page-header">
      <h1>Reports Dashboard</h1>
      <p>Manage leave, payroll, and daily end-of-day reports.</p>
    </header>

    <!-- EOD Form Section -->
    <div class="reporting-section">
      <h2>Submit Your End-of-Day Report</h2>
      <div class="user-role-selector">
        <span>Select Your Role:</span>
        <label><input type="radio" v-model="userRole" value="teacher"> Teacher</label>
        <label><input type="radio" v-model="userRole" value="admin"> Admin</label>
      </div>
      <component :is="eodFormComponent" />
    </div>

    <!-- Leave & Salary Management -->
    <div class="reporting-section">
      <h2>Salary and Leave Adjustment</h2>
      <div class="content-wrapper">
        <div class="form-container">
          <form @submit.prevent="adjustLeave">
            <input type="text" placeholder="Employee ID/Name" v-model="leaveAdjustment.employee" required>
            <select v-model="leaveAdjustment.leaveType" required>
              <option disabled value="">Select Leave Type</option>
              <option>Sick</option>
              <option>Casual</option>
              <option>LOP</option>
            </select>
            <input type="number" placeholder="Days Taken" v-model.number="leaveAdjustment.days" required min="0">
            <button type="submit" class="action-btn">Calculate & Update</button>
          </form>
          <div v-if="leaveUpdate.employee" class="calculation-output">
            <h4>Adjustment Details:</h4>
            <p><strong>Employee:</strong> {{ leaveUpdate.employee }}</p>
            <p><strong>Remaining Leave:</strong> {{ leaveUpdate.remainingLeave }} days</p>
            <p><strong>Salary Deduction:</strong> ${{ leaveUpdate.deduction }}</p>
          </div>
        </div>
        <div class="leave-history">
          <h4>Leave History</h4>
          <table class="data-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Date</th>
                <th>Type</th>
                <th>Days</th>
                <th>Deduction</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in leaveHistory" :key="item.id">
                <td>{{ item.employee }}</td>
                <td>{{ item.date }}</td>
                <td>{{ item.type }}</td>
                <td>{{ item.days }}</td>
                <td>${{ item.deduction }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Employee Daily EOD Tracking -->
    <div class="reporting-section">
      <h2>Employee EOD Tracking</h2>
      <div class="eod-filters">
        <input type="date" v-model="eodFilters.startDate">
        <input type="date" v-model="eodFilters.endDate">
        <input type="text" placeholder="Employee Name/ID" v-model="eodFilters.employee">
        <select v-model="eodFilters.role">
          <option>All Roles</option>
          <option>Teacher</option>
          <option>Admin</option>
        </select>
        <button @click="filterEODs" class="action-btn">Filter</button>
      </div>
      <div class="eod-summary-view">
        <table class="data-table">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Role</th>
              <th>Date</th>
              <th>Time</th>
              <th>Summary</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="eod in filteredEodSubmissions" :key="eod.id">
              <td>{{ eod.employee }}</td>
              <td>{{ eod.role }}</td>
              <td>{{ eod.date }}</td>
              <td>{{ eod.time }}</td>
              <td>{{ eod.summary }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import TeacherEODForm from './TeacherEODForm.vue';
import AdminEODForm from './AdminEODForm.vue';

// EOD Form
const userRole = ref('teacher');
const eodFormComponent = computed(() => {
  return userRole.value === 'teacher' ? TeacherEODForm : AdminEODForm;
});

// Leave & Salary Management
const leaveAdjustment = ref({ employee: '', leaveType: '', days: 0 });
const leaveUpdate = ref({ employee: '', remainingLeave: 0, deduction: 0 });
const leaveHistory = ref([
  { id: 1, employee: 'John Doe', date: '2024-07-15', type: 'LOP', days: 2, deduction: 200 },
  { id: 2, employee: 'Jane Smith', date: '2024-07-12', type: 'Sick', days: 1, deduction: 0 },
  { id: 3, employee: 'John Doe', date: '2024-06-20', type: 'Casual', days: 1, deduction: 0 },
]);

const adjustLeave = () => {
  leaveUpdate.value.employee = leaveAdjustment.value.employee;
  leaveUpdate.value.remainingLeave = 20 - leaveAdjustment.value.days; // Example
  leaveUpdate.value.deduction = leaveAdjustment.value.leaveType === 'LOP' ? leaveAdjustment.value.days * 100 : 0; // Example
  // Add to history
  leaveHistory.value.unshift({ id: Date.now(), ...leaveAdjustment.value, deduction: leaveUpdate.value.deduction });
};

// EOD Tracking
const eodFilters = ref({ startDate: '', endDate: '', employee: '', role: 'All Roles' });
const allEodSubmissions = ref([
    { id: 1, employee: 'Alice', role: 'Teacher', date: '2024-07-28', time: '17:30', summary: 'Taught Math and Science...' },
    { id: 2, employee: 'Bob', role: 'Admin', date: '2024-07-28', time: '17:45', summary: 'Processed payroll...' },
    { id: 3, employee: 'Charlie', role: 'Teacher', date: '2024-07-27', time: '18:00', summary: 'Conducted parent-teacher meetings...' },
    { id: 4, employee: 'Alice', role: 'Teacher', date: '2024-07-26', time: '17:35', summary: 'Graded assignments...' },
]);
const filteredEodSubmissions = ref([...allEodSubmissions.value]);

const filterEODs = () => {
  filteredEodSubmissions.value = allEodSubmissions.value.filter(eod => {
    const filter = eodFilters.value;
    const employeeMatch = filter.employee ? eod.employee.toLowerCase().includes(filter.employee.toLowerCase()) : true;
    const roleMatch = filter.role !== 'All Roles' ? eod.role === filter.role : true;
    const dateMatch = filter.startDate && filter.endDate ? (eod.date >= filter.startDate && eod.date <= filter.endDate) : true;
    return employeeMatch && roleMatch && dateMatch;
  });
};
</script>

<style scoped>
.reporting-page { padding: 30px; background-color: #f4f7fa; }
.page-header { text-align: center; margin-bottom: 40px; }
.page-header h1 { font-size: 2.2rem; font-weight: 700; color: #333; }
.page-header p { font-size: 1.1rem; color: #666; }

.reporting-section { background-color: #fff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); padding: 25px; margin-bottom: 30px; }
.reporting-section h2 { font-size: 1.6rem; font-weight: 600; margin-bottom: 20px; }

.content-wrapper { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
.form-container, .leave-history { padding: 20px; border: 1px solid #e9eef2; border-radius: 8px; }

form { display: flex; flex-direction: column; gap: 15px; }
input, select { padding: 12px; border: 1px solid #ccc; border-radius: 5px; font-size: 1rem; }
.action-btn { padding: 12px 18px; border: none; border-radius: 5px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background-color 0.3s ease; background-color: #007bff; color: #fff; }

.calculation-output { margin-top: 20px; padding: 15px; background-color: #e9f5ff; border-left: 4px solid #007bff; }

.eod-filters { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px; }

.user-role-selector { margin-bottom: 20px; display: flex; align-items: center; gap: 15px; }
.user-role-selector span { font-weight: 600; }

.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 12px 15px; border: 1px solid #e0e0e0; text-align: left; }
.data-table thead { background-color: #f7f9fc; }
.data-table th { font-weight: 600; }
.data-table tbody tr:nth-child(even) { background-color: #fdfdfd; }
</style>
