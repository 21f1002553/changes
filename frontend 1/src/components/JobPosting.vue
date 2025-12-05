<template>
  <div class="job-posting-container">
    <div class="job-posting-content">
      <div class="ai-section">
        <span>AI</span>
        <input type="text" v-model="jobTitleInput" placeholder="e.g., Robotics Instructor" />
        <button @click="generateDescription" class="generate-btn">Generate</button>
      </div>

      <div v-if="jobDescription" class="description-output-section">
        <textarea v-model="jobDescription" rows="15"></textarea>
      </div>

      <div class="upload-section" @click="downloadDescription" :class="{ disabled: !jobDescription }">
        <div class="download-icon">
          <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Noun_Project_cloud_download_icon_411601_cc.svg/1024px-Noun_Project_cloud_download_icon_411601_cc.svg.png" alt="Download Icon" />
        </div>
        <span>Download your job description</span>
      </div>

      <div class="job-portals">
        <a href="#"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/LinkedIn_logo_initials.png/600px-LinkedIn_logo_initials.png" alt="LinkedIn"></a>
        <a href="#"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Indeed_logo.svg/2560px-Indeed_logo.svg.png" alt="Indeed"></a>
        <a href="#"><img src="https://static.naukimg.com/s/4/100/i/naukri_Logo.png" alt="Naukri"></a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const jobTitleInput = ref('');
const jobDescription = ref('');

const hardcodedDescription = `Job Title: Robotics Instructor

Company: SE Team 18 Company

Location: [chennai, Madras]

About Us:
SE Team 18  is a leading provider of STEM education, dedicated to inspiring the next generation of engineers, programmers, and scientists. We believe in hands-on learning and provide a fun, engaging environment where students can explore the exciting world of robotics.

Job Summary:
We are seeking a passionate and energetic Robotics Instructor to lead our after-school programs and workshops. The ideal candidate will have a strong interest in robotics and a talent for working with children and teenagers. You will be responsible for delivering our curriculum, guiding students through robot builds, and fostering a collaborative and creative classroom atmosphere.

Key Responsibilities:
- Deliver engaging, hands-on robotics lessons to students aged 8-16.
- Assist students in assembling, programming, and troubleshooting robots using kits like LEGO Mindstorms, VEX, or Arduino.
- Manage classroom dynamics to ensure a safe, positive, and productive learning environment.
- Prepare and maintain classroom materials, equipment, and robotics kits.
- Provide constructive feedback to students to encourage their growth and problem-solving skills.

Qualifications:
- Strong interest and basic knowledge of robotics, electronics, or programming.
- Experience working with children or in an educational setting is highly preferred.
- Excellent communication and interpersonal skills.
- Ability to explain complex concepts in a simple and understandable way.
- Currently pursuing or completed a degree in Engineering, Computer Science, Education, or a related field is a plus.`;

const generateDescription = () => {
  if (jobTitleInput.value.trim() !== '') {
    jobDescription.value = hardcodedDescription;
  }
};

const downloadDescription = () => {
  if (!jobDescription.value) {
    return; // Do nothing if there is no description
  }

  const blob = new Blob([jobDescription.value], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'job-description.txt';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
</script>

<style scoped>
.job-posting-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  height: 100%;
}

.job-posting-content {
  background-color: #ffffff;
  padding: 40px;
  border-radius: 8px;
  width: 800px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.ai-section {
  display: flex;
  align-items: center;
  border: 1px solid #bdc3c7;
  padding: 10px;
  border-radius: 5px;
}

.ai-section span {
  padding-right: 15px;
  border-right: 1px solid #bdc3c7;
  font-weight: 600;
  color: #2c3e50;
}

.ai-section input {
  flex-grow: 1;
  padding-left: 15px;
  border: none;
  outline: none;
  font-size: 1rem;
}
.ai-section .generate-btn {
  padding: 10px 20px;
  border: none;
  background-color: #3498db;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s ease;
}
.ai-section .generate-btn:hover {
  background-color: #2980b9;
}

.upload-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  cursor: pointer;
}
.upload-section.disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.description-output-section textarea {
  width: 100%;
  padding: 15px;
  border: 1px solid #bdc3c7;
  border-radius: 5px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 0.95rem;
  line-height: 1.6;
  resize: vertical;
  box-sizing: border-box;
}

.download-icon img {
  width: 60px;
  height: 60px;
}

.upload-section span {
  color: #34495e;
  font-weight: 500;
}

.job-portals {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 30px;
}

.job-portals img {
  width: 50px;
  height: 50px;
  transition: transform 0.2s ease;
}

.job-portals img:hover {
  transform: scale(1.1);
}
</style>
