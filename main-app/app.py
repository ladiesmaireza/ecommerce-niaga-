from flask import Flask, jsonify, render_template, request
import requests
import os
from functools import lru_cache

app = Flask(__name__)

# Detect local vs docker
if os.getenv("HOSTNAME") is None:
    product_service_host = "localhost"
    cart_service_host = "localhost"
    review_service_host = "localhost"
else:
    product_service_host = "product-service"
    cart_service_host = "cart-service"
    review_service_host = "review-service"


# @lru_cache(maxsize=128)
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
        response = requests.get(f'http://{cart_service_host}:3001/cart/{product_id}')
        response.raise_for_status()
        data = response.json()

        if 'data' not in data:
            print("Invalid data format:", data)
            return 0

        cart_data = data['data']

        total_quantity = 0

        # Jika data adalah dict tunggal
        if isinstance(cart_data, dict):
            if cart_data.get('product_id') == product_id:
                total_quantity = cart_data.get('quantity', 0)

        # Jika data adalah list
        elif isinstance(cart_data, list):
            for item in cart_data:
                if item.get('product_id') == product_id:
                    total_quantity += item.get('quantity', 0)

        print(f"Total quantity in cart for product_id {product_id}: {total_quantity}")
        return total_quantity

    except requests.exceptions.RequestException as e:
        print(f"Error fetching cart data: {e}")
        return 0


def get_reviews(product_id):
    try:
        response = requests.get(f'http://{review_service_host}:3003/reviews/{product_id}')
        response.raise_for_status()
        data = response.json()

        return data.get('data', {
            "reviews": [],
            "product": {}
        })

    except requests.exceptions.RequestException as e:
        print(f"Error fetching review data: {e}")
        return {"error": "Failed to fetch review data"}


@app.route('/products/<int:product_id>')
def get_product_info(product_id):
    product_data = get_products(product_id)
    cart = get_carts(product_id)
    review = get_reviews(product_id)

    combined_response = {
        "product": product_data if 'error' not in product_data else None,
        "cart": cart,
        "review": review.get("reviews") if "error" not in review else []
    }

    if request.args.get('format') == 'json':
        return jsonify({
            "data": combined_response,
            "message": "Product info fetched successfully"
        })

    return render_template('product.html', **combined_response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3005, debug=True)