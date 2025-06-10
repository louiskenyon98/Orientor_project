from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import List, Optional
import logging
from sqlalchemy.orm import Session

from app.routers.user import get_current_user
from app.models import User
from app.utils.database import get_db
from app.services.conversation_service import ConversationService
from app.services.category_service import CategoryService
from app.services.chat_message_service import ChatMessageService
from app.schemas.conversation import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    ConversationListResponse, ConversationFilters
)
from app.schemas.chat_message import ExportRequest, MessageStats

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat/conversations",
    tags=["conversations"]
)

@router.post("", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    try:
        new_conversation = await ConversationService.create_conversation(
            db, current_user.id, conversation.initial_message, conversation.title
        )
        return ConversationResponse.from_orm(new_conversation)
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation"""
    conversation = await ConversationService.get_conversation_by_id(
        db, conversation_id, current_user.id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return ConversationResponse.from_orm(conversation)

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    updates: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update conversation properties"""
    conversation = await ConversationService.get_conversation_by_id(
        db, conversation_id, current_user.id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Apply updates
    if updates.title is not None:
        await ConversationService.update_conversation_title(
            db, conversation_id, updates.title, current_user.id
        )
    if updates.category_id is not None:
        await ConversationService.set_category(
            db, conversation_id, updates.category_id, current_user.id
        )
    if updates.is_favorite is not None:
        conversation.is_favorite = updates.is_favorite
    if updates.is_archived is not None:
        conversation.is_archived = updates.is_archived
    
    db.commit()
    db.refresh(conversation)
    
    return ConversationResponse.from_orm(conversation)

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation permanently"""
    success = await ConversationService.delete_conversation(
        db, conversation_id, current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return {"message": "Conversation deleted successfully"}

@router.post("/{conversation_id}/favorite")
async def toggle_favorite(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle favorite status of a conversation"""
    is_favorite = await ConversationService.toggle_favorite(
        db, conversation_id, current_user.id
    )
    if is_favorite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return {"is_favorite": is_favorite}

@router.post("/{conversation_id}/archive")
async def toggle_archive(
    conversation_id: int,
    archive: bool = Body(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive or unarchive a conversation"""
    success = await ConversationService.archive_conversation(
        db, conversation_id, current_user.id, archive
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return {"archived": archive}

@router.post("/{conversation_id}/generate-title")
async def generate_title(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate an automatic title for the conversation"""
    title = await ConversationService.auto_generate_title(
        db, conversation_id, current_user.id
    )
    if not title:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or unable to generate title"
        )
    return {"title": title}

@router.get("/{conversation_id}/statistics", response_model=MessageStats)
async def get_conversation_statistics(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for a conversation"""
    # Verify conversation belongs to user
    conversation = await ConversationService.get_conversation_by_id(
        db, conversation_id, current_user.id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    stats = await ChatMessageService.get_message_statistics(db, conversation_id)
    return stats

@router.post("/{conversation_id}/export")
async def export_conversation(
    conversation_id: int,
    export_request: ExportRequest = Body(ExportRequest()),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export conversation in various formats"""
    # Verify conversation belongs to user
    conversation = await ConversationService.get_conversation_by_id(
        db, conversation_id, current_user.id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    try:
        export_data = await ChatMessageService.export_conversation(
            db, conversation_id, export_request.format
        )
        
        # Set appropriate content type based on format
        content_types = {
            "json": "application/json",
            "txt": "text/plain",
            "pdf": "application/pdf"
        }
        
        from fastapi.responses import Response
        
        return Response(
            content=export_data,
            media_type=content_types.get(export_request.format, "application/octet-stream"),
            headers={
                "Content-Disposition": f"attachment; filename=conversation_{conversation_id}.{export_request.format}"
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error exporting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export conversation"
        )