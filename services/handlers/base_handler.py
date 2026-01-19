import abc

from services.models.handler_models import MockAiogramMessage


class Handler(abc.ABC):
    @abc.abstractmethod
    async def execute(self, message: MockAiogramMessage): ...
