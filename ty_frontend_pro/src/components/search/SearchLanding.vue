<template>
  <section v-if="!hasSubmitted" class="legacy-landing panel">
    <div class="legacy-search-wrapper">
      <h2 class="legacy-title">情报检索</h2>
      <p class="legacy-subtitle">请输入关键词、Hash、手机号或 Telegram ID...</p>
      <div class="legacy-search-box">
        <select v-model="currentView" class="control-input view-select">
          <option value="all">全域检索 (All)</option>
          <option value="intel">情报线索 (Event)</option>
          <option value="person">人物画像 (Entity)</option>
          <option value="account">账号视图 (Account)</option>
        </select>

        <input
          v-model="inputKeyword"
          class="control-input search-input"
          type="text"
          placeholder="请输入关键词，例如：USDT / 珠江口 / 走私"
          @keyup.enter="submitSearch('normal')"
        />

        <button class="btn btn-primary" @click="submitSearch('normal')">
          <i class="fa-solid fa-magnifying-glass"></i>
          搜索
        </button>
        <button class="btn btn-ai" @click="submitSearch('ai')">
          <i class="fa-solid fa-wand-magic-sparkles"></i>
          AI深度分析
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  hasSubmitted: {
    type: Boolean,
    default: false
  },
  currentView: {
    type: String,
    default: 'all'
  },
  inputKeyword: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:currentView', 'update:inputKeyword', 'submit-search']);

const submitSearch = (mode) => {
  emit('submit-search', mode);
};
</script>

