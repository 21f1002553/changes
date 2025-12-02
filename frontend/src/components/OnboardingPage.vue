<template>
  <div class="onboarding-page">
    <div class="progress-tracker">
      <h3>Onboarding Progress</h3>
      <div class="progress-bar">
        <div class="progress" :style="{ width: progress + '%' }"></div>
      </div>
      <span>{{ progress }}% Complete</span>
    </div>

    <div class="onboarding-tabs">
      <div class="tab-headers">
        <button @click="currentTab = 'documents'" :class="{ active: currentTab === 'documents' }">Documents</button>
        <button @click="currentTab = 'forms'" :class="{ active: currentTab === 'forms' }">Forms</button>
        <button @click="currentTab = 'support'" :class="{ active: currentTab === 'support' }">Support</button>
      </div>

      <div class="tab-content">
        <div v-if="currentTab === 'documents'" class="document-section">
          <h2>Document Submission</h2>
          <div v-for="(doc, index) in documents" :key="index" class="document-item">
            <div class="doc-info">
              <span>{{ doc.name }}</span>
              <span :class="['status', doc.status.toLowerCase()]">{{ doc.status }}</span>
            </div>
            <div class="doc-actions">
              <button @click="uploadDocument(index)" :disabled="doc.status !== 'Required'" class="action-btn upload-btn">Upload</button>
              <button @click="verifyDocument(index)" :disabled="doc.status !== 'Uploaded'" class="action-btn verify-btn">Verify</button>
            </div>
          </div>
        </div>

        <div v-if="currentTab === 'forms'" class="forms-section">
          <div class="form-container">
            <h3>Offer Letter Generation (HR)</h3>
            <form @submit.prevent="generateOfferLetter">
              <input type="text" placeholder="CTC (e.g., $100,000)" required>
              <input type="text" placeholder="Designation (e.g., Software Engineer)" required>
              <input type="date" required>
              <button type="submit" class="action-btn">Generate PDF</button>
            </form>
          </div>
          <div class="form-container">
            <h3>Code of Conduct</h3>
            <div class="conduct-actions">
              <button class="action-btn">View/Sign on Portal</button>
              <button class="action-btn">Download Template</button>
              <button class="action-btn">Upload Signed Document</button>
            </div>
          </div>
        </div>

        <div v-if="currentTab === 'support'" class="support-section">
          <h2>AI Chatbot Support</h2>
          <div class="chat-widget">
            <div class="chat-history">
              <div v-for="(message, index) in chatMessages" :key="index" :class="['chat-message', message.sender]">
                {{ message.text }}
              </div>
            </div>
            <form @submit.prevent="sendChatMessage" class="chat-input">
              <input type="text" v-model="chatInput" placeholder="Ask a question...">
              <button type="submit" class="action-btn">Send</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const currentTab = ref('documents');

// Documents Tab
const documents = ref([
  { name: 'Passport Photo', status: 'Required' },
  { name: 'ID Proof', status: 'Required' },
  { name: 'Address Proof', status: 'Uploaded' },
  { name: 'Educational Certificates', status: 'Verified' },
]);

const uploadDocument = (index) => {
  documents.value[index].status = 'Uploaded';
};

const verifyDocument = (index) => {
  documents.value[index].status = 'Verified';
};

// Progress Calculation
const progress = computed(() => {
  const verifiedCount = documents.value.filter(doc => doc.status === 'Verified').length;
  return Math.round((verifiedCount / documents.value.length) * 100);
});

// Support Tab
const chatInput = ref('');
const chatMessages = ref([
  { sender: 'bot', text: 'Welcome to onboarding support! How can I help you?' },
]);

const sendChatMessage = () => {
  if (chatInput.value.trim() === '') return;
  chatMessages.value.push({ sender: 'user', text: chatInput.value });
  // Simulate a bot response
  setTimeout(() => {
    chatMessages.value.push({ sender: 'bot', text: 'Thanks for your question! An HR representative will get back to you shortly.' });
  }, 1000);
  chatInput.value = '';
};

const generateOfferLetter = (event) => {
  alert("Offer letter generation is a placeholder. In a real application, this would generate a PDF.");
  event.target.reset();
};
</script>

<style scoped>
/* General */
.onboarding-page { padding: 30px; background-color: #f4f7fa; }
.action-btn { padding: 10px 15px; border: none; border-radius: 5px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: background-color 0.3s ease; }

/* Progress Tracker */
.progress-tracker { margin-bottom: 30px; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
.progress-tracker h3 { font-size: 1.4rem; font-weight: 600; margin-bottom: 15px; }
.progress-bar { width: 100%; height: 20px; background-color: #e9eef2; border-radius: 10px; overflow: hidden; }
.progress { height: 100%; background-color: #28a745; transition: width 0.3s ease; }
.progress-tracker span { display: block; margin-top: 10px; font-size: 0.9rem; font-weight: 500; }

/* Tabs */
.onboarding-tabs { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
.tab-headers { display: flex; margin-bottom: 20px; border-bottom: 2px solid #e9eef2; }
.tab-headers button { padding: 10px 20px; border: none; background-color: transparent; font-size: 1.1rem; font-weight: 600; cursor: pointer; transition: color 0.3s ease, border-bottom 0.3s ease; color: #666; border-bottom: 2px solid transparent; }
.tab-headers button.active { color: #007bff; border-bottom: 2px solid #007bff; }
.tab-content h2 { font-size: 1.5rem; font-weight: 600; margin-bottom: 20px; }

/* Documents Section */
.document-item { display: flex; justify-content: space-between; align-items: center; padding: 15px; border-bottom: 1px solid #e9eef2; }
.doc-info .status { margin-left: 15px; padding: 5px 10px; border-radius: 15px; font-weight: 600; color: #fff; }
.doc-info .status.required { background-color: #dc3545; }
.doc-info .status.uploaded { background-color: #ffc107; }
.doc-info .status.verified { background-color: #28a745; }
.doc-actions .upload-btn { background-color: #007bff; color: #fff; }
.doc-actions .verify-btn { background-color: #28a745; color: #fff; }
.doc-actions button:disabled { background-color: #ccc; }

/* Forms Section */
.forms-section .form-container { margin-bottom: 30px; }
.forms-section h3 { font-size: 1.2rem; font-weight: 600; margin-bottom: 15px; }
.forms-section form { display: flex; gap: 15px; }
.forms-section input { padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
.conduct-actions { display: flex; gap: 15px; }
.conduct-actions .action-btn { background-color: #17a2b8; color: #fff; }

/* Support Section */
.chat-widget { border: 1px solid #e9eef2; border-radius: 8px; overflow: hidden; }
.chat-history { height: 300px; padding: 15px; overflow-y: auto; background-color: #f4f7fa; }
.chat-message { margin-bottom: 10px; padding: 10px; border-radius: 8px; max-width: 80%; }
.chat-message.user { background-color: #007bff; color: #fff; align-self: flex-end; margin-left: auto; }
.chat-message.bot { background-color: #e9eef2; color: #333; }
.chat-input { display: flex; padding: 15px; border-top: 1px solid #e9eef2; }
.chat-input input { flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
.chat-input button { margin-left: 10px; background-color: #007bff; color: #fff; }
</style>
