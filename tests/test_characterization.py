"""Testes de caracterização de process_order.

Objetivo: travar o comportamento ATUAL do sistema legado antes da refatoração.
Nenhuma regra nova é inventada aqui: cada valor esperado vem do que o código
faz hoje.
"""

import pytest

import legacy_checkout
from legacy_checkout import process_order


def make_customer(customer_type, name="Cliente"):
    return {"name": name, "type": customer_type}


def make_item(name="Produto", price=100, qty=1, weight=0):
    return {"name": name, "price": price, "qty": qty, "weight": weight}


@pytest.fixture(autouse=True)
def clean_orders_history():
    legacy_checkout.ORDERS_PROCESSED.clear()
    yield
    legacy_checkout.ORDERS_PROCESSED.clear()


# ---------------------------------------------------------------- subtotal


def test_subtotal_sums_price_times_quantity_of_all_items():
    items = [make_item("A", price=100, qty=1), make_item("B", price=200, qty=2)]

    result = process_order(make_customer("regular"), items)

    assert result["subtotal"] == 500


def test_subtotal_ignores_items_with_zero_quantity():
    items = [make_item("A", price=50, qty=0), make_item("B", price=100, qty=2)]

    result = process_order(make_customer("regular"), items)

    assert result["subtotal"] == 200


# ------------------------------------------------- desconto por tipo de cliente


def test_vip_below_1000_receives_10_percent_discount():
    result = process_order(make_customer("vip"), [make_item(price=500)])

    assert result["discount"] == 50
    assert result["total"] == 481.50
    assert result["points"] == 96


def test_vip_at_1000_receives_15_percent_discount():
    result = process_order(make_customer("vip"), [make_item(price=1000)])

    assert result["discount"] == 150
    assert result["total"] == 909.50
    assert result["points"] == 181


def test_employee_receives_20_percent_discount():
    result = process_order(make_customer("employee"), [make_item(price=100)])

    assert result["discount"] == 20
    assert result["shipping"] == 20
    assert result["tax"] == 5.60
    assert result["total"] == 105.60
    assert result["points"] == 10


def test_regular_below_800_receives_no_discount():
    result = process_order(make_customer("regular"), [make_item(price=700)])

    assert result["discount"] == 0


def test_regular_at_800_receives_5_percent_discount():
    result = process_order(make_customer("regular"), [make_item(price=800)])

    assert result["discount"] == 40


def test_unknown_customer_type_receives_no_discount():
    result = process_order(make_customer("guest"), [make_item(price=100)])

    assert result["discount"] == 0


# ------------------------------------------------------------------ cupons


def test_promo20_adds_20_percent_when_subtotal_is_at_least_500():
    result = process_order(
        make_customer("regular"), [make_item(price=500)], coupon="PROMO20"
    )

    assert result["discount"] == 100


def test_promo20_is_ignored_when_subtotal_is_below_500():
    result = process_order(
        make_customer("regular"), [make_item(price=499)], coupon="PROMO20"
    )

    assert result["discount"] == 0


def test_vip50_adds_fixed_50_for_vip_customer():
    result = process_order(
        make_customer("vip"), [make_item(price=600)], coupon="VIP50"
    )

    assert result["discount"] == 110


def test_vip50_is_ignored_for_non_vip_customer():
    result = process_order(
        make_customer("regular"), [make_item(price=600)], coupon="VIP50"
    )

    assert result["discount"] == 0


def test_unknown_coupon_gives_no_discount():
    result = process_order(
        make_customer("regular"), [make_item(price=100)], coupon="INEXISTENTE"
    )

    assert result["discount"] == 0


def test_discount_is_capped_at_25_percent_of_subtotal():
    # funcionário (20%) + PROMO10 (10%) = 30%, limitado a 25% de 1000
    result = process_order(
        make_customer("employee"), [make_item(price=1000)], coupon="PROMO10"
    )

    assert result["discount"] == 250


# -------------------------------------------------------------------- frete


def test_shipping_is_free_when_subtotal_is_at_least_500():
    result = process_order(
        make_customer("regular"), [make_item(price=500, weight=5)]
    )

    assert result["shipping"] == 0


def test_express_shipping_is_charged_even_with_subtotal_above_500():
    # (20 + 5 * 0.4) * 1.8
    result = process_order(
        make_customer("regular"),
        [make_item(price=500, weight=5)],
        express=True,
    )

    assert result["shipping"] == 39.60


def test_shipping_in_southeast_state_uses_base_20_plus_040_per_kg():
    result = process_order(
        make_customer("regular"), [make_item(price=100, weight=10)], state="MG"
    )

    assert result["shipping"] == 24


def test_shipping_outside_southeast_uses_base_35_plus_060_per_kg():
    result = process_order(
        make_customer("regular"), [make_item(price=100, weight=10)], state="BA"
    )

    assert result["shipping"] == 41
    assert result["tax"] == 12
    assert result["total"] == 153


def test_express_shipping_outside_southeast_applies_multiplier():
    # (35 + 10 * 0.6) * 1.8
    result = process_order(
        make_customer("regular"),
        [make_item(price=100, weight=10)],
        state="BA",
        express=True,
    )

    assert result["shipping"] == 73.80


def test_shipping_weight_is_multiplied_by_quantity():
    # peso total = 2 * 3 = 6 -> 20 + 6 * 0.4
    result = process_order(
        make_customer("regular"), [make_item(price=100, qty=3, weight=2)]
    )

    assert result["shipping"] == 22.40


# ------------------------------------------------------------------ impostos


@pytest.mark.parametrize(
    "state, expected_tax",
    [
        ("MG", 7.00),
        ("SP", 9.00),
        ("RJ", 8.00),
        ("ES", 7.00),
        ("BA", 12.00),
    ],
)
def test_tax_rate_depends_on_state(state, expected_tax):
    result = process_order(
        make_customer("regular"), [make_item(price=100)], state=state
    )

    assert result["tax"] == expected_tax


def test_default_state_is_mg():
    result = process_order(make_customer("regular"), [make_item(price=100)])

    assert result["tax"] == 7.00


# ----------------------------------------------------------------- duplicados


def test_no_duplicates_returns_empty_list():
    items = [make_item("A"), make_item("B")]

    result = process_order(make_customer("regular"), items)

    assert result["duplicate_products"] == []


def test_duplicate_name_appears_only_once_even_if_repeated_many_times():
    items = [make_item("A"), make_item("A"), make_item("A")]

    result = process_order(make_customer("regular"), items)

    assert result["duplicate_products"] == ["A"]


def test_duplicates_keep_order_of_first_occurrence():
    items = [make_item("B"), make_item("A"), make_item("B"), make_item("A")]

    result = process_order(make_customer("regular"), items)

    assert result["duplicate_products"] == ["B", "A"]


# ------------------------------------------------------- efeitos colaterais


def test_processed_order_is_appended_to_history():
    result = process_order(make_customer("regular"), [make_item()])

    assert legacy_checkout.ORDERS_PROCESSED == [result]


def test_order_summary_is_printed(capsys):
    process_order(make_customer("regular", name="Ana"), [make_item(price=100)])

    output = capsys.readouterr().out
    assert "Pedido processado para Ana" in output
    assert "TOTAL:" in output


def test_result_contains_customer_name():
    result = process_order(make_customer("regular", name="Ana"), [make_item()])

    assert result["customer"] == "Ana"
