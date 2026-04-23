from fastapi import FastAPI

from app.routers import intel, search, topics
from app.milvus.router import router as milvus_router

app = FastAPI()

app.include_router(search.router, tags=["全局检索"])
app.include_router(topics.router, tags=["专题管理"])
app.include_router(translate.router, tags=["翻译"])
app.include_router(milvus_router, prefix="/api/milvus", tags=["Milvus同步"])
app.include_router(rag_search_router, tags=["RAG 搜索"])

@app.get("/")
async def root():
    return {"message": "Project is running"}
