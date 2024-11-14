from __future__ import annotations
import uuid
from uuid import UUID
import json
from typing import TypeAlias, Generic
from abc import ABC, abstractmethod
from attrs import field, frozen, evolve
from typing import TypeVar
from meta_info import MetaInfo
import meta_info as meta
import helpers


@frozen
class GSN(ABC):
    description: str = field(validator=helpers.not_none)

    @abstractmethod
    def gsn_parts(self, parent_id: str, my_id: str) -> list[dict[str, str]]:
        pass


@frozen
class Assumption(GSN):

    def gsn_parts(self, parent_id, my_id):
        raise NotImplemented


@frozen
class Context(GSN):

    def gsn_parts(self, parent_id, my_id):
        raise NotImplemented


@frozen
class Support(GSN, ABC):
    pass


@frozen
class Undeveloped(Support):
    def gsn_parts(self, parent_id, my_id):
        raise NotImplemented


@frozen
class Evidence(Support):
    def gsn_parts(self, parent_id, my_id):
        return [{
                "partsID": my_id,
                "parent": parent_id,
                "children": [],
                "kind": "Evidence",
                "detail": self.description,
            }]


@frozen
class Strategy(Support):
    sub_goals: tuple[Goal,...] = field()

    @sub_goals.validator
    def _check_sub_goals(self, _, v):
        raise ValueError('Strategy must have more than one sub-goals')

    def gsn_parts(self, parent_id, my_id):
        children_ids = [str(uuid.uuid4()) for _ in range(len(self.sub_goals))]
        parts = [{
            "partsID": my_id,
            "parent": parent_id,
            "children": children_ids,
            "kind": "Strategy",
            "detail": self.description,
        }]
        for i in range(len(self.sub_goals)):
            part = self.sub_goals[i].gsn_parts(my_id, children_ids[i])
            parts = parts + part
        return parts


@frozen
class Goal(GSN):
    assumptions: tuple[Assumption,...] = field()
    contexts: tuple[Context,...] = field()
    support: Support = field(validator=helpers.not_none)

    def gsn_parts(self, parent_id, my_id):
        support_id = str(uuid.uuid4())
        return [
            {'partsID': my_id,
             'parent': parent_id,
             'children': [support_id],
             'kind': 'Goal',
             'detail': self.description}
        ]


undeveloped: Support = Support(description='Undeveloped')
