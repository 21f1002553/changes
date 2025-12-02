<template>
  <form @submit.prevent="submitEOD">
    <h3>Admin End-of-Day Report</h3>
    <textarea v-model="eodData.reportsCompleted" placeholder="List the reports or administrative tasks completed today..." required></textarea>
    <textarea v-model="eodData.actionItems" placeholder="Outline any pending action items or follow-ups..." required></textarea>
    <button type="submit" class="action-btn">Submit EOD</button>
  </form>
</template>

<script setup>
import { ref } from 'vue';

const eodData = ref({ reportsCompleted: '', actionItems: '' });

const submitEOD = () => {
  console.log('Submitting Admin EOD:', eodData.value);
  // Logic to save the EOD data
};
</script>

<style scoped>
form { display: flex; flex-direction: column; gap: 15px; padding: 20px; border: 1px solid #e9eef2; border-radius: 8px; }
h3 { font-size: 1.3rem; font-weight: 600; margin-bottom: 10px; }
textarea { padding: 12px; border: 1px solid #ccc; border-radius: 5px; font-size: 1rem; min-height: 100px; }
.action-btn { padding: 12px 18px; border: none; border-radius: 5px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background-color 0.3s ease; background-color: #28a745; color: #fff; }
</style>
