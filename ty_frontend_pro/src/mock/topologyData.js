// src/mock/topologyData.js

export const predicateMap = {
    "DIRECT_CONTROL": { zh: "直接控制/指挥", type: "command" }, "COORDINATE": { zh: "行动密谋", type: "command" }, "AUTHORIZE": { zh: "授权招募", type: "command" }, "INSTRUCT": { zh: "指令下达", type: "command" },
    "ACCOUNT_LOGIN": { zh: "涉黑运维", type: "propaganda" }, "DEVICE_FINGERPRINT": { zh: "设备指纹一致", type: "traffic" }, "URL_REDIRECT": { zh: "引流跳转", type: "referral" }, "BIO_LINK": { zh: "主页挂链", type: "referral" }, "PINNED_MSG": { zh: "置顶引流", type: "referral" },
    "ITEM_PURCHASE": { zh: "暗网采购", type: "material" }, "PROCURE": { zh: "前体/原料采购", type: "material" }, "CUSTOM_ORDER": { zh: "黑产定制", type: "material" },
    "ASSET_TRANSFER": { zh: "黑资转账", type: "finance" }, "OTC_TRADE": { zh: "场外洗白", type: "finance" }, "CROWDFUNDING": { zh: "非法众筹", type: "finance" },
    "REMOTE_ACCESS": { zh: "跳板控制", type: "traffic" }, "DNS_RESOLUTION": { zh: "域名解析", type: "traffic" }, "PHYSICAL_MEET": { zh: "线下碰头", type: "traffic" },
    "CUSTOMS_DECLARATION": { zh: "虚假报关", type: "logistics" }, "MANIFEST_MATCH": { zh: "单货匹配", type: "logistics" }, "PHYSICAL_TRANSPORT": { zh: "实体承运", type: "logistics" },
    "SHARED_IOC": { zh: "共享IOC特征", type: "command" } 
};

export const scenarioDB = {
    "terrorism": {
        meta: { group_id: "Operation-918-Terror", category: "INTEL_TERRORISM", category_label: "918特大连环暴恐袭击案", level: "S", risk_score: 99.8, description: "极端组织通过海外加密群组招募本土死忠分子，利用比特币网络规避监管进行暴恐资金众筹，并通过多层洗钱网络多批次采购硝酸铵与无人机起爆组件。系统检测到高危线下碰头网络与 C2 联络基建。" },
        sourceRegistry: {
            "SRC-001": { type: "SIGINT/国安", name: "骨干网加密流量侦测", reliability: "A", frequency: "实时", desc: "国家级防火墙流量审计与 TLS 指纹识别。" },
            "SRC-002": { type: "OSINT/暗网", name: "极端主义论坛爬虫", reliability: "C", frequency: "周更", desc: "自动提取宣传手册与招募帖。" },
            "SRC-003": { type: "HUMINT/反恐", name: "线人代号 [深潜者]", reliability: "A", frequency: "单次", desc: "打入组织内部获取的核心密会情报。" },
            "SRC-004": { type: "SIGINT/网安", name: "C2 资产测绘系统", reliability: "A", frequency: "每日", desc: "全球高危端口与协议扫描。" },
            "SRC-005": { type: "FIN/网链", name: "AML 链上追踪引擎", reliability: "A", frequency: "实时", desc: "去匿名化资金溯源与混币器穿透。" },
            "SRC-006": { type: "GOV/公安", name: "化危品管控平台", reliability: "A", frequency: "实时", desc: "易制爆化学品流向监控。" }
        },
        nodes: [
            { id: "u1", type: "user", role: "leader", name: "Al_Zawahiri_X", avatar: "/offline/avatar-default.svg", score: 99, risk: "CRITICAL", tags: ["精神领袖", "海外遥控"], known_aliases: ["Abu_Bakr_Admin", "The_Guide"], location: "Middle East" },
            { id: "u2", type: "user", role: "finance", name: "Crypto_Fund_Ops", avatar: "/offline/avatar-default.svg", score: 85, risk: "HIGH", tags: ["地下钱庄", "暴恐融资"], location: "SE Asia" },
            { id: "u3", type: "user", role: "member", name: "Local_Cell_Lead", avatar: "/offline/avatar-default.svg", score: 95, risk: "CRITICAL", tags: ["行动组长", "潜伏人员"], location: "Domestic" },
            { id: "u4", type: "user", role: "contact", name: "Tech_Support_Abu", avatar: "/offline/avatar-default.svg", score: 75, risk: "HIGH", tags: ["网络运维", "炸药技师"], location: "Eastern Europe" },
            { id: "s_alfida", type: "social_private", subtype: "DARKWEB_FORUM", value: "Al-Fida.onion", label: "🧅 DW: Al-Fida 论坛", risk: "CRITICAL", location: "Tor Network", provenance: { source: "极端主义论坛爬虫", time: "2026-01-10 10:05" } },
            { 
                id: "s1", type: "social_private", subtype: "TELEGRAM", value: "t.me/Holy_War_Channel", label: "✈️ TG: 主频道", risk: "CRITICAL", location: "Proxy IP", 
                known_aliases: ["Al-Fida Official", "Voice of Jihad (旧群)"],
                pending_aliases: [ { target_id: "s_ghost", target_name: "t.me/Holy_War_Backup", conf: 0.92, reason: "发帖时间序列 99% 重合，且经常互相转发置顶消息，引擎判定为防封备用群矩阵。" } ],
                provenance: { source: "流量还原分析", time: "2026-01-10 12:00", reliability: "B", telemetry: { funnel_stage: "PROMOTION", route_corridor: "SOCIAL_TG_API", query_family: "KEYWORD_OSINT" } }, 
                content_cluster: [
                    { time: "2026-01-10 10:05", source: "暗网论坛 Al-Fida", desc: "首发阿拉伯语版《圣战招募手册》与加密宣誓视频。发布者带有头目专属 PGP 签名。", hash: "sha256:8f2a99c..." }, 
                    { time: "2026-01-10 12:00", source: "Telegram 主频道", desc: "翻译为本地语言并置顶，附带了众筹专用的 BTC 混币前地址。", hash: "sha256:1a2b55d..." },
                    { time: "2026-01-11 08:30", source: "Twitter/X 矩阵号", desc: "外围矩阵发布“狗哨”短文，使用隐晦的 Emoji 组合，并在评论区第一条挂载了 Telegram 加密群组的短链接。", hash: "sha256:3c4d77f..." },
                    { time: "2026-01-11 15:00", source: "Discord (FPS 私服)", desc: "将宣传手册伪装成“射击游戏透视MOD.zip”，在玩家群内诱导下载，内部包含木马与参组链接。", hash: "sha256:9e8b11c..." },
                    { time: "2026-01-12 22:00", source: "本地地下 BBS", desc: "出现高度同源的招募黑话，指导如何使用 VPN 翻墙接入主 Telegram 频道。", hash: "sha256:5d6e22a..." }
                ] 
            },
            { id: "s_ghost", type: "social_private", subtype: "TELEGRAM", value: "t.me/Holy_War_Backup", label: "✈️ TG: 备用群(矩阵)", risk: "HIGH", location: "Proxy IP", provenance: { source: "自动拓线发现", time: "2026-01-10 10:05" } },
            { id: "s2", type: "social_public", subtype: "TWITTER", value: "@Truth_Awaken_99", label: "🐦 X: 宣传矩阵号", risk: "MEDIUM", location: "Proxy IP", known_aliases: ["@Awaken_Truth_88", "@Truth_Backup_01"], provenance: { source: "OSINT 爬虫", time: "2026-01-11 08:30" } },
            { id: "s_discord", type: "social_private", subtype: "DISCORD", value: "Discord_FPS_Server", label: "🎮 Discord: 游戏私服", risk: "HIGH", location: "US East", provenance: { source: "文件木马外联溯源", time: "2026-01-11 15:00" } },
            { id: "s_bbs", type: "social_public", subtype: "DARKWEB_FORUM", value: "Local_Underground_BBS", label: "🌐 本地地下 BBS", risk: "MEDIUM", location: "Domestic", provenance: { source: "全网舆情监测", time: "2026-01-12 22:00" } },
            { id: "e1", type: "wallet", subtype: "BTC", value: "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", label: "BTC: 众筹主地址", risk: "CRITICAL", location: "Proxy IP", provenance: { source: "链上监测", time: "2026-01-11 15:30" } },
            { id: "e2", type: "wallet", subtype: "BTC", value: "Tornado_Cash_Router_A", label: "🌪️ 混币器路由节点", risk: "HIGH", location: "Unknown", provenance: { source: "链上图分析", time: "2026-01-14 10:00" } },
            { id: "m1", type: "material", subtype: "CHEMICAL", value: "Ammonium_Nitrate_200kg", label: "🧪 硝酸铵 200kg", risk: "CRITICAL", location: "Domestic", provenance: { source: "化工交易系统", time: "2026-02-01 08:00" } },
            { id: "t1", type: "traffic", subtype: "LOCATION", value: "Safehouse_Abnd_Factory", label: "📍 废弃化工厂密会点", risk: "CRITICAL", location: "Domestic", provenance: { source: "线人代号 [深潜者]", time: "2026-02-10 22:00" } },
            { id: "t2", type: "traffic", subtype: "C2", value: "185.11.22.33", label: "🖥️ 加密通讯 C2", risk: "HIGH", location: "Bulletproof Hosting", provenance: { source: "C2 资产测绘系统", time: "2026-01-05 11:00" } }
        ],
        links: [
            { source: "u1", target: "s_alfida", type: "command", predicate: "ACCOUNT_LOGIN", evidence_id: "T-P01", timestamp: "2026-01-10 10:05", conf: 0.99, evidences: [{ evidence_id: "CAP-T00", source_id: "SRC-001", method: "TLS指纹溯源", conf: 0.99, capsule: { vitality_status: "ARCHIVED", capture_time: "2026-01-10Z", target_url: "tcp://tor_node", snapshot: { type: "JSON", content_hash: "sha256:ja3_match" } } }] },
            { source: "s_alfida", target: "s1", type: "referral", predicate: "URL_REDIRECT", evidence_id: "T-P02", timestamp: "2026-01-10 12:00", conf: 0.95, evidences: [{ evidence_id: "CAP-T01", source_id: "SRC-002", method: "暗网发帖外链提取", conf: 0.95, capsule: { vitality_status: "LIVE", capture_time: "2026-01-10Z", snapshot: { type: "JSON", content_hash: "sha256:onion_html" } } }] },
            { source: "s2", target: "s1", type: "referral", predicate: "URL_REDIRECT", evidence_id: "T-P03", timestamp: "2026-01-11 08:30", conf: 0.9, evidences: [{ evidence_id: "CAP-T02", source_id: "SRC-002", method: "短链穿透", conf: 0.9, capsule: { vitality_status: "DEGRADED", capture_time: "2026-01-11Z", snapshot: { type: "JSON", content_hash: "sha256:bitly_redirect" } } }] },
            { source: "s1", target: "s_discord", type: "referral", predicate: "SHARED_IOC", evidence_id: "T-P04", timestamp: "2026-01-11 15:00", conf: 0.85 },
            { source: "s_discord", target: "s_bbs", type: "referral", predicate: "URL_REDIRECT", evidence_id: "T-P05", timestamp: "2026-01-12 22:00", conf: 0.8 },
            { source: "u1", target: "u4", type: "command", predicate: "DIRECT_CONTROL", evidence_id: "T-001b", timestamp: "2026-01-08 12:00", conf: 0.88 },
            { source: "u4", target: "t2", type: "traffic", predicate: "REMOTE_ACCESS", evidence_id: "T-001c", timestamp: "2026-01-09 15:00", conf: 0.95, evidences: [{ evidence_id: "CAP-T03", source_id: "SRC-004", method: "主动测绘探针", conf: 0.95, capsule: { vitality_status: "LIVE", capture_time: "2026-01-09Z", target_url: "ssh://185.11.22.33", snapshot: { type: "JSON", content_hash: "sha256:banner_grab" } } }] },
            { source: "u1", target: "s_ghost", type: "command", predicate: "ACCOUNT_LOGIN", evidence_id: "T-001g", timestamp: "2026-01-10 10:10", conf: 0.88 },
            { source: "s1", target: "e1", type: "finance", predicate: "CROWDFUNDING", evidence_id: "T-002", timestamp: "2026-01-11 15:30", conf: 1.0, raw_content_preview: "兄弟们，圣战需要你们的支持，为了真主，请将资金打入此比特币众筹主地址：bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", matched_terms: {"TERRORISM": ["圣战", "真主"], "FINANCE": ["众筹"]}, evidences: [{ evidence_id: "CAP-T04", source_id: "SRC-002", method: "OCR图像提取", conf: 1.0, capsule: { vitality_status: "LIVE", target_url: "tg://msg", capture_time: "2026-01-11Z", snapshot: { type: "IMAGE", content_hash: "sha256:xx", url: "/offline/evidence-snapshot.svg", ocr_text: "支持圣战资金众筹账户\nBTC Address: bc1qxy...wlh" } } }] },
            { source: "e1", target: "e2", type: "finance", predicate: "ASSET_TRANSFER", evidence_id: "T-003", timestamp: "2026-01-14 10:15", conf: 0.9, evidences: [{ evidence_id: "CAP-T05", source_id: "SRC-005", method: "链上资金流向分析", conf: 0.9, capsule: { vitality_status: "LIVE", capture_time: "2026-01-14Z", target_url: "btc://tx/998ab...", snapshot: { type: "JSON", content_hash: "sha256:blockchain_ledger_tx" } } }] },
            { source: "e2", target: "u2", type: "finance", predicate: "OTC_TRADE", evidence_id: "T-004", timestamp: "2026-01-15 09:15", conf: 0.85, evidences: [{ evidence_id: "CAP-T06", source_id: "SRC-005", method: "混币器去匿名化溯源", conf: 0.85, note: "通过交易时间差与金额匹配锁定承兑商。", capsule: { vitality_status: "ARCHIVED", capture_time: "2026-01-15Z", snapshot: { type: "JSON", content_hash: "sha256:heuristics_match" } } }] },
            { source: "u2", target: "m1", type: "material", predicate: "PROCURE", evidence_id: "T-005", timestamp: "2026-02-01 08:00", conf: 0.9, evidences: [{ evidence_id: "CAP-T07", source_id: "SRC-006", method: "对公账户流水比对", conf: 0.9, capsule: { vitality_status: "LIVE", capture_time: "2026-02-01Z", snapshot: { type: "PDF", content_hash: "sha256:bank_statement_scan" } } }] },
            { source: "u3", target: "m1", type: "logistics", predicate: "PHYSICAL_TRANSPORT", evidence_id: "T-007", timestamp: "2026-02-05 14:00", conf: 0.8 },
            { source: "u3", target: "t1", type: "traffic", predicate: "PHYSICAL_MEET", evidence_id: "T-009", timestamp: "2026-02-10 22:00", conf: 0.95, evidences: [{ evidence_id: "CAP-T09", source_id: "SRC-003", method: "基站定位伴随", conf: 0.95, capsule: { vitality_status: "ARCHIVED", capture_time: "2026-02-10Z", snapshot: { type: "JSON", content_hash: "loc:9981_audio_record" } } }] },
            { source: "u4", target: "u3", type: "command", predicate: "COORDINATE", evidence_id: "T-010", timestamp: "2026-02-09 20:00", conf: 0.75 } 
        ]
    },
    "smuggling": {
        meta: { group_id: "Smuggle-Syndicate-V", category: "INTEL_SMUGGLING", category_label: "猎狐行动：跨国豪车走私网络", level: "A", risk_score: 88.5, description: "锁定一条利用离岸空壳公司洗钱，通过虚假贸易合同掩护，并买通内部人员伪造海关提单走私的产业链。" },
        sourceRegistry: {
            "SRC-CUST": { type: "GOV/海关", name: "国家口岸报关数据库", reliability: "A", frequency: "实时", desc: "电子提单与货柜流转记录。" },
            "SRC-BANK": { type: "FIN/银监", name: "SWIFT 跨国结算追踪", reliability: "A", frequency: "T+1", desc: "对公账户大额流水监控。" },
            "SRC-CORP": { type: "OSINT/企查查", name: "全球离岸公司注册库", reliability: "B", frequency: "月更", desc: "挖掘空壳公司董监高信息。" },
            "SRC-LI": { type: "GOV/技侦", name: "合法监听截获 (Lawful Intercept)", reliability: "A", frequency: "实时", desc: "通讯运营商短信及语音截获。" }
        },
        nodes: [
            { id: "u1", type: "user", role: "leader", name: "Boss_Wang", avatar: "/offline/avatar-default.svg", score: 92, risk: "HIGH", known_aliases: ["王老板", "大飞王", "HK-Wang"], location: "Hong Kong" },
            { id: "u2", type: "user", role: "logistics", name: "Port_Insider_L", avatar: "/offline/avatar-default.svg", score: 80, risk: "HIGH", location: "Shanghai" },
            { id: "u3", type: "user", role: "contact", name: "Legal_Rep_Chen", avatar: "/offline/avatar-default.svg", score: 65, risk: "MEDIUM", tags: ["白手套", "法代"], location: "BVI" },
            { id: "e1", type: "bank", subtype: "BANK", value: "BVI_Shell_Corp_Account", label: "🏦 离岸空壳对公账户", risk: "CRITICAL", location: "Proxy IP", provenance: { source: "SWIFT 跨国结算追踪", time: "2026-01-20 09:00" } },
            { id: "s_proton", type: "social_private", subtype: "EMAIL", value: "Boss_ProtonMail", label: "📧 Proton: 头目邮箱", risk: "HIGH", location: "Switzerland", provenance: { source: "骨干网加密流量", time: "2026-02-01 07:00" } },
            { id: "s_wa", type: "social_private", subtype: "WHATSAPP", value: "WA_Contact_Chen", label: "💬 WA: 阅后即焚", risk: "HIGH", location: "Mobile Net", provenance: { source: "设备后门提取", time: "2026-02-01 08:30" } },
            { id: "s_ding", type: "social_private", subtype: "DINGTALK", value: "Ding_Port_Group", label: "📱 钉钉: 港口外包群", risk: "MEDIUM", location: "Domestic", provenance: { source: "内部举证", time: "2026-02-04 09:00" } },
            { 
                id: "s1", type: "social_private", subtype: "WECHAT", value: "wxid_smuggle99", label: "💬 WX: 内部对接群", risk: "HIGH", location: "Domestic", 
                known_aliases: ["A-王总报关代理", "顺风货运-老李"],
                provenance: { source: "内部举证", time: "2026-02-01 10:00" },
                content_cluster: [
                    { time: "2026-02-01 07:00", source: "ProtonMail (端到端加密邮件)", desc: "香港头目向中间人发送原始的真实车辆清单（PDF）与虚假废塑料报关单模板，要求‘老规矩处理’。", hash: "sha256:77b102c..." },
                    { time: "2026-02-01 08:30", source: "WhatsApp (阅后即焚)", desc: "中间人将修改后的集装箱柜号脱敏后，发送给上海港口的内鬼，并约定了 USDT 尾款的支付时间。", hash: "sha256:88c213d..." },
                    { time: "2026-02-01 10:00", source: "WeChat (内部项目群)", desc: "内鬼在微信群内使用黑话，如‘今晚两批海鲜到港，走绿色通道，别开箱伤了货’，同步给地面接应车队。", hash: "sha256:99d324e..." },
                    { time: "2026-02-04 09:00", source: "DingTalk (港口外包调度群)", desc: "内鬼滥用职权，在正常工作群中下发了修改监控摄像头朝向的‘日常维护’工单，为走私车辆出港清空视野。", hash: "sha256:00e435f..." }
                ]
            },
            { id: "e2", type: "bol", subtype: "DOCUMENT", value: "BOL-HK-2026091", label: "📄 伪造提单:废塑料", risk: "CRITICAL", location: "Hong Kong", provenance: { source: "国家口岸报关数据库", time: "2026-02-05 11:00" } },
            { id: "e3", type: "container", subtype: "CONTAINER", value: "TGHU8992110", label: "📦 货柜 TGHU899...", risk: "CRITICAL", location: "Shanghai", provenance: { source: "港口调度系统", time: "2026-02-06 14:00" } },
            { id: "m1", type: "material", subtype: "VEHICLE", value: "Porsche_911_GT3_x4", label: "🚗 保时捷GT3 x4台", risk: "HIGH", location: "Shanghai", provenance: { time: "2026-02-10 08:00" } }
        ],
        links: [
            { source: "u1", target: "s_proton", type: "command", predicate: "ACCOUNT_LOGIN", evidence_id: "S-P01", timestamp: "2026-02-01 07:00", conf: 0.99 },
            { source: "s_proton", target: "s_wa", type: "command", predicate: "INSTRUCT", evidence_id: "S-P02", timestamp: "2026-02-01 08:30", conf: 0.9, evidences: [{ evidence_id: "CAP-S01", source_id: "SRC-LI", method: "消息解密", conf: 0.9, capsule: { vitality_status: "DEGRADED", capture_time: "2026-02-01Z", snapshot: { type: "JSON", content_hash: "sha256:wa_msg_dump" } } }] },
            { source: "s_wa", target: "s1", type: "command", predicate: "INSTRUCT", evidence_id: "S-P03", timestamp: "2026-02-01 10:00", conf: 0.85 },
            { source: "s1", target: "s_ding", type: "command", predicate: "INSTRUCT", evidence_id: "S-P04", timestamp: "2026-02-04 09:00", conf: 0.95 },
            { source: "u1", target: "u3", type: "command", predicate: "DIRECT_CONTROL", evidence_id: "S-000", timestamp: "2025-10-15 09:00", conf: 0.95, evidences: [{ evidence_id: "CAP-S02", source_id: "SRC-CORP", method: "工商档案穿透", conf: 0.95, capsule: { vitality_status: "LIVE", capture_time: "2025-10-15Z", snapshot: { type: "PDF", content_hash: "sha256:registry_doc" } } }] },
            { source: "u3", target: "e1", type: "finance", predicate: "AUTHORIZE", evidence_id: "S-000c", timestamp: "2025-12-01 09:00", conf: 0.99 },
            { source: "u1", target: "e1", type: "finance", predicate: "ASSET_TRANSFER", evidence_id: "S-001", timestamp: "2026-01-20 09:00", conf: 1.0, evidences: [{ evidence_id: "CAP-S03", source_id: "SRC-BANK", method: "SWIFT报文解析", conf: 1.0, capsule: { vitality_status: "LIVE", capture_time: "2026-01-20Z", snapshot: { type: "JSON", content_hash: "sha256:mt103_msg" } } }] },
            { source: "u2", target: "e2", type: "logistics", predicate: "CUSTOMS_DECLARATION", evidence_id: "S-003", timestamp: "2026-02-05 11:00", conf: 1.0, evidences: [{ evidence_id: "CAP-S04", source_id: "SRC-CUST", method: "EDI电子报关单比对", conf: 1.0, capsule: { vitality_status: "LIVE", capture_time: "2026-02-05Z", snapshot: { type: "PDF", content_hash: "sha256:edi_doc" } } }] },
            { source: "e2", target: "e3", type: "logistics", predicate: "MANIFEST_MATCH", evidence_id: "S-004", timestamp: "2026-02-06 14:00", conf: 0.95, evidences: [{ evidence_id: "CAP-S05", source_id: "SRC-CUST", method: "舱单系统拉取", conf: 0.95, capsule: { vitality_status: "LIVE", capture_time: "2026-02-06Z", snapshot: { type: "JSON", content_hash: "sha256:manifest" } } }] },
            { source: "e3", target: "m1", type: "logistics", predicate: "PHYSICAL_TRANSPORT", evidence_id: "S-005", timestamp: "2026-02-10 08:00", conf: 0.99, evidences: [{ evidence_id: "CAP-S06", source_id: "SRC-CUST", method: "X光机检图像比对", conf: 0.99, capsule: { vitality_status: "LIVE", capture_time: "2026-02-10Z", snapshot: { type: "IMAGE", content_hash: "sha256:xray_anomaly" } } }] }
        ]
    },
    "narcotics": {
        meta: { group_id: "Cartel-DarkNet-X", category: "INTEL_NARCOTICS", category_label: "暗网网络贩毒与加密资产洗白", level: "S", risk_score: 95.0, description: "跨国贩毒集团通过暗网论坛挂售毒品，使用 XMR 隐私币交易，并通过复杂的混币器网络及交易所套现洗白资产。" },
        sourceRegistry: {
            "SRC-003": { type: "DARKWEB/探针", name: "Tor 交易监控网", reliability: "B", frequency: "每日", desc: "暗网黑市商品快照提取。" },
            "SRC-005": { type: "SIGINT/链上", name: "AML 链上追踪引擎", reliability: "A", frequency: "实时", desc: "去匿名化资金溯源。" },
            "SRC-006": { type: "OSINT/社交", name: "TG 僵尸网络捕获", reliability: "B", frequency: "实时", desc: "诱捕并反向解析 TG 交易机器人。" }
        },
        nodes: [
            { id: "u1", type: "user", role: "leader", name: "El_Patron", avatar: "/offline/avatar-default.svg", score: 99, risk: "CRITICAL", tags: ["毒枭", "暗网担保"], location: "Mexico" },
            { id: "u2", type: "user", role: "member", name: "Mule_Runner_01", avatar: "/offline/avatar-default.svg", score: 65, risk: "MEDIUM", tags: ["骡子", "线下抛货"], location: "Hong Kong" },
            { id: "s4", type: "social_private", subtype: "DARKWEB_FORUM", value: "onion...market", label: "🧅 DW: SilkRoad V4", risk: "CRITICAL", location: "Proxy IP", provenance: { source: "Tor 交易监控网", time: "2026-02-01 02:00" } },
            { id: "s_dread", type: "social_public", subtype: "DARKWEB_FORUM", value: "Dread_Forum_Post", label: "🧅 DW: Dread 测评帖", risk: "HIGH", location: "Tor Network", provenance: { source: "Tor 交易监控网", time: "2026-02-01 05:00" } },
            { id: "s_session", type: "social_private", subtype: "OTHER", value: "Session_App_Chat", label: "📱 Session: 端到端通讯", risk: "CRITICAL", location: "Decentralized", provenance: { source: "手机取证", time: "2026-02-03 20:00" } },
            { 
                id: "s1", type: "social_private", subtype: "TELEGRAM", value: "@Auto_DeadDrop_Bot", label: "🤖 TG: 抛货机器人", risk: "HIGH", location: "Telegram API", 
                known_aliases: ["@HK_Drop_Bot_V2", "@SafeTrade_Bot"],
                pending_aliases: [ { target_id: "s1_matrix", target_name: "@HK_DeadDrop_Bot_03", conf: 0.88, reason: "机器人代码框架与交互指令集完全一致，归属同一套僵尸网络 C2 矩阵。" } ],
                provenance: { source: "TG 僵尸网络捕获", time: "2026-02-02 10:00" },
                content_cluster: [
                    { time: "2026-02-01 02:00", source: "SilkRoad V4 (商家后台)", desc: "供应商账号 El_Patron 上架了新的 SKU: 50kg 纯品可卡因，设置了动态价格锚定 BTC 汇率，并配置了自动化回执。", hash: "sha256:11a2b3c..." },
                    { time: "2026-02-01 05:00", source: "Dread 论坛 (暗网 Reddit)", desc: "发布预热帖，利用信誉分极高的老号发布产品测评背书，并留下了专属的隐蔽交易链接。命中地下黑市推广模式。", hash: "sha256:22b3c4d..." },
                    { time: "2026-02-02 10:00", source: "Telegram 机器人群发", desc: "自动抛货机器人 @Auto_DeadDrop_Bot 向历史有过交易记录的 500+ VIP 买家定向推送了补货通知及最新的 XMR 收款地址。", hash: "sha256:33c4d5e..." },
                    { time: "2026-02-03 20:00", source: "Session App (去中心化即时通讯)", desc: "接单的“骡子”在端到端加密应用内，收到了系统自动生成的包含埋货点 GPS 坐标和挖掘深度的阅后即焚消息。", hash: "sha256:44d5e6f..." }
                ]
            },
            { id: "s1_matrix", type: "social_private", subtype: "TELEGRAM", value: "@HK_DeadDrop_Bot_03", label: "🤖 TG: 矩阵抛货号", risk: "MEDIUM", location: "Telegram API", provenance: { source: "僵尸网络扩线", time: "2026-02-02 10:15" } },
            { id: "m1", type: "material", subtype: "CHEMICAL", value: "Cocaine-50kg", label: "🧪 高纯度可卡因 50kg", risk: "CRITICAL", location: "Mexico", provenance: { source: "Tor 交易监控网", time: "2026-02-05 23:00" } },
            { id: "e1", type: "wallet", subtype: "XMR", value: "44AFFq5kSiGBo...", label: "XMR: 隐私收款池", risk: "HIGH", location: "Proxy IP", provenance: { source: "AML 链上追踪引擎", time: "2026-02-06 10:00" } }
        ],
        links: [
            { source: "u1", target: "s4", type: "command", predicate: "ACCOUNT_LOGIN", evidence_id: "N-P00", timestamp: "2026-02-01 02:00", conf: 0.99 },
            { source: "s4", target: "s_dread", type: "referral", predicate: "BIO_LINK", evidence_id: "N-P01", timestamp: "2026-02-01 05:00", conf: 0.95, evidences: [{ evidence_id: "CAP-N01", source_id: "SRC-003", method: "暗网挂链解析", conf: 0.95, capsule: { vitality_status: "LIVE", capture_time: "2026-02-01Z", snapshot: { type: "JSON", content_hash: "sha256:dread_html" } } }] },
            { source: "s_dread", target: "s1", type: "referral", predicate: "URL_REDIRECT", evidence_id: "N-P02", timestamp: "2026-02-02 10:00", conf: 0.88 },
            { source: "s1", target: "s_session", type: "referral", predicate: "URL_REDIRECT", evidence_id: "N-P03", timestamp: "2026-02-03 20:00", conf: 0.92 },
            { source: "s4", target: "s1_matrix", type: "referral", predicate: "BIO_LINK", evidence_id: "N-001c", timestamp: "2026-02-02 10:15", conf: 0.95 },
            { source: "s4", target: "m1", type: "material", predicate: "ITEM_PURCHASE", evidence_id: "N-002", timestamp: "2026-02-05 23:00", conf: 0.85, raw_content_preview: "【担保交易】发往海外，高纯度可卡因 50kg 现货，只接受 XMR 隐私币结算。请通过 PGP 加密联系我拿货。备用联络TG：@Auto_DeadDrop_Bot。", matched_terms: {"NARCOTICS": ["可卡因", "现货", "拿货"], "FINANCE": ["XMR 隐私币结算", "担保交易"]}, evidences: [{ evidence_id: "CAP-N02", source_id: "SRC-003", method: "页面镜像", conf: 0.85, capsule: { vitality_status: "DEGRADED", capture_time: "2026-02-05Z", target_url: "http://onion.../item/1", snapshot: { type: "IMAGE", content_hash: "sha256:xx", url: "/offline/evidence-snapshot.svg", ocr_text: "SILK ROAD V4\nHigh Purity Cocaine 50kg\nPrice: 100 XMR" }, llm_mock: { raw_text: "【担保交易】发往海外，高纯度可卡因 50kg 现货，只接受 XMR 隐私币结算。备用联络TG：@Auto_DeadDrop_Bot。提币地址: 44AFFq5kSiGBo... 这批货必须避开海关X光机。", intents: [{ label: "涉毒交易 (Narcotics)", score: 0.98, color: "bg-purple-500" }, { label: "黑资洗白 (Money Laundering)", score: 0.85, color: "bg-yellow-500" }], entities: [{ type: "user", value: "@Auto_DeadDrop_Bot", role: "自动联络人/机器人", highlight: "备用联络TG：@Auto_DeadDrop_Bot" }, { type: "wallet", subtype: "XMR", value: "44AFFq5kSiGBo...", role: "收款池", highlight: "提币地址: 44AFFq5kSiGBo..." }, { type: "material", value: "可卡因 50kg", role: "违禁品", highlight: "高纯度可卡因 50kg 现货" }] } } }] },
            { source: "u2", target: "s1", type: "command", predicate: "INSTRUCT", evidence_id: "N-002b", timestamp: "2026-02-06 09:00", conf: 0.8, evidences: [{ evidence_id: "CAP-N03", source_id: "SRC-006", method: "TG Bot 后台蜜罐", conf: 0.8, capsule: { vitality_status: "LIVE", capture_time: "2026-02-06Z", snapshot: { type: "JSON", content_hash: "sha256:bot_api_dump" } } }] },
            { source: "s1", target: "e1", type: "finance", predicate: "ASSET_TRANSFER", evidence_id: "N-003", timestamp: "2026-02-06 10:00", conf: 0.95, evidences: [{ evidence_id: "CAP-N04", source_id: "SRC-005", method: "交互流水记录提取", conf: 0.95, capsule: { vitality_status: "LIVE", capture_time: "2026-02-06Z", snapshot: { type: "JSON", content_hash: "sha256:payment_req" } } }] },
            { source: "u1", target: "u2", type: "command", predicate: "COORDINATE", evidence_id: "N-007", timestamp: "2026-02-09 12:00", conf: 0.75 } 
        ]
    }
};