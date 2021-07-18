from .database_provider import DatabaseProvider


class BaseModel:
    def __init__(self) -> None:
        self.db_helper = DatabaseProvider.instance()

    @staticmethod
    def update_all_attributes(base_class, base, current, skip_fields=None):
        if skip_fields is None:
            skip_fields = []

        attr_list = base_class.__table__.columns.keys()
        for k in attr_list:
            if k != 'id' and k not in skip_fields:
                attribute_value = getattr(current, k)
                if getattr(base, k) != attribute_value:
                    setattr(base, k, attribute_value)
