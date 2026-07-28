from functools import lru_cache

from supabase import Client, create_client
from supabase.client import ClientOptions

from app.core.config import settings


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    if not settings.supabase_url or not settings.supabase_secret_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SECRET_KEY are required")
    return create_client(
        settings.supabase_url,
        settings.supabase_secret_key,
        options=ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            function_client_timeout=10,
        ),
    )


@lru_cache(maxsize=1)
def get_supabase_auth_client() -> Client:
    if not settings.supabase_url or not settings.supabase_publishable_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY are required")
    return create_client(
        settings.supabase_url,
        settings.supabase_publishable_key,
        options=ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            function_client_timeout=10,
        ),
    )
