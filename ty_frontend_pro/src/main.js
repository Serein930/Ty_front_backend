import { createApp } from 'vue'
import './style.css'  // ✨ 必须有这一行，确保全局样式被加载
import './assets/styles/variables.css' 
import '@fortawesome/fontawesome-free/css/all.min.css'
import router from './router'
import App from './App.vue'

const app = createApp(App)
app.use(router)
app.mount('#app')