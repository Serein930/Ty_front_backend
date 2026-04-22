from pymilvus import connections

try:
    connections.connect(host="172.23.216.104", port="19530", alias="default")
    print("✅ 连接成功！")
    connections.disconnect("default")
except Exception as e:
    print(f"❌ 连接失败: {e}")