from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import String
from sqlalchemy import Column

from .declarative_base import DeclarativeBase
from .base_model import BaseModel
from .database_provider import DatabaseProvider

class User(DeclarativeBase, BaseModel):
    __tablename__ = 'user'

    id = Column(String(255), primary_key=True)
    nickname = Column(String(255))
    card_bills = relationship(
        "NuBankCardBill", backref="user", lazy=True)

    def __init__(self) -> None:
            self.db_helper = DatabaseProvider.instance()

    def from_dict(self, values: dict): 
        self.id = values.get('id', None)
        self.nickname = values.get('nickname', None)

        return self

    def sync(self, current_value: dict):
        session = self.db_helper.session
        base_values = session.query(User).all()

        # This get the value if exists
        query_result = [x for x in base_values if x.id == current_value['id']]
        current_value = User().from_dict(current_value)

        if len(query_result) > 0:

            base_value: User = query_result[0]

            self.update_all_attributes(
                User, base_value, current_value)
            session.add(base_value)

            print(f'{base_value.id} has been updated')

        else:
            session.add(current_value)
            print(f'{current_value.id} has been added')

        session.commit()