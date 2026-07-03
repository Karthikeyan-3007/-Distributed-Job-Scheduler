from app.models.queue import Queue
from app.models.retry_policy import RetryPolicy
from app.repositories.base import BaseRepository


class QueueRepository(BaseRepository[Queue]):
    model = Queue


class RetryPolicyRepository(BaseRepository[RetryPolicy]):
    model = RetryPolicy
