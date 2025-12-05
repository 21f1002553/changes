<template>
  <div class="background-img">
    <div class="auth-page">
      <div class="auth-card">
        <h2>Login</h2>
        <p class="muted">Sign in to your account to access the HR Dashboard.</p>
        <form @submit.prevent="loginUser">
          <label for="email">Email</label>
          <input type="email" id="email" v-model="email" placeholder="Email" autocomplete="email" required />
          <label for="password">Password</label>
          <input type="password" id="password" v-model="password" placeholder="Password" autocomplete="current-password"
            required />
          <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
          <button class="primary" type="submit">Login</button>
          <button type="button"
            style="margin-top: 15px; background:transparent; border:none; color:#2d8cff; cursor:pointer"
            @click="goSignup">Don't have an account? Sign up</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
      errorMessage: null,
    };
  },
  methods: {
    async loginUser() {
      this.errorMessage = null;
      const payload = {
        email: this.email,
        password: this.password,
      };
      try {
        const response = await fetch("/api/auth/login", {
          method: "POST",
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });
        const result = await response.json();
        if (!response.ok) {
          this.errorMessage = result.message || "Login Failed";
        } else {
          alert("Login Successful");
          // Store tokens
          localStorage.setItem("access_token", result.access_token);
          localStorage.setItem("refresh_token", result.refresh_token);
          localStorage.setItem("userRole", result.user.role_name);
          localStorage.setItem("userName", result.user.name);
          localStorage.setItem("userId", result.user.id);

          // Role-based redirection (using role_name from backend)
          const role = result.user.role_name && result.user.role_name.toLowerCase();
          if (role === 'admin') {
            alert("Admin login successful");
            this.$router.push("/adminDashboard");
          } else if (role === 'hr') {
            alert("HR login successful");
            this.$router.push("/hrDashboard");
          } else if (role === 'candidate') {
            alert("Candidate login successful");
            this.$router.push("/candidateDashboard");
          } else if (role === 'ho') {
            alert("Head officer login successful");
            this.$router.push("/ho/dashboard");
          }else if (role === 'bda') {
            alert("Bussiness development associate login successful");
            this.$router.push("/bda/dashboard");
          }
          else {
            alert("Unknown role, unable to redirect.");
          }
        }
      } catch (error) {
        this.errorMessage = "Unable to connect to server";
      }
    },

    goSignup() {
      this.$router.push('/signup');
    }
  },
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

/* Card is solid white, but you can use rgba(255,255,255,0.95) to make it slightly see-through */
.auth-card {
  width: 420px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  text-align: center
}

label {
  display: block;
  font-size: 0.9rem;
  margin-top: 12px
}

input {
  width: 100%;
  padding: 10px 12px;
  margin-top: 6px;
  border-radius: 8px;
  border: 1px solid #e6e9ee
}

.primary {
  width: 100%;
  background: #2d8cff;
  color: #fff;
  border: none;
  padding: 10px 14px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 20px
}

.muted {
  color: #7b8a95;
  margin-bottom: 18px
}

.error {
  color: #c0392b;
  margin-top: 12px
}
</style>
