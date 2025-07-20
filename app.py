# app.py
from flask import Flask, request, jsonify
from database import menu, orders

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    user_id = request.json.get("user_id")

    # Simple rule-based NLP
    if "menu" in user_input:
        return jsonify({"response": "\n".join([f"{item}: ${info['price']}" for item, info in menu.items()])})
    
    elif "order" in user_input:
        for item in menu:
            if item in user_input:
                orders.setdefault(user_id, {"items": [], "status": "preparing"})
                orders[user_id]["items"].append(item)
                return jsonify({"response": f"{item} added to your order."})
        return jsonify({"response": "Item not found in menu."})

    elif "track" in user_input:
        order = orders.get(user_id)
        if order:
            return jsonify({"response": f"Your order is {order['status']}."})
        return jsonify({"response": "No active order."})

    elif "bye" in user_input:
        return jsonify({"response": "Thanks for visiting!"})

    return jsonify({"response": "I didn't understand that. You can ask for the menu or place an order."})

if __name__ == "__main__":
    app.run(debug=True)