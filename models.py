from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DECIMAL
from sqlalchemy.sql.expression import true
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Date, Float


Base = declarative_base()

class NuBankCardBill(Base):
   
    __tablename__ = 'card_bill'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nubank_id = Column(String(255))
    cpf = Column(String(255))
    state = Column(String(255))
    due_date = Column(String(255))
    close_date = Column(String(255))
    past_balance = Column(DECIMAL(10, 4))
    effective_due_date = Column(String(255))
    total_balance = Column(DECIMAL(10, 4))
    interest_rate = Column(Float)
    interest = Column(Float)
    total_cumulative = Column(DECIMAL(10, 4))
    paid = Column(DECIMAL(10, 4))
    minimum_payment = Column(DECIMAL(10, 4))
    open_date = Column(String(255))
    link_href = Column(String(255))
    transactions = relationship("NubankCardTransaction", backref="card_bill", lazy=True)

    def from_dict(self, values: dict):
        self.id=values.get('id', None)
        self.state=values.get('state', None)
        self.nubank_id=values.get('nubank_id', None)
        self.cpf=values.get('cpf', None)
        self.due_date=values.get('due_date', None)
        self.close_date=values.get('close_date', None)
        self.past_balance=values.get('past_balance', None)
        self.effective_due_date=values.get('effective_due_date', None)
        self.total_balance=values.get('total_balance', None)
        self.interest_rate=values.get('interest_rate', None)
        self.interest=values.get('interest', None)
        self.total_cumulative=values.get('total_cumulative', None)
        self.paid=values.get('paid', None)
        self.minimum_payment=values.get('minimum_payment', None)
        self.open_date=values.get('open_date', None)
        self.link_href=values.get('link_href', None)

        # This means that it is a future card bill and we could not get the details.
        if 'transactions' in values: 
            for transaction in values['transactions']:
                self.transactions.append(NubankCardTransaction().from_dict(transaction))
        
        return self


class NubankCardTransaction(Base):
    __tablename__ = 'card_bill_transaction'

    id = Column((Integer), primary_key=True, autoincrement=True)
    card_bill_id = Column(Integer, ForeignKey('card_bill.id'))
    state=Column(String(255))
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
        self.state = values.get('state')
        self.category = values['category']
        self.amount = values['amount']
        self.transaction_id = values['transaction_id']
        self.index = values['index']
        self.charges = values['charges']
        self.type = values['type']
        self.title = values['title']
        self.nubank_id = values['nubank_id']
        self.href = values['href']
        self.post_date = values['post_date']

        return self

class NuBankMonthlyAccountSummary(Base):
    __tablename__ = 'monthly_account_summary'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ref_date = Column(Date)
    debit = Column(Float)
    credit = Column(Float)
    total = Column(Float)

    def from_dict(self, values: dict):
        self.id = values.get('id', None)
        self.credit = values.get('credit', 0)
        self.debit = values.get('debit', 0)
        self.total = values.get('total', 0)
