from utils.paginate import paginate_items


def test_paginate_items_with_next():
    items = list(range(1, 101))  # 100 items
    result = paginate_items(items, "/test_endpoint", page=1, page_size=10)
    assert result["total_items"] == 100
    assert result["total_pages"] == 10
    assert result["next"] == "/test_endpoint?page=2&page_size=10"
    assert result["data"] == list(range(1, 11))

def test_paginate_items_last_page():
    items = list(range(1, 101))
    result = paginate_items(items, "/test_endpoint", page=10, page_size=10)
    assert result["next"] is None  # No next page
    assert result["data"] == list(range(91, 101))
