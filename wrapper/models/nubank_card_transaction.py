from datetime import date
from wrapper.models.base_model import BaseModel


class NuBankCardTransaction(BaseModel):

    id: int
    card_bill_id: int
    state: str
    category: str
    amount: float
    transaction_id: str
    index: int
    charges: int
    type: str
    title: str
    nubank_id: str
    href: str
    post_date: str
    tags: dict[str, float]


class NuBankCardBillTransactions(BaseModel):
    ref_date: str
    close_date: date
    cpf: str
    transactions: list[NuBankCardTransaction]
