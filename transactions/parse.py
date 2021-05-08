import json
from typing import MutableMapping

import xmltodict

from transactions.model import *


class XmlTransactionParser:
    _element_label = 'element'

    def parse(self, xml_str: str) -> Transaction:
        xml_dict = xmltodict.parse(xml_str, force_list=[self._element_label])
        xml_dict = self._flatten_lists(xml_dict['root'])
        return Transaction.parse_obj(xml_dict)

    def __call__(self, xml_str: str) -> Transaction:
        return self.parse(xml_str)

    def _flatten_lists(self, obj: MutableMapping) -> Union[dict, list]:
        if self._element_label in obj:
            return self._obj_to_list(obj)

        flattened_obj = {}
        for key, value in obj.items():
            if isinstance(value, MutableMapping):
                value = self._flatten_lists(value)
            elif value is None:
                value = []
            flattened_obj[key] = value

        return flattened_obj

    def _obj_to_list(self, obj: MutableMapping) -> list:
        list_ = []
        for element in obj[self._element_label]:
            if isinstance(element, MutableMapping):
                list_.append(self._flatten_lists(element))
            else:
                list_.append(element)
        return list_


def parse_json_transaction(json_str: str) -> Transaction:
    return Transaction.parse_obj(json.loads(json_str))
