"""Verificação diferencial: compara o process_order atual com a versão original.

Gera casos aleatórios (sementes fixas, resultado reproduzível) e exige que
resultado E texto impresso sejam idênticos aos da versão original, que é
lida do histórico do Git (commit ORIGINAL_SHA).

Uso (na raiz do repositório):
    python tools/differential_check.py [quantidade_de_casos]
"""

import contextlib
import importlib.util
import io
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ORIGINAL_SHA = "554c20d5b3d53a4d1133efede0f1bf8cce9d0d88"
SOURCE_PATH = "src/legacy_checkout.py"

CUSTOMER_TYPES = ["vip", "employee", "regular", "guest", "VIP"]
COUPONS = ["", "PROMO10", "PROMO20", "VIP50", "promo10", "XYZ"]
STATES = ["MG", "SP", "RJ", "ES", "BA", "RS", ""]
PRODUCT_NAMES = ["A", "B", "C", "D"]


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_original_module():
    source = subprocess.run(
        ["git", "show", f"{ORIGINAL_SHA}:{SOURCE_PATH}"],
        check=True, capture_output=True, text=True,
    ).stdout
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "original_checkout.py"
        path.write_text(source, encoding="utf-8")
        return load_module(path, "original_checkout")


def random_items(rnd):
    items = []
    for _ in range(rnd.randint(0, 6)):
        item = {
            "name": rnd.choice(PRODUCT_NAMES),
            "price": rnd.choice(
                [rnd.randint(0, 1500), round(rnd.uniform(0, 1500), 2), 0.1, 0.2, 0.3]
            ),
            "qty": rnd.choice([0, 1, 1, 2, 3, 5, -1]),
        }
        if rnd.random() < 0.8:
            item["weight"] = rnd.choice([0, 1, 2.5, 0.1, 0.2, 7, round(rnd.uniform(0, 20), 3)])
        items.append(item)
    return items


def run(module, customer, items, options):
    module.ORDERS_PROCESSED.clear()
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = module.process_order(customer, items, **options)
    return result, buffer.getvalue(), list(module.ORDERS_PROCESSED)


def main():
    total_cases = int(sys.argv[1]) if len(sys.argv) > 1 else 60000
    original = load_original_module()
    current = load_module(SOURCE_PATH, "current_checkout")
    rnd = random.Random(12345)

    for case in range(total_cases):
        items = random_items(rnd)
        customer = {"name": f"Cliente{case}", "type": rnd.choice(CUSTOMER_TYPES)}
        options = {
            "coupon": rnd.choice(COUPONS),
            "state": rnd.choice(STATES),
            "express": rnd.choice([True, False]),
        }
        expected = run(original, customer, items, options)
        obtained = run(current, customer, items, options)
        if expected != obtained:
            print("DIVERGÊNCIA no caso", case)
            print("entrada:", customer, items, options)
            print("original:", expected)
            print("atual:   ", obtained)
            sys.exit(1)

    print(f"OK: {total_cases} casos idênticos (resultado + saída impressa)")


if __name__ == "__main__":
    main()
