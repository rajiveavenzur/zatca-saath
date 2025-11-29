"""Draft endpoints for invoice auto-save functionality."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.draft import InvoiceDraft
from app.schemas.draft import DraftCreate, DraftResponse
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/drafts", tags=["drafts"])


@router.post("/", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
async def save_draft(
    draft: DraftCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save invoice draft (auto-save from frontend).
    
    - If is_auto_saved=True, update existing auto-save draft (only 1 per user)
    - If is_auto_saved=False, create new named draft
    
    Args:
        draft: Draft data to save
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Saved draft object
    """
    if draft.is_auto_saved:
        # Update or create auto-save draft (only 1 per user)
        existing = db.query(InvoiceDraft).filter(
            InvoiceDraft.user_id == current_user.id,
            InvoiceDraft.is_auto_saved == True
        ).first()

        if existing:
            # Update existing auto-save draft
            existing.draft_data = draft.draft_data
            db.commit()
            db.refresh(existing)
            return existing

    # Create new draft
    new_draft = InvoiceDraft(
        user_id=current_user.id,
        draft_data=draft.draft_data,
        name=draft.name,
        is_auto_saved=draft.is_auto_saved
    )

    db.add(new_draft)
    db.commit()
    db.refresh(new_draft)

    return new_draft


@router.get("/latest", response_model=DraftResponse)
async def get_latest_draft(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get most recent auto-saved draft.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Latest auto-saved draft
        
    Raises:
        HTTPException: If no draft found
    """
    draft = db.query(InvoiceDraft).filter(
        InvoiceDraft.user_id == current_user.id,
        InvoiceDraft.is_auto_saved == True
    ).order_by(InvoiceDraft.updated_at.desc()).first()

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No draft found"
        )

    return draft


@router.get("/", response_model=List[DraftResponse])
async def list_drafts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all saved drafts (manual saves only).
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of manually saved drafts
    """
    drafts = db.query(InvoiceDraft).filter(
        InvoiceDraft.user_id == current_user.id,
        InvoiceDraft.is_auto_saved == False
    ).order_by(InvoiceDraft.updated_at.desc()).all()

    return drafts


@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft(
    draft_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific draft by ID.
    
    Args:
        draft_id: Draft ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Draft object
        
    Raises:
        HTTPException: If draft not found
    """
    draft = db.query(InvoiceDraft).filter(
        InvoiceDraft.id == draft_id,
        InvoiceDraft.user_id == current_user.id
    ).first()

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )

    return draft


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a draft.
    
    Args:
        draft_id: Draft ID to delete
        current_user: Authenticated user
        db: Database session
        
    Returns:
        None
        
    Raises:
        HTTPException: If draft not found
    """
    draft = db.query(InvoiceDraft).filter(
        InvoiceDraft.id == draft_id,
        InvoiceDraft.user_id == current_user.id
    ).first()

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )

    db.delete(draft)
    db.commit()

    return None
