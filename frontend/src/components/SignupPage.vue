<template>
  <div class="background-img">
    <div class="auth-page">
      <div class="auth-card">
        <h2>Create account</h2>
        <p class="muted">Sign up HrM Solutions</p>
        <form @submit.prevent="signUpUser">
          <label>Full Name</label>
          <input v-model="name" type="text" placeholder="Your name" autocomplete="name" required minlength="3" maxlength="100" />

          <label>Email</label>
          <input v-model="email" type="email" placeholder="you@company.com" autocomplete="email" required />

          <label>Password</label>
          <input v-model="password" type="password" placeholder="Choose a password" autocomplete="new-password" required minlength="4" maxlength="20" />

          <label>Role</label>
          <select v-model="selected_role_id" required>
            <option disabled value="">Select role</option>
            <option v-for="role in roles" :key="role.id" :value="role.id">{{ role.name }}</option>
          </select>

          <div class="actions">
            <button class="primary" type="submit">Sign up</button>
            <button type="button" class="link" @click="goLogin">Already have an account?</button>
          </div>
        </form>
        <p v-if="message" class="alert alert-success">{{ message }}</p>
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Signup',
  data() {
    return {
      name: '',
      email: '',
      password: '',
      selected_role_id: '',
      roles: [],
      message: '',
      errorMessage: ''
    };
  },
  created() {
    // Fetch roles from backend when component is mounted
    fetch('/api/roles')
      .then(res => res.json())
      .then(data => {
        this.roles = data;
      })
      .catch(() => {
        this.errorMessage = 'Failed to load roles';
      });
  },
  methods: {
    async signUpUser() {
      this.message = '';
      this.errorMessage = '';

      // Make sure a role was selected
      const selectedRole = this.roles.find(role => String(role.id) === String(this.selected_role_id));
      if (!selectedRole) {
        this.errorMessage = 'Please select a role.';
        return;
      }

      // Send role_id to backend
      const payload = {
        name: this.name,
        email: this.email,
        password: this.password,
        role_id: this.selected_role_id
      };

      try {
        const res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) {
          this.errorMessage = data.error || data.message || 'Signup failed.';
          return;
        }
        this.message = data.message;
        alert(this.message);
        this.name = '';
        this.email = '';
        this.password = '';
        this.selected_role_id = '';
        this.$router.push('/login');
      } catch (err) {
        this.errorMessage = 'Signup failed. Server error.';
      }
    },
    goLogin() {
      this.$router.push('/login');
    }
  }
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
  display: flex;
  align-items: center;
  justify-content: center;
}
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100vw;
  height: 100vh;
}
.auth-card {
  width: 420px;
  background: rgba(255,255,255,0.95);
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.08);
  text-align: center;
}
label { display:block; font-size:0.9rem; margin-top:12px; }
input, select { width:100%; padding:10px 12px; margin-top:6px; border-radius:8px; border:1px solid #e6e9ee; }
.actions { display:flex; gap:12px; align-items:center; margin-top:18px; }
.primary { flex:1; background:#2d8cff; color:#fff; border:none; padding:10px 14px; border-radius:8px; cursor:pointer; }
.link { background:transparent; border:none; color:#2d8cff; cursor:pointer; }
.muted { color:#7b8a95; margin-bottom:18px; }
.error { color:#c0392b; margin-top:12px; }
.alert { margin-top:12px; }
</style>
