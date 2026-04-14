<template>
  <header class="top-header">
    <div class="logo-area">
      <i class="fa-solid fa-eye"></i> 天眼情报
    </div>
    
    <nav class="nav-menu">
      <router-link to="/home" class="nav-item" active-class="active">
        <i class="fa-regular fa-chart-bar"></i> 态势感知
      </router-link>
      <router-link to="/search" class="nav-item" active-class="active">
        <i class="fa-solid fa-magnifying-glass"></i> 情报检索
      </router-link>
      <router-link to="/dashboard" class="nav-item" active-class="active">
        <i class="fa-solid fa-circle-exclamation"></i> 监测预警
      </router-link>
      <router-link to="/topology" class="nav-item" active-class="active">
        <i class="fa-solid fa-share-nodes"></i> 取证溯源
      </router-link>
    </nav>
    
    <div class="sys-info">
      <span>{{ currentUser }}, 欢迎您!</span>
      <span>{{ currentTime }}</span>
      <span style="cursor: pointer;">页面风格设置 <i class="fa-solid fa-caret-down"></i></span>
      <span style="cursor: pointer;" @click="handleLogout"><i class="fa-solid fa-power-off"></i> 退出</span>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { getAuthUser, logout } from '../auth';

// 加入一个简单的动态时钟，替代原本写死的 "2024-06-10"
const currentTime = ref('');
const currentUser = ref(getAuthUser()?.displayName || 'Administrator');
const router = useRouter();
let timer = null;

const updateTime = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  currentTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

onMounted(() => {
  updateTime();
  timer = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  clearInterval(timer);
});

const handleLogout = () => {
  logout();
  router.replace('/login');
};
</script>

<style scoped>
/* ====== 顶部导航栏样式 (完全从 dashboard.html 搬运) ====== */
.top-header {
    height: 70px;
    background: rgba(18, 26, 45, 0.95);
    border-bottom: 2px solid var(--border-color);
    display: flex;
    align-items: center;
    padding: 0 20px;
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.12);
    position: relative;
    z-index: 100;
    flex-shrink: 0;
}

.logo-area {
    font-size: 24px;
    font-weight: bold;
    color: var(--accent-blue);
    margin-right: 60px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.nav-menu {
    display: flex;
    gap: 5px;
    flex: 1;
}

.nav-item {
    padding: 8px 20px;
    color: var(--text-dim);
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none; /* 针对 router-link 的 a 标签重置下划线 */
}

.nav-item.active,
.nav-item:hover {
    color: var(--accent-blue);
    background: linear-gradient(180deg, rgba(59,130,246,0) 0%, rgba(59,130,246,0.08) 100%);
    border-bottom: 2px solid var(--accent-blue);
}

.sys-info {
    display: flex;
    align-items: center;
    gap: 20px;
    color: var(--text-dim);
    font-size: 12px;
}
</style>