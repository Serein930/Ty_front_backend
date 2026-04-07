# # app/routers/debug.py
# from fastapi import APIRouter
# from app.utils.ch_client import ch_client
#
# router = APIRouter()
#
# @router.get("/ch/test")
# async def test_clickhouse_connection():
#     try:
#         # 执行一个简单的 SQL 检查版本
#         result = ch_client.execute('SELECT version()')
#         return {
#             "status": "connected",
#             "version": result[0][0]
#         }
#     except Exception as e:
#         return {
#             "status": "failed",
#             "error": str(e)
#         }


# app/routers/debug.py
from fastapi import APIRouter
from app.utils.ch_client import execute_ch_query

router = APIRouter()


@router.get("/ch/test")
async def test_clickhouse_connection():
    try:
        # 执行测试 SQL
        result = await execute_ch_query('SELECT version() AS v')

        # ClickHouse 返回的 JSON 结构中，数据在 'data' 列表里
        db_version = result['data'][0]['v']

        return {
            "status": "success",
            "message": "ClickHouse (HTTP 8123) 连接成功啦！",
            "data": {
                "version": db_version,
                "host": "172.23.216.106"
            }
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": "ClickHouse 8123 连接失败",
            "error_detail": str(e)
        }

