from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class TreeNode(BaseModel):
    id: str = Field(..., description="Unique lowercase-dash-separated ID")
    label: str = Field(..., description="Short human-readable label")
    type: Literal["root", "skill", "outcome", "career"] = Field(..., description="Node type")
    level: int = Field(..., description="Tree level (0=root, 1=skill, 2=outcome, 3=skill, 4=career)")
    actions: Optional[List[str]] = Field(None, description="List of actions (required for skill nodes)")
    children: Optional[List["TreeNode"]] = Field(None, description="List of child nodes")


class ProfileInput(BaseModel):
    profile: str = Field(..., description="Student profile description (interests, traits, etc.)")


class TreeResponse(BaseModel):
    tree: TreeNode = Field(..., description="Generated skill tree")


# Update forward reference for TreeNode.children
TreeNode.model_rebuild() 