from typing import Optional


def append_offset_and_limit(
    query: str, offset: Optional[int] = None, limit: Optional[int] = None
) -> str:
    if offset:
        query += f" OFFSET {offset}"
    if limit:
        query += f" LIMIT {limit}"
    return query
