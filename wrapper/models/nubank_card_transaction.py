from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer, String, DECIMAL
from sqlalchemy import Column
from sqlalchemy.sql.schema import ForeignKey

from .declarative_base import DeclarativeBase



class NuBankCardTransaction(DeclarativeBase):
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

    def from_dict(self, values: dict):
        self.id = values.get('id', None)
        self.card_bill_id = values.get('card_bill_id', None)
        self.state = values.get('state', None)
        self.category = values.get('category', None)
        self.amount = values.get('amount', None)
        self.transaction_id = values.get('transaction_id', None)
        self.index = values.get('index', None)
        self.charges = values.get('charges', None)
        self.type = values.get('type', None)
        self.title = values.get('title', None)
        self.nubank_id = values.get('nubank_id', None)
        self.href = values.get('href', None)
        self.post_date = values.get('post_date', None)

        return self