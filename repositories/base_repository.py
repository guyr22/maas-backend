from abc import ABC
from typing import List, Optional, Type, TypeVar, Generic, Dict, Any
from beanie import Document


T = TypeVar('T', bound=Document)

class BaseRepository(Generic[T], ABC):
    def __init__(self, model: Type[T]):
        self.model = model

    async def get_all(self) -> List[T]:
        raise NotImplementedError
    
    async def get(self, **kwargs) -> Optional[T]:
        raise NotImplementedError

    async def create(self, document: T) -> T:
        raise NotImplementedError

    async def update(self, document: T, data: Dict[str, Any]) -> T:
        raise NotImplementedError

    async def delete(self, document: T) -> T:
        raise NotImplementedError
