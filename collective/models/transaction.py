from typing import Any, Optional, Union
import uuid

from sqlalchemy import String
from sqlalchemy import select
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped, Session

from models import Base


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[str] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(15))
    amount: Mapped[int]
    author: Mapped[str] = mapped_column(String(255))
    user: Mapped[Optional[str]] = mapped_column(String(255))

    def __init__(self, action: str, amount: int, author: str, **kw: Any):
        super().__init__(**kw)

        self.id = uuid.uuid1()

        self.action = action
        self.amount = amount
        self.author = author

    def get(id: int, session: Session) -> Union['Transaction', None]:
        transaction = session.scalars(
            select(Transaction).where(Transaction.id == id)
        ).one_or_none()

        return transaction
