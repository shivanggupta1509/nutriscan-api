from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# ✅ Load your saved model and label encoder
model = joblib.load("nutrition_model.pkl")
encoder = joblib.load("label_encoder.pkl")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # ✅ Extract and structure the input features
    features = pd.DataFrame([{
        "energy-kcal_100g": data.get("energy", 0),
        "sugars_100g": data.get("sugar", 0),
        "fat_100g": data.get("fat", 0),
        "saturated-fat_100g": data.get("sat_fat", 0),
        "fiber_100g": data.get("fiber", 0),
        "proteins_100g": data.get("protein", 0),
        "salt_100g": data.get("salt", 0),
        "nova_group": data.get("nova", 0)
    }])

    # ✅ Make prediction
    prediction = model.predict(features)
    label = encoder.inverse_transform(prediction)[0]

    # ✅ Return result
    return jsonify({
        "prediction": label
    })

# ✅ Required for Render to run the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
