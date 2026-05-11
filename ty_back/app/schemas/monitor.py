from typing import Optional, List
from pydantic import BaseModel, Field


class AuthorIdentifier(BaseModel):
    """
    作者标识符，用于批量查询时的内部实体定义。
    """
    profile_id: Optional[str] = ""
    platform: str
    source_handle_norm: str

    @property
    def target_id(self) -> str:
        """
        生成作者唯一标识（target_id）。
        规则：
        - 如果 profile_id 有值且不为空，则 target_id = profile_id
        - 否则退化为使用账号标识：target_id = f"{platform}:{source_handle_norm}"
        """
        if self.profile_id and self.profile_id.strip():
            return self.profile_id
        return f"{self.platform}:{self.source_handle_norm}"


class FollowAuthorReq(BaseModel):
    """
    关注/取消关注作者的请求参数。
    """
    profile_id: Optional[str] = ""
    platform: str
    source_handle_norm: str
    author_name: Optional[str] = ""
    avatar_url: Optional[str] = ""

    @property
    def target_id(self) -> str:
        """
        生成作者唯一标识（target_id）。
        规则：
        - 如果 profile_id 有值且不为空，则 target_id = profile_id
        - 否则退化为使用账号标识：target_id = f"{platform}:{source_handle_norm}"
        """
        if self.profile_id and self.profile_id.strip():
            return self.profile_id
        return f"{self.platform}:{self.source_handle_norm}"


class FollowStatusBatchReq(BaseModel):
    """
    批量查询作者关注状态的请求参数。
    """
    authors: List[AuthorIdentifier]


class FeedCursorReq(BaseModel):
    """
    动态拉取请求，用于游标分页。
    """
    page_size: int = 50
    cursor_time: Optional[str] = None
    cursor_id: Optional[str] = None


class AuthorActivityStatResp(BaseModel):
    """
    作者活跃时段统计响应。
    横轴为小时 (0-23)，纵轴为星期 (周一-周日)。
    grid[day_index][hour] = 该小时发布的帖子数量。
    day_index: 0=周一, 1=周二, ..., 6=周日
    """
    profile_id: str
    grid: List[List[int]] = Field(
        description="7x24 二维数组，grid[day_index][hour] = 帖子数量，day_index 0=周一 6=周日"
    )
    total_posts: int = Field(description="该画像发布的总帖子数")
