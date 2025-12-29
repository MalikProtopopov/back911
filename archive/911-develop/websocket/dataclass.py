from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ChatMessageData:
    command: str
    message_text: str

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass(slots=True, frozen=True)
class ChatHistoryData:
    command: str
    page: int

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass(slots=True, frozen=True)
class PartnerOrderAddRequest:
    order_id: int
    command: str

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass(slots=True, frozen=True)
class OrderStatusChangeRequest:
    order_id: int
    command: str
    status: str

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass(slots=True, frozen=True)
class NotifyPartnersRequest:
    command: str

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass(slots=True, frozen=True)
class ChangeOrderOptionsRequest:
    command: str
    order_id: int
    options: list[dict]

    def __getitem__(self, item):
        return getattr(self, item)
