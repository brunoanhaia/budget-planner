from .nubank_card_transaction import NuBankCardTransaction
from .base_model import BaseModel


class NuBankCardBill(BaseModel):
    id: int
    nubank_id: str
    cpf: str
    state: str
    due_date: str
    close_date: str
    past_balance: float
    effective_due_date: str
    total_balance: float
    interest_rate: float
    interest: float
    total_cumulative: float
    paid: float
    minimum_payment: float
    open_date: str
    link_href: str

    def __init__(self) -> None:
        BaseModel.__init__(self)

    def from_dict(self, values: dict):
        BaseModel.from_dict(self, values)

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

                if 'details' in current_value:
                    self.__sync_card_transactions(
                        current_value['details'], base_bill.id)

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
