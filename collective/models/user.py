from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped, Session
from sqlalchemy.types import BigInteger

from models import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    is_admin: Mapped[bool]

    strength: Mapped[int]
    agility: Mapped[int]
    knowledge: Mapped[int]

    def __init__(
        self,
        id: int,
        is_admin: bool = False,
        strength: int = 0,
        agility: int = 0,
        knowledge: int = 0,
        **kw: Any
    ):
        super().__init__(**kw)

        self.id = id
        self.is_admin = is_admin

        self.strength = strength
        self.agility = agility
        self.knowledge = knowledge

    def get_or_reg(id: int, session: Session) -> 'User':
        user = session.scalars(
            select(User).where(User.id == id)
        ).one_or_none()

        if user is None:
            user = User(id)
            session.add(user)

        return user
