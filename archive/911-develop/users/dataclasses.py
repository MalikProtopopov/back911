from dataclasses import dataclass


@dataclass(slots=True)
class AuthTokenData:
    """
    For user auth
    """

    code: int
    access_token: str
    refresh_token: str
    is_new: bool
    is_active: bool

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass(slots=True)
class CodeAuthData:
    """
    For user auth
    """

    code: int
    attempt_counter: int = 3

    def __getitem__(self, item):
        return getattr(self, item)

    def __eq__(self, other):
        if isinstance(other, CodeAuthData):
            return (
                self.code == other.code
                and self.attempt_counter == other.attempt_counter
            )
        return False


@dataclass(slots=True)
class AuthTokenDataNew:
    """
    For user auth
    """

    access_token: str
    refresh_token: str
    is_new: bool
    is_active: bool

    def __getitem__(self, item):
        return getattr(self, item)
