from functools import wraps


def ws_auth(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if self.auth and self.user:
            await func(self, *args, **kwargs)
        else:
            await self.auth_close()

    return wrapper
