from datetime import date
from .base_model import BaseModel

class CardBillAmountPerTag(BaseModel):

    cpf: str
    ref_date: str
    close_date: date
    values: dict

    def __init__(self) -> None:
        BaseModel.__init__(self)