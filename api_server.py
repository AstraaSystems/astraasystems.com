from flask import Flask, request, jsonify
from vsv_construction_ai import build_system

app = Flask(__name__)
# Initialize your ecosystem
arka, os_kernel = build_system()

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    try:
        # Pass the payload directly to Arka
        result = arka.evaluate_project(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    # This is the "Whole System" check we discussed
    return jsonify(os_kernel.snapshot()), 200

if __name__ == '__main__':
    # Ensure this port matches your ngrok configuration (8920)
    app.run(port=8920)
