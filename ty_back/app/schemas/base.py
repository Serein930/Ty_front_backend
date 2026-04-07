from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel

# 定义泛型变量 T
T = TypeVar("T")

class Result(BaseModel, Generic[T]):
    """
    统一响应结果类，模仿 Java Result<T>
    """
    code: int           # 状态码 (如 200 为成功)
    msg: str            # 提示信息
    data: Optional[T] = None  # 数据载体

    @classmethod
    def success(cls, data: Any = None, msg: str = "success"):
        """成功返回的快捷方法"""
        return cls(code=200, msg=msg, data=data)

    @classmethod
    def error(cls, code: int = 500, msg: str = "error"):
        """失败返回的快捷方法"""
        return cls(code=code, msg=msg, data=None)