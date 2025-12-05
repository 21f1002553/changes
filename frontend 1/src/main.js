//main.js
import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router'
import { createPinia } from 'pinia'
import './style.css'
import "@fortawesome/fontawesome-free/css/all.css";
import "@fortawesome/fontawesome-free/js/all.js";

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)


app.use(router)

app.mount('#app')
