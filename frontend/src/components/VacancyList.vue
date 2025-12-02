<template>
  <div class="vacancy-list-container">
    <div class="card vacancy-form-card">
      <h3>Vacancy List</h3>
      <form @submit.prevent="submitVacancy">
        <div class="form-group">
          <label for="location">Select location</label>
          <select id="location" v-model="newVacancy.location" required>
            <option value="">-- Select --</option>
            <option value="Amritsar">Amritsar</option>
            <option value="Chandigarh">Chandigarh</option>
            <option value="Jaipur">Jaipur</option>
          </select>
        </div>
        <div class="form-group">
          <label for="school">Select School</label>
          <select id="school" v-model="newVacancy.school" required>
            <option value="">-- Select --</option>
            <option value="St John's school">St John's school</option>
            <option value="St Michael's school">St Michael's school</option>
            <option value="Sacred Heart convent school">Sacred Heart convent school</option>
          </select>
        </div>
        <div class="form-group">
          <label for="vacancy-count">Number of Vacancies</label>
          <input type="number" id="vacancy-count" v-model.number="newVacancy.count" min="1" required />
        </div>
        <button type="submit" class="submit-btn">Add Vacancy</button>
      </form>
    </div>

    <div class="card current-vacancies-card">
      <h3>Current Open Vacancies</h3>
      <div v-if="currentVacancies.length === 0" class="no-vacancies">
        <p>No open vacancies at the moment. Add new ones using the form above!</p>
      </div>
      <div v-else class="table-responsive">
        <table class="vacancies-table">
          <thead>
            <tr>
              <th>Location</th>
              <th>School</th>
              <th>Count</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="vacancy in currentVacancies" :key="vacancy.id">
              <td>{{ vacancy.location }}</td>
              <td>{{ vacancy.school }}</td>
              <td>{{ vacancy.count }}</td>
              <td><span class="status-tag open">Open</span></td>
              <td>
                <button @click="closeVacancy(vacancy.id)" class="close-btn">Close</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const newVacancy = ref({
  location: '',
  school: '',
  count: 1,
});

const currentVacancies = ref([
  // Example initial data
  { id: 1, location: 'Amritsar', school: 'St John\'s school', count: 2, status: 'Open' },
  { id: 2, location: 'Chandigarh', school: 'St Michael\'s school', count: 1, status: 'Open' },
]);

const submitVacancy = () => {
  if (newVacancy.value.location && newVacancy.value.school && newVacancy.value.count > 0) {
    currentVacancies.value.push({
      id: Date.now(), // Simple unique ID
      ...newVacancy.value,
      status: 'Open',
    });
    // Reset form
    newVacancy.value = { location: '', school: '', count: 1 };
  }
};

const closeVacancy = (id) => {
  currentVacancies.value = currentVacancies.value.filter(vacancy => vacancy.id !== id);
};
</script>

<style scoped>
.vacancy-list-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 30px; /* Space between form and list */
  padding: 20px;
  flex-wrap: wrap; /* Allow wrapping on smaller screens */
}

.card {
  background-color: #ffffff;
  padding: 30px;
  border-radius: 8px;
  flex: 1; /* Allow cards to grow */
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

h3 {
  text-align: center;
  margin-bottom: 25px;
  color: #2c3e50;
  font-size: 1.6rem;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #34495e;
  font-weight: 500;
}

select,
input {
  width: 100%;
  padding: 12px;
  border: 1px solid #bdc3c7;
  border-radius: 5px;
  box-sizing: border-box;
  transition: border-color 0.2s ease;
}

select:focus,
input:focus {
  outline: none;
  border-color: #3498db;
}

.submit-btn {
  width: 100%;
  padding: 12px 18px;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
  background-color: #28a745; /* Green for add */
  color: #fff;
  margin-top: 15px;
}

.submit-btn:hover {
  background-color: #218838;
}

.current-vacancies-card {
  min-width: 450px; /* Ensure it doesn't get too small */
}

.no-vacancies {
  text-align: center;
  color: #666;
  padding: 20px;
  border: 1px dashed #ccc;
  border-radius: 8px;
}

.table-responsive {
  overflow-x: auto;
}

.vacancies-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.vacancies-table th,
.vacancies-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #e0e0e0;
  text-align: left;
}

.vacancies-table th {
  background-color: #f7f9fc;
  font-weight: 600;
}

.status-tag {
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}
.status-tag.open { background-color: #d4edda; color: #28a745; } /* Green for open */

.close-btn { background-color: #dc3545; color: white; border: none; padding: 8px 12px; border-radius: 5px; cursor: pointer; transition: background-color 0.2s ease; }
.close-btn:hover { background-color: #c82333; }

@media (max-width: 768px) {
  .vacancy-list-container {
    flex-direction: column;
    align-items: center;
  }
  .vacancy-form-card, .current-vacancies-card {
    width: 100%;
    max-width: 450px; /* Constrain width on smaller screens */
  }
}
</style>
