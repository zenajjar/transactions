import unittest

from pydantic import ValidationError

from transactions.parse import parse_json_transaction, XmlTransactionParser
from transactions.validate import TransactionValidator


class JsonValidatorTest(unittest.TestCase):
    def setUp(self):
        self.validator = TransactionValidator(parse_json_transaction)

    def test_pass(self):
        with open('../res/transaction.json', encoding='utf-8') as json_file:
            json_str = json_file.read()

        self.validator(json_str)

    def test_inconsistent_item_tax(self):
        with open('../res/transaction_inconsistent_item_tax.json', encoding='utf-8') as json_file:
            json_str = json_file.read()

        try:
            self.validator(json_str)
            self.fail()
        except ValueError:
            pass

    def test_inconsistent_total_item_money(self):
        with open('../res/transaction_inconsistent_total_item_money.json', encoding='utf-8') as json_file:
            json_str = json_file.read()

        try:
            self.validator(json_str)
            self.fail()
        except ValueError:
            pass

    def test_inconsistent_total_money(self):
        with open('../res/transaction_inconsistent_total_money.json', encoding='utf-8') as json_file:
            json_str = json_file.read()

        try:
            self.validator(json_str)
            self.fail()
        except ValueError:
            pass

    def test_inconsistent_tax_money(self):
        with open('../res/transaction_inconsistent_tax_money.json', encoding='utf-8') as json_file:
            json_str = json_file.read()

        try:
            self.validator(json_str)
            self.fail()
        except ValueError:
            pass

    def test_inconsistent_currency(self):
        with open('../res/transaction_inconsistent_currencies.json', encoding='utf-8') as json_file:
            json_str = json_file.read()

        try:
            self.validator(json_str)
            self.fail()
        except ValueError:
            pass


class XmlValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = TransactionValidator(XmlTransactionParser())

    def test_pass(self):
        with open('../res/transaction.xml', encoding='utf-8') as xml_file:
            xml_str = xml_file.read()

        self.validator(xml_str)

    def test_missing_fields(self):
        with open('../res/transaction_missing_fields.xml', encoding='utf-8') as xml_file:
            xml_str = xml_file.read()

        try:
            self.validator(xml_str)
            self.fail()
        except ValidationError:
            pass


class XmlJsonConsistencyTest(unittest.TestCase):
    def setUp(self):
        self.xml_validator = TransactionValidator(XmlTransactionParser())
        self.json_validator = TransactionValidator(parse_json_transaction)

    def test_consistency(self):
        with open('../res/transaction.json', encoding='utf-8') as json_file:
            json_str = json_file.read()

        json_trans = self.json_validator(json_str)

        with open('../res/transaction.xml', encoding='utf-8') as xml_file:
            xml_str = xml_file.read()

        xml_trans = self.xml_validator(xml_str)

        self.assertEqual(json_trans, xml_trans)


if __name__ == '__main__':
    unittest.main()
