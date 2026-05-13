"""In-memory data store for demo purposes."""

USERS = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "user"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
    99: {"id": 99, "name": "Admin", "email": "admin@example.com", "role": "admin"},
}

ORDERS = {
    101: {"id": 101, "user_id": 1, "total": 49.99, "items": ["book"]},
    102: {"id": 102, "user_id": 2, "total": 19.99, "items": ["pen"]},
    103: {"id": 103, "user_id": 1, "total": 99.99, "items": ["headphones"]},
}

COUPONS = {
    "SAVE10": {"code": "SAVE10", "discount": 10, "redeemed_by": set()},
}


def get_user(user_id):
    return USERS.get(user_id)


def get_order(order_id):
    return ORDERS.get(order_id)


def update_user(user_id, **fields):
    if user_id in USERS:
        USERS[user_id].update(fields)
        return USERS[user_id]
    return None


def get_coupon(code):
    return COUPONS.get(code)