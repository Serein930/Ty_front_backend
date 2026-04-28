<template>
  <div id="cloneWorkspaceModal" class="modal-overlay" v-show="visible" @click.self="$emit('close')" style="z-index:1200;">
    <div class="modal-content" style="max-width: 1400px; width: 95%; height: 90vh;">
      <div class="modal-header" style="background: linear-gradient(90deg, #1e1b4b 0%, #0f172a 100%); border-bottom-color: #4338ca;">
        <div class="modal-title" style="color: #a855f7; display:flex;align-items:center;gap:8px;">
          <i class="fa-solid fa-robot"></i> 数字分身社工工作台
        </div>
        <button class="modal-close" @click="$emit('close')">&times;</button>
      </div>
      <div class="workspace-layout">
        <div class="ws-sidebar">
          <div class="ws-section-title">Agent配置 <span class="status-dot"></span></div>
          <div class="ws-config-box">
            <label class="ws-label">目标人物</label>
            <input class="ws-input" :value="target?.alias || ''" disabled />
            <label class="ws-label">侵入通道</label>
            <select class="ws-select" v-model="channel">
              <option value="telegram">Telegram</option>
              <option value="x">X</option>
              <option value="facebook">Facebook</option>
            </select>
          </div>
          <div class="ws-config-box">
            <div class="agent-stats">
              <div class="agent-stat-card">
                <div class="agent-stat-val">{{ stats.replies }}</div>
                <div class="ws-label">回复轮次</div>
              </div>
              <div class="agent-stat-card">
                <div class="agent-stat-val">{{ stats.hitRate }}%</div>
                <div class="ws-label">命中率</div>
              </div>
            </div>
          </div>
        </div>
        <div class="ws-chat-area">
          <div class="chat-header">
            <div class="chat-target-info">
              <img class="chat-target-avatar" :src="target?.avatar || 'https://i.pravatar.cc/80?img=10'" alt="avatar" />
              <div>
                <div style="font-size:13px;color:#fff;font-weight:700;">{{ target?.alias || 'Unknown' }}</div>
                <div style="font-size:11px;color:#94a3b8;">通道: {{ channel.toUpperCase() }}</div>
              </div>
            </div>
          </div>
          <div class="chat-messages">
            <div v-for="m in messages" :key="m.id" class="msg-bubble-wrapper" :class="m.side">
              <img class="msg-avatar" :src="m.side === 'left' ? (target?.avatar || 'https://i.pravatar.cc/40?img=4') : 'https://i.pravatar.cc/40?img=18'" alt="avatar" />
              <div class="msg-bubble">
                <div v-if="m.thought" class="llm-thought">{{ m.thought }}</div>
                <div>{{ m.text }}</div>
                <div class="msg-meta"><span>{{ m.time }}</span></div>
              </div>
            </div>
          </div>
          <div class="chat-input-area">
            <div class="hitl-toolbar">
              <span style="font-size:12px;color:#94a3b8;">HITL人工审核</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="hitlEnabled" />
                <span class="slider"></span>
              </label>
            </div>
            <textarea class="hitl-textarea" v-model="draft" placeholder="输入话术...按发送模拟大模型对话"></textarea>
            <div style="display:flex;justify-content:flex-end;margin-top:10px;gap:10px;">
              <button class="btn-dash3" @click="draft = ''">清空</button>
              <button class="btn-dash3 primary" @click="sendMessage"><i class="fa-solid fa-paper-plane"></i> 发送</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  target: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close']);

const channel = ref('telegram');
const draft = ref('');
const hitlEnabled = ref(true);
const stats = ref({ replies: 0, hitRate: 93 });
const messages = ref([]);

watch(() => props.visible, (newVal) => {
  if (newVal && props.target) {
    const detectPlatformType = (platform) => {
      const p = String(platform || '').toLowerCase();
      if (p.includes('telegram') || p.includes('tg')) return 'telegram';
      if (p === 'x' || p.includes('twitter')) return 'x';
      return 'facebook';
    };
    channel.value = detectPlatformType(props.target.platform);
    stats.value = { replies: 0, hitRate: Math.max(80, Math.min(99, Math.round(props.target.score * 0.92))) };
    messages.value = [
      {
        id: 1,
        side: 'left',
        thought: '',
        text: `我是${props.target.alias}，最近有个新项目可以聊。`,
        time: '10:21'
      }
    ];
    draft.value = `你好，我看到你最近在${props.target.platform}很活跃，想和你交流下资源。`;
  }
});

const sendMessage = () => {
  const text = draft.value.trim();
  if (!text) return;

  const t = new Date();
  const hm = `${String(t.getHours()).padStart(2, '0')}:${String(t.getMinutes()).padStart(2, '0')}`;
  messages.value.push({
    id: Date.now(),
    side: 'right',
    thought: hitlEnabled.value ? 'HITL审核已启用，话术通过风控后发送。' : '',
    text,
    time: hm
  });
  draft.value = '';

  const replyPool = [
    '可以，先说你的合作模式。',
    '我这边只接受熟人介绍，你是谁带的？',
    '先发下你手里的量和周期。',
    '这个方向可以聊，但需要看你历史记录。'
  ];
  const reply = replyPool[Math.floor(Math.random() * replyPool.length)];

  setTimeout(() => {
    const tt = new Date();
    const rhm = `${String(tt.getHours()).padStart(2, '0')}:${String(tt.getMinutes()).padStart(2, '0')}`;
    messages.value.push({
      id: Date.now() + 1,
      side: 'left',
      thought: '',
      text: reply,
      time: rhm
    });
    stats.value.replies += 1;
  }, 700);
};
</script>

