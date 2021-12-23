from django.contrib import admin

from core.models.card import Card, Bill, CategorySummary, Statement, TagSummary, Transaction, Tag
from core.models.client import Client

modules = [Card, Bill, CategorySummary, Statement, TagSummary, Transaction, Tag, Client]

[admin.site.register(module) for module in modules]
