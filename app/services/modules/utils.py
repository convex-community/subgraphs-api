from typing import Optional


def append_offset_and_limit(
    query: str, offset: Optional[int] = None, limit: Optional[int] = None
) -> str:
    if offset or limit:
        query += f" OFFSET {offset if offset else 0}"
        query += f" LIMIT {limit if limit else 1}"
    return query
