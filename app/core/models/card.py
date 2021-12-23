from django.db import models
from core.models.client import Client

class Card(models.Model):
    client=models.ForeignKey(Client, on_delete=models.CASCADE, related_name='cards')
    sponsor = 'nubank'

class Statement(models.Model):
    card = models.ForeignKey('Card', on_delete=models.CASCADE, related_name='statements')

class Bill(models.Model):
    card = models.ForeignKey('Card', on_delete=models.CASCADE, related_name='bills')
    bill_id=models.CharField(max_length=255)
    state=models.CharField(max_length=255)
    due_date=models.DateField
    effective_due_date=models.CharField(max_length=255)
    open_date=models.DateField
    link_href=models.CharField(max_length=255)
    ref_date=models.DateField
    close_date=models.DateField
    past_balance=models.DecimalField(max_digits=10, decimal_places=2)
    total_balance=models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate=models.DecimalField(max_digits=4, decimal_places=2)
    interest=models.DecimalField(max_digits=4, decimal_places=2)
    total_cumulative=models.DecimalField(max_digits=10, decimal_places=2)
    paid=models.DecimalField(max_digits=10, decimal_places=2)
    minimum_payment=models.DecimalField(max_digits=10, decimal_places=2)

class Tag(models.Model):
    name=models.CharField(max_length=50)

class Transaction(models.Model):
    bill = models.ForeignKey('Bill', on_delete=models.CASCADE, related_name='transactions')
    state=models.CharField(max_length=255)
    category=models.CharField(max_length=255)
    transaction_id=models.CharField(max_length=255)
    index=models.IntegerField()
    charges=models.IntegerField()
    type=models.CharField(max_length=255)
    title=models.CharField(max_length=255)
    nubank_id=models.CharField(max_length=255)
    href=models.CharField(max_length=255)
    post_date=models.DateField()
    tags=models.ManyToManyField(Tag)
    amount=models.DecimalField(max_digits=10, decimal_places=2)

class TagSummary(models.Model):
    bill=models.ForeignKey('Bill', on_delete=models.CASCADE, related_name='tagSummary')
    value=models.DecimalField(max_digits=10, decimal_places=2)
    tag=models.ForeignKey(Tag, on_delete=models.CASCADE)


class CategorySummary(models.Model):
    bill = models.ForeignKey('Bill', on_delete=models.CASCADE, related_name='categorySummary')
    value=models.DecimalField(max_digits=10, decimal_places=2)
    tag=models.CharField(max_length=255)
