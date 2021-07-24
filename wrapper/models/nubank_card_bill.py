from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Float, Integer, String, DECIMAL
from sqlalchemy import Column
from sqlalchemy.sql.schema import ForeignKey

from .declarative_base import DeclarativeBase
from .nubank_card_transaction import NuBankCardTransaction
from .base_model import BaseModel


class NuBankCardBill(DeclarativeBase, BaseModel):
    __tablename__ = 'card_bill'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nubank_id = Column(String(255))
    cpf = Column(String(255), ForeignKey('user.id'))
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
    transactions = relationship(
        "NuBankCardTransaction", backref="card_bill", lazy=True)

    def __init__(self) -> None:
        BaseModel.__init__(self)

    def from_dict(self, values: dict):
        self.id = values.get('id', None)
        self.state = values.get('state', None)
        self.nubank_id = values.get('nubank_id', None)
        self.cpf = values.get('cpf', None)
        self.due_date = values.get('due_date', None)
        self.close_date = values.get('close_date', None)
        self.past_balance = values.get('past_balance', None)
        self.effective_due_date = values.get('effective_due_date', None)
        self.total_balance = values.get('total_balance', None)
        self.interest_rate = values.get('interest_rate', None)
        self.interest = values.get('interest', None)
        self.total_cumulative = values.get('total_cumulative', None)
        self.paid = values.get('paid', None)
        self.minimum_payment = values.get('minimum_payment', None)
        self.open_date = values.get('open_date', None)
        self.link_href = values.get('link_href', None)

        # This means that it is a future card bill and we could not get the details.
        if 'transactions' in values:
            for transaction in values['transactions']:
                self.transactions.append(
                    NuBankCardTransaction().from_dict(transaction))

        return self

    def sync(self, values: list[dict]):
        session = self.db_helper.session
        base_bills = session.query(NuBankCardBill).all()

        for current_value in values:

            # This get the transaction if exists
            query_result = [x for x in base_bills if x.close_date ==
                            current_value['close_date'] and x.cpf == current_value['cpf']]
            current_bill = NuBankCardBill().from_dict(current_value)

            if len(query_result) > 0:

                base_bill: NuBankCardBill = query_result[0]

                self.update_all_attributes(
                    NuBankCardBill, base_bill, current_bill)
                session.add(base_bill)

                if 'transactions' in current_value:
                    self.__sync_card_transactions(
                        current_value['transactions'], base_bill.id)

                print(f'{base_bill.close_date} has been updated')

            else:
                session.add(current_bill)
                print(f'{current_bill.nubank_id} has been added')

        session.commit()

    def __sync_card_transactions(self, current_transactions: list[dict], bill_id: int):
        session = self.db_helper.session
        base_transactions = session.query(NuBankCardTransaction).where(
            NuBankCardTransaction.card_bill_id == bill_id).all()

        # Here we could check the if the base transactions exists in the current transactions, otherwise the transaction
        # should be deleted.
        for base_transaction in base_transactions:
            query_result = [
                x for x in current_transactions if x['nubank_id'] == base_transaction.nubank_id]
            if len(query_result) == 0:
                session.delete(base_transaction)

        for transaction in current_transactions:
            query_result = [
                x for x in base_transactions if x.nubank_id == transaction['nubank_id']]

            current_transaction = NuBankCardTransaction().from_dict(transaction)

            # If the transaction does not exist
            if len(query_result) == 0:
                current_transaction.card_bill_id = bill_id

                session.add(current_transaction)

            # If the transaction exist and should be updated
            else:
                self.update_all_attributes(NuBankCardTransaction, query_result[0], current_transaction, [
                    'nubank_id', 'card_bill_id'])
                session.add(query_result[0])
