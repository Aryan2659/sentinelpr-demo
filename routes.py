from flask import Flask, jsonify, request, session
from auth import login_required, require_admin, current_user_id
from models import get_user, get_order, update_user, USERS, ORDERS

app = Flask(__name__)
app.secret_key = "demo-secret-not-for-production"


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get("user_id")
    user = get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    session["user_id"] = user["id"]
    session["user_role"] = user["role"]
    return jsonify({"status": "logged in", "user_id": user["id"]})


@app.route('/profile')
@login_required
def profile():
    user = get_user(current_user_id())
    return jsonify(user)


@app.route('/users/<int:user_id>')
@login_required
def get_user_public(user_id):
    """Public profile lookup. Only returns name and id, not email."""
    user = get_user(user_id)
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": user["id"], "name": user["name"]})


@app.route('/admin/users')
@require_admin
def admin_list_users():
    return jsonify(list(USERS.values()))


@app.route('/admin/users/<int:user_id>/promote', methods=['POST'])
@require_admin
def admin_promote_user(user_id):
    user = update_user(user_id, role="admin")
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify(user)


@app.route('/admin/orders')
@require_admin
def admin_list_orders():
    return jsonify(list(ORDERS.values()))

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
def admin_delete_user(user_id):
    """Permanently delete a user from the system."""
    if user_id in USERS:
        del USERS[user_id]
        return jsonify({"status": "deleted", "user_id": user_id})
    return jsonify({"error": "not found"}), 404



@app.route('/orders/<int:order_id>')
@login_required
def get_order_detail(order_id):
    """Fetch full order details including total and items."""
    order = get_order(order_id)
    if not order:
        return jsonify({"error": "not found"}), 404
    return jsonify(order)


if __name__ == '__main__':
    
    app.run(debug=True)


#1
#2
#5

#3
#4
