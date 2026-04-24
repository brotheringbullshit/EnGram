from typing import Any, Union

class EngramType:
    def __init__(self, value: Any):
        self.value = value
    
    @property
    def type_name(self) -> str:
        return type(self.value).__name__
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return f"EngramType({self.value!r})"


class EngramInteger(EngramType):
    def __init__(self, value: int):
        super().__init__(int(value))
    
    @property
    def type_name(self) -> str:
        return "integer"
    
    def __add__(self, other):
        if isinstance(other, EngramInteger):
            return EngramInteger(self.value + other.value)
        return EngramInteger(self.value + other)
    
    def __sub__(self, other):
        if isinstance(other, EngramInteger):
            return EngramInteger(self.value - other.value)
        return EngramInteger(self.value - other)
    
    def __mul__(self, other):
        if isinstance(other, EngramInteger):
            return EngramInteger(self.value * other.value)
        return EngramInteger(self.value * other)
    
    def __truediv__(self, other):
        if isinstance(other, EngramInteger):
            return EngramFloat(self.value / other.value)
        return EngramFloat(self.value / other)
    
    def __eq__(self, other):
        if isinstance(other, EngramInteger):
            return self.value == other.value
        return self.value == other
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __gt__(self, other):
        if isinstance(other, EngramInteger):
            return self.value > other.value
        return self.value > other
    
    def __lt__(self, other):
        if isinstance(other, EngramInteger):
            return self.value < other.value
        return self.value < other
    
    def __ge__(self, other):
        return not self.__lt__(other)
    
    def __le__(self, other):
        return not self.__gt__(other)


class EngramFloat(EngramType):
    def __init__(self, value: float):
        super().__init__(float(value))
    
    @property
    def type_name(self) -> str:
        return "float"
    
    def __add__(self, other):
        if isinstance(other, (EngramInteger, EngramFloat)):
            return EngramFloat(self.value + other.value)
        return EngramFloat(self.value + other)
    
    def __sub__(self, other):
        if isinstance(other, (EngramInteger, EngramFloat)):
            return EngramFloat(self.value - other.value)
        return EngramFloat(self.value - other)
    
    def __mul__(self, other):
        if isinstance(other, (EngramInteger, EngramFloat)):
            return EngramFloat(self.value * other.value)
        return EngramFloat(self.value * other)
    
    def __truediv__(self, other):
        if isinstance(other, (EngramInteger, EngramFloat)):
            return EngramFloat(self.value / other.value)
        return EngramFloat(self.value / other)
    
    def __eq__(self, other):
        if isinstance(other, (EngramInteger, EngramFloat)):
            return self.value == other.value
        return self.value == other
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __gt__(self, other):
        if isinstance(other, (EngramInteger, EngramFloat)):
            return self.value > other.value
        return self.value > other
    
    def __lt__(self, other):
        if isinstance(other, (EngramInteger, EngramFloat)):
            return self.value < other.value
        return self.value < other
    
    def __ge__(self, other):
        return not self.__lt__(other)
    
    def __le__(self, other):
        return not self.__gt__(other)


class EngramString(EngramType):
    def __init__(self, value: str):
        super().__init__(str(value))
    
    @property
    def type_name(self) -> str:
        return "string"
    
    def __add__(self, other):
        if isinstance(other, EngramString):
            return EngramString(self.value + other.value)
        return EngramString(self.value + str(other))
    
    def __eq__(self, other):
        if isinstance(other, EngramString):
            return self.value == other.value
        return self.value == other
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __contains__(self, item):
        if isinstance(item, EngramString):
            return item.value in self.value
        return str(item) in self.value
    
    def length(self) -> int:
        return len(self.value)
    
    def char_at(self, index: int) -> str:
        if 0 <= index < len(self.value):
            return self.value[index]
        return ""
    
    def substring(self, start: int, end: int = None) -> 'EngramString':
        if end is None:
            end = len(self.value)
        return EngramString(self.value[start:end])
    
    def split(self, delimiter: str = "") -> list:
        if delimiter == "":
            return [EngramString(c) for c in self.value]
        parts = self.value.split(delimiter)
        return [EngramString(p) for p in parts]
    
    def to_list(self) -> list:
        return [EngramString(c) for c in self.value]


class EngramBoolean(EngramType):
    def __init__(self, value: bool):
        super().__init__(bool(value))
    
    @property
    def type_name(self) -> str:
        return "boolean"
    
    def __eq__(self, other):
        if isinstance(other, EngramBoolean):
            return self.value == other.value
        return self.value == other
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __bool__(self) -> bool:
        return self.value


class EngramList(EngramType):
    def __init__(self, value: list):
        super().__init__(list(value))
    
    @property
    def type_name(self) -> str:
        return "list"
    
    def __len__(self) -> int:
        return len(self.value)
    
    def __getitem__(self, index):
        return self.value[index]
    
    def __setitem__(self, index, value):
        self.value[index] = value
    
    def append(self, item):
        self.value.append(item)
    
    def __add__(self, other):
        if isinstance(other, EngramList):
            return EngramList(self.value + other.value)
        return EngramList(self.value + [other])


class EngramObject(EngramType):
    def __init__(self, value: dict):
        super().__init__(dict(value))
    
    @property
    def type_name(self) -> str:
        return "object"
    
    def __len__(self) -> int:
        return len(self.value)
    
    def __getitem__(self, key):
        return self.value[key]
    
    def __setitem__(self, key, value):
        self.value[key] = value
    
    def __contains__(self, key):
        return key in self.value
    
    def get(self, key, default=None):
        return self.value.get(key, default)
    
    def keys(self):
        return self.value.keys()
    
    def values(self):
        return self.value.values()
    
    def items(self):
        return self.value.items()


def create_engram_value(value: Any) -> EngramType:
    if isinstance(value, EngramType):
        return value
    if isinstance(value, bool):
        return EngramBoolean(value)
    if isinstance(value, int):
        return EngramInteger(value)
    if isinstance(value, float):
        return EngramFloat(value)
    if isinstance(value, str):
        return EngramString(value)
    if isinstance(value, list):
        return EngramList(value)
    if isinstance(value, dict):
        return EngramObject(value)
    return EngramType(value)