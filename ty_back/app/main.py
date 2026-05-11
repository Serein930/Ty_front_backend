import logging
import sys
from fastapi import FastAPI

from app.routers import search, topics, translate, rag_search, sa, monitor
from app.milvus.router import router as milvus_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(search.router, tags=["全局检索"])
app.include_router(topics.router, tags=["专题管理"])
app.include_router(translate.router, tags=["翻译"])
app.include_router(milvus_router, prefix="/api/milvus", tags=["Milvus同步"])
app.include_router(rag_search.router, tags=["RAG 搜索"])
app.include_router(sa.router, tags=["态势感知"])
app.include_router(monitor.router, tags=["关注管理"])

@app.get("/")
async def root():
    return {"message": "Project is running"}
