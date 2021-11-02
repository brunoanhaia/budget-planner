from ..base_model import BaseList, BaseModel


class StatementList(BaseList):

    def __init__(self, cpf):
        super().__init__(cpf)
        self.__list: list[Statement] = []

    def save_file(self):
        pass

    def get_data(self):
        card_statements = self.nu.get_card_statements()

        for statement in card_statements:
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
        self.cache_data.data.card.statements = card_statements
        file_path = self.file_helper.card_statements.path
        self.file_helper.save_to_file(file_path, card_statements)

        return card_statements

    def get_list(self):
        return self.__list

    def __getitem__(self, index):
        return self.__list[index]

    def __len__(self):
        return len(self.__list)


class Statement(BaseModel):
    pass
