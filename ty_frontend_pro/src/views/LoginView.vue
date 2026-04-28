<template>
  <div class="login-page">
    <div class="login-bg-grid"></div>
    <div class="login-shell">
      <BrandPanel />
      <LoginForm @login-success="handleLoginSuccess" />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { isAuthenticated } from '../auth';
import BrandPanel from '../components/login/BrandPanel.vue';
import LoginForm from '../components/login/LoginForm.vue';

const router = useRouter();
const route = useRoute();

const handleLoginSuccess = (result) => {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/home';
  router.replace(redirect);
};

onMounted(() => {
  if (isAuthenticated()) {
    router.replace('/home');
  }
});
</script>

<style src="../assets/styles/pages/login.css"></style>