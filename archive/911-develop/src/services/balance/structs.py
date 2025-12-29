from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BalanceHistory:
    """
    Partner BalanceHistory
    """

    before: str
    after: str
    balance_type: str

    def __getitem__(self, item):
        return getattr(self, item)
