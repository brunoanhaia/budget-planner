from .models import DeclarativeBase, DatabaseProvider, NuBankCardBill


class DatabaseManager:
    @staticmethod
    def sync(data: dict):
        pass
        class_map = {
            'card_bills': NuBankCardBill(),
            # 'account_statement_summary': Account.MonthlySummary(cls.instance())
        }

        for key in data:
            if key in class_map:
                class_map[key].sync(data[key])

    @staticmethod
    def reset():
        DeclarativeBase.metadata.drop_all(DatabaseProvider.instance())
        DeclarativeBase.metadata.create_all(DatabaseProvider.instance())
