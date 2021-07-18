from .base_model import BaseModel
from sqlalchemy import Integer, Column, Date, DECIMAL, String

from .declarative_base import DeclarativeBase


class NuBankAccountMonthlySummary(DeclarativeBase, BaseModel):
    __tablename__ = 'account_monthly_summary'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cpf = Column(String(255))
    ref_date = Column(Date)
    debit = Column(DECIMAL(10, 2))
    credit = Column(DECIMAL(10, 2))
    total = Column(DECIMAL(10, 2))
    balance = Column(DECIMAL(10, 2))

    def __init__(self) -> None:
        BaseModel.__init__(self)

    def from_dict(self, values: list[dict]):
        self.id = values.get('id', None)
        self.ref_date = values.get('post_date', 0)
        self.credit = values.get('credit', 0)
        self.debit = values.get('debit', 0)
        self.total = values.get('total', 0)
        self.balance = values.get('balance', 0)

        return self

    def sync(self, current_values_list: dict):
        session = self.db_helper.session
        base_values = session.query(NuBankAccountMonthlySummary).all()

        for current_value_dict in current_values_list:

            # This get the value if exists
            query_result = [x for x in base_values if x.ref_date ==
                            current_value_dict['ref_date'] and x.cpf == current_value_dict['cpf']]
            current_value = NuBankAccountMonthlySummary().from_dict(current_value_dict)

            if len(query_result) > 0:

                base_value: NuBankAccountMonthlySummary = query_result[0]

                self.update_all_attributes(
                    NuBankAccountMonthlySummary, base_value, current_value)
                session.add(base_value)

                print(f'{base_value.ref_date} has been updated')

            else:
                session.add(current_value)
                print(f'{current_value.ref_date} has been added')

        session.commit()