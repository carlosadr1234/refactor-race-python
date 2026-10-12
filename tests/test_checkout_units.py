"""Testes unitários das funções extraídas de process_order.

Antes da refatoração, estas regras só podiam ser testadas passando por
process_order inteiro. Agora cada regra é verificada isoladamente.
"""

import pytest

from legacy_checkout import (
    calculate_coupon_discount,
    calculate_customer_discount,
    calculate_discount,
    calculate_loyalty_points,
    calculate_shipping,
    calculate_subtotal,
    calculate_total_weight,
    find_duplicate_products,
    get_tax_rate,
)


def test_calculate_subtotal_of_empty_list_is_zero():
    assert calculate_subtotal([]) == 0


def test_calculate_subtotal_skips_non_positive_quantities():
    items = [
        {"price": 10, "qty": 2},
        {"price": 99, "qty": 0},
    ]

    assert calculate_subtotal(items) == 20


def test_calculate_total_weight_treats_missing_weight_as_zero():
    items = [
        {"qty": 2, "weight": 1.5},
        {"qty": 3},
    ]

    assert calculate_total_weight(items) == 3


def test_find_duplicate_products_ignores_unique_names():
    items = [{"name": "A"}, {"name": "B"}]

    assert find_duplicate_products(items) == []


def test_find_duplicate_products_returns_each_name_once_in_order():
    items = [{"name": n} for n in ["B", "A", "B", "A", "B"]]

    assert find_duplicate_products(items) == ["B", "A"]


@pytest.mark.parametrize(
    "customer_type, subtotal, expected",
    [
        ("vip", 999, 99.9),
        ("vip", 1000, 150),
        ("employee", 100, 20),
        ("regular", 799, 0),
        ("regular", 800, 40),
        ("guest", 5000, 0),
    ],
)
def test_calculate_customer_discount(customer_type, subtotal, expected):
    assert calculate_customer_discount(customer_type, subtotal) == pytest.approx(
        expected
    )


@pytest.mark.parametrize(
    "coupon, customer_type, subtotal, expected",
    [
        ("PROMO10", "regular", 100, 10),
        ("PROMO20", "regular", 500, 100),
        ("PROMO20", "regular", 499, 0),
        ("VIP50", "vip", 100, 50),
        ("VIP50", "regular", 100, 0),
        ("", "vip", 100, 0),
        ("OUTRO", "vip", 100, 0),
    ],
)
def test_calculate_coupon_discount(coupon, customer_type, subtotal, expected):
    assert calculate_coupon_discount(coupon, customer_type, subtotal) == expected


def test_calculate_discount_is_limited_to_25_percent_of_subtotal():
    assert calculate_discount("employee", "PROMO10", 1000) == 250


def test_calculate_discount_below_the_cap_is_not_changed():
    assert calculate_discount("employee", "", 1000) == 200


def test_calculate_shipping_is_free_for_large_non_express_order():
    assert calculate_shipping(500, 10, "BA", express=False) == 0


def test_calculate_shipping_express_overrides_free_shipping():
    assert calculate_shipping(500, 0, "MG", express=True) == pytest.approx(36)


def test_calculate_shipping_southeast_vs_other_states():
    assert calculate_shipping(100, 10, "SP", express=False) == pytest.approx(24)
    assert calculate_shipping(100, 10, "BA", express=False) == pytest.approx(41)


@pytest.mark.parametrize(
    "state, expected",
    [("MG", 0.07), ("SP", 0.09), ("RJ", 0.08), ("ES", 0.07), ("PR", 0.12)],
)
def test_get_tax_rate(state, expected):
    assert get_tax_rate(state) == expected


def test_vip_earns_one_point_per_5_and_others_per_10():
    assert calculate_loyalty_points("vip", 109.9) == 21
    assert calculate_loyalty_points("regular", 109.9) == 10


def test_loyalty_points_are_truncated_not_rounded():
    assert calculate_loyalty_points("regular", 19.99) == 1
