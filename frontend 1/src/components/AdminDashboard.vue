<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Welcome, {{ adminName }}!</h1>
      <button @click="logout" class="logout-btn">Logout</button>
    </div>
    <div class="dashboard-cards">
      <div class="dashboard-card" v-for="card in statCards" :key="card.label">
        <div class="card-title">{{ card.label }}</div>
        <div class="card-value">{{ card.value }}</div>
      </div>
    </div>
    <!-- You can add tables, user management, and more widgets here -->
  </div>
</template>

<script>
export default {
  name: "AdminDashboard",
  data() {
    return {
      adminName: localStorage.getItem("userName") || "Admin",
      statCards: [
        { label: "Total Users", value: 128 },       // Example stats, fetch in mounted()
        { label: "New Signups", value: 5 },
        { label: "Open Jobs", value: 9 },
        { label: "Reports", value: 3 }
      ]
    };
  },
  methods: {
    logout() {
      localStorage.clear();
      this.$router.push("/login");
    },
    // Optionally: Fetch dashboard metrics from backend in mounted()
  }
};
</script>

<style scoped>
.dashboard {
  max-width: 1100px; 
  margin: 40px auto; 
  background: #fff; 
  border-radius: 18px; 
  box-shadow: 0 4px 16px rgba(30,34,90,0.06);
  padding: 40px 40px 80px;
}
.dashboard-header {
  display: flex; 
  justify-content: space-between; 
  align-items: center;
}
.logout-btn {
  background: #c0392b;
  color: #fff;
  border: none;
  padding: 10px 22px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}
.dashboard-cards {
  display: flex;
  flex-wrap: wrap;
  margin-top: 32px;
  gap: 24px;
}
.dashboard-card {
  flex: 1 1 180px;
  background: #f5f8fa;
  border-radius: 11px;
  padding: 26px 22px 22px 18px;
  box-shadow: 0 3px 12px rgba(80,80,180,0.03);
  min-width: 160px;
}
.card-title {
  font-size: 1rem;
  color: #6a768b;
  margin-bottom: 7px;
}
.card-value {
  font-size: 2.1rem;
  font-weight: 700;
  color: #25386f;
}
</style>
