import random
import datetime
import uuid
import httpx

CLICKHOUSE_HOST = "172.23.216.106"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USER = "default"
CLICKHOUSE_PASSWORD = "clickhouse"
CLICKHOUSE_DATABASE = "hawkeye"

NUM_RECORDS = 50
OUTPUT_FILE = 'test_hawkeye_data_50.sql'
INSERT_DIRECTLY = True

# 依据 1.json 提取的字典
platforms_map = {
    'Telegram': {'type': 'chat', 'sites': ['drug_deal_backup', '致幻剂交流', '海峡观察站', 'restore_support', 'edu_task_pool']},
    'Tor': {'type': 'web', 'sites': ['暗网中文论坛', '灰港货运板', 'RansomBoard', 'MirrorActionHub']},
    'Weibo': {'type': 'social', 'sites': ['公开情报镜像', '物流异常线索']},
    'I2P': {'type': 'web', 'sites': ['隐匿行动板', 'DataHub-I2P']}
}

topics = ['TopicDrugs', 'TopicSmuggle', 'TopicTerror', 'TopicRansom', 'TopicDataLeak', 'TopicTaiwan']
industries = ['Finance', 'Tech', 'Gov', 'Edu', 'Health']
regions = ['海外/匿名网络', '全国/广州', '海外/欧洲', '广东/深圳', '新疆/乌鲁木齐', '海外/东欧', '北京/海淀', '台湾/台北', '上海/浦东', '福建/厦门', '海外/中东', '浙江/杭州', '湖北/武汉']

# 依据 1.json 提取的词库与实体模板
vocab = {
    'TopicDrugs': {
        'keywords': ['冰毒', '纯白哈希', '担保交易', '肉', '埋包', '邮票', '致幻剂', '代理起拿'],
        'rule': 'Rule_Drug_Slang',
        'entity_pool': [('slang', '纯白哈希'), ('slang', '肉'), ('slang', '埋包'), ('money', 'USDT'), ('money', 'BTC Wallet')]
    },
    'TopicSmuggle': {
        'keywords': ['国际EMS', '固定线路', '港口堆场', '夜间中转', '冻品', '电子件混装', '报关单'],
        'rule': 'Rule_Smuggle_Route',
        'entity_pool': [('logistics', '国际EMS'), ('logistics', '中转车队'), ('logistics', '冷链柜'), ('loc', '深圳港'), ('identity', '仓单编号A-19')]
    },
    'TopicTerror': {
        'keywords': ['聚集', '试爆', '时间窗口', '极端行动', '倒计时', '器材说明'],
        'rule': 'Rule_Terror_Action',
        'entity_pool': [('slang', '集合点'), ('identity', '行动窗口'), ('identity', '倒计时脚本'), ('slang', '目标点位')]
    },
    'TopicRansom': {
        'keywords': ['钱包轮换', '赎金协商', '加密货币', '分账说明', '受害通告'],
        'rule': 'Rule_Crypto_Transfer',
        'entity_pool': [('money', 'BTC Wallet'), ('identity', 'decrypt key'), ('money', 'XMR Wallet')]
    },
    'TopicDataLeak': {
        'keywords': ['数据泄露', '账号包试售', '地址库', '身份证段', '高校邮箱批量验证'],
        'rule': 'Rule_Crypto_Transfer',
        'entity_pool': [('identity', '账号包'), ('identity', '身份证段'), ('identity', '高校邮箱'), ('money', 'USDT')]
    },
    'TopicTaiwan': {
        'keywords': ['匿名筹资', '导流短链', '海峡观察', '大选资金', '网军招募'],
        'rule': 'Rule_Crypto_Transfer',
        'entity_pool': [('money', 'TRX Wallet'), ('identity', '短链跳转'), ('identity', '筹款渠道')]
    }
}

authors = ['drug_dealer_001', '毒枭之王', 'ChemMaster', 'RouteBroker', 'ShadowCell', 'LockBitClone', 'LeakMirror', 'island_watch']

def generate_record(index):
    # 模拟时间：以 2024-06-10 为基准倒推
    base_time = datetime.datetime(2024, 6, 10, 12, 0, 0)
    time_offset = datetime.timedelta(minutes=random.randint(1, 10000))
    pub_time = base_time - time_offset
    event_date = pub_time.strftime('%Y-%m-%d')
    pub_time_str = pub_time.strftime('%Y-%m-%d %H:%M:%S.000')
    
    content_id = f"MSG-{pub_time.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # 抽取核心维度
    platform = random.choice(list(platforms_map.keys()))
    source_type = platforms_map[platform]['type']
    site_name = random.choice(platforms_map[platform]['sites'])
    
    topic = random.choice(topics)
    industry = random.choice(industries)
    region_full = random.choice(regions)
    region_province = region_full.split('/')[0] if '/' in region_full else region_full
    author = random.choice(authors)
    
    # 风险与评分
    severity_map = {1: 'LOW', 2: 'MEDIUM', 3: 'HIGH', 4: 'CRITICAL'}
    severity_level = random.choices([1, 2, 3, 4], weights=[20, 30, 40, 10], k=1)[0]
    severity = severity_map[severity_level]
    risk_score = round(random.uniform(severity_level * 20, severity_level * 25), 1)
    
    # 抽取词汇与实体
    vocab_data = vocab[topic]
    keys = random.sample(vocab_data['keywords'], random.randint(2, 3))
    raw_entities = random.sample(vocab_data['entity_pool'], random.randint(1, len(vocab_data['entity_pool'])))
    
    # 格式化 ClickHouse 数组
    keyword_hits_sql = f"[{', '.join([f'{repr(k)}' for k in keys])}]"
    
    # 实体标签转为 "type:value" 格式
    entity_tags = [f"{e[0]}:{e[1]}" for e in raw_entities]
    entity_tags.append(f"loc:{region_full.split('/')[-1]}") # 把地名也作为实体塞进去
    entity_tags_sql = f"[{', '.join([f'{repr(t)}' for t in entity_tags])}]"
    
    title = f"{topic}预警：发现{keys[0]}与{keys[1]}活动"
    text_preview = f"监测到引擎输出场景，内容包含“{keys[0]}”和“{keys[1]}”，涉及{industry}行业，用于验证筛选联动。"
    
    # 冷表长文本
    raw_content = f"原文转储：\n源平台：{platform} | 频道/站点：{site_name}\n发布者：{author}\n正文：我们提供优质的{keys[0]}服务。如需{keys[1]}请联系客服。交易支持{raw_entities[0][1] if raw_entities else '加密转账'}结算。坐标位于{region_full}，闲聊勿扰。\n(此文本用于 RAG 向量化与全文搜索测试)"
    normalized_text = f"{title} {text_preview} {author} {site_name} {' '.join(keys)}".lower()

    # 1. 热表 SQL
    hot_sql = f"""INSERT INTO hawkeye.hawkeye_dwd_intel_content_test (
        content_id, platform, source_type, content_kind, site_name, author_name,
        publish_time, ingest_time, update_time,
        title, text_preview, language, region, region_province, industry, topic, threat_category, severity, risk_score,
        keyword_hits, entity_tags
    ) VALUES (
        '{content_id}', '{platform}', '{source_type}', 'text', '{site_name}', '{author}',
        '{pub_time_str}', '{pub_time_str}', '{pub_time_str}',
        '{title}', '{text_preview}', 'zh', '{region_full}', '{region_province}', '{industry}', '{topic}', '{topic}', '{severity}', {risk_score},
        {keyword_hits_sql}, {entity_tags_sql}
    );"""

    # 2. 冷表 SQL
    cold_sql = f"""INSERT INTO hawkeye.hawkeye_dwd_intel_content_cold_test (
        content_id, ingest_time, update_time, raw_content, raw_content_uri
    ) VALUES (
        '{content_id}', '{pub_time_str}', '{pub_time_str}', '{raw_content}', 's3://hawkeye/raw/{event_date.replace('-','')}/{content_id}.json'
    );"""

    # 3. 极热 ADS 表 SQL
    ads_sql = f"""INSERT INTO hawkeye.hawkeye_ads_case_content_latest_test (
        content_id, event_date, publish_time, update_time,
        platform, source_type, content_kind, site_name, author_name,
        title, text_preview, language, region, region_province, industry, topic, threat_category, severity, risk_score,
        keyword_hits, entity_tags
    ) VALUES (
        '{content_id}', '{event_date}', '{pub_time_str}', '{pub_time_str}',
        '{platform}', '{source_type}', 'text', '{site_name}', '{author}',
        '{title}', '{text_preview}', 'zh', '{region_full}', '{region_province}', '{industry}', '{topic}', '{topic}', '{severity}', {risk_score},
        {keyword_hits_sql}, {entity_tags_sql}
    );"""
    
    return hot_sql, cold_sql, ads_sql


def execute_ch_insert(sql: str) -> bool:
    url = f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/"
    params = {
        "query": sql,
        "user": CLICKHOUSE_USER,
        "password": CLICKHOUSE_PASSWORD,
        "database": CLICKHOUSE_DATABASE,
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, params=params)
            if response.status_code != 200:
                print(f"Response: {response.text[:500]}")
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Insert failed: {e}")
        return False


print(f"开始生成 {NUM_RECORDS} 条高度仿真的业务测试数据...")

if INSERT_DIRECTLY:
    success_count = 0
    fail_count = 0
    for i in range(NUM_RECORDS):
        hot, cold, ads = generate_record(i)
        if execute_ch_insert(hot):
            success_count += 1
        else:
            fail_count += 1
            print(f"记录 {i+1} 热表插入失败")
        if execute_ch_insert(cold):
            success_count += 1
        else:
            fail_count += 1
            print(f"记录 {i+1} 冷表插入失败")
        if execute_ch_insert(ads):
            success_count += 1
        else:
            fail_count += 1
            print(f"记录 {i+1} ADS表插入失败")
        if (i + 1) % 10 == 0:
            print(f"已处理 {i+1}/{NUM_RECORDS} 条记录...")
    print(f"✅ 插入完毕！成功 {success_count} 条，失败 {fail_count} 条")
else:
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("-- =========================================================\n")
        f.write(f"-- Hawkeye 融合 RAG 链路测试数据 (按照 1.json 字典生成，共 {NUM_RECORDS} 条)\n")
        f.write("-- 包含表: dwd_intel_content, dwd_intel_content_cold, ads_case_content_latest\n")
        f.write("-- =========================================================\n\n")
        
        for i in range(NUM_RECORDS):
            hot, cold, ads = generate_record(i)
            f.write(f"-- ----------------- 测试记录 {i+1} -----------------\n")
            f.write(hot + "\n")
            f.write(cold + "\n")
            f.write(ads + "\n\n")

    print(f"✅ 生成完毕！文件已保存为: {OUTPUT_FILE}")