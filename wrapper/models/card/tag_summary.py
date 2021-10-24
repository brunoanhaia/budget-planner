from __future__ import annotations

from datetime import date

from ..base_model import BaseModel


class CardBillAmountPerTag(BaseModel):

    cpf: str
    ref_date: str
    close_date: date
    values: dict

    def __init__(self, cpf='') -> None:
        BaseModel.__init__(self, cpf)

        self.ref_date: str = ''
        self.close_date: date = date.today()
        self.values: dict = {}
