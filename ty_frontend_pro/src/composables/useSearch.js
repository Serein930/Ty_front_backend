// composables/useSearch.js
// Search页面数据处理逻辑

import { ref, computed, reactive, watch } from 'vue';

const BASE_DATE = new Date('2026-03-25T00:00:00+08:00');

// 基础模拟数据
const baseMockItems = [
  { id: 1, viewType: 'intel', title: '跨平台洗钱通道曝光（USDT）', summary: '发现 Telegram 与 X 双平台账号共用收款地址，资金在 24 小时内多跳转移。', risk: '高危', media: '跨平台聚合', region: '广东省', topic: '黑产', date: '2026-03-24', dayDiff: 1, entities: ['USDT', '0xA91f...D33', '@shadow_pay', '跨平台聚合'], relatedAccounts: ['@shadow_pay', 'x:shadow_pay_02', 'tg:pay_lane'] },
  { id: 2, viewType: 'intel', title: '疑似沿海走私补给链条', summary: '线索显示夜间海域接驳频繁，关联多个匿名账号同步发布暗语。', risk: '中危', media: 'Telegram', region: '福建省', topic: '走私', date: '2026-03-20', dayDiff: 5, entities: ['珠江口', '接驳', '@sea-hub', 'Tor'], relatedAccounts: ['@sea-hub', '@dock_signal'] },
  { id: 3, viewType: 'person', title: '人物画像：暗网前体中介 "M"', summary: '常用 Tor 论坛与 Telegram 进行撮合，近一月活动显著上升。', risk: '高危', media: 'Tor', region: '云南省', topic: '毒品', date: '2026-03-23', dayDiff: 2, entities: ['前体', 'Monero', 'M-bridge'], relatedAccounts: ['tor:m_bridge', 'tg:@m-ops'] },
  { id: 4, viewType: 'person', title: '人物画像：跨境社工库倒卖组织者', summary: '社工库关联渠道活跃，疑似按行业批量售卖账号与身份数据。', risk: '中危', media: '社工库关联', region: '北京市', topic: '黑产', date: '2026-03-12', dayDiff: 13, entities: ['社工库', '身份信息', '数据包'], relatedAccounts: ['@data_whale', 'x:leak-river'] },
  { id: 5, viewType: 'account', title: '账号视图：@Guide_Jihad', summary: '账号多次发布暴恐导向话题，存在群组扩散行为。', risk: '高危', media: 'Telegram', region: '新疆维吾尔自治区', topic: '暴恐', date: '2026-03-24', dayDiff: 1, entities: ['Guide_Jihad', '群组扩散', '节点账号'], relatedAccounts: ['@Guide_Jihad_backup', '@silent_node'] },
  { id: 6, viewType: 'account', title: '账号视图：x:runner_007', summary: '同城隐语交易高频，疑似向多平台引流。', risk: '低危', media: 'X', region: '上海市', topic: '毒品', date: '2025-12-28', dayDiff: 87, entities: ['飞叶子', '同城配送', 'runner_007'], relatedAccounts: ['weibo:runner_007', 'tg:@runner-007'] }
];

const formatDateByDiff = (dayDiff) => {
  const ms = BASE_DATE.getTime() - (dayDiff * 24 * 60 * 60 * 1000);
  const d = new Date(ms);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
};

export function useSearch() {
  const state = reactive({
    currentView: 'all',
    inputKeyword: '',
    submittedKeyword: '',
    hasSubmitted: false,
    mode: 'normal',
    groupTab: 'all',
    detailItem: null,
    quickTime: 'all',
    region: 'all',
    riskSet: [],
    mediaSet: [],
    topicSet: [],
    selectedRule: '',
    aiFullscreenTarget: null
  });

  // 初始化列表
  const allItems = ref(baseMockItems.map(item => ({
    ...item,
    date: formatDateByDiff(item.dayDiff || 0)
  })));

  // 筛选后的列表
  const filteredItems = computed(() => {
    let result = allItems.value;

    // 视图筛选
    if (state.currentView !== 'all') {
      const viewMap = { intel: 'intel', person: 'person', account: 'account' };
      result = result.filter(item => item.viewType === viewMap[state.currentView]);
    }

    // 关键词筛选
    if (state.submittedKeyword) {
      const kw = state.submittedKeyword.toLowerCase();
      result = result.filter(item =>
        item.title?.toLowerCase().includes(kw) ||
        item.summary?.toLowerCase().includes(kw) ||
        item.entities?.some(e => e.toLowerCase().includes(kw))
      );
    }

    return result;
  });

  // 分组后的数据
  const groupedItems = computed(() => {
    const groups = {
      intel: { type: 'intel', label: '情报线索', items: [] },
      person: { type: 'person', label: '人物画像', items: [] },
      account: { type: 'account', label: '账号视图', items: [] }
    };

    filteredItems.value.forEach(item => {
      if (groups[item.viewType]) {
        groups[item.viewType].items.push(item);
      }
    });

    return Object.values(groups);
  });

  // 可见的分组标签
  const visibleGroupTabs = computed(() => {
    return [
      { type: 'all', label: '全部', count: filteredItems.value.length },
      { type: 'intel', label: '情报', count: groupedItems.value.find(g => g.type === 'intel')?.items.length || 0 },
      { type: 'person', label: '人物', count: groupedItems.value.find(g => g.type === 'person')?.items.length || 0 },
      { type: 'account', label: '账号', count: groupedItems.value.find(g => g.type === 'account')?.items.length || 0 }
    ];
  });

  // 渲染结果
  const renderGroups = computed(() => {
    if (state.groupTab === 'all') {
      return groupedItems.value.filter(g => g.items.length > 0);
    }
    return groupedItems.value.filter(g => g.type === state.groupTab);
  });

  // 线索篮
  const basket = ref([]);

  const basketIdSet = computed(() => new Set(basket.value.map(i => i.id)));

  const toggleBasket = (item) => {
    const index = basket.value.findIndex(i => i.id === item.id);
    if (index > -1) {
      basket.value.splice(index, 1);
    } else {
      basket.value.push(item);
    }
  };

  // 快速时间标签
  const quickTimeLabel = computed(() => {
    const labels = { all: '全部', '24h': '24小时', '7d': '近7天', '30d': '近30天' };
    return labels[state.quickTime] || state.quickTime;
  });

  // 方法
  const submitSearch = (mode = 'normal') => {
    state.mode = mode;
    state.submittedKeyword = state.inputKeyword;
    state.hasSubmitted = true;
  };

  const resetAll = () => {
    state.inputKeyword = '';
    state.submittedKeyword = '';
    state.hasSubmitted = false;
    state.mode = 'normal';
    state.currentView = 'all';
    state.quickTime = 'all';
    state.region = 'all';
    state.riskSet = [];
    state.mediaSet = [];
    state.topicSet = [];
    state.selectedRule = '';
    basket.value = [];
  };

  const openDetail = (item) => {
    state.detailItem = item;
  };

  const closeDetail = () => {
    state.detailItem = null;
  };

  const drillDown = (keyword) => {
    state.inputKeyword = keyword;
    submitSearch('normal');
  };

  const showToast = (message) => {
    console.log('Toast:', message);
  };

  // 辅助函数
  const getMediaIcon = (media) => {
    const icons = {
      'Telegram': 'fa-brands fa-telegram',
      'Tor': 'fa-solid fa-user-secret',
      'X': 'fa-brands fa-x-twitter',
      'Weibo': 'fa-brands fa-weibo',
      '跨平台聚合': 'fa-solid fa-globe',
      '社工库关联': 'fa-solid fa-database'
    };
    return icons[media] || 'fa-solid fa-globe';
  };

  const getPlatformLabel = (media) => {
    const labels = {
      'Telegram': 'TG',
      'Tor': '暗网',
      'X': 'X',
      'Weibo': '微博',
      '跨平台聚合': '聚合',
      '社工库关联': '社工库'
    };
    return labels[media] || media;
  };

  const riskClass = (risk) => {
    const classes = { '高危': 'high', '中危': 'mid', '低危': 'low' };
    return classes[risk] || '';
  };

  const highlightKeyword = (text, keyword) => {
    if (!keyword || !text) return text;
    const regex = new RegExp(`(${keyword})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  };

  // 账号相关辅助函数
  const getAccountDisplayName = (item) => item.title?.replace('账号视图：', '') || item.entities?.[0] || '未知';
  const getAccountHandle = (item) => item.entities?.[0] || '';
  const getAccountStat = (item, stat) => {
    const stats = { followers: '1.2K', following: '234', posts: '56' };
    return stats[stat] || '-';
  };
  const getAssociatedPerson = (item) => item.entities?.[0] || '未知';

  // 人物相关辅助函数
  const getPersonDisplayName = (item) => item.title?.replace('人物画像：', '') || item.entities?.[0] || '未知';
  const getPersonAliases = (item) => item.relatedAccounts?.slice(0, 2) || [];
  const getPersonConfidence = (item) => Math.floor(Math.random() * 20) + 80;
  const getPersonEvidenceLine = (item) => '用户名与签名特征';

  const viewAssociatedPerson = (item) => {
    console.log('View person:', item);
  };

  return {
    state,
    allItems,
    filteredItems,
    groupedItems,
    visibleGroupTabs,
    renderGroups,
    basket,
    basketIdSet,
    quickTimeLabel,

    // 方法
    submitSearch,
    resetAll,
    openDetail,
    closeDetail,
    drillDown,
    toggleBasket,
    showToast,

    // 辅助函数
    getMediaIcon,
    getPlatformLabel,
    riskClass,
    highlightKeyword,
    getAccountDisplayName,
    getAccountHandle,
    getAccountStat,
    getAssociatedPerson,
    getPersonDisplayName,
    getPersonAliases,
    getPersonConfidence,
    getPersonEvidenceLine,
    viewAssociatedPerson
  };
}
