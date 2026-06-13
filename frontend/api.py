from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# ✅ ESTIMATOR ENDPOINT
@app.route('/estimate', methods=['POST'])
def estimate():
    data = request.json

    sqft = data.get("sqft", 10000)
    material = data.get("material", 1.1)
    labor = data.get("labor", 1.05)
    complexity = data.get("complexity", 0.8)

    base = sqft * 400  # base cost model

    estimate_value = base * material * labor * complexity

    return jsonify({
        "base_estimate": estimate_value,
        "confidence": 0.92
    })


# ✅ PAYMENT (MONERIS SIMULATION)
@app.route('/pay', methods=['POST'])
def pay():
    return jsonify({
        "status": "success",
        "message": "Payment endpoint ready"
    })


# ✅ HEALTH CHECK (important for debugging)
@app.route('/', methods=['GET'])
def home():
    return "Astraa API is running"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
