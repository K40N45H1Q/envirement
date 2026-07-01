from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Query


api_router = APIRouter()

PLAN_CATALOG = [
    {
        "id": "basic",
        "name": "Basic",
        "monthly_price": Decimal("99"),
        "currency": "EUR",
    },
    {
        "id": "standard",
        "name": "Standard",
        "monthly_price": Decimal("149"),
        "currency": "EUR",
    },
    {
        "id": "pro",
        "name": "Pro",
        "monthly_price": Decimal("229"),
        "currency": "EUR",
    },
]
YEARLY_DISCOUNT_PERCENT = 15


def calculate_price(monthly_price: Decimal, billing_period: str) -> Decimal:
    if billing_period != "yearly":
        return monthly_price

    yearly_base_price = monthly_price * Decimal("12")
    discounted_price = yearly_base_price * (Decimal("1") - (Decimal(YEARLY_DISCOUNT_PERCENT) / Decimal("100")))
    return discounted_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@api_router.get("/health", tags=["system"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@api_router.get("/bootstrap-status", tags=["system"])
async def bootstrap_status() -> dict[str, str]:
    return {
        "status": "ok",
        "mode": "hybrid",
        "detail": "New app foundation is active and legacy MVP routes are mounted for continuity.",
    }


@api_router.get("/pricing/plans", tags=["pricing"])
async def get_pricing_plans(
    billing_period: str = Query("monthly", pattern="^(monthly|yearly)$"),
) -> dict[str, object]:
    return {
        "billing_period": billing_period,
        "discount_percent": YEARLY_DISCOUNT_PERCENT if billing_period == "yearly" else 0,
        "plans": [
            {
                "id": plan["id"],
                "name": plan["name"],
                "price": float(calculate_price(plan["monthly_price"], billing_period)),
                "currency": plan["currency"],
            }
            for plan in PLAN_CATALOG
        ],
    }
