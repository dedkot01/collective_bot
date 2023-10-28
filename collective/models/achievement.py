from typing import Any, List

from sqlalchemy import select
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped, Session
from sqlalchemy.types import BigInteger

from models import Base


class Achievement(Base):
    __tablename__ = "achievement"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    description: Mapped[str]
    award: Mapped[str]
    req_strength: Mapped[int]
    req_agility: Mapped[int]
    req_knowledge: Mapped[int]

    def __init__(
        self,
        id: int,
        description: str,
        award: str,
        req_strength: int,
        req_agility: int,
        req_knowledge: int,
        **kw: Any
    ):
        super().__init__(**kw)

        self.id = id

        self.description = description
        self.award = award

        self.req_strength = req_strength
        self.req_agility = req_agility
        self.req_knowledge = req_knowledge

    def get_all(session: Session) -> List['Achievement']:
        achievements = session.scalars(
            select(Achievement)
        ).all()

        return achievements
