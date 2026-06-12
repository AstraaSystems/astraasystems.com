from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/estimate', methods=['POST'])
def estimate():
    data = request.json

    sqft = float(data.get("sqft", 12000))
    material = float(data.get("material", 1.1))
    labor = float(data.get("labor", 1.05))
    complexity = float(data.get("complexity", 0.8))

    base = sqft * 220 * (1 + (material - 1)*0.3 + (labor - 1)*0.25 + complexity*0.15)

    return jsonify({
        "base_estimate": base,
        "low": base - 20000,
        "high": base + 20000,
        "confidence": 0.92,
        "risk": 0.30
    })

if __name__ == "__main__":
    app.run(port=5000)
