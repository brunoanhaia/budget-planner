from sqlalchemy import Integer, Column, Date, DECIMAL

from .declarative_base import DeclarativeBase


class NuBankMonthlyAccountSummary(DeclarativeBase):
    __tablename__ = 'monthly_account_summary'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ref_date = Column(Date)
    debit = (DECIMAL(10, 4))
    credit = (DECIMAL(10, 4))
    total = (DECIMAL(10, 4))
    balance = (DECIMAL(10, 4))

    def from_dict(self, values: dict):
        self.id = values.get('id', None)
        self.ref_date = values.get('post_date', 0)
        self.credit = values.get('credit', 0)
        self.debit = values.get('debit', 0)
        self.total = values.get('total', 0)
        self.balance = values.get('balance', 0)
