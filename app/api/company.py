"""Company profile management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/v1/companies", tags=["companies"])


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a company profile for the current user.
    
    Args:
        company_data: Company profile data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        The created company profile
    """
    # Create new company
    new_company = Company(
        user_id=current_user.id,
        name_en=company_data.name_en,
        name_ar=company_data.name_ar,
        vat_number=company_data.vat_number,
        address=company_data.address,
        phone=company_data.phone,
        email=company_data.email
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return new_company


@router.get("", response_model=List[CompanyResponse])
async def list_companies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all companies for the current user.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of company profiles
    """
    companies = db.query(Company).filter(Company.user_id == current_user.id).all()
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific company by ID.
    
    Args:
        company_id: Company UUID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        The company profile
        
    Raises:
        HTTPException: If company not found or not owned by user
    """
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    company_data: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a company profile.
    
    Args:
        company_id: Company UUID
        company_data: Updated company data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        The updated company profile
        
    Raises:
        HTTPException: If company not found or not owned by user
    """
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    # Update fields if provided
    update_data = company_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a company profile.
    
    Args:
        company_id: Company UUID
        current_user: Authenticated user
        db: Database session
        
    Raises:
        HTTPException: If company not found or not owned by user
    """
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    db.delete(company)
    db.commit()
