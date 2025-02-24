from flask import Flask, request, jsonify
from flask_cors import CORS
from predict import MedicalBot
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

print("Initializing bot...")
try:
    bot = MedicalBot()
    print("Bot initialized successfully")
except Exception as e:
    print(f"Error initializing bot: {str(e)}")
    print(traceback.format_exc())

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        print("Received request")
        data = request.json
        print(f"Request data: {data}")
        
        user_message = data['message']
        print(f"User message: {user_message}")
        
        response = bot.get_response(user_message)
        print(f"Bot response: {response}")
        
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error in predict: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Modificat pentru a asculta pe toate interfețele 