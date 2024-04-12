from typing import Annotated

from fastapi import Depends

from src.api.stub import Stub
from src.business_logic.comment.dto import CommentUpdate
from src.business_logic.comment.exceptions import CommentNotExist, NotOwnerOfComment
from src.business_logic.room.exceptions import RoomNotExist
from src.db import User, Comment
from src.db.dao.comment_dao import CommentDAO
from src.db.dao.room_dao import RoomDAO
from src.db.dao.user_dao import UserDAO


class CommentBusinessLogicService:
    def __init__(self, dao_comment: CommentDAO, dao_room: RoomDAO, dao_user: UserDAO):
        self._dao_comment = dao_comment
        self._dao_room = dao_room
        self._dao_user = dao_user

    async def create_comment(self, content: str, room_id: int, user_token: str) -> Comment:
        user = await self._dao_user.get_user_by_token(user_token)

        if self._dao_room.get_room_by_id(room_id) is None:
            raise RoomNotExist()

        comment = await self._dao_comment.create_comment(content, room_id, user)

        return comment

    async def get_comments(self, room_id: int, skip: int, limit: int) -> list[Comment]:

        if self._dao_room.get_room_by_id(room_id) is None:
            raise RoomNotExist()

        comments = await self._dao_comment.get_comments(room_id, skip, limit)
        return comments

    async def update_comment(self, comment_id: int, comment_data: CommentUpdate, user: User):

        if await self._dao_comment.get_comment_by_id(comment_id) is None:
            raise CommentNotExist()

        if await self._dao_comment.get_user_id_by_comment_id(comment_id) != user.id:
            raise NotOwnerOfComment()

        comment = await self._dao_comment.update_comment_by_id(comment_id, comment_data, user)
        return comment

    async def delete_comment(self, comment_id: int, user: User):

        if await self._dao_comment.get_comment_by_id(comment_id) is None:
            raise CommentNotExist()

        if await self._dao_comment.get_user_id_by_comment_id(comment_id) != user.id:
            raise NotOwnerOfComment()

        await self._dao_comment.delete_comment_by_id(comment_id, user)


CommentLogicService = Annotated[CommentBusinessLogicService, Depends(Stub(CommentBusinessLogicService))]
