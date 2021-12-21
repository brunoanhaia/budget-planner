

from django.db import models

from app.nubank.wrapper.src.models.card import model

class Card(models.Model):
    cpf = models.CharField(max_length=11)
    ref_month = models.DateField()
    statements: StatementList = StatementList(cpf)
    bills: BillList = BillList(cpf)
    tag_summary: TagSummaryList = TagSummaryList(cpf)
    transaction_list: TransactionBillList = TransactionBillList(cpf)
    category_summary: CategorySummaryList = CategorySummaryList(cpf) = models.CharField(max_length=30)