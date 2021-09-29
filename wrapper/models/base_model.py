from .database_provider import DatabaseProvider


class BaseModel:
    def __init__(self) -> None:
        pass
    
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

    def to_json(self):
        return self.__dict__

    def from_dict(self, values: dict):
        keys = type(self).__dict__.keys()

        for key in keys:
            dict_value = values.get(key, None)
            value_type = type(dict_value)

            if value_type not in [dict, list] and dict_value is not None:
                self.__setattr__(key, dict_value)

        return self
