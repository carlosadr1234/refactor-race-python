# legacy_checkout.py

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


def process_order(customer, items, coupon="", state="MG", express=False):

    subtotal = calculate_subtotal(items)

    desconto = calculate_discount(customer["type"], coupon, subtotal)

    valor_com_desconto = subtotal - desconto

    peso = calculate_total_weight(items)

    # frete
    frete = 0

    if subtotal >= FREE_SHIPPING_MIN_SUBTOTAL and not express:
        frete = 0
    else:
        if state in SOUTHEAST_STATES:
            frete = SOUTHEAST_BASE_SHIPPING + peso * SOUTHEAST_SHIPPING_PER_KG
        else:
            frete = OTHER_BASE_SHIPPING + peso * OTHER_SHIPPING_PER_KG

        if express:
            frete = frete * EXPRESS_SHIPPING_MULTIPLIER

    # impostos
    taxa = TAX_RATES.get(state, DEFAULT_TAX_RATE)

    imposto = valor_com_desconto * taxa

    # pontos de fidelidade
    pontos = 0

    if customer["type"] == CUSTOMER_VIP:
        pontos = int((valor_com_desconto + frete + imposto) / VIP_POINTS_DIVISOR)
    else:
        pontos = int((valor_com_desconto + frete + imposto) / DEFAULT_POINTS_DIVISOR)

    duplicados = find_duplicate_products(items)

    total_final = round(valor_com_desconto + frete + imposto, 2)

    resultado = {
        "customer": customer["name"],
        "subtotal": round(subtotal, 2),
        "discount": round(desconto, 2),
        "shipping": round(frete, 2),
        "tax": round(imposto, 2),
        "total": total_final,
        "points": pontos,
        "duplicate_products": duplicados
    }

    ORDERS_PROCESSED.append(resultado)

    print("Pedido processado para " + customer["name"])
    print("Subtotal:", subtotal)
    print("Desconto:", desconto)
    print("Frete:", frete)
    print("Imposto:", imposto)
    print("TOTAL:", total_final)

    return resultado
