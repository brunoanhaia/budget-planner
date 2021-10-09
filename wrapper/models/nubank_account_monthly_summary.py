from .base_model import BaseModel
from datetime import date


class NuBankAccountMonthlySummary(BaseModel):

    def __init__(self, cpf='') -> None:
        BaseModel.__init__(self, cpf)
        self.id: int = None
        self.ref_date: date = date.today()
        self._debit: float = 0
        self._credit: float = 0
        self._total: float = 0
        self._balance: float = 0

    # region Properties
    @property
    def debit(self) -> float:
        return self._debit

    @debit.setter
    def debit(self, value: float):
        self._debit = self.round_to_two_decimal(value)

    @property
    def credit(self) -> float:
        return self._credit

    @credit.setter
    def credit(self, value: float):
        self._credit = self.round_to_two_decimal(value)

    @property
    def total(self) -> float:
        return self._total

    @total.setter
    def total(self, value: float):
        self._total = self.round_to_two_decimal(value)

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float):
        self._balance = self.round_to_two_decimal(value)

    # endregion

    def from_dict(self, values: list[dict]):
        self.id = values.get('id', None)
        self.cpf = values.get('cpf', None)
        self.ref_date = values.get('ref_date', 0)
        self.credit = values.get('credit', 0)
        self.debit = values.get('debit', 0)
        self.total = values.get('total', 0)
        self.balance = values.get('balance', 0)

        return self

    def sync(self, current_values_list: dict):
        # Todo: Refactor this method to update the current values in the worksheet with the new values.
        pass
