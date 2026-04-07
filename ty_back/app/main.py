from fastapi import FastAPI
from app.routers import debug
from app.routers import debug, intel # 导入新路由

app = FastAPI()


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     print(name)
#     print(type(name))
#     return {"message": f"Hello {name}"}

# 注册路由
# app.include_router(debug.router, prefix="/api/v1")
app.include_router(intel.router, prefix="/api/v1", tags=["情报数据"])

@app.get("/")
async def root():
    return {"message": "Project is running"}
