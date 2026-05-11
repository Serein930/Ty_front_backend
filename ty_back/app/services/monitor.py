from typing import Dict, Any, List
from app.crud.monitor import (
    upsert_follow_state,
    get_following_authors,
    batch_get_follow_status,
    get_author_feed,
    get_author_activity_stat,
)
from app.schemas.monitor import FollowAuthorReq, AuthorIdentifier, AuthorActivityStatResp


class AuthorFollowService:

    @staticmethod
    async def follow_author(
        tenant_id: str,
        user_id: str,
        req: FollowAuthorReq,
    ) -> Dict[str, Any]:
        """
        关注作者。
        """
        await upsert_follow_state(
            client=None,
            tenant_id=tenant_id,
            user_id=user_id,
            req=req,
            is_followed=1,
        )
        return {"target_id": req.target_id}

    @staticmethod
    async def unfollow_author(
        tenant_id: str,
        user_id: str,
        req: FollowAuthorReq,
    ) -> Dict[str, Any]:
        """
        取消关注作者。
        """
        await upsert_follow_state(
            client=None,
            tenant_id=tenant_id,
            user_id=user_id,
            req=req,
            is_followed=0,
        )
        return {"target_id": req.target_id}

    @staticmethod
    async def get_follow_status_batch(
        tenant_id: str,
        user_id: str,
        authors: List[AuthorIdentifier],
    ) -> Dict[str, bool]:
        """
        批量查询作者关注状态。
        """
        target_ids = [author.target_id for author in authors]
        return await batch_get_follow_status(
            client=None,
            tenant_id=tenant_id,
            user_id=user_id,
            target_ids=target_ids,
        )

    @staticmethod
    async def list_following_authors(
        tenant_id: str,
        user_id: str,
        page: int,
        page_size: int,
    ) -> Dict[str, Any]:
        """
        分页获取当前用户已关注的作者列表。
        """
        limit = page_size
        offset = (page - 1) * page_size
        result = await get_following_authors(
            client=None,
            tenant_id=tenant_id,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        rows = result.get("data", [])
        total = len(rows)
        return {
            "list": rows,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_author_activity(
        profile_id: str,
    ) -> AuthorActivityStatResp:
        """
        统计指定作者的活跃时段分布。
        返回 7x24 二维数组（grid[day_index][hour]），
        day_index: 0=周一, 1=周二, ..., 6=周日。
        """
        result = await get_author_activity_stat(client=None, profile_id=profile_id)
        rows = result.get("data", [])

        grid: List[List[int]] = [[0] * 24 for _ in range(7)]
        total_posts = 0

        for row in rows:
            day_index = int(row.get("day_index", 0))
            hour = int(row.get("hour", 0))
            cnt = int(row.get("cnt", 0))

            if 0 <= day_index < 7 and 0 <= hour < 24:
                grid[day_index][hour] = cnt
                total_posts += cnt

        return AuthorActivityStatResp(
            profile_id=profile_id,
            grid=grid,
            total_posts=total_posts,
        )

    @staticmethod
    async def get_author_feed_list(
        tenant_id: str,
        user_id: str,
        page: int,
        page_size: int,
    ) -> Dict[str, Any]:
        """
        分页获取被关注作者的最新动态（Feed 流）。
        """
        limit = page_size
        offset = (page - 1) * page_size
        result = await get_author_feed(
            client=None,
            tenant_id=tenant_id,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        rows = result.get("data", [])
        total = len(rows)
        return {
            "list": rows,
            "total": total,
            "page": page,
            "page_size": page_size,
        }


author_follow_service = AuthorFollowService()
