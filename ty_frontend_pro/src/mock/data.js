// src/mock/data.js
export const mockData = [
    {
        id: 1,
        title: "TG告警：备用涉毒频道与BTC收款地址联动出现",
        content: "模拟引擎输出场景：频道中出现“冰毒”“纯白哈希”“担保交易”等高危词，同时附带 BTC 地址与备用频道，用于验证规则筛选、关键词搜索和详情弹窗联动。",
        risk: "high",
        source: "Telegram",
        sourceType: "chat",
        siteName: "drug_deal_backup",
        author: "drug_dealer_001",
        hitRule: 'Rule_Drug_Slang',
        hitRules: ['Rule_Drug_Slang', 'Rule_Crypto_Transfer'],
        date: "2024-06-10 10:25:12",
        region: "海外/匿名网络",
        topic: "TopicDrugs",
        industry: "Finance",
        read: false,
        selected: false,
        stats: { fwd: 88, cmt: 16, sim: 3 },
        chatMeta: { groupName: "drug_deal_backup", userName: "drug_dealer_001", avatarChar: "D" },
        entities: [
            { type: 'slang', value: '纯白哈希' },
            { type: 'money', value: 'BTC:1A1zP1...' },
            { type: 'identity', value: 'drug_deal_backup' },
            { type: 'loc', value: '匿名网络' }
        ],
        children: [
            { id: '1-1', author: 'relay_node_17', date: '2024-06-10 10:32:41', content: '同一BTC地址在另一频道复现，文本结构高度相似。' },
            { id: '1-2', author: 'watcher_404', date: '2024-06-10 10:36:05', content: '备用频道元数据已进入下一跳抓取队列。' }
        ]
    },
    {
        id: 2,
        title: "暗网交易：高纯度冰毒批发与埋包",
        content: "出售高纯度冰毒（肉），支持 USDT 付款，提供埋包交易说明与地区投放信息。该条用于测试涉毒规则、地区筛选与已读状态。",
        risk: "high",
        source: "Tor",
        sourceType: "web",
        siteName: "暗网中文论坛",
        author: "毒枭之王",
        hitRule: 'Rule_Drug_Slang',
        hitRules: ['Rule_Drug_Slang'],
        date: "2024-06-10 08:00:25",
        region: "全国/广州",
        topic: "TopicDrugs",
        industry: "Finance",
        read: false,
        selected: false,
        stats: { fwd: 6, cmt: 4, sim: 5 },
        entities: [
            { type: 'slang', value: '肉' },
            { type: 'money', value: 'USDT' },
            { type: 'loc', value: '广州' },
            { type: 'slang', value: '埋包' }
        ],
        children: [
            { id: '2-1', author: '买家A', date: '2024-06-10 08:13:11', content: '询问珠三角是否支持当日投放。' }
        ]
    },
    {
        id: 3,
        title: "毒品分销群：新型致幻剂邮票流转监测",
        content: "频道中多次出现“邮票”“国际EMS”“代理起拿”等词，用于测试 Telegram 卡片样式、作者统计与规则排行。",
        risk: "high",
        source: "Telegram",
        sourceType: "chat",
        siteName: "致幻剂交流",
        author: "ChemMaster",
        hitRule: 'Rule_Drug_Slang',
        hitRules: ['Rule_Drug_Slang', 'Rule_Smuggle_Route'],
        date: "2024-06-09 14:20:10",
        region: "海外/欧洲",
        topic: "TopicDrugs",
        industry: "Tech",
        read: true,
        selected: false,
        stats: { fwd: 120, cmt: 45, sim: 2 },
        chatMeta: { groupName: "致幻剂交流", userName: "ChemMaster", avatarChar: "C" },
        entities: [
            { type: 'slang', value: '邮票' },
            { type: 'loc', value: '欧洲' },
            { type: 'logistics', value: '国际EMS' }
        ]
    },
    {
        id: 4,
        title: "跨境走私路线复盘：港口仓单与中转车队",
        content: "监测样本出现固定线路、港口堆场与夜间中转描述，匹配走私路径监控规则。适合测试地区排行、行业分布与风险排序。",
        risk: "high",
        source: "Tor",
        sourceType: "web",
        siteName: "灰港货运板",
        author: "RouteBroker",
        hitRule: 'Rule_Smuggle_Route',
        hitRules: ['Rule_Smuggle_Route'],
        date: "2024-06-08 22:11:34",
        region: "广东/深圳",
        topic: "TopicSmuggle",
        industry: "Gov",
        read: false,
        selected: false,
        stats: { fwd: 12, cmt: 3, sim: 4 },
        entities: [
            { type: 'loc', value: '深圳港' },
            { type: 'logistics', value: '中转车队' },
            { type: 'identity', value: '仓单编号A-19' }
        ]
    },
    {
        id: 5,
        title: "I2P 节点发现极端行动号召样本",
        content: "帖子中出现聚集、试爆、时间窗口等行为描述，属于高危行为意图测试样本，可用于验证恐怖暴力专题与规则点击筛选。",
        risk: "high",
        source: "I2P",
        sourceType: "web",
        siteName: "隐匿行动板",
        author: "ShadowCell",
        hitRule: 'Rule_Terror_Action',
        hitRules: ['Rule_Terror_Action'],
        date: "2024-06-10 07:42:18",
        region: "新疆/乌鲁木齐",
        topic: "TopicTerror",
        industry: "Gov",
        read: false,
        selected: false,
        stats: { fwd: 3, cmt: 1, sim: 1 },
        entities: [
            { type: 'loc', value: '乌鲁木齐' },
            { type: 'identity', value: '行动窗口' },
            { type: 'slang', value: '集合点' }
        ]
    },
    {
        id: 6,
        title: "勒索论坛：钱包轮换与赎金协商记录",
        content: "样本中反复出现加密货币收款地址、分账说明与赎金协商关键词，适合测试加密交易规则和全文搜索。",
        risk: "mid",
        source: "Tor",
        sourceType: "web",
        siteName: "RansomBoard",
        author: "LockBitClone",
        hitRule: 'Rule_Crypto_Transfer',
        hitRules: ['Rule_Crypto_Transfer'],
        date: "2024-06-07 19:15:42",
        region: "海外/东欧",
        topic: "TopicRansom",
        industry: "Tech",
        read: true,
        selected: false,
        stats: { fwd: 18, cmt: 11, sim: 4 },
        entities: [
            { type: 'money', value: 'BTC Wallet' },
            { type: 'identity', value: 'decrypt key' },
            { type: 'loc', value: '东欧' }
        ]
    },
    {
        id: 7,
        title: "数据泄露样本：教育机构账号包试售",
        content: "帖子出售教育行业账号包，要求加密货币结算并提供样例截图。可用于测试数据泄露专题、行业分布和低风险筛选。",
        risk: "low",
        source: "Weibo",
        sourceType: "social",
        siteName: "公开情报镜像",
        author: "LeakMirror",
        hitRule: 'Rule_Crypto_Transfer',
        hitRules: ['Rule_Crypto_Transfer'],
        date: "2024-06-06 11:40:00",
        region: "北京/海淀",
        topic: "TopicDataLeak",
        industry: "Edu",
        read: false,
        selected: false,
        stats: { fwd: 35, cmt: 18, sim: 2 },
        entities: [
            { type: 'identity', value: '账号包' },
            { type: 'money', value: 'USDT' },
            { type: 'loc', value: '海淀' }
        ]
    },
    {
        id: 8,
        title: "台湾议题频道：匿名筹资地址传播",
        content: "频道持续传播匿名筹资地址和导流短链，用于测试台湾专题、作者排行与加密转账规则多条件组合筛选。",
        risk: "mid",
        source: "Telegram",
        sourceType: "chat",
        siteName: "海峡观察站",
        author: "island_watch",
        hitRule: 'Rule_Crypto_Transfer',
        hitRules: ['Rule_Crypto_Transfer'],
        date: "2024-06-05 09:16:21",
        region: "台湾/台北",
        topic: "TopicTaiwan",
        industry: "Gov",
        read: false,
        selected: false,
        stats: { fwd: 64, cmt: 9, sim: 2 },
        chatMeta: { groupName: "海峡观察站", userName: "island_watch", avatarChar: "I" },
        entities: [
            { type: 'money', value: 'TRX Wallet' },
            { type: 'identity', value: '短链跳转' },
            { type: 'loc', value: '台北' }
        ]
    },
    {
        id: 9,
        title: "医疗行业样本：勒索售后协商频道",
        content: "目标为医疗行业的勒索受害通告，附有赎金钱包与客服频道信息，用来测试行业、媒体类型与多规则共现。",
        risk: "high",
        source: "Telegram",
        sourceType: "chat",
        siteName: "restore_support",
        author: "LockBitClone",
        hitRule: 'Rule_Crypto_Transfer',
        hitRules: ['Rule_Crypto_Transfer', 'Rule_Terror_Action'],
        date: "2024-06-04 16:28:09",
        region: "上海/浦东",
        topic: "TopicRansom",
        industry: "Health",
        read: true,
        selected: false,
        stats: { fwd: 91, cmt: 24, sim: 5 },
        chatMeta: { groupName: "restore_support", userName: "LockBitClone", avatarChar: "L" },
        entities: [
            { type: 'money', value: 'XMR Wallet' },
            { type: 'identity', value: 'restore_support' },
            { type: 'loc', value: '浦东' }
        ],
        children: [
            { id: '9-1', author: 'victim_case_01', date: '2024-06-04 16:40:11', content: '同一客服频道在另一条勒索通告中再次出现。' },
            { id: '9-2', author: 'victim_case_02', date: '2024-06-04 17:03:44', content: '发现相同 XMR 收款钱包，风险等级上调。' }
        ]
    },
    {
        id: 10,
        title: "闽粤海运暗线：冻品与电子件混装测试样本",
        content: "模拟情报显示货物通过冷链与电子件混装转运，命中走私路径监控规则。适合测试 7 天/30 天时间筛选差异。",
        risk: "mid",
        source: "Weibo",
        sourceType: "social",
        siteName: "物流异常线索",
        author: "RouteBroker",
        hitRule: 'Rule_Smuggle_Route',
        hitRules: ['Rule_Smuggle_Route'],
        date: "2024-05-28 13:09:27",
        region: "福建/厦门",
        topic: "TopicSmuggle",
        industry: "Tech",
        read: false,
        selected: false,
        stats: { fwd: 20, cmt: 6, sim: 1 },
        entities: [
            { type: 'logistics', value: '冷链柜' },
            { type: 'loc', value: '厦门港' },
            { type: 'identity', value: '报关单异常' }
        ]
    },
    {
        id: 11,
        title: "暴力教程镜像站：行动倒计时话术复现",
        content: "镜像站内出现倒计时、目标点位和器材说明等文本，用于测试恐怖暴力专题与规则面板的高亮联动。",
        risk: "high",
        source: "Tor",
        sourceType: "web",
        siteName: "MirrorActionHub",
        author: "ShadowCell",
        hitRule: 'Rule_Terror_Action',
        hitRules: ['Rule_Terror_Action'],
        date: "2024-06-03 21:54:50",
        region: "海外/中东",
        topic: "TopicTerror",
        industry: "Gov",
        read: false,
        selected: false,
        stats: { fwd: 7, cmt: 2, sim: 2 },
        entities: [
            { type: 'identity', value: '倒计时脚本' },
            { type: 'loc', value: '中东' },
            { type: 'slang', value: '目标点位' }
        ]
    },
    {
        id: 12,
        title: "政务数据碰撞包：地址库与身份证段测试样本",
        content: "用于模拟政务数据泄露后的黑产售卖场景，包含地址库、身份段与收款钱包信息，可测试行业、地区和风险升降序。",
        risk: "mid",
        source: "I2P",
        sourceType: "web",
        siteName: "DataHub-I2P",
        author: "LeakMirror",
        hitRule: 'Rule_Crypto_Transfer',
        hitRules: ['Rule_Crypto_Transfer'],
        date: "2024-06-02 12:06:33",
        region: "浙江/杭州",
        topic: "TopicDataLeak",
        industry: "Gov",
        read: true,
        selected: false,
        stats: { fwd: 14, cmt: 7, sim: 3 },
        entities: [
            { type: 'identity', value: '身份证段' },
            { type: 'money', value: 'USDT' },
            { type: 'loc', value: '杭州' }
        ]
    },
    {
        id: 13,
        title: "社工短链分发：高校邮箱批量验证任务",
        content: "样本中出现高校邮箱、短链登录页和返利结算地址，便于测试搜索框、专题过滤和作者统计滚动。",
        risk: "low",
        source: "Telegram",
        sourceType: "chat",
        siteName: "edu_task_pool",
        author: "LeakMirror",
        hitRule: 'Rule_Crypto_Transfer',
        hitRules: ['Rule_Crypto_Transfer'],
        date: "2024-06-01 18:22:48",
        region: "湖北/武汉",
        topic: "TopicDataLeak",
        industry: "Edu",
        read: false,
        selected: false,
        stats: { fwd: 47, cmt: 13, sim: 2 },
        chatMeta: { groupName: "edu_task_pool", userName: "LeakMirror", avatarChar: "L" },
        entities: [
            { type: 'identity', value: '高校邮箱' },
            { type: 'money', value: 'USDT' },
            { type: 'loc', value: '武汉' }
        ]
    },
    {
        id: 14,
        title: "旧样本：30 天外历史暗网交易帖",
        content: "这是一条专门用于测试时间筛选边界的历史样本，默认近 7 天和近 30 天均不会展示。",
        risk: "low",
        source: "Tor",
        sourceType: "web",
        siteName: "Archive Market",
        author: "old_vendor",
        hitRule: 'Rule_Drug_Slang',
        hitRules: ['Rule_Drug_Slang'],
        date: "2024-04-25 09:00:00",
        region: "海外/历史库",
        topic: "TopicDrugs",
        industry: "Finance",
        read: true,
        selected: false,
        stats: { fwd: 2, cmt: 0, sim: 0 },
        entities: [
            { type: 'slang', value: '历史样本' },
            { type: 'loc', value: '历史库' }
        ]
    }
];

// 在 data.js 末尾追加
export const topologyData = {
    nodes: [
        { id: "User_001", name: "暗网用户A", type: "user", color: "#ef4444" },
        { id: "IP_127.0.0.1", name: "出口节点IP", type: "ip", color: "#3b82f6" },
        { id: "Wallet_XYZ", name: "BTC钱包", type: "wallet", color: "#f59e0b" },
        { id: "Site_Abc", name: "非法交易平台", type: "site", color: "#10b981" }
    ],
    links: [
        { source: "User_001", target: "IP_127.0.0.1", relation: "登录" },
        { source: "User_001", target: "Wallet_XYZ", relation: "关联" },
        { source: "Wallet_XYZ", target: "Site_Abc", relation: "支付" }
    ]
};