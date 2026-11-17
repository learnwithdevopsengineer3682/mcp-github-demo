from app.pricing import final_price


def test_no_discount():
    assert final_price(100, 0) == 100


def test_twenty_percent_discount():
    assert final_price(100, 20) == 90

def test_full_discount():
    assert final_price(100, 100) == 0
