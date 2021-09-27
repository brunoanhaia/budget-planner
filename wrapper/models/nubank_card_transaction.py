from wrapper.models.base_model import BaseModel


class NuBankCardTransaction(BaseModel):
    __tablename__ = 'card_bill_transaction'

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
