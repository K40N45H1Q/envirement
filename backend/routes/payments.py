import hmac
import json
import time
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request as UrlRequest, urlopen

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import select

from app.core.config import settings
from database.models import User, get_session
from routes.safety import get_current_user, serialize_user


router = APIRouter(prefix="/payments", tags=["payments"])

PLAN_CATALOG = {
    "basic": {"name": "Basic", "unit_amount": 9900, "currency": "eur", "job_limit": 1},
    "standard": {"name": "Standard", "unit_amount": 14900, "currency": "eur", "job_limit": 5},
    "pro": {"name": "Pro", "unit_amount": 22900, "currency": "eur", "job_limit": 20},
}
STRIPE_API_BASE = "https://api.stripe.com/v1"


def require_stripe_secret() -> str:
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=500, detail={"error": "stripe_not_configured"})
    return settings.stripe_secret_key


def is_allowed_origin(value: str | None) -> bool:
    if not value:
        return False
    origin = normalize_origin(value)
    return bool(origin and origin in {normalize_origin(item) for item in settings.cors_origins})


def normalize_origin(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def normalize_return_path(value: Any) -> str:
    raw = str(value or "/dashboard?section=pricing").strip()
    if not raw.startswith("/") or raw.startswith("//"):
        return "/dashboard?section=pricing"
    return raw


def build_return_url(origin: str, path: str, params: dict[str, str]) -> str:
    separator = "&" if "?" in path else "?"
    query = urlencode(params).replace(
        "%7BCHECKOUT_SESSION_ID%7D",
        "{CHECKOUT_SESSION_ID}",
    )
    return f"{origin.rstrip('/')}{path}{separator}{query}"


def get_request_origin(request: Request) -> str:
    forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",")[0].strip()
    forwarded_host = request.headers.get("x-forwarded-host", "").split(",")[0].strip()
    scheme = forwarded_proto or request.url.scheme
    host = forwarded_host or request.headers.get("host") or request.url.netloc
    return f"{scheme}://{host}".rstrip("/")


def stripe_request(method: str, path: str, data: dict[str, Any] | None = None) -> dict:
    secret_key = require_stripe_secret()
    encoded_data = urlencode(data or {}).encode("utf-8") if data is not None else None
    request = UrlRequest(
        f"{STRIPE_API_BASE}{path}",
        data=encoded_data,
        method=method,
        headers={
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except Exception:
            payload = {"error": {"message": "stripe_request_failed"}}
        raise HTTPException(
            status_code=502,
            detail={"error": "stripe_request_failed", "stripe": payload.get("error", {})},
        ) from exc
    except URLError as exc:
        raise HTTPException(status_code=502, detail={"error": "stripe_unavailable"}) from exc


def is_active_subscription(user: User) -> bool:
    expires_at = user.subscription_expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return bool(user.subscription_plan in PLAN_CATALOG and expires_at and expires_at > datetime.now(timezone.utc))


def activate_plan(user: User, plan_id: str, session) -> User:
    if plan_id not in PLAN_CATALOG:
        raise HTTPException(status_code=400, detail={"error": "invalid_subscription_plan"})

    if is_active_subscription(user) and user.subscription_plan == plan_id:
        return user

    user.subscription_plan = plan_id
    user.subscription_expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    user.subscription_jobs_used = 0
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def activate_paid_checkout_session(session_id: str, db_session) -> tuple[User, dict]:
    if not session_id.startswith("cs_"):
        raise HTTPException(status_code=400, detail={"error": "invalid_checkout_session"})

    checkout_session = stripe_request("GET", f"/checkout/sessions/{session_id}")
    metadata = checkout_session.get("metadata") or {}
    plan_id = str(metadata.get("plan_id") or "").strip().lower()
    user_id = str(metadata.get("user_id") or "").strip()

    if checkout_session.get("status") != "complete" or checkout_session.get("payment_status") != "paid":
        raise HTTPException(status_code=402, detail={"error": "payment_not_completed"})
    if not user_id.isdigit():
        raise HTTPException(status_code=400, detail={"error": "invalid_checkout_session"})

    user = db_session.exec(select(User).where(User.id == int(user_id))).first()
    if not user or user.account_type != "employer":
        raise HTTPException(status_code=404, detail={"error": "user_not_found"})

    return activate_plan(user, plan_id, db_session), checkout_session


def get_invoice_links(invoice_id: str | None) -> dict[str, str]:
    if not invoice_id:
        return {}

    invoice = stripe_request("GET", f"/invoices/{invoice_id}")
    return {
        "invoice_url": invoice.get("hosted_invoice_url") or "",
        "invoice_pdf": invoice.get("invoice_pdf") or "",
    }


async def read_json_object(request: Request) -> dict:
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail={"error": "invalid_payload"})
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail={"error": "invalid_payload"})
    return data


@router.get("/stripe/config")
def get_stripe_config() -> dict[str, str]:
    return {"publishable_key": settings.stripe_publishable_key or ""}


@router.post("/checkout")
async def create_checkout_session(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    if current_user.account_type != "employer":
        raise HTTPException(status_code=403, detail={"error": "employer_account_required"})

    data = await read_json_object(request)
    plan_id = str(data.get("plan_id") or data.get("planId") or "").strip().lower()
    plan = PLAN_CATALOG.get(plan_id)
    if not plan:
        raise HTTPException(status_code=400, detail={"error": "invalid_subscription_plan"})
    if is_active_subscription(current_user):
        raise HTTPException(status_code=409, detail={"error": "active_subscription_exists"})

    origin = normalize_origin(request.headers.get("origin"))
    if not origin or not is_allowed_origin(origin):
        raise HTTPException(status_code=400, detail={"error": "invalid_origin"})

    return_path = normalize_return_path(data.get("return_path") or data.get("returnPath"))
    backend_origin = get_request_origin(request)
    success_url = build_return_url(backend_origin, "/api/payments/checkout/success", {
        "session_id": "{CHECKOUT_SESSION_ID}",
        "return_origin": origin,
        "return_path": return_path,
    })
    cancel_url = build_return_url(origin, return_path, {
        "stripe_payment": "cancelled",
    })
    frontend_success_url = build_return_url(origin, return_path, {
        "stripe_payment": "success",
        "stripe_session_id": "{CHECKOUT_SESSION_ID}",
    })

    checkout_session = stripe_request("POST", "/checkout/sessions", {
        "mode": "payment",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "customer_email": current_user.email,
        "client_reference_id": str(current_user.id),
        "invoice_creation[enabled]": "true",
        "invoice_creation[invoice_data][metadata][user_id]": str(current_user.id),
        "invoice_creation[invoice_data][metadata][plan_id]": plan_id,
        "metadata[user_id]": str(current_user.id),
        "metadata[plan_id]": plan_id,
        "metadata[source]": "cvhold-employer-dashboard",
        "metadata[frontend_success_url]": frontend_success_url,
        "line_items[0][price_data][currency]": plan["currency"],
        "line_items[0][price_data][unit_amount]": str(plan["unit_amount"]),
        "line_items[0][price_data][product_data][name]": f"CVHOLD {plan['name']} plan",
        "line_items[0][quantity]": "1",
    })

    checkout_url = checkout_session.get("url")
    if not checkout_url:
        raise HTTPException(status_code=502, detail={"error": "stripe_checkout_url_missing"})

    return {"id": checkout_session["id"], "url": checkout_url}


@router.get("/checkout/success")
def checkout_success(
    session_id: str,
    return_origin: str,
    return_path: str = "/dashboard?section=pricing",
    session=Depends(get_session),
):
    origin = normalize_origin(return_origin)
    if not origin or not is_allowed_origin(origin):
        raise HTTPException(status_code=400, detail={"error": "invalid_origin"})

    _, checkout_session = activate_paid_checkout_session(session_id, session)
    redirect_params = {
        "stripe_payment": "success",
        "stripe_session_id": session_id,
    }
    if checkout_session.get("invoice"):
        redirect_params["stripe_invoice_id"] = str(checkout_session["invoice"])
        invoice_links = get_invoice_links(str(checkout_session["invoice"]))
        if invoice_links.get("invoice_pdf"):
            redirect_params["stripe_invoice_pdf"] = invoice_links["invoice_pdf"]
        if invoice_links.get("invoice_url"):
            redirect_params["stripe_invoice_url"] = invoice_links["invoice_url"]

    return RedirectResponse(
        build_return_url(origin, normalize_return_path(return_path), redirect_params),
        status_code=303,
    )


@router.post("/checkout/confirm")
async def confirm_checkout_session(
    request: Request,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
) -> dict[str, Any]:
    data = await read_json_object(request)
    session_id = str(data.get("session_id") or data.get("sessionId") or "").strip()
    if not session_id.startswith("cs_"):
        raise HTTPException(status_code=400, detail={"error": "invalid_checkout_session"})

    user, checkout_session = activate_paid_checkout_session(session_id, session)
    if user.id != current_user.id:
        raise HTTPException(status_code=403, detail={"error": "forbidden"})

    invoice_links = get_invoice_links(checkout_session.get("invoice"))
    return {
        "status": "ok",
        "user": serialize_user(user),
        **invoice_links,
    }


def verify_stripe_signature(payload: bytes, signature_header: str) -> None:
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=500, detail={"error": "stripe_webhook_not_configured"})

    values = {}
    for item in signature_header.split(","):
        key, _, value = item.partition("=")
        values.setdefault(key, []).append(value)

    timestamp = values.get("t", [""])[0]
    signatures = values.get("v1", [])
    if not timestamp or not signatures:
        raise HTTPException(status_code=400, detail={"error": "invalid_stripe_signature"})
    if abs(time.time() - int(timestamp)) > 300:
        raise HTTPException(status_code=400, detail={"error": "stale_stripe_signature"})

    signed_payload = f"{timestamp}.".encode("utf-8") + payload
    expected = hmac.new(settings.stripe_webhook_secret.encode("utf-8"), signed_payload, sha256).hexdigest()
    if not any(hmac.compare_digest(expected, signature) for signature in signatures):
        raise HTTPException(status_code=400, detail={"error": "invalid_stripe_signature"})


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, session=Depends(get_session)) -> dict[str, str]:
    payload = await request.body()
    verify_stripe_signature(payload, request.headers.get("stripe-signature", ""))

    event = json.loads(payload.decode("utf-8"))
    if event.get("type") == "checkout.session.completed":
        checkout_session = (event.get("data") or {}).get("object") or {}
        if checkout_session.get("payment_status") == "paid":
            metadata = checkout_session.get("metadata") or {}
            user_id = str(metadata.get("user_id") or "").strip()
            plan_id = str(metadata.get("plan_id") or "").strip().lower()
            user = session.exec(select(User).where(User.id == int(user_id))).first() if user_id.isdigit() else None
            if user and user.account_type == "employer":
                activate_plan(user, plan_id, session)

    return {"status": "ok"}
