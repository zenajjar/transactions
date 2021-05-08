import re
from datetime import datetime
from typing import List, Union
from uuid import UUID

from pydantic import validator, BaseModel

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


class FrozenModel(BaseModel):
    class Config:
        frozen = True


class MoneyAmount(FrozenModel):
    amount: int
    currency: str

    def __add__(self, other: Union[int, 'MoneyAmount']) -> 'MoneyAmount':
        if isinstance(other, int):
            return MoneyAmount(amount=self.amount + other, currency=self.currency)
        elif isinstance(other, MoneyAmount):
            if self.currency == other.currency:
                return MoneyAmount(amount=self.amount + other.amount, currency=self.currency)
            else:
                raise ValueError(f"operands have mismatched currencies: '{self.currency}' and '{other.currency}'")
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{self.__class__.__name__}' and '{other.__class__.__name__}'")

    def __radd__(self, other: int) -> 'MoneyAmount':
        return self + other

    def __mul__(self, other: float) -> 'MoneyAmount':
        return MoneyAmount(amount=int(round(self.amount * other)), currency=self.currency)

    def __str__(self):
        return f'{self.amount} {self.currency}'


class Tender(FrozenModel):
    type: str
    name: str
    total_money: MoneyAmount


class Tax(FrozenModel):
    id: UUID
    name: str
    rate: float
    inclusion_type: str
    is_custom_amount: bool
    applied_money: MoneyAmount


class Creator(FrozenModel):
    id: UUID
    name: str
    email: str

    @classmethod
    @validator('email')
    def validate_email(cls, v):
        if not re.match(EMAIL_REGEX, v):
            raise ValueError(f"invalid email address '{v}'")
        return v


class Category(FrozenModel):
    id: UUID
    name: str


class Variation(FrozenModel):
    id: UUID
    name: str
    pricing_type: str
    price_money: MoneyAmount


class Discount(FrozenModel):
    ...


class Modifier(FrozenModel):
    id: UUID
    name: str
    quantity: int
    applied_money: MoneyAmount


class Item(FrozenModel):
    id: UUID
    name: str
    quantity: int
    total_money: MoneyAmount
    single_quantity_money: MoneyAmount
    gross_sales_money: MoneyAmount
    discount_money: MoneyAmount
    net_sales_money: MoneyAmount
    category: Category
    variation: Variation
    taxes: List[Tax]
    discounts: List[Discount]
    modifiers: List[Modifier]


class Transaction(FrozenModel):
    id: str
    business_id: UUID
    location_id: UUID
    transaction_id: UUID
    receipt_id: str
    serial_number: str
    dining_option: str
    creation_time: datetime
    discount_money: MoneyAmount
    additive_tax_money: MoneyAmount
    inclusive_tax_money: MoneyAmount
    refunded_money: MoneyAmount
    tax_money: MoneyAmount
    tip_money: MoneyAmount
    total_collected_money: MoneyAmount
    creator: Creator
    tender: Tender
    taxes: List[Tax]
    itemization: List[Item]

    class Config:
        fields = {'id': '_id'}
