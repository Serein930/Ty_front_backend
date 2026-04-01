<template>
  <router-view></router-view>
</template>

<script setup>
// 暂时不需要写逻辑
</script>

<style>
/* 基础重置，消除浏览器默认边距 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  background-color: var(--bg-dark); /* 我们马上会定义这个变量 */
  color: var(--text-main);
}
</style>