# # app/config/config.py
#
# class ClickHouseSettings:
#     HOST: str = "172.23.216.106"
#     PORT: int = 9000  # 注意：clickhouse-driver 使用的是 TCP 端口，默认 9000
#     USER: str = "default"
#     PASSWORD: str = "clickhouse"
#     DATABASE: str = "hawkeye"
#
# ch_settings = ClickHouseSettings()


# app/config/config.py

class ClickHouseSettings:
    HOST: str = "172.23.216.106"
    PORT: int = 8123  # 满足你，使用 HTTP 端口 8123
    USER: str = "default"
    PASSWORD: str = "clickhouse"
    DATABASE: str = "hawkeye"

ch_settings = ClickHouseSettings()

