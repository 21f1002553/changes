<template>
  <div class="training-page">
    <header class="page-header">
      <h1>Your Training Journey</h1>
      <p>Follow the path to enhance your skills and knowledge.</p>
    </header>

    <div class="learning-path">
      <div v-for="(module, index) in modules" :key="module.id" class="module-card" :class="[module.status.toLowerCase(), { active: expandedModule === module.id }]" @click="toggleModule(module.id)">
        <div class="module-header">
          <h3>{{ module.title }}</h3>
          <div class="status-indicator">{{ module.status }}</div>
        </div>
        <div v-if="expandedModule === module.id" class="module-content">
          <p>{{ module.description }}</p>
          <!-- More content will be added here based on the plan -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const expandedModule = ref(null);
const modules = ref([
  { id: 1, title: 'Module 1: Introduction to Company Policies', description: 'Understanding the company culture, policies, and procedures.', status: 'Completed' },
  { id: 2, title: 'Module 2: Technical Skills Development', description: 'In-depth training on the technical aspects of your role.', status: 'In Progress' },
  { id: 3, title: 'Module 3: Mentorship with a Senior Teacher', description: 'One-on-one sessions with a senior teacher for personalized guidance.', status: 'Pending' },
  { id: 4, title: 'Module 4: Self-Paced Practice Projects', description: 'Hands-on projects to apply your skills.', status: 'Pending' },
  { id: 5, title: 'Module 5: Soft Skills Workshop', description: 'Developing communication, teamwork, and leadership skills.', status: 'Pending' },
]);

const toggleModule = (moduleId) => {
  expandedModule.value = expandedModule.value === moduleId ? null : moduleId;
};
</script>

<style scoped>
.training-page { padding: 30px; background-color: #f4f7fa; }
.page-header { text-align: center; margin-bottom: 40px; }
.page-header h1 { font-size: 2.2rem; font-weight: 700; color: #333; }
.page-header p { font-size: 1.1rem; color: #666; }

.learning-path { display: flex; flex-direction: column; gap: 20px; }
.module-card { background-color: #fff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); cursor: pointer; transition: all 0.3s ease; border-left: 5px solid; }

/* Status-based styling */
.module-card.completed { border-color: #28a745; }
.module-card.in-progress { border-color: #ffc107; }
.module-card.pending { border-color: #dc3545; }

.module-header { display: flex; justify-content: space-between; align-items: center; padding: 20px; }
.module-header h3 { font-size: 1.3rem; font-weight: 600; margin: 0; }
.status-indicator { padding: 6px 12px; border-radius: 20px; font-weight: 600; color: #fff; }

.completed .status-indicator { background-color: #28a745; }
.in-progress .status-indicator { background-color: #ffc107; }
.pending .status-indicator { background-color: #dc3545; }

.module-content { padding: 0 20px 20px; }
.module-content p { color: #555; }

.module-card.active { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.12); }
</style>
