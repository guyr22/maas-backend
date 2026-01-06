from abc import ABC
from typing import TypeVar, Generic, List, Optional, Dict, Any
from repositories.base_repository import BaseRepository

T = TypeVar('T')
R = TypeVar('R', bound=BaseRepository)


class BaseService(Generic[T, R], ABC):
    def __init__(self, repo: R):
        self.repo = repo

    async def create(self, document: T) -> T:
        raise NotImplementedError

    async def get(self, **kwargs) -> Optional[T]:
        raise NotImplementedError

    async def update(self, document: T, data: Dict[str, Any]) -> T:
        raise NotImplementedError

    async def delete(self, document: T) -> T:
        raise NotImplementedError

    async def get_all(self) -> List[T]:
        raise NotImplementedError

    