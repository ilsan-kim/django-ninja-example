from math import ceil

from config.utils.schemas import Paginated


def paginated_response(queryset, mapper_func, return_schema, *, per_page=10, page=1):
    try:
        total_count = len(queryset)
    except TypeError:
        total_count = 1
    limit = per_page
    offset = per_page * (page - 1)
    page_count = ceil(total_count / per_page)

    try:
        data = list(queryset[offset: limit + offset])
    except TypeError:
        data = queryset

    return return_schema(
        total_count=total_count,
        per_page=limit,
        from_record=offset + 1,
        to_record=(offset + limit) if (offset + limit) <= total_count else (total_count % per_page) + offset,
        previous_page=page - 1 if page > 2 else 1,
        current_page=page,
        next_page=min(page + 1, page_count),
        page_count=page_count,
        data=[mapper_func(d) for d in data],
    )
