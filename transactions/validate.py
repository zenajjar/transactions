from typing import Callable, Any, Set, Union

from transactions.model import Transaction, MoneyAmount, Item


class TransactionValidator:
    def __init__(self, parser: Callable[[str], Transaction]):
        self.parse = parser

    def validate(self, encoded_transaction: Union[str, Transaction]) -> Transaction:
        """parses the passed transaction and runs it through validation tests"""
        if isinstance(encoded_transaction, str):
            transaction = self.parse(encoded_transaction)
        elif isinstance(encoded_transaction, Transaction):
            transaction = encoded_transaction
        else:
            raise TypeError(f'argument must be str or Transaction, '
                            f'not {encoded_transaction.__class__.__name__}')

        self._validate_currencies(transaction)
        self.validate_items_taxes(transaction)
        self._validate_taxes(transaction)
        return transaction

    def __call__(self, encoded_transaction: Union[str, Transaction]) -> Transaction:
        """alternative way to call `validate` which could be more convenient"""
        return self.validate(encoded_transaction)

    def _validate_currencies(self, transaction: Transaction) -> None:
        """validates that all currencies in transaction are consistent"""
        currencies = self.get_currencies(transaction)
        if len(currencies) > 1:
            raise ValueError(f"inconsistent currencies found: {currencies}")

    def get_currencies(self, obj: Any) -> Set[str]:
        """finds all `MoneyAmount` objects under `obj` recursively and returns their currencies in a set"""
        if isinstance(obj, MoneyAmount):
            return {obj.currency}

        currencies = set()
        if hasattr(obj, '__dict__'):
            for element in obj.__dict__.values():
                currencies |= self.get_currencies(element)

        return currencies

    def validate_items_taxes(self, transaction: Transaction) -> None:
        for item in transaction.itemization:
            self._validate_item_taxes(item)

    @staticmethod
    def _validate_taxes(transaction: Transaction) -> None:
        """"validates that all item taxes are consistent with the total tax money and the total collected money"""
        total_net_sales_money = 0
        total_money = 0

        for item in transaction.itemization:
            total_money += item.total_money
            total_net_sales_money += item.net_sales_money

        if total_money != transaction.total_collected_money:
            raise ValueError(f"total collected money is inconsistent with total items money. "
                             f"expected ({total_money}), found ({transaction.total_collected_money}) in:\n"
                             f"{transaction!r}")

        if total_net_sales_money + transaction.tax_money != total_money:
            raise ValueError(f"tax money is inconsistent with total items money in:"
                             f"{transaction!r}")

    @staticmethod
    def _validate_item_taxes(item: Item) -> None:
        """validates applied money for all taxes of an `Item` and that they're consistent with the total money"""
        item_taxes = set(item.taxes)
        total_item_taxes = 0
        for tax in item_taxes:
            tax_money = item.net_sales_money * tax.rate
            if tax_money != tax.applied_money:
                raise ValueError(
                    f"inconsistent applied tax money. expected ({tax_money}), found ({tax.applied_money}) in:\n"
                    f"{tax!r}")
            total_item_taxes += tax_money

        total_item_money = total_item_taxes + item.net_sales_money
        if total_item_money != item.total_money:
            raise ValueError(f"inconsistent total money. expected ({total_item_money}), "
                             f"found ({item.total_money}) in:\n"
                             f"{item!r}")
