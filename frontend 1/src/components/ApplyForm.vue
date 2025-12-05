<template>
  <div class="apply-form-container">
    <div class="apply-form">
      <h3>Apply for a Job</h3>
      <form @submit.prevent="submitApplication">
        <div class="form-group">
          <label for="name">Full Name</label>
          <input type="text" id="name" v-model="formData.name" required />
        </div>
        <div class="form-group">
          <label for="age">Age</label>
          <input type="number" id="age" v-model="formData.age" required />
        </div>
        <div class="form-group">
          <label for="job">Select Job</label>
          <select id="job" v-model="formData.job" required>
            <option value="">-- Select a Job --</option>
            <option value="robotics-instructor-one">Robotics Instructor Level1</option>
            <option value="robotics-instructor-two">Robotics Instructor Level2</option>
            <option value="academic-coordinator">Academic Coordinator</option>
            <option value="manager">Manager</option>
            <option value="hr">HR</option>
            <option value="bda">BDA</option>
          </select>
        </div>
        <div class="form-group">
          <label for="resume">Upload Resume</label>
          <input type="file" id="resume" @change="handleFileUpload" required />
        </div>
        <button type="submit">Submit Application</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';

const formData = reactive({
  name: '',
  age: null,
  job: '',
  resume: null
});

function handleFileUpload(event) {
  formData.resume = event.target.files[0];
}

function submitApplication() {
  // Handle form submission logic here
  console.log('Form Data:', formData);
  alert('Application submitted successfully!');
}
</script>

<style scoped>
.apply-form-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  height: 100%;
}

.apply-form {
  background-color: #ffffff;
  padding: 30px;
  border-radius: 8px;
  width: 500px;
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

input[type="text"],
input[type="number"],
select,
input[type="file"] {
  width: 100%;
  padding: 12px;
  border: 1px solid #bdc3c7;
  border-radius: 5px;
  box-sizing: border-box;
  transition: border-color 0.2s ease;
}

input:focus,
select:focus {
  outline: none;
  border-color: #3498db;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

button:hover {
  background-color: #2980b9;
}
</style>
