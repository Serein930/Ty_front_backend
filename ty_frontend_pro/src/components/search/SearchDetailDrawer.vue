<template>
  <div class="drawer-mask" :class="{ open: visible }" @click.self="$emit('close')">
    <div class="drawer" v-if="item">
      <div class="drawer-header">
        <h3>{{ item.viewType === 'person' ? getPersonDisplayName(item) : item.viewType === 'account' ? getAccountDisplayName(item) : item.title }}</h3>
        <button class="icon-btn" @click="$emit('close')"><i class="fa-solid fa-xmark"></i></button>
      </div>

      <div class="drawer-body custom-scrollbar">
        <template v-if="item.viewType === 'intel'">
          <div class="intel-drawer-chat">
            <div class="intel-drawer-chat-head">
              <span><i :class="getMediaIcon(item.media)"></i> {{ getIntelChannel(item) }}</span>
              <span>Members: {{ getIntelMemberCount(item) }}</span>
            </div>
            <div class="intel-drawer-chat-body">
              <div class="intel-msg">
                <div class="intel-msg-head">
                  <span>{{ getIntelPeerName(item) }}</span>
                  <span>{{ getIntelPeerTime(item) }}</span>
                </div>
                <div>{{ getIntelPeerText(item) }}</div>
              </div>
              <div class="intel-msg self">
                <div class="intel-msg-head">
                  <span>{{ getIntelPosterName(item) }}</span>
                  <span>{{ getIntelPosterTime(item) }}</span>
                </div>
                <div>{{ item.summary }}</div>
              </div>
            </div>
          </div>

          <div class="intel-entities-box">
            <div class="module-title"><i class="fa-solid fa-tags"></i> 机器提取实体 (NLP Entities)</div>
            <div class="intel-entities-wrap">
              <span v-for="ent in getIntelEntities(item)" :key="`drawer-${ent}`" class="intel-drawer-entity-chip" :class="`tone-${getIntelEntityTone(ent)}`">
                <i class="fa-solid fa-tag"></i>
                {{ ent }}
              </span>
            </div>
          </div>

          <div class="intel-workflow-title">工作流指令 (P2 Actions)</div>
        </template>

        <template v-else-if="item.viewType === 'person'">
          <div class="person2-hero">
            <img src="/offline/avatar-default.svg" alt="avatar" class="person2-avatar" />
            <div class="person2-meta">
              <div class="person2-name">{{ getPersonDisplayName(item) }}</div>
              <div class="person2-confidence">多源聚合置信度 {{ getPersonConfidence(item) }}%</div>
            </div>
          </div>

          <div class="person2-proof-box">
            <div class="person2-proof-title"><i class="fa-solid fa-link"></i> 同人聚合证据链推演</div>
            <div class="person2-proof-line"><strong>[用户名特征]</strong> {{ getPersonEvidenceLine(item) }} 呈现高度重合</div>
          </div>

          <div class="intel-workflow-title">工作流指令 (P2 Actions)</div>
        </template>

        <template v-else-if="item.viewType === 'account'">
          <div class="account2-hero">
            <img src="/offline/avatar-default.svg" alt="avatar" class="account2-avatar" />
            <div class="account2-meta">
              <div class="account2-name">{{ getAccountDisplayName(item) }}</div>
              <div class="account2-platform"><i :class="getMediaIcon(item.media)"></i> {{ getPlatformLabel(item.media) }} 账号</div>
            </div>
          </div>

          <div class="account2-profile-box">
            <div class="account2-profile-title"><i class="fa-solid fa-address-card"></i> 账号档案 (Profile)</div>
            <div class="account2-profile-row"><strong>签名/Bio:</strong><span>{{ getAccountBio(item) }}</span></div>
            <div class="account2-profile-row"><strong>归属人物:</strong><button class="account2-owner-link" @click="$emit('open-owner', item)">{{ getAccountOwnerName(item) }}</button></div>
          </div>

          <div class="intel-workflow-title">工作流指令 (P2 Actions)</div>
        </template>

        <template v-else>
          <div class="base-grid">
            <div><span>类型：</span>{{ item.viewType }}</div>
            <div><span>风险：</span>{{ getRiskText(item.risk) }}</div>
            <div><span>媒介：</span>{{ item.media }}</div>
            <div><span>地区：</span>{{ item.region }}</div>
            <div><span>话题：</span>{{ item.topic }}</div>
            <div><span>时间：</span>{{ item.date }}</div>
          </div>

          <div class="detail-summary">{{ item.summary }}</div>

          <div v-if="item.relatedAccounts?.length" class="related-block">
            <div class="module-title">关联账号</div>
            <ul>
              <li v-for="acc in item.relatedAccounts" :key="acc">
                <img src="/offline/avatar-default.svg" alt="avatar" />
                <span>{{ acc }}</span>
              </li>
            </ul>
          </div>
        </template>
      </div>

      <div class="drawer-actions" :class="{ 'intel-actions': item.viewType === 'intel' || item.viewType === 'person' || item.viewType === 'account' }">
        <template v-if="item.viewType === 'intel'">
          <button class="btn intel-action-btn" @click="$emit('action', 'monitor')"><i class="fa-solid fa-satellite-dish"></i> 开启实时监控</button>
          <button class="btn intel-action-btn" @click="$emit('action', 'annotate')"><i class="fa-solid fa-pen-to-square"></i> 人工标注研判</button>
          <button class="btn btn-ai intel-action-btn primary" @click="$emit('action', 'graph')"><i class="fa-solid fa-diagram-project"></i> 推送图谱扩线引擎</button>
        </template>
        <template v-else-if="item.viewType === 'person'">
          <button class="btn intel-action-btn" @click="$emit('action', 'monitor')"><i class="fa-solid fa-satellite-dish"></i> 开启实时监控</button>
          <button class="btn intel-action-btn" @click="$emit('action', 'annotate')"><i class="fa-solid fa-pen-to-square"></i> 人工标注研判</button>
          <button class="btn btn-ai intel-action-btn primary" @click="$emit('action', 'graph')"><i class="fa-solid fa-diagram-project"></i> 推送图谱扩线引擎</button>
        </template>
        <template v-else-if="item.viewType === 'account'">
          <button class="btn intel-action-btn" @click="$emit('action', 'monitor')"><i class="fa-solid fa-satellite-dish"></i> 开启实时监控</button>
          <button class="btn intel-action-btn" @click="$emit('action', 'annotate')"><i class="fa-solid fa-pen-to-square"></i> 人工标注研判</button>
          <button class="btn btn-ai intel-action-btn primary" @click="$emit('action', 'graph')"><i class="fa-solid fa-diagram-project"></i> 推送图谱扩线引擎</button>
        </template>
        <template v-else>
          <button class="btn btn-primary" @click="$emit('action', 'monitor')">开启监控</button>
          <button class="btn" @click="$emit('action', 'annotate')">人工标注</button>
          <button class="btn btn-ai" @click="$emit('action', 'graph')">推送图谱扩线引擎</button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  item: {
    type: Object,
    default: null
  },
  getPersonDisplayName: {
    type: Function,
    default: (item) => item?.title || '未命名对象'
  },
  getAccountDisplayName: {
    type: Function,
    default: (item) => item?.title || '未知账号'
  },
  getMediaIcon: {
    type: Function,
    default: () => 'fa-solid fa-globe'
  },
  getIntelChannel: {
    type: Function,
    default: () => '默认渠道'
  },
  getIntelMemberCount: {
    type: Function,
    default: () => '1K'
  },
  getIntelPeerName: {
    type: Function,
    default: () => 'Unknown'
  },
  getIntelPeerTime: {
    type: Function,
    default: () => '00:00'
  },
  getIntelPeerText: {
    type: Function,
    default: () => ''
  },
  getIntelPosterName: {
    type: Function,
    default: () => 'Unknown'
  },
  getIntelPosterTime: {
    type: Function,
    default: () => '00:00'
  },
  getIntelEntities: {
    type: Function,
    default: () => []
  },
  getIntelEntityTone: {
    type: Function,
    default: () => 'id'
  },
  getPersonConfidence: {
    type: Function,
    default: () => 80
  },
  getPersonEvidenceLine: {
    type: Function,
    default: () => ''
  },
  getPlatformLabel: {
    type: Function,
    default: (media) => media
  },
  getAccountBio: {
    type: Function,
    default: () => ''
  },
  getAccountOwnerName: {
    type: Function,
    default: () => '未知'
  }
});

defineEmits(['close', 'action', 'open-owner']);

const getRiskText = (risk) => ({ high: '高危', mid: '中危', low: '低危' }[risk] || risk);
</script>

