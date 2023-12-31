import uuid
from pydantic import BaseModel, Field


class LeafIndex(BaseModel):
    leaf_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    user_id: str


class Leaf(LeafIndex):
    content: str
