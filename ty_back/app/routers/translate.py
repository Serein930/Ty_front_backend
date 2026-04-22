from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.translate import TranslateRequest
from app.schemas.base import Result
from app.services.translation import translation_service

router = APIRouter(prefix="/api/topics", tags=["告警翻译"])


@router.post("/translate", response_model=Result[str])
def translate(payload: TranslateRequest):
    """
    翻译告警内容
    - title: 标题
    - content: 正文内容
    - target_lang: 目标语言（默认简体中文）
    """
    try:
        result = translation_service.translate(
            title=payload.title,
            content=payload.content,
            target_lang=payload.target_lang or "简体中文"
        )
        return Result.success(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")


@router.post("/translate/stream")
def translate_stream(payload: TranslateRequest):
    """
    流式翻译告警内容
    - title: 标题
    - content: 正文内容
    - target_lang: 目标语言（默认简体中文）
    """
    try:
        return StreamingResponse(
            translation_service.translate_stream(
                title=payload.title,
                content=payload.content,
                target_lang=payload.target_lang or "简体中文"
            ),
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")