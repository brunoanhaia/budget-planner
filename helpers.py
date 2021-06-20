import json
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.sqltypes import Integer, String
from models import NuBankCardBill, NubankCardTransaction


class Helper:

    @staticmethod
    def update_all_attributes(base_class, base, current, skip_fields=[]):
        attr_list = base_class.__table__.columns.keys()
        for k in attr_list:
            if k != 'id' and k not in skip_fields:
                attribute_value = getattr(current, k)
                if getattr(base, k) != attribute_value:
                    setattr(base, k, attribute_value)

    @staticmethod
    def sync_card_transactions(session, current_transactions: list[dict], bill_id: Integer):
        base_transactions = session.query(NubankCardTransaction).where(
            NubankCardTransaction.card_bill_id == bill_id).all()

        # Here we could check the if the base transactions exists in the current transations, otherwise the transaction
        # should be deleted.
        for base_transaction in base_transactions:
            query_result = [
                x for x in current_transactions if x['nubank_id'] == base_transaction.nubank_id]
            if len(query_result) == 0:
                session.delete(base_transaction)

        for transaction in current_transactions:
            query_result = [
                x for x in base_transactions if x.nubank_id == transaction['nubank_id']]

            current_transaction = NubankCardTransaction().from_dict(transaction)

            # If the transaction does not exist
            if len(query_result) == 0:
                current_transaction.card_bill_id = bill_id

                session.add(current_transaction)

            # If the transaction exist and should be updated
            else:
                Helper.update_all_attributes(NubankCardTransaction, query_result[0], current_transaction, [
                                             'nubank_id', 'card_bill_id'])
                session.add(query_result[0])

    @staticmethod
    def update_database_card_bills(session: sessionmaker, values: list[dict]) -> BooleanClauseList:
        base_bills = session.query(NuBankCardBill).all()

        for current_value in values:

            # This get the transaction if exists
            query_result = [x for x in base_bills if x.close_date ==
                            current_value['close_date'] and x.cpf == current_value['cpf']]
            current_bill = NuBankCardBill().from_dict(current_value)

            if len(query_result) > 0:

                base_bill: NuBankCardBill = query_result[0]

                Helper.update_all_attributes(
                    NuBankCardBill, base_bill, current_bill)
                session.add(base_bill)

                if 'transactions' in current_value:
                    Helper.sync_card_transactions(
                        session, current_value['transactions'], base_bill.id)

                print(f'{base_bill.close_date} has been updated')

            else:
                session.add(current_bill)
                print(f'{current_bill.nubank_id} has been added')

        session.commit()

    @staticmethod
    def load_json_config(path: String):
        with open(path) as f:
            config = json.load(f)
            return config

    @staticmethod
    def save_json_config(path: String, json_content: dict):
        with open(path, 'w+', encoding='utf-8') as outfile:
            json.dump(json_content, outfile, ensure_ascii=False, indent='\t')
