// composables/useDashboardData.js
// Dashboard数据处理和筛选逻辑

import { ref, computed, reactive, watch } from 'vue';
import { mockData } from '../mock/data.js';

// 模拟时间偏移，让数据显示为当前时间附近
const MOCK_REFERENCE_TIME = '2024-06-10 10:25:12';

const parseDateTime = (dateStr) => {
  if (!dateStr) return null;
  const normalized = dateStr.includes('T') ? dateStr : dateStr.replace(' ', 'T');
  const parsed = new Date(normalized);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
};

const padTime = (value) => String(value).padStart(2, '0');

const toDateTimeString = (date) => {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) return '';
  return `${date.getFullYear()}-${padTime(date.getMonth() + 1)}-${padTime(date.getDate())} ${padTime(date.getHours())}:${padTime(date.getMinutes())}:${padTime(date.getSeconds())}`;
};

const shiftDateString = (dateStr, offsetMs) => {
  const parsed = parseDateTime(dateStr);
  if (!parsed) return dateStr;
  return toDateTimeString(new Date(parsed.getTime() + offsetMs));
};

const syncMockItemDates = (item, offsetMs) => {
  const nextItem = { ...item, date: shiftDateString(item.date, offsetMs) };
  if (Array.isArray(item.children)) {
    nextItem.children = item.children.map(child => ({
      ...child,
      date: shiftDateString(child.date, offsetMs)
    }));
  }
  return nextItem;
};

// 专题映射
const TOPIC_MAP = {
  'TopicDrugs': '毒品交易',
  'TopicSmuggle': '非法走私',
  'TopicTerror': '恐怖暴力',
  'TopicDataLeak': '数据泄露',
  'TopicTaiwan': '台湾议题'
};

// 行业映射
const INDUSTRY_MAP = {
  'Finance': '金融',
  'Tech': '科技',
  'Gov': '政府',
  'Health': '医疗',
  'Edu': '教育'
};

export function useDashboardData() {
  // 初始化数据
  const initialListData = (() => {
    const offsetMs = Date.now() - (parseDateTime(MOCK_REFERENCE_TIME)?.getTime() || Date.now());
    return mockData.map(item => syncMockItemDates(item, offsetMs));
  })();

  const listData = ref(JSON.parse(JSON.stringify(initialListData)));

  // 筛选条件
  const filters = reactive({
    time: 'all',
    customStart: '',
    customEnd: '',
    risk: 'all',
    read: 'all',
    media: 'all',
    topic: 'all',
    region: 'all',
    rule: '',
    author: '',
    industry: ''
  });

  // UI状态
  const state = reactive({
    activeModule: 'alerts',
    leftCollapsed: false,
    rightCollapsed: false,
    isFilterCollapsed: false,
    selectAll: false,
    sort: 'time-desc',
    isSortDropdownOpen: false,
    searchQuery: '',
    pagination: {
      currentPage: 1,
      pageSize: 10
    },
    isImmersive: false,
    showCustomDate: false,
    carousel: {
      region: 0,
      author: 0
    },
    detailItem: null,
    detailVisible: false
  });

  // 计算可用筛选选项
  const availableTopics = computed(() => {
    const topics = new Set();
    listData.value.forEach(item => {
      if (item.topic) topics.add(item.topic);
    });
    return Array.from(topics);
  });

  const availableRegions = computed(() => {
    const regions = new Set();
    listData.value.forEach(item => {
      if (item.region) regions.add(item.region);
    });
    return Array.from(regions);
  });

  // 筛选后的列表
  const filteredList = computed(() => {
    let result = listData.value;

    // 时间筛选
    if (filters.time !== 'all') {
      const now = new Date();
      let startDate;
      switch (filters.time) {
        case 'today':
          startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
          break;
        case '7days':
          startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          break;
        case '30days':
          startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          break;
        case 'custom':
          if (filters.customStart) {
            startDate = parseDateTime(filters.customStart);
          }
          break;
      }
      if (startDate) {
        result = result.filter(item => {
          const itemDate = parseDateTime(item.date);
          return itemDate && itemDate >= startDate;
        });
      }
    }

    // 风险筛选
    if (filters.risk !== 'all') {
      result = result.filter(item => item.risk === filters.risk);
    }

    // 已读筛选
    if (filters.read !== 'all') {
      result = result.filter(item =>
        filters.read === 'read' ? item.read : !item.read
      );
    }

    // 媒体类型筛选
    if (filters.media !== 'all') {
      result = result.filter(item => item.source === filters.media);
    }

    // 专题筛选
    if (filters.topic !== 'all') {
      result = result.filter(item => item.topic === filters.topic);
    }

    // 地区筛选
    if (filters.region !== 'all') {
      result = result.filter(item => item.region === filters.region);
    }

    // 规则筛选
    if (filters.rule) {
      result = result.filter(item =>
        item.hitRule === filters.rule || item.hitRules?.includes(filters.rule)
      );
    }

    // 作者筛选
    if (filters.author) {
      result = result.filter(item => item.author === filters.author);
    }

    // 行业筛选
    if (filters.industry) {
      result = result.filter(item => item.industry === filters.industry);
    }

    // 排序
    result = [...result].sort((a, b) => {
      switch (state.sort) {
        case 'time-desc':
          return parseDateTime(b.date) - parseDateTime(a.date);
        case 'time-asc':
          return parseDateTime(a.date) - parseDateTime(b.date);
        case 'risk-desc':
          const riskOrder = { high: 3, mid: 2, low: 1 };
          return riskOrder[b.risk] - riskOrder[a.risk];
        case 'risk-asc':
          const riskOrderAsc = { high: 3, mid: 2, low: 1 };
          return riskOrderAsc[a.risk] - riskOrderAsc[b.risk];
        default:
          return 0;
      }
    });

    // 搜索
    if (state.searchQuery) {
      const query = state.searchQuery.toLowerCase();
      result = result.filter(item =>
        item.title?.toLowerCase().includes(query) ||
        item.content?.toLowerCase().includes(query) ||
        item.author?.toLowerCase().includes(query)
      );
    }

    return result;
  });

  // 分页后的列表
  const paginatedList = computed(() => {
    const start = (state.pagination.currentPage - 1) * state.pagination.pageSize;
    const end = start + state.pagination.pageSize;
    return filteredList.value.slice(start, end);
  });

  // 总页数
  const totalPages = computed(() =>
    Math.ceil(filteredList.value.length / state.pagination.pageSize)
  );

  // 统计数据
  const statistics = computed(() => {
    const total = filteredList.value.length;
    const high = filteredList.value.filter(i => i.risk === 'high').length;
    const mid = filteredList.value.filter(i => i.risk === 'mid').length;
    const low = filteredList.value.filter(i => i.risk === 'low').length;
    const unread = filteredList.value.filter(i => !i.read).length;
    const followed = filteredList.value.filter(i => i.followed).length;

    return { total, high, mid, low, unread, followed };
  });

  // 地区排名
  const topRegions = computed(() => {
    const regionCounts = {};
    filteredList.value.forEach(item => {
      const region = item.region || '未知';
      regionCounts[region] = (regionCounts[region] || 0) + 1;
    });

    const sorted = Object.entries(regionCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    const maxCount = sorted[0]?.[1] || 1;
    return sorted.map(([name, count]) => ({
      name,
      count,
      percent: Math.round((count / maxCount) * 100)
    }));
  });

  // 规则排名
  const topRules = computed(() => {
    const ruleCounts = {};
    filteredList.value.forEach(item => {
      if (item.hitRules) {
        item.hitRules.forEach(rule => {
          ruleCounts[rule] = (ruleCounts[rule] || 0) + 1;
        });
      } else if (item.hitRule) {
        ruleCounts[item.hitRule] = (ruleCounts[item.hitRule] || 0) + 1;
      }
    });

    const sorted = Object.entries(ruleCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    const maxCount = sorted[0]?.[1] || 1;
    return sorted.map(([name, count]) => ({
      name,
      count,
      percent: Math.round((count / maxCount) * 100)
    }));
  });

  // 作者排名
  const topAuthors = computed(() => {
    const authorCounts = {};
    filteredList.value.forEach(item => {
      if (item.author) {
        authorCounts[item.author] = (authorCounts[item.author] || 0) + 1;
      }
    });

    const sorted = Object.entries(authorCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    return sorted.map(([name, count]) => ({ name, count }));
  });

  // 方法
  const changePage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
      state.pagination.currentPage = page;
    }
  };

  const changeSort = (sort) => {
    state.sort = sort;
    state.isSortDropdownOpen = false;
  };

  const toggleSelectAll = () => {
    const newValue = state.selectAll;
    paginatedList.value.forEach(item => {
      item.selected = newValue;
    });
  };

  const markAsRead = (item) => {
    item.read = true;
  };

  const toggleAlertFollow = (item) => {
    item.followed = !item.followed;
  };

  const markFalsePositive = (item) => {
    item.risk = 'low';
    item.falsePositive = true;
  };

  const resetFilters = () => {
    Object.assign(filters, {
      time: 'all',
      customStart: '',
      customEnd: '',
      risk: 'all',
      read: 'all',
      media: 'all',
      topic: 'all',
      region: 'all',
      rule: '',
      author: '',
      industry: ''
    });
    state.showCustomDate = false;
  };

  const saveFilters = () => {
    console.log('Filters saved:', { ...filters });
  };

  const getTopicName = (topicId) => TOPIC_MAP[topicId] || topicId;
  const getIndustryName = (industryId) => INDUSTRY_MAP[industryId] || industryId;

  const getRiskText = (risk) => {
    const map = { high: '高危', mid: '中危', low: '低危' };
    return map[risk] || risk;
  };

  const getSourceIcon = (source) => {
    const icons = {
      'Telegram': 'fa-brands fa-telegram',
      'Tor': 'fa-solid fa-user-secret',
      'I2P': 'fa-solid fa-network-wired',
      'Weibo': 'fa-brands fa-weibo'
    };
    return icons[source] || 'fa-solid fa-globe';
  };

  const getEntityIcon = (type) => {
    const icons = {
      'slang': 'fa-solid fa-mask',
      'money': 'fa-solid fa-coins',
      'identity': 'fa-solid fa-id-card',
      'loc': 'fa-solid fa-location-dot',
      'logistics': 'fa-solid fa-truck'
    };
    return icons[type] || 'fa-solid fa-tag';
  };

  const getEntityClass = (type) => {
    const classes = {
      'slang': 'entity-slang',
      'money': 'entity-money',
      'identity': 'entity-identity',
      'loc': 'entity-loc',
      'logistics': 'entity-logistics'
    };
    return classes[type] || '';
  };

  const formatTime = (dateStr) => {
    const date = parseDateTime(dateStr);
    if (!date) return dateStr;
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    if (days < 7) return `${days}天前`;
    return toDateTimeString(date).split(' ')[0];
  };

  const getProvince = (region) => {
    if (!region) return '未知';
    const parts = region.split('/');
    return parts.length > 1 ? parts[1] : parts[0];
  };

  const getDisplayTitle = (item) => {
    return item.title || item.content?.slice(0, 50) || '无标题';
  };

  const getSiteLabel = (item) => {
    if (item.sourceType === 'chat') return '频道/群组';
    if (item.sourceType === 'web') return '站点';
    return '来源';
  };

  return {
    // 数据
    listData,
    filters,
    state,

    // 计算属性
    availableTopics,
    availableRegions,
    filteredList,
    paginatedList,
    totalPages,
    statistics,
    topRegions,
    topRules,
    topAuthors,

    // 方法
    changePage,
    changeSort,
    toggleSelectAll,
    markAsRead,
    toggleAlertFollow,
    markFalsePositive,
    resetFilters,
    saveFilters,
    getTopicName,
    getIndustryName,
    getRiskText,
    getSourceIcon,
    getEntityIcon,
    getEntityClass,
    formatTime,
    getProvince,
    getDisplayTitle,
    getSiteLabel
  };
}
