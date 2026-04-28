<template>
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
</template>

<script setup>
import { reactive, ref } from 'vue';
import { login } from '../../auth';

const emit = defineEmits(['login-success']);

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

  emit('login-success', result);
};
</script>

