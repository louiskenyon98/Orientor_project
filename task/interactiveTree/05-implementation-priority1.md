# Priority 1 Implementation: Fix Tree Generation

## Issue Analysis
The 404 error occurs because:
1. Frontend is trying to call `/api/v1/trees/generate-from-anchors` endpoint
2. This endpoint doesn't exist in the current backend
3. Current `/competence-tree/generate` endpoint generates trees automatically without accepting anchor skills

## Solution Implementation

### 1. Create New Endpoint for Anchor Skills
We need to add a new endpoint that accepts 5 anchor skills as input and generates a tree based on them.

### 2. Enhanced Tree Generation Service
Modify the competence tree service to support generating trees from specific anchor skills.

### 3. Error Handling & Validation
Add proper validation to ensure exactly 5 anchor skills are provided.

## Files to Create/Modify

1. **Add to competence_tree.py router**: New endpoint for anchor skill tree generation
2. **Enhance competenceTree.py service**: Add method to generate from specific anchors
3. **Update frontend service**: Fix the API call to use correct endpoint

## Implementation Code

### Backend Router Enhancement
```python
@router.post("/generate-from-anchors", response_model=Dict[str, Any])
def generate_tree_from_anchors(
    request: AnchorSkillsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a competence tree from 5 specific anchor skills.
    
    Args:
        request: Contains anchor_skills list with exactly 5 ESCO skill IDs
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dict with graph_id for accessing the generated tree
    """
    # Validate anchor skills
    if len(request.anchor_skills) != 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Exactly 5 anchor skills required, got {len(request.anchor_skills)}"
        )
    
    # Generate tree from anchors
    tree_data = get_competence_tree_service().create_tree_from_anchors(
        db,
        current_user.id,
        request.anchor_skills,
        max_depth=request.max_depth,
        max_nodes=request.max_nodes
    )
    
    # Save and return graph_id
    graph_id = get_competence_tree_service().save_skill_tree(db, current_user.id, tree_data)
    
    return {
        "graph_id": graph_id,
        "status": "success",
        "nodes_generated": len(tree_data.get('nodes', [])),
        "edges_generated": len(tree_data.get('edges', []))
    }
```

### Request Schema
```python
from pydantic import BaseModel, Field
from typing import List

class AnchorSkillsRequest(BaseModel):
    anchor_skills: List[str] = Field(..., min_items=5, max_items=5, description="Exactly 5 ESCO skill IDs")
    max_depth: int = Field(3, ge=1, le=6, description="Maximum tree depth")
    max_nodes: int = Field(50, ge=10, le=100, description="Maximum nodes in tree")
    include_occupations: bool = Field(True, description="Include occupation nodes")
```

### Service Method Enhancement
```python
def create_tree_from_anchors(
    self,
    db: Session,
    user_id: int,
    anchor_skills: List[str],
    max_depth: int = 3,
    max_nodes: int = 50
) -> Dict[str, Any]:
    """
    Create a competence tree from specific anchor skills.
    """
    try:
        # Validate anchor skills exist in ESCO
        validated_anchors = self._validate_anchor_skills(anchor_skills)
        
        # Build tree structure from anchors
        tree_data = self._build_tree_from_anchors(
            validated_anchors,
            max_depth=max_depth,
            max_nodes=max_nodes
        )
        
        # Apply gamification rules
        tree_data = self._apply_gamification(tree_data)
        
        return tree_data
        
    except Exception as e:
        logger.error(f"Error creating tree from anchors: {str(e)}")
        raise
```

### Frontend Service Fix
```typescript
export const generateTreeFromAnchors = async (
  anchorSkills: string[]
): Promise<{ graph_id: string }> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('Authentication token not found');
    }
    
    const response = await axios.post(
      `${API_URL}/competence-tree/generate-from-anchors`,
      {
        anchor_skills: anchorSkills,
        max_depth: 3,
        max_nodes: 50,
        include_occupations: true
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        timeout: 60000 // 1 minute timeout
      }
    );
    
    return response.data;
  } catch (error: any) {
    console.error('Error generating tree from anchors:', error);
    throw error;
  }
};
```

## Next Steps
1. Implement the backend endpoint
2. Add proper error handling
3. Test with mock anchor skills
4. Update frontend to use new endpoint
5. Add loading states and user feedback