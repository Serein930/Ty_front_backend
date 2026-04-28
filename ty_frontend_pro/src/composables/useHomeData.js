// composables/useHomeData.js
// Home页面数据处理逻辑

import { ref, computed, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useRouter } from 'vue-router';
import { logout } from '../auth';

export function useHomeData() {
  const router = useRouter();

  // 时间显示
  const nowTime = ref('');
  const nowTimeDisplay = ref('');
  let timeTimer = null;

  const updateNowTime = () => {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, '0');
    const d = String(now.getDate()).padStart(2, '0');
    const hh = String(now.getHours()).padStart(2, '0');
    const mm = String(now.getMinutes()).padStart(2, '0');
    const ss = String(now.getSeconds()).padStart(2, '0');
    nowTime.value = `${y}-${m}-${d} ${hh}:${mm}:${ss}`;
    nowTimeDisplay.value = `${y}年${m}月${d}日 ${hh}:${mm}:${ss}`;
  };

  // Toast
  const toastVisible = ref(false);
  const toastMessage = ref('');
  let toastTimer = null;

  const showToast = (msg) => {
    toastMessage.value = msg;
    toastVisible.value = true;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toastVisible.value = false;
    }, 1800);
  };

  // 订阅列表
  const subscriptions = ref([
    { name: '全局监控态势（默认）', country: null, type: 'all' },
    { name: '中国重点监测战位', country: '中国', type: 'all' },
    { name: '东南亚黑灰产战位', country: '新加坡', type: 'black' }
  ]);
  const selectedSubscription = ref('全局监控态势（默认）');

  // 筛选条件
  const warningStatusFilter = ref('all');
  const selectedType = ref('all');
  const statsTimeFilter = ref('24h');
  const trendTypeFilter = ref('all');
  const trendRangeFilter = ref('24');

  // 案件数据
  const warnings = ref([
    { id: 1, name: '跨境Telegram频道诈骗组织活跃', time: '2023-10-27 11:24:19', level: 'high', country: '中国', type: 'fraud', status: '待处理', detail: '多个TG频道同步发布高收益投资诱导内容，疑似同团伙控制。' },
    { id: 2, name: '暗网信用卡交易论坛出现新卖家', time: '2023-10-27 10:11:03', level: 'medium', country: '美国', type: 'black', status: '正在研判', detail: '新账户72小时内上架大量卡料，活跃于多个交易串。' },
    { id: 3, name: '仿冒支付页面钓鱼攻击升级', time: '2023-10-27 09:43:30', level: 'high', country: '中国', type: 'attack', status: '待处理', detail: '检测到批量仿冒收银台页面并通过短信进行分发。' },
    { id: 4, name: '跨境洗钱链路关联钱包增多', time: '2023-10-26 21:16:45', level: 'medium', country: '新加坡', type: 'black', status: '正在研判', detail: '链上标签显示新地址簇与历史风险实体关系增强。' },
    { id: 5, name: 'Apache漏洞攻击溯源', time: '2023-10-23 10:55:47', level: 'high', country: '日本', type: 'attack', status: '已结案', detail: '检测到Apache Struts2远程代码执行漏洞攻击尝试，需研判攻击组织。' }
  ]);

  const filteredWarnings = computed(() => {
    return warnings.value.filter(w => {
      const matchStatus = warningStatusFilter.value === 'all' || w.status === warningStatusFilter.value;
      const matchType = selectedType.value === 'all' || w.type === selectedType.value;
      const sub = subscriptions.value.find(s => s.name === selectedSubscription.value);
      const matchCountry = !sub || !sub.country || w.country === sub.country;
      const matchSubType = !sub || sub.type === 'all' || w.type === sub.type;
      return matchStatus && matchType && matchCountry && matchSubType;
    });
  });

  // 统计数据
  const warningCount = computed(() => filteredWarnings.value.filter(w => w.status !== '已结案').length);
  const handledCount = computed(() => filteredWarnings.value.filter(w => w.status === '已结案').length);
  const totalCount = computed(() => {
    const scale = statsTimeFilter.value === '24h' ? 4 : statsTimeFilter.value === '7d' ? 28 : 110;
    return filteredWarnings.value.length * scale;
  });

  // 重点人物数据
  const hotPersons = ref([
    {
      id: 101,
      alias: 'Nexus_47',
      country: '中国',
      city: '广东省 深圳市',
      platform: 'Telegram',
      score: 95,
      confidence: 97,
      type: 'fraud',
      tags: ['洗钱', '电诈', '分销'],
      desc: '活跃于跨境诈骗群组，近期交易频次上升。',
      avatar: 'https://i.pravatar.cc/80?img=12',
      assets: {
        identities: ['Nexus_47', 'Nexus-OPS', 'K-Node'],
        comms: ['+852 6912 88xx', 'nexus47@proton.me', '@nexus_ops'],
        finance: ['TRX: TQ7s...9Aa', 'USDT OTC 账户簇 #A31', '风险钱包簇 RW-13'],
        network: ['103.221.xx.xx', 'AS4134 异常节点', 'Tor Exit #9f3'],
        cases: ['Case-2024-041 电诈洗钱链', 'Case-2023-227 跨境资金回流']
      }
    },
    {
      id: 102,
      alias: 'GhostMall',
      country: '美国',
      city: '加利福尼亚州 洛杉矶',
      platform: 'Darkweb',
      score: 88,
      confidence: 92,
      type: 'black',
      tags: ['卡料', '黑市'],
      desc: '暗网交易论坛核心中介，关联多个卖家。',
      avatar: 'https://i.pravatar.cc/80?img=31',
      assets: {
        identities: ['GhostMall', 'GM-Root'],
        comms: ['session: 05ab...d2', 'ghostmall@onionmail.org'],
        finance: ['BTC: bc1q...k2p', 'Monero: 87x...4u'],
        network: ['TOR Hidden Service #gmu7', 'Cloud VPS 簇 #US-2'],
        cases: ['Case-2024-019 卡料交易网络']
      }
    },
    {
      id: 103,
      alias: 'RiverFox',
      country: '中国',
      city: '浙江省 杭州市',
      platform: 'X',
      score: 79,
      confidence: 86,
      type: 'attack',
      tags: ['漏洞', '扫描'],
      desc: '频繁发布漏洞利用脚本与目标IP段信息。',
      avatar: 'https://i.pravatar.cc/80?img=22',
      assets: {
        identities: ['RiverFox', 'rf_lab'],
        comms: ['riverfox@riseup.net', '@rf_scan'],
        finance: ['ETH: 0x8a...f3'],
        network: ['CDN 节点簇 #CN-EAST', '扫描出口 #hx2'],
        cases: ['Case-2023-088 漏洞扩散事件']
      }
    },
    {
      id: 104,
      alias: 'BlueLedger',
      country: '新加坡',
      city: '新加坡 乌节路',
      platform: 'Telegram',
      score: 84,
      confidence: 89,
      type: 'black',
      tags: ['USDT', 'OTC'],
      desc: '加密资产OTC群主，地址簇关联异常。',
      avatar: 'https://i.pravatar.cc/80?img=52',
      assets: {
        identities: ['BlueLedger', 'BL-trade'],
        comms: ['+65 91xx 77xx', '@blueledger_sg'],
        finance: ['USDT 簇 #SG-11', 'TRX: TY2...Kq'],
        network: ['SG IDC 节点 #3', '边界网关 #A7'],
        cases: ['Case-2024-113 OTC 洗钱路径']
      }
    }
  ]);

  const filteredPersons = computed(() => {
    return hotPersons.value.filter(p => {
      const matchType = selectedType.value === 'all' || p.type === selectedType.value;
      const sub = subscriptions.value.find(s => s.name === selectedSubscription.value);
      const matchCountry = !sub || !sub.country || p.country === sub.country;
      const matchSubType = !sub || sub.type === 'all' || p.type === sub.type;
      return matchType && matchCountry && matchSubType;
    });
  });

  // 实时情报数据
  const feed = ref([
    { id: 1, source: 'Telegram', icon: 'fa-brands fa-telegram', level: 'critical', clusterCount: 12, time: '11:26', title: '诈骗脚本包更新', text: '发现新版本话术模板，含银行客服冒充流程。', country: '中国' },
    { id: 2, source: 'Darkweb', icon: 'fa-solid fa-mask', level: 'high', clusterCount: 8, time: '11:14', title: '卡料交易价格波动', text: '欧美卡料批发价下调，疑似供给增加。', country: '美国' },
    { id: 3, source: 'X', icon: 'fa-brands fa-x-twitter', level: 'medium', clusterCount: 6, time: '10:58', title: '漏洞利用POC传播', text: '多个账号扩散同一漏洞POC链接，需持续跟踪。', country: '日本' },
    { id: 4, source: 'Facebook', icon: 'fa-brands fa-facebook', level: 'high', clusterCount: 4, time: '10:33', title: '仿冒投放活动', text: '发现新一轮仿冒商城广告，导流至钓鱼域名。', country: '新加坡' }
  ]);

  const filteredFeed = computed(() => {
    const sub = subscriptions.value.find(s => s.name === selectedSubscription.value);
    return feed.value.filter(f => {
      const matchCountry = !sub || !sub.country || f.country === sub.country;
      return matchCountry;
    });
  });

  // 监控节点数据
  const monitoredEntities = ref([
    { id: 1, name: 'Nexus_47', stat: '高危链路活跃', levelClass: 'critical', platformClass: 'plat-tg', icon: 'fa-brands fa-telegram', avatar: 'https://i.pravatar.cc/40?img=12' },
    { id: 2, name: 'GhostMall', stat: '黑市成交增长', levelClass: 'warning', platformClass: 'plat-tor', icon: 'fa-solid fa-ghost', avatar: 'https://i.pravatar.cc/40?img=31' },
    { id: 3, name: 'RiverFox', stat: '漏洞话题上升', levelClass: 'warning', platformClass: 'plat-x', icon: 'fa-brands fa-x-twitter', avatar: 'https://i.pravatar.cc/40?img=22' },
    { id: 4, name: 'BlueLedger', stat: '资金流向异常', levelClass: 'critical', platformClass: 'plat-fb', icon: 'fa-brands fa-facebook-f', avatar: 'https://i.pravatar.cc/40?img=52' }
  ]);

  // 国家坐标
  const countryCoordinates = {
    中国: [116.4074, 39.9042],
    美国: [-95.7129, 37.0902],
    日本: [139.6917, 35.6895],
    新加坡: [103.8198, 1.3521]
  };

  // 组织数据
  const orgRows = ref([
    { id: 1, name: 'SEA-OTC-HUB', platform: 'telegram', risk: 'high', members: 8421, country: '新加坡' },
    { id: 2, name: 'Fraud-Script-Market', platform: 'forum', risk: 'high', members: 2388, country: '中国' },
    { id: 3, name: 'Carding-Exchange', platform: 'forum', risk: 'medium', members: 1350, country: '美国' },
    { id: 4, name: 'BlueLedger Channel', platform: 'telegram', risk: 'medium', members: 6233, country: '新加坡' },
    { id: 5, name: 'RiverFox Mirror', platform: 'social', risk: 'low', members: 932, country: '中国' }
  ]);

  // 弹窗状态
  const detailVisible = ref(false);
  const detailTitle = ref('详情');
  const detailHtml = ref('');
  const detailMode = ref('generic');
  const currentPerson = ref(null);

  const eventsModalVisible = ref(false);
  const personsModalVisible = ref(false);
  const personsModalCountry = ref('all');
  const orgModalVisible = ref(false);
  const orgCountry = ref('中国');
  const orgTab = ref('telegram');
  const orgRiskFilter = ref('all');
  const countryEventsModalVisible = ref(false);
  const countryEventsTitle = ref('国家事件列表');
  const mapContextVisible = ref(false);
  const mapContextX = ref(0);
  const mapContextY = ref(0);
  const mapContextCountry = ref('中国');
  const circleMenuVisible = ref(false);
  const circleMenuX = ref(0);
  const circleMenuY = ref(0);
  const drawerVisible = ref(false);
  const drawerCountry = ref('全球');
  const cloneWorkspaceVisible = ref(false);
  const cloneTarget = ref(null);

  // 计算属性
  const drawerPersons = computed(() => hotPersons.value.filter(p => p.country === drawerCountry.value).slice(0, 5));
  const drawerEvents = computed(() => warnings.value.filter(w => w.country === drawerCountry.value).slice(0, 8));
  const drawerThreat = computed(() => {
    const all = [...drawerPersons.value.map(p => p.score), ...drawerEvents.value.map(e => (e.level === 'high' ? 90 : 70))];
    return all.length ? Math.max(...all) : 'N/A';
  });
  const drawerCount = computed(() => drawerEvents.value.length * 120 + drawerPersons.value.length * 40);

  const filteredOrgRows = computed(() => {
    return orgRows.value.filter(r => {
      const platformMatch = orgTab.value === 'social' ? r.platform === 'social' : r.platform === orgTab.value;
      const riskMatch = orgRiskFilter.value === 'all' || r.risk === orgRiskFilter.value;
      const countryMatch = !orgCountry.value || r.country === orgCountry.value;
      return platformMatch && riskMatch && countryMatch;
    });
  });

  const personsTableRows = computed(() => {
    if (personsModalCountry.value === 'all') return hotPersons.value;
    return hotPersons.value.filter(p => p.country === personsModalCountry.value);
  });

  const countryEventRows = computed(() => {
    return warnings.value.filter(w => w.country === mapContextCountry.value);
  });

  // 方法
  const applySubscription = () => {
    const current = subscriptions.value.find(s => s.name === selectedSubscription.value);
    if (!current) return;
    selectedType.value = current.type;
    showToast(`已切换至专属战位视图：【${current.name}】`);
  };

  const showWarningDetail = (item) => {
    detailMode.value = 'generic';
    currentPerson.value = null;
    detailTitle.value = '案件追踪档案 (InvestigationCase)';
    detailHtml.value = `
      <h3 style="color:#fff;margin-bottom:10px;">${escapeHTML(item.name)}</h3>
      <p style="margin-bottom:8px;"><b>发生时间:</b> ${escapeHTML(item.time)}</p>
      <p style="margin-bottom:8px;"><b>地区:</b> ${escapeHTML(item.country)}</p>
      <p style="margin-bottom:8px;"><b>状态:</b> ${escapeHTML(item.status)}</p>
      <p><b>研判摘要:</b> ${escapeHTML(item.detail || '暂无')}</p>
    `;
    detailVisible.value = true;
  };

  const showPersonDetail = (person) => {
    detailMode.value = 'person';
    currentPerson.value = person;
    detailTitle.value = '重点人物战术画像 (SubjectProfile)';
    detailVisible.value = true;
  };

  const showFeedDetail = (cluster) => {
    detailMode.value = 'generic';
    currentPerson.value = null;
    detailTitle.value = '事件簇详情 (CorrelationCluster)';
    detailHtml.value = `
      <h3 style="color:#fff;margin-bottom:10px;">${escapeHTML(cluster.title)}</h3>
      <p style="margin-bottom:8px;"><b>来源:</b> ${escapeHTML(cluster.source)}</p>
      <p style="margin-bottom:8px;"><b>时间:</b> ${escapeHTML(cluster.time)}</p>
      <p style="margin-bottom:8px;"><b>归并量:</b> ${escapeHTML(String(cluster.clusterCount))}</p>
      <p style="margin-bottom:8px;"><b>等级:</b> ${escapeHTML(levelText(cluster.level))}</p>
      <p><b>摘要:</b> ${escapeHTML(cluster.text)}</p>
    `;
    detailVisible.value = true;
  };

  const openOrgList = (country) => {
    orgCountry.value = country || '中国';
    orgModalVisible.value = true;
  };

  const showCountryEventsList = (country) => {
    mapContextCountry.value = country || '中国';
    countryEventsTitle.value = `${mapContextCountry.value} 国家事件列表`;
    countryEventsModalVisible.value = true;
    mapContextVisible.value = false;
    circleMenuVisible.value = false;
  };

  const showPersonList = (country) => {
    personsModalCountry.value = country || 'all';
    personsModalVisible.value = true;
    mapContextVisible.value = false;
    circleMenuVisible.value = false;
  };

  const showCountryDrawerFromMenu = () => {
    drawerCountry.value = mapContextCountry.value;
    drawerVisible.value = true;
    mapContextVisible.value = false;
    circleMenuVisible.value = false;
  };

  const openCircleMenuAtContext = () => {
    circleMenuX.value = mapContextX.value + 10;
    circleMenuY.value = mapContextY.value + 10;
    circleMenuVisible.value = true;
    mapContextVisible.value = false;
  };

  const hideFloatingMenus = () => {
    mapContextVisible.value = false;
    circleMenuVisible.value = false;
  };

  const openCloneWorkspace = (person) => {
    cloneTarget.value = person;
    cloneWorkspaceVisible.value = true;
  };

  const goTo = (path) => {
    router.push(path);
  };

  const logoutToLogin = () => {
    logout();
    router.replace('/login');
  };

  const avatarInitial = (name = '') => {
    const s = String(name).trim();
    if (!s) return 'NA';
    if (s.length === 1) return s.toUpperCase();
    return s.slice(0, 2).toUpperCase();
  };

  const scoreClass = (score) => {
    if (score >= 90) return 'p-score-critical';
    if (score >= 75) return 'p-score-high';
    if (score >= 50) return 'p-score-medium';
    return 'p-score-low';
  };

  const statusClass = (status) => {
    if (status === '待处理') return 'status-todo';
    if (status === '正在研判') return 'status-doing';
    return 'status-done';
  };

  const escapeHTML = (str = '') => {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  };

  const levelText = (level) => {
    if (level === 'critical') return '高危';
    if (level === 'high') return '关注';
    if (level === 'medium') return '追踪';
    return '低危';
  };

  const closeDetailModal = () => {
    detailVisible.value = false;
  };

  const handleMapClick = (countryName) => {
    drawerCountry.value = countryName;
    mapContextCountry.value = countryName;
    drawerVisible.value = true;
  };

  const handleContextMenu = ({ x, y }) => {
    const sub = subscriptions.value.find(s => s.name === selectedSubscription.value);
    mapContextCountry.value = drawerCountry.value !== '全球' ? drawerCountry.value : (sub?.country || '中国');
    mapContextX.value = x;
    mapContextY.value = y;
    mapContextVisible.value = true;
    circleMenuVisible.value = false;
  };

  // 生命周期
  onMounted(() => {
    updateNowTime();
    timeTimer = setInterval(updateNowTime, 1000);
    document.addEventListener('click', hideFloatingMenus);
  });

  onUnmounted(() => {
    clearInterval(timeTimer);
    clearTimeout(toastTimer);
    document.removeEventListener('click', hideFloatingMenus);
  });

  return {
    // 时间
    nowTime,
    nowTimeDisplay,

    // Toast
    toastVisible,
    toastMessage,
    showToast,

    // 订阅
    subscriptions,
    selectedSubscription,

    // 筛选
    warningStatusFilter,
    selectedType,
    statsTimeFilter,
    trendTypeFilter,
    trendRangeFilter,

    // 数据
    warnings,
    filteredWarnings,
    warningCount,
    handledCount,
    totalCount,
    hotPersons,
    filteredPersons,
    feed,
    filteredFeed,
    monitoredEntities,
    countryCoordinates,
    orgRows,

    // 弹窗状态
    detailVisible,
    detailTitle,
    detailHtml,
    detailMode,
    currentPerson,
    eventsModalVisible,
    personsModalVisible,
    personsModalCountry,
    orgModalVisible,
    orgCountry,
    orgTab,
    orgRiskFilter,
    countryEventsModalVisible,
    countryEventsTitle,
    mapContextVisible,
    mapContextX,
    mapContextY,
    mapContextCountry,
    circleMenuVisible,
    circleMenuX,
    circleMenuY,
    drawerVisible,
    drawerCountry,
    cloneWorkspaceVisible,
    cloneTarget,

    // 计算属性
    drawerPersons,
    drawerEvents,
    drawerThreat,
    drawerCount,
    filteredOrgRows,
    personsTableRows,
    countryEventRows,

    // 方法
    applySubscription,
    showWarningDetail,
    showPersonDetail,
    showFeedDetail,
    openOrgList,
    showCountryEventsList,
    showPersonList,
    showCountryDrawerFromMenu,
    openCircleMenuAtContext,
    hideFloatingMenus,
    openCloneWorkspace,
    goTo,
    logoutToLogin,
    avatarInitial,
    scoreClass,
    statusClass,
    escapeHTML,
    levelText,
    closeDetailModal,
    handleMapClick,
    handleContextMenu
  };
}
