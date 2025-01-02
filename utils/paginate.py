from urllib.parse import urlencode

def paginate_items(items: list, base_url: str, page: int = 1, page_size: int = 50, max_page_size: int = 100) -> dict:
    """
    Paginate a list of items and generate metadata including the next page URL.

    Args:
        items (list): The list of items to paginate.
        base_url (str): Base URL for constructing the next page link.
        page (int, optional): The page number (1-based). Defaults to 1.
        page_size (int, optional): Number of items per page. Defaults to 50.
        max_page_size (int, optional): Maximum allowed page size. Defaults to 100.

    Returns:
        dict: A dictionary containing the paginated items and metadata.
    """
    if page_size > max_page_size:
        page_size = max_page_size

    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    next_page = None
    if page < total_pages:
        query_params = {"page": page + 1, "page_size": page_size}
        next_page = f"{base_url}?{urlencode(query_params)}"

    return {
        "page": page, 
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "next": next_page,
        "data": items[start_index:end_index]
    }
