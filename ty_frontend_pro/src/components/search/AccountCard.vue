<template>
  <article class="entity-card" @click="$emit('click')">
    <div class="account-card-head">
      <label class="account-pick" @click.stop>
        <input type="checkbox" :checked="isSelected" @change="$emit('toggle-basket')" />
      </label>

      <div class="account-main">
        <div class="account-title-row">
          <img class="account-avatar" :src="item.avatar || '/offline/avatar-default.svg'" alt="avatar" />
          <div class="account-name-wrap">
            <div class="account-name-line">
              <strong class="account-name">{{ displayName }}</strong>
              <span class="media-pill"><i :class="getMediaIcon(item.media)"></i> {{ platformLabel }}</span>
              <span class="risk-badge" :class="riskClass(item.risk)">{{ item.risk }}</span>
              <span class="topic-badge"># {{ item.topic }}</span>
            </div>
            <div class="account-handle">{{ handle }}</div>
            <div class="desc account-desc" v-html="highlightKeyword(item.summary, keyword)"></div>
          </div>
        </div>

        <div class="account-metrics">
          <div class="metric-box">
            <div class="metric-k">粉丝</div>
            <div class="metric-v">{{ stats.followers }}</div>
          </div>
          <div class="metric-box">
            <div class="metric-k">关注</div>
            <div class="metric-v">{{ stats.following }}</div>
          </div>
          <div class="metric-box">
            <div class="metric-k">发帖</div>
            <div class="metric-v">{{ stats.posts }}</div>
          </div>
          <div class="metric-box">
            <div class="metric-k">记录时间</div>
            <div class="metric-v">{{ item.date }}</div>
          </div>
        </div>

        <div class="account-actions">
          <button class="entity-chip account-action-btn" @click.stop="$emit('view-person')">
            <i class="fa-solid fa-user-check"></i>
            查看人物
          </button>
          <button class="entity-chip account-action-btn" @click.stop="$emit('toggle-basket')">
            <i class="fa-solid" :class="isSelected ? 'fa-circle-check' : 'fa-circle-plus'"></i>
            {{ isSelected ? '移出线索篮' : '加入线索篮' }}
          </button>
        </div>
      </div>

      <div class="account-side">
        <div class="account-side-label">归属人物</div>
        <button class="account-side-link" @click.stop="$emit('view-person')">
          {{ associatedPerson }}
        </button>
      </div>
    </div>
  </article>
</template>

<script setup>
defineProps({
  item: {
    type: Object,
    required: true
  },
  isSelected: {
    type: Boolean,
    default: false
  },
  keyword: {
    type: String,
    default: ''
  },
  displayName: {
    type: String,
    default: ''
  },
  handle: {
    type: String,
    default: ''
  },
  platformLabel: {
    type: String,
    default: ''
  },
  associatedPerson: {
    type: String,
    default: ''
  },
  stats: {
    type: Object,
    default: () => ({ followers: '-', following: '-', posts: '-' })
  },
  riskClass: {
    type: Function,
    default: (risk) => risk === '高危' ? 'high' : risk === '中危' ? 'mid' : 'low'
  },
  getMediaIcon: {
    type: Function,
    default: () => 'fa-solid fa-globe'
  },
  highlightKeyword: {
    type: Function,
    default: (text) => text
  }
});

defineEmits(['click', 'toggle-basket', 'view-person']);
</script>

