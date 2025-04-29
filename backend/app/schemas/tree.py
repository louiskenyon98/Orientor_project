from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field


class TreeNode(BaseModel):
    id: str = Field(..., description="Unique lowercase-dash-separated ID")
    label: str = Field(..., description="Short human-readable label")
    type: Literal["root", "skill", "outcome", "career"] = Field(..., description="Node type")
    level: int = Field(..., description="Tree level (0=root, 1=skill, 2=outcome, 3=skill, 4=career)")
    actions: Optional[List[str]] = Field(None, description="List of actions (required for skill nodes)")
    children: Optional[List["TreeNode"]] = Field(None, description="List of child nodes")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "root",
                "label": "Student Profile",
                "type": "root",
                "level": 0,
                "children": [
                    {
                        "id": "skill-1",
                        "label": "Communication",
                        "type": "skill",
                        "level": 1,
                        "actions": ["Join debate club", "Practice public speaking", "Write blog posts"],
                        "children": []
                    }
                ]
            }
        }


class ProfileInput(BaseModel):
    profile: str = Field(..., description="User profile text for tree generation")


class SkillsTreeInput(BaseModel):
    profile: str = Field(..., description="Technical profile for skills tree generation")
    custom_prompt: str = Field("", description="Custom prompt for generating a technical skills tree")


class TreeResponse(BaseModel):
    tree: TreeNode = Field(..., description="Generated skill tree")


# Update forward reference for TreeNode.children
TreeNode.model_rebuild() 