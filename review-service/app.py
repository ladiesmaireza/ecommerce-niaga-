from flask import Flask, jsonify, render_template, request
import requests
from functools import lru_cache
import os

app = Flask(__name__)

product_service_host = "localhost" if os.getenv("HOSTNAME") is None else "product-service"
cart_service_host = "localhost" if os.getenv("HOSTNAME") is None else "cart-service"
review_service_host = "localhost" if os.getenv("HOSTNAME") is None else "review-service"


@lru_cache(maxsize=128)
def get_products(product_id):
    try:
        response = requests.get(f'http://{product_service_host}:3000/products/{product_id}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching product data: {e}")
        return {"error": "Failed to fetch product data"}


def get_carts(product_id):
    try:
        response = requests.get(f'http://{cart_service_host}:3002/cart/{product_id}')
        response.raise_for_status()
        data = response.json().get("data", [])
        for item in data:
            if item.get("product_id") == product_id:
                return item.get("quantity", 0)
        return 0
    except requests.exceptions.RequestException as e:
        print(f"Error fetching cart data: {e}")
        return 0


def get_reviews(product_id):
    try:
        response = requests.get(f'http://{review_service_host}:3003/products/{product_id}/reviews')
        response.raise_for_status()
        data = response.json()
        return data.get('data', {"reviews": [], "product": {}})
    except requests.exceptions.RequestException as e:
        print(f"Error fetching review data: {e}")
        return {"error": "Failed to fetch review data"}


@app.route('/products/<int:product_id>')
def get_product_info(product_id):
    product = get_products(product_id)
    cart = get_carts(product_id)
    review = get_reviews(product_id)
    reviews_list = review.get("reviews", []) if "error" not in review else []

    return render_template(
        'product.html',
        product=product,
        cart=cart,
        reviews=reviews_list
    )


# Endpoint untuk menambah cart
@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    try:
        response = requests.post(f'http://{cart_service_host}:3002/cart/add/{product_id}')
        response.raise_for_status()
        data = response.json()
        return jsonify({"new_quantity": data.get("quantity", 0)})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e), "new_quantity": 0})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3005, debug=True)
