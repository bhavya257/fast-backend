def pagination_index(offset, limit, total_items):
    page = {}
    if offset + limit < total_items:
        page["next"] = offset + limit
    page["limit"] = limit
    if offset > 0:
        page["previous"] = max(0, min(offset - limit, total_items - limit))
    return page