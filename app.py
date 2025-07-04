# app.py
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os

app = Flask(__name__)

# --- Model Loading ---
# Define paths for your model and encoder
MODEL_PATH = "nutrition_model.pkl"
ENCODER_PATH = "label_encoder.pkl"

model = None
encoder = None

# Load models when the application starts
# This ensures models are loaded only once, improving performance
# The app_context ensures Flask's context is available during startup if needed
with app.app_context():
    try:
        model = joblib.load(MODEL_PATH)
        encoder = joblib.load(ENCODER_PATH)
        print(f"Models loaded successfully from {MODEL_PATH} and {ENCODER_PATH}")
    except FileNotFoundError as e:
        print(f"Error: Model file not found. Ensure '{MODEL_PATH}' and '{ENCODER_PATH}' are in the same directory as app.py. Error: {e}")
        # In a production environment, you might want to exit or raise an error here
        # For now, we'll just print a warning.
    except Exception as e:
        print(f"An unexpected error occurred while loading models: {e}")

# --- Prediction Endpoint ---
@app.route('/predict', methods=['POST'])
def predict():
    # Check if models were loaded successfully
    if model is None or encoder is None:
        return jsonify({"error": "Model or encoder not loaded. Server might be misconfigured or files are missing."}), 500

    try:
        data = request.get_json()

        # Validate input data structure (basic check)
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid input format. Expected JSON object."}), 400

        # Extract and structure the input features
        # Ensure all expected keys are present, provide defaults if not
        features = pd.DataFrame([{
            "energy-kcal_100g": data.get("energy", 0.0), # Use 0.0 for float defaults
            "sugars_100g": data.get("sugar", 0.0),
            "fat_100g": data.get("fat", 0.0),
            "saturated-fat_100g": data.get("sat_fat", 0.0),
            "fiber_100g": data.get("fiber", 0.0),
            "proteins_100g": data.get("protein", 0.0),
            "salt_100g": data.get("salt", 0.0),
            "nova_group": data.get("nova", 0) # nova_group might be int
        }])

        # ✅ Make prediction
        prediction = model.predict(features)
        label = encoder.inverse_transform(prediction)[0]

        # ✅ Return result
        return jsonify({
            "prediction": label
        })

    except KeyError as e:
        # Specific error for missing keys in the JSON input
        return jsonify({"error": f"Missing data key in input: '{e}'. Please provide all required features (energy, sugar, fat, sat_fat, fiber, protein, salt, nova)."}), 400
    except Exception as e:
        # Catch any other unexpected errors during prediction
        print(f"Prediction error: {e}")
        return jsonify({"error": f"An unexpected error occurred during prediction: {str(e)}"}), 500

# ✅ Required for local testing (Gunicorn will handle this in production)
if __name__ == '__main__':
    # When running locally, Flask's development server will use this.
    # In Hugging Face Spaces, Gunicorn will be used to run the app.
    app.run(host='0.0.0.0', port=5000)
