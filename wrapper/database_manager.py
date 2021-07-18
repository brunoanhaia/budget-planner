from wrapper.models.nubank_monthly_account_summary import NuBankAccountMonthlySummary
from .models import DeclarativeBase, DatabaseProvider, NuBankCardBill


class DatabaseManager:
    @staticmethod
    def sync(data: dict):
        
        class_map = {
            'card_bills': NuBankCardBill(),
            'account_monthly_summary': NuBankAccountMonthlySummary()
        }

        for key in data:
            if key in class_map:
                class_map[key].sync(data[key])

    @staticmethod
    def reset():
        DeclarativeBase.metadata.drop_all(DatabaseProvider.instance().engine)
        DeclarativeBase.metadata.create_all(DatabaseProvider.instance().engine)
