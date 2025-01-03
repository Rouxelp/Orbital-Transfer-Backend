from utils.paginate import paginate_items
from utils.paginate import PaginatedResponse

def test_paginate_items_with_next():
    items = list(range(1, 101))  # 100 items
    result = paginate_items(items, "/test_endpoint", page=1, page_size=10)

    assert isinstance(result, PaginatedResponse)
    assert result.total_items == 100
    assert result.total_pages == 10
    assert result.next == "/test_endpoint?page=2&page_size=10"
    assert result.data == list(range(1, 11))

    # Test to_json method
    result_json = result.to_json()
    assert result_json.get("page", None) == 1
    assert result_json.get("page_size", None) == 10
    assert result_json.get("total_items", None) == 100
    assert result_json.get("total_pages", None) == 10
    assert result_json.get("next", None) == "/test_endpoint?page=2&page_size=10"
    assert result_json.get("data", None) == list(range(1, 11))

def test_paginate_items_last_page():
    items = list(range(1, 101))  # 100 items
    result = paginate_items(items, "/test_endpoint", page=10, page_size=10)

    assert isinstance(result, PaginatedResponse)
    assert result.next is None  # No next page
    assert result.data == list(range(91, 101))

    # Test to_json method
    result_json = result.to_json()
    assert result_json.get("page", None) == 10
    assert result_json.get("page_size", None) == 10
    assert result_json.get("total_items", None) == 100
    assert result_json.get("total_pages", None) == 10
    assert result_json.get("next", None) is None
    assert result_json.get("data", None) == list(range(91, 101))
