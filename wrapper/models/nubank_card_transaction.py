from wrapper.models.base_model import BaseModel
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer, String, DECIMAL
from sqlalchemy import Column
from sqlalchemy.sql.schema import ForeignKey

from .declarative_base import DeclarativeBase



class NuBankCardTransaction(DeclarativeBase, BaseModel):
    __tablename__ = 'card_bill_transaction'

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_bill_id = Column(Integer, ForeignKey('card_bill.id'))
    state = Column(String(255))
    category = Column(String(255))
    amount = Column(DECIMAL(10, 4))
    transaction_id = Column(String(255))
    index = Column(Integer, default=0)
    charges = Column(Integer, default=0)
    type = Column(String(255))
    title = Column(String(255))
    nubank_id = Column(String(255))
    href = Column(String(255))
    post_date = Column(String(255))
