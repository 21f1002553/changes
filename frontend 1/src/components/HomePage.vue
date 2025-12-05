<!-- HomePage.vue -->
<template>
  <div class="background-img">
    <div class="home-container text-center d-flex flex-column justify-content-center align-items-center">
      <h1 class="mb-4 text-white">Welcome to HRM Solution App</h1>
      <div>
        <router-link to="/login" class="btn btn-primary me-2">Login</router-link>
        <router-link to="/signup" class="btn btn-success">Signup</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomePage",
};
</script>

<style scoped>
.background-img {
  background-image: url('/hr.jpg');
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center center;
  min-height: 100vh;
  min-width: 100vw;
}

.home-container {
  padding: 2rem;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>
