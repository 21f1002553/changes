<template>
  <form @submit.prevent="submitEOD">
    <h3>Teacher End-of-Day Report</h3>
    <textarea v-model="eodData.classesTaught" placeholder="Enter details about classes taught today..." required></textarea>
    <textarea v-model="eodData.studentProgress" placeholder="Summarize student progress and any issues..." required></textarea>
    <button type="submit" class="action-btn">Submit EOD</button>
  </form>
</template>

<script setup>
import { ref } from 'vue';

const eodData = ref({ classesTaught: '', studentProgress: '' });

const submitEOD = () => {
  console.log('Submitting Teacher EOD:', eodData.value);
  // Logic to save the EOD data
};
</script>

<style scoped>
form { display: flex; flex-direction: column; gap: 15px; padding: 20px; border: 1px solid #e9eef2; border-radius: 8px; }
h3 { font-size: 1.3rem; font-weight: 600; margin-bottom: 10px; }
textarea { padding: 12px; border: 1px solid #ccc; border-radius: 5px; font-size: 1rem; min-height: 100px; }
.action-btn { padding: 12px 18px; border: none; border-radius: 5px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background-color 0.3s ease; background-color: #28a745; color: #fff; }
</style>
