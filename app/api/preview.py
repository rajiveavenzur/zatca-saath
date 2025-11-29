"""Preview endpoints for live invoice preview."""
from fastapi import APIRouter, HTTPException
from decimal import Decimal

from app.schemas.preview import PreviewRequest, PreviewResponse

router = APIRouter(prefix="/api/v1/preview", tags=["preview"])


@router.post("/calculate", response_model=PreviewResponse)
async def calculate_preview(request: PreviewRequest):
    """
    Fast calculation endpoint for live preview.
    
    NO database calls, NO PDF generation.
    Just validate and calculate totals.
    
    Target response time: < 100ms
    
    Args:
        request: Preview request with line items
        
    Returns:
        Calculated totals with validation status
    """
    try:
        subtotal = Decimal("0")
        vat_amount = Decimal("0")
        errors = []

        # Validate and calculate each line item
        for idx, item in enumerate(request.line_items):
            try:
                # Extract values with defaults
                qty = Decimal(str(item.get('quantity', 0)))
                price = Decimal(str(item.get('unit_price', 0)))
                vat_rate = Decimal(str(item.get('vat_rate', 15)))

                # Validate values
                if qty < 0:
                    errors.append(f"Item {idx + 1}: Quantity cannot be negative")
                if price < 0:
                    errors.append(f"Item {idx + 1}: Unit price cannot be negative")
                if vat_rate not in [Decimal("0"), Decimal("5"), Decimal("15")]:
                    errors.append(f"Item {idx + 1}: VAT rate must be 0%, 5%, or 15%")

                # Calculate item totals
                item_subtotal = qty * price
                item_vat = (item_subtotal * vat_rate) / Decimal("100")

                subtotal += item_subtotal
                vat_amount += item_vat

            except (ValueError, TypeError, KeyError) as e:
                errors.append(f"Item {idx + 1}: Invalid number format - {str(e)}")

        # Calculate total
        total_amount = subtotal + vat_amount

        return PreviewResponse(
            subtotal=round(subtotal, 2),
            vat_amount=round(vat_amount, 2),
            total_amount=round(total_amount, 2),
            is_valid=len(errors) == 0,
            errors=errors
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Preview calculation failed: {str(e)}"
        )
