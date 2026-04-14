<template>
  <div class="login-page">
    <div class="login-bg-grid"></div>
    <div class="login-shell">
      <div class="login-brand-panel">
        <div class="brand-badge">TY-A Intelligence Platform</div>
        <div class="brand-title-wrap">
          <div class="brand-logo"><i class="fa-solid fa-eye"></i></div>
          <div>
            <h1>天眼情报</h1>
            <p>多维情报分析与取证溯源系统</p>
          </div>
        </div>

        <div class="brand-intro">
          <div class="intro-title">安全接入说明</div>
          <div class="intro-item"><i class="fa-solid fa-shield-halved"></i><span>登录后方可访问监测预警、检索分析与取证溯源页面</span></div>
          <div class="intro-item"><i class="fa-solid fa-tower-broadcast"></i><span>延续当前系统深色科技风格，与整体界面保持统一</span></div>
          <div class="intro-item"><i class="fa-solid fa-fingerprint"></i><span>当前为前端演示鉴权，登录状态保存在本地会话中</span></div>
        </div>

        <div class="brand-tip">
          <div class="tip-title">测试账号</div>
          <div class="tip-line">Administrator / admin123</div>
          <div class="tip-line">analyst / 123456</div>
        </div>
      </div>

      <div class="login-card">
        <div class="login-card-header">
          <div class="login-card-title">账号登录</div>
          <div class="login-card-subtitle">请输入账号和密码以进入系统</div>
        </div>

        <form class="login-form" @submit.prevent="handleLogin">
          <label class="form-label">账号</label>
          <div class="input-wrap">
            <i class="fa-solid fa-user"></i>
            <input v-model.trim="form.username" type="text" placeholder="请输入账号" autocomplete="username" />
          </div>

          <label class="form-label">密码</label>
          <div class="input-wrap">
            <i class="fa-solid fa-lock"></i>
            <input v-model="form.password" :type="showPassword ? 'text' : 'password'" placeholder="请输入密码" autocomplete="current-password" />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              <i class="fa-solid" :class="showPassword ? 'fa-eye-slash' : 'fa-eye'"></i>
            </button>
          </div>

          <div class="form-row">
            <label class="remember-line">
              <input v-model="form.remember" type="checkbox" />
              <span>记住当前账号</span>
            </label>
            <span class="login-status">安全链路已加密</span>
          </div>

          <div v-if="errorMessage" class="error-message">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <span>{{ errorMessage }}</span>
          </div>

          <button class="login-btn" type="submit" :disabled="submitting">
            <i class="fa-solid" :class="submitting ? 'fa-circle-notch fa-spin' : 'fa-right-to-bracket'"></i>
            {{ submitting ? '登录中...' : '登录系统' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { login, isAuthenticated } from '../auth';

const router = useRouter();
const route = useRoute();

const form = reactive({
  username: 'Administrator',
  password: 'admin123',
  remember: true
});

const showPassword = ref(false);
const submitting = ref(false);
const errorMessage = ref('');

const handleLogin = async () => {
  errorMessage.value = '';

  if (!form.username || !form.password) {
    errorMessage.value = '请输入账号和密码';
    return;
  }

  submitting.value = true;

  await new Promise(resolve => setTimeout(resolve, 450));
  const result = login(form.username, form.password);
  submitting.value = false;

  if (!result.success) {
    errorMessage.value = result.message;
    return;
  }

  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/home';
  router.replace(redirect);
};

onMounted(() => {
  if (isAuthenticated()) {
    router.replace('/home');
  }
});
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.16), transparent 28%),
    radial-gradient(circle at right center, rgba(168, 85, 247, 0.14), transparent 22%),
    linear-gradient(180deg, #061225 0%, #07111f 100%);
  color: var(--text-main);
}

.login-bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(59, 130, 246, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.06) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.25));
}

.login-shell {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  align-items: center;
  gap: 48px;
  max-width: 1280px;
  margin: 0 auto;
  padding: 48px;
}

.login-brand-panel,
.login-card {
  border: 1px solid rgba(59, 130, 246, 0.22);
  background: rgba(8, 18, 38, 0.82);
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.32), inset 0 0 35px rgba(59, 130, 246, 0.06);
  backdrop-filter: blur(14px);
}

.login-brand-panel {
  border-radius: 24px;
  padding: 36px;
  min-height: 560px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.brand-badge {
  width: fit-content;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid rgba(59, 130, 246, 0.35);
  background: rgba(59, 130, 246, 0.08);
  color: var(--accent-blue);
  font-size: 12px;
  letter-spacing: 0.08em;
  margin-bottom: 24px;
}

.brand-title-wrap {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 28px;
}

.brand-logo {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  color: var(--accent-blue);
  border: 1px solid rgba(59, 130, 246, 0.38);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.18), rgba(14, 165, 233, 0.08));
  box-shadow: 0 0 24px rgba(59, 130, 246, 0.14);
}

.brand-title-wrap h1 {
  font-size: 36px;
  font-weight: 700;
  color: #f8fbff;
  margin-bottom: 6px;
}

.brand-title-wrap p {
  color: #8ea3c5;
  font-size: 15px;
}

.brand-intro {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 28px;
}

.intro-title,
.tip-title {
  color: #f8fbff;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.intro-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: #a8bad6;
  line-height: 1.7;
}

.intro-item i {
  color: var(--accent-blue);
  margin-top: 5px;
}

.brand-tip {
  margin-top: auto;
  padding: 18px 20px;
  border-radius: 16px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  background: rgba(2, 8, 23, 0.35);
}

.tip-line {
  color: #c8d6ea;
  font-family: Consolas, monospace;
  font-size: 13px;
  line-height: 1.8;
}

.login-card {
  border-radius: 24px;
  padding: 34px 30px;
}

.login-card-header {
  margin-bottom: 28px;
}

.login-card-title {
  font-size: 28px;
  font-weight: 700;
  color: #f8fbff;
  margin-bottom: 8px;
}

.login-card-subtitle {
  color: #8ea3c5;
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-size: 13px;
  color: #a8bad6;
  margin-bottom: 10px;
}

.input-wrap {
  height: 50px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  border-radius: 14px;
  border: 1px solid rgba(59, 130, 246, 0.18);
  background: rgba(2, 8, 23, 0.45);
  margin-bottom: 18px;
  transition: 0.25s;
}

.input-wrap:focus-within {
  border-color: rgba(59, 130, 246, 0.55);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.input-wrap i {
  color: var(--accent-blue);
  width: 16px;
}

.input-wrap input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #f8fbff;
  font-size: 14px;
}

.input-wrap input::placeholder {
  color: #5f7394;
}

.toggle-password {
  background: transparent;
  border: none;
  color: #88a0c5;
  cursor: pointer;
}

.form-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
  gap: 10px;
}

.remember-line {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #a8bad6;
  font-size: 13px;
}

.login-status {
  color: #6dd3ff;
  font-size: 12px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid rgba(239, 68, 68, 0.25);
  background: rgba(239, 68, 68, 0.08);
  color: #fca5a5;
  font-size: 13px;
  margin-bottom: 18px;
}

.login-btn {
  height: 50px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: 0.25s;
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.3);
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 26px rgba(37, 99, 235, 0.36);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 1100px) {
  .login-shell {
    grid-template-columns: 1fr;
    padding: 28px;
  }

  .login-brand-panel {
    min-height: auto;
  }
}

@media (max-width: 640px) {
  .login-shell {
    padding: 18px;
    gap: 20px;
  }

  .login-brand-panel,
  .login-card {
    padding: 22px 18px;
    border-radius: 18px;
  }

  .brand-title-wrap {
    align-items: flex-start;
  }

  .brand-title-wrap h1 {
    font-size: 28px;
  }
}
</style>
