from ..base_model import BaseList, BaseModel


class StatementList(BaseList):
    __sheet_name__ = 'card_statements'

    def __init__(self, cpf):
        super().__init__(cpf)
        self.__list: list[Statement] = []

    def save_file(self):
        file_path = self.file_helper.card_statements.path
        self.file_helper.save_to_file(file_path, self.__list)

    def get_data(self):
        if len(self.__list) > 0:
            return self.__list

        card_statements = self.nu.get_card_statements()

        for statement in card_statements:
            statement['cpf'] = self.cpf

            if 'amount' in statement:
                statement['amount'] = statement['amount']/100

            if 'amount_without_iof' in statement:
                statement['amount_without_iof'] = \
                    statement['amount_without_iof']/100

            if 'details' in statement:
                for key in statement['details'].keys():
                    statement[key] = statement['details'][key]

                    if type(statement[key]) is dict and key == 'charges':
                        statement[key]['charge_amount'] = \
                            statement[key]['amount']/100
                        statement[key]['total_amount'] = \
                            statement['amount']/100

                        statement[key].pop('amount')

                statement.pop('details')

        # Storing the data in the class instance for future use
        self.__list = card_statements

        return card_statements

    def get_list(self):
        return self.__list

    def __getitem__(self, index):
        return self.__list[index]

    def __len__(self):
        return len(self.__list)


class Statement(BaseModel):
    pass
