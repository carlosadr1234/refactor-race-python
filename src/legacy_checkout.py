"""Processamento de pedidos.

Versão refatorada do sistema legado. O módulo mantém o nome ``legacy_checkout``
para preservar a interface usada pelos testes; o comportamento de
``process_order`` não foi alterado.
"""

from collections import Counter

ORDERS_PROCESSED = []

CUSTOMER_VIP = "vip"
CUSTOMER_EMPLOYEE = "employee"
CUSTOMER_REGULAR = "regular"

COUPON_PROMO10 = "PROMO10"
COUPON_PROMO20 = "PROMO20"
COUPON_VIP50 = "VIP50"

VIP_HIGH_DISCOUNT_THRESHOLD = 1000
VIP_HIGH_DISCOUNT_RATE = 0.15
VIP_BASE_DISCOUNT_RATE = 0.10
EMPLOYEE_DISCOUNT_RATE = 0.20
REGULAR_DISCOUNT_THRESHOLD = 800
REGULAR_DISCOUNT_RATE = 0.05

PROMO10_RATE = 0.10
PROMO20_RATE = 0.20
PROMO20_MIN_SUBTOTAL = 500
VIP50_FIXED_DISCOUNT = 50
MAX_DISCOUNT_RATE = 0.25

FREE_SHIPPING_MIN_SUBTOTAL = 500
SOUTHEAST_STATES = {"MG", "SP", "RJ", "ES"}
SOUTHEAST_BASE_SHIPPING = 20
SOUTHEAST_SHIPPING_PER_KG = 0.4
OTHER_BASE_SHIPPING = 35
OTHER_SHIPPING_PER_KG = 0.6
EXPRESS_SHIPPING_MULTIPLIER = 1.8

TAX_RATES = {"MG": 0.07, "SP": 0.09, "RJ": 0.08, "ES": 0.07}
DEFAULT_TAX_RATE = 0.12

VIP_POINTS_DIVISOR = 5
DEFAULT_POINTS_DIVISOR = 10


def calculate_subtotal(items):
    """Soma preço x quantidade dos itens com quantidade positiva."""
    # Laço explícito (e não sum()) para manter exatamente a mesma soma de
    # ponto flutuante do código original: sum() de floats usa soma compensada
    # no Python 3.12+ e poderia mudar centavos.
    subtotal = 0
    for item in items:
        if item["qty"] > 0:
            subtotal += item["price"] * item["qty"]
    return subtotal


def calculate_total_weight(items):
    """Soma peso x quantidade de todos os itens (peso ausente vale 0)."""
    total_weight = 0
    for item in items:
        total_weight += item.get("weight", 0) * item["qty"]
    return total_weight


def find_duplicate_products(items):
    """Nomes que aparecem mais de uma vez, na ordem da primeira ocorrência."""
    name_counts = Counter(item["name"] for item in items)
    return [name for name, count in name_counts.items() if count > 1]


def calculate_customer_discount(customer_type, subtotal):
    """Desconto pelo tipo de cliente."""
    if customer_type == CUSTOMER_VIP:
        if subtotal >= VIP_HIGH_DISCOUNT_THRESHOLD:
            return subtotal * VIP_HIGH_DISCOUNT_RATE
        return subtotal * VIP_BASE_DISCOUNT_RATE
    if customer_type == CUSTOMER_EMPLOYEE:
        return subtotal * EMPLOYEE_DISCOUNT_RATE
    if customer_type == CUSTOMER_REGULAR and subtotal >= REGULAR_DISCOUNT_THRESHOLD:
        return subtotal * REGULAR_DISCOUNT_RATE
    return 0


def calculate_coupon_discount(coupon, customer_type, subtotal):
    """Desconto do cupom informado (cupom desconhecido não dá desconto)."""
    if coupon == COUPON_PROMO10:
        return subtotal * PROMO10_RATE
    if coupon == COUPON_PROMO20 and subtotal >= PROMO20_MIN_SUBTOTAL:
        return subtotal * PROMO20_RATE
    if coupon == COUPON_VIP50 and customer_type == CUSTOMER_VIP:
        return VIP50_FIXED_DISCOUNT
    return 0


def calculate_discount(customer_type, coupon, subtotal):
    """Desconto total, limitado a 25% do subtotal."""
    discount = calculate_customer_discount(customer_type, subtotal)
    discount += calculate_coupon_discount(coupon, customer_type, subtotal)
    return min(discount, subtotal * MAX_DISCOUNT_RATE)


def calculate_shipping(subtotal, total_weight, state, express):
    """Frete: grátis a partir de 500 (exceto expresso), senão base + peso."""
    if subtotal >= FREE_SHIPPING_MIN_SUBTOTAL and not express:
        return 0

    if state in SOUTHEAST_STATES:
        shipping = SOUTHEAST_BASE_SHIPPING + total_weight * SOUTHEAST_SHIPPING_PER_KG
    else:
        shipping = OTHER_BASE_SHIPPING + total_weight * OTHER_SHIPPING_PER_KG

    if express:
        shipping = shipping * EXPRESS_SHIPPING_MULTIPLIER
    return shipping


def get_tax_rate(state):
    """Alíquota do estado (estados sem alíquota própria usam a padrão)."""
    return TAX_RATES.get(state, DEFAULT_TAX_RATE)


def calculate_loyalty_points(customer_type, amount_due):
    """Pontos sobre o valor ainda não arredondado (VIP ganha mais)."""
    if customer_type == CUSTOMER_VIP:
        return int(amount_due / VIP_POINTS_DIVISOR)
    return int(amount_due / DEFAULT_POINTS_DIVISOR)


def print_order_summary(customer_name, subtotal, discount, shipping, tax, total):
    print("Pedido processado para " + customer_name)
    print("Subtotal:", subtotal)
    print("Desconto:", discount)
    print("Frete:", shipping)
    print("Imposto:", tax)
    print("TOTAL:", total)


def process_order(customer, items, coupon="", state="MG", express=False):
    customer_type = customer["type"]

    subtotal = calculate_subtotal(items)
    discount = calculate_discount(customer_type, coupon, subtotal)
    discounted_value = subtotal - discount

    shipping = calculate_shipping(
        subtotal, calculate_total_weight(items), state, express
    )
    tax = discounted_value * get_tax_rate(state)
    amount_due = discounted_value + shipping + tax
    total = round(amount_due, 2)

    result = {
        "customer": customer["name"],
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "shipping": round(shipping, 2),
        "tax": round(tax, 2),
        "total": total,
        "points": calculate_loyalty_points(customer_type, amount_due),
        "duplicate_products": find_duplicate_products(items),
    }

    ORDERS_PROCESSED.append(result)
    print_order_summary(customer["name"], subtotal, discount, shipping, tax, total)

    return result
