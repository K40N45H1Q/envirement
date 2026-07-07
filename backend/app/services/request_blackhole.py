from typing import Any


async def close_blocked_connection(send: Any) -> bool:
    cycle = getattr(send, "__self__", None)
    transport = getattr(cycle, "transport", None)
    if transport is None:
        return False

    transport.close()
    return True
