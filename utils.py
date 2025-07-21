def pagination_index(offset, limit, total_items, selected_items_count):
    page = {}
    if offset + limit < total_items:
        page["next"] = offset + limit
    page["limit"] = selected_items_count
    if offset > 0:
        page["previous"] = max(0, min(offset - selected_items_count, total_items - limit))
    return page