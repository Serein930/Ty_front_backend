from fastapi import FastAPI

from app.routers import intel, search

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

app.include_router(intel.router, prefix="/api/v1", tags=["情报数据"])
app.include_router(search.router, tags=["全局检索"])

@app.get("/")
async def root():
    return {"message": "Project is running"}
