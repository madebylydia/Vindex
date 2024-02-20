import asyncio
import collections.abc
import typing


class AsyncIterator[_T](
    collections.abc.AsyncIterator[_T], collections.abc.Awaitable[collections.abc.Iterable[_T]]
):
    """Permits the iteration of an iterable using an async context, allowing and to set a step
    between each iteration.
    """

    _subjectsubject: _T

    delay: float | int

    def __init__(self, subject: collections.abc.Iterable[_T], delay: float | int = 0) -> None:
        """Create a new AsyncIterator from an iterable subject.

        Parameters
        ----------
        subject : Iterable[_T]
            The iterable subject to iterate over.
        delaty : int
            The delay in seconds between each iteration.
        """
        self._subject = iter(subject)
        self.delay = delay
        super().__init__()

    def __aiter__(self) -> "AsyncIterator[_T]":
        return self

    async def __anext__(self) -> _T:
        try:
            item = next(self._subject)
        except StopIteration as exception:
            raise StopAsyncIteration from exception
        await asyncio.sleep(self.delay)
        return item

    def __await__(
        self,
    ) -> collections.abc.Generator[typing.Any, None, collections.abc.Iterable[_T]]:
        return self.to_list().__await__()

    async def next(self) -> _T:
        return await anext(self)

    async def to_list(self) -> list[_T]:
        return [item async for item in self]
