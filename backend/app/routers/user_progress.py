from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.routers.user import get_current_user
from app.models.user import User
from app.models.user_progress import UserProgress
from app.schemas.tree import UserProgressCreate, UserProgressUpdate, UserProgress as UserProgressSchema

router = APIRouter(
    prefix="/user-progress",
    tags=["user-progress"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/", response_model=UserProgressSchema)
async def get_user_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get existing progress or create new
    progress = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).first()
    
    if not progress:
        # Initialize user progress
        progress = UserProgress(
            user_id=current_user.id,
            total_xp=0,
            level=1
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    return progress

@router.post("/update", response_model=UserProgressSchema)
async def update_user_progress(
    update: UserProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get existing progress or create new
    progress = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).first()
    
    if not progress:
        # Initialize user progress
        progress = UserProgress(
            user_id=current_user.id,
            total_xp=update.xp_gained,
            level=1,
            last_completed_node=update.node_id
        )
    else:
        # Update existing progress
        progress.total_xp += update.xp_gained
        progress.last_completed_node = update.node_id
        
        # Calculate level based on XP
        if progress.total_xp <= 50:
            progress.level = 1
        elif progress.total_xp <= 150:
            progress.level = 2
        elif progress.total_xp <= 300:
            progress.level = 3
        elif progress.total_xp <= 500:
            progress.level = 4
        elif progress.total_xp <= 750:
            progress.level = 5
        else:
            progress.level = 6
    
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress 