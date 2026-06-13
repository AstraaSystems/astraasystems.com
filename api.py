from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/estimate', methods=['POST'])
def estimate():
    data = request.json

    sqft = data.get("sqft", 12000)
    material = data.get("material", 1.1)
    labor = data.get("labor", 1.05)
    complexity = data.get("complexity", 0.8)

    base = sqft * 220 * (1 + (material-1)*0.3 + (labor-1)*0.25 + complexity*0.15)

    result = {
        "base_estimate": base,
        "low": base - 20000,
        "high": base + 20000,
        "confidence": 0.92,
        "risk": 0.3
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000)
