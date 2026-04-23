"""
MinIO Image Handler 模块
======================

该模块提供 MinIO 对象存储的图片处理功能。

主要功能：
- 连接 MinIO 服务器
- 获取/上传图片对象
- 图片 URL 生成

使用场景：
- RAG 搜索结果中的图片展示
- 情报数据的附件图片管理

依赖：
- minio>=7.0.0
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MinioImageHandler:
    """
    MinIO 图片处理器

    用于从 MinIO 存储中获取图片或生成预签名 URL

    Attributes:
        endpoint: MinIO 服务器地址
        access_key: 访问密钥
        secret_key: 秘密密钥
        bucket: 存储桶名称
        secure: 是否使用 HTTPS
    """

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool = False
    ):
        """
        初始化 MinIO 客户端

        Args:
            endpoint: MinIO 服务器地址 (如 "localhost:9000")
            access_key: 访问密钥
            secret_key: 秘密密钥
            bucket: 存储桶名称
            secure: 是否使用 HTTPS 连接
        """
        self.endpoint = endpoint
        self.bucket = bucket
        self.secure = secure

        try:
            from minio import Minio

            self.client = Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )
            logger.info(f"MinIO 客户端初始化成功: {endpoint}/{bucket}")
        except ImportError:
            logger.warning("minio 库未安装，MinIO 功能不可用")
            self.client = None
        except Exception as e:
            logger.error(f"MinIO 客户端初始化失败: {e}")
            self.client = None

    def get_image(self, object_name: str) -> Optional[bytes]:
        """
        获取图片二进制数据

        Args:
            object_name: 对象名称（存储路径）

        Returns:
            图片二进制数据，失败返回 None
        """
        if not self.client:
            logger.warning("MinIO 客户端不可用")
            return None

        try:
            response = self.client.get_object(self.bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except Exception as e:
            logger.error(f"获取图片失败 {object_name}: {e}")
            return None

    def get_presigned_url(
        self,
        object_name: str,
        expires: int = 3600
    ) -> Optional[str]:
        """
        生成预签名 URL

        Args:
            object_name: 对象名称
            expires: 过期时间（秒）

        Returns:
            预签名 URL 字符串
        """
        if not self.client:
            logger.warning("MinIO 客户端不可用")
            return None

        try:
            url = self.client.presigned_get_object(
                self.bucket,
                object_name,
                expires=expires
            )
            return url
        except Exception as e:
            logger.error(f"生成预签名 URL 失败 {object_name}: {e}")
            return None

    def upload_image(
        self,
        object_name: str,
        data: bytes,
        content_type: str = "image/jpeg"
    ) -> bool:
        """
        上传图片

        Args:
            object_name: 对象名称
            data: 图片二进制数据
            content_type: MIME 类型

        Returns:
            成功返回 True
        """
        if not self.client:
            logger.warning("MinIO 客户端不可用")
            return False

        try:
            from io import BytesIO
            self.client.put_object(
                self.bucket,
                object_name,
                BytesIO(data),
                length=len(data),
                content_type=content_type
            )
            logger.info(f"图片上传成功: {object_name}")
            return True
        except Exception as e:
            logger.error(f"图片上传失败 {object_name}: {e}")
            return False

    def list_images(self, prefix: str = "") -> list:
        """
        列出图片对象

        Args:
            prefix: 对象名前缀过滤

        Returns:
            对象名称列表
        """
        if not self.client:
            return []

        try:
            objects = self.client.list_objects(
                self.bucket,
                prefix=prefix,
                recursive=True
            )
            return [obj.object_name for obj in objects]
        except Exception as e:
            logger.error(f"列出图片失败: {e}")
            return []

    def delete_image(self, object_name: str) -> bool:
        """
        删除图片

        Args:
            object_name: 对象名称

        Returns:
            成功返回 True
        """
        if not self.client:
            return False

        try:
            self.client.remove_object(self.bucket, object_name)
            logger.info(f"图片删除成功: {object_name}")
            return True
        except Exception as e:
            logger.error(f"图片删除失败 {object_name}: {e}")
            return False
