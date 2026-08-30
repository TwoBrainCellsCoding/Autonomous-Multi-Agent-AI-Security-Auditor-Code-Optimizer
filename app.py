import sqlite3
from typing import Any, Iterable, List, Optional, Tuple

# Module‑level SQLite connection reused across calls. SQLite connections are lightweight and
# thread‑safe for read‑only operations. For write‑heavy workloads a connection pool would be
# preferable, but for this simple example a single shared connection is sufficient and avoids
# the overhead of opening/closing a connection on every function call.

_DB_PATH = "app.db"
_connection: Optional[sqlite3.Connection] = None


def _get_connection() -> sqlite3.Connection:
    """Return a cached SQLite connection, creating it on first use.

    The connection uses ``row_factory`` to return rows as ``sqlite3.Row`` objects, which
    behave like dictionaries (allowing column access by name) while keeping the memory
    footprint low.
    """
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(_DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        _connection.row_factory = sqlite3.Row
    return _connection


def fetch_user(username: str) -> Optional[sqlite3.Row]:
    """Fetch a single user record by *username*.

    The function uses a parameterised query to prevent SQL injection and reuses a
    module‑level connection to avoid the cost of repeatedly opening/closing the database.
    It returns ``None`` when the user does not exist.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()
    finally:
        cursor.close()


def compute_sum(numbers: Iterable[int]) -> int:
    """Return the arithmetic sum of *numbers*.

    Utilises Python's built‑in ``sum`` which is implemented in C and therefore faster than
    a manual Python loop. Accepts any iterable of integers (list, tuple, generator, etc.).
    """
    # ``sum`` gracefully handles empty iterables, returning ``0``.
    return sum(numbers)
