
# Import libraries required by the Flask backend
import os

import joblib
import pandas as pd

from flask import Flask, jsonify, request


# ---------------------------------------------------------
# Create the Flask application
# ---------------------------------------------------------

superkart_api = Flask(__name__)


# ---------------------------------------------------------
# Load the serialized machine learning pipeline
# ---------------------------------------------------------

# Identify the folder containing this app.py file
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# Build the path to the serialized model
MODEL_PATH = os.path.join(
    BASE_DIR,
    "superkart_model.joblib"
)

# Load the complete preprocessing + model pipeline
model = joblib.load(MODEL_PATH)


# ---------------------------------------------------------
# Define the exact input features expected by the model
# ---------------------------------------------------------

EXPECTED_FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# ---------------------------------------------------------
# Health-check route
# ---------------------------------------------------------

@superkart_api.get("/")
def health_check():
    """
    Simple route used to confirm that the Flask API is running.
    """

    return jsonify(
        {
            "status": "ok",
            "service": "SuperKart Prediction API"
        }
    )


# ---------------------------------------------------------
# Single prediction endpoint
# ---------------------------------------------------------

@superkart_api.post("/v1/predict")
def predict():
    """
    Accept one observation as JSON and return one
    predicted Product_Store_Sales_Total value.
    """

    try:

        # Read the JSON sent by the client
        payload = request.get_json(
            silent=True
        )

        # Make sure JSON data was provided
        if not isinstance(payload, dict):

            return jsonify(
                {
                    "error":
                    "A JSON object containing the model features is required."
                }
            ), 400

        # Check whether any required features are missing
        missing_features = [
            feature
            for feature in EXPECTED_FEATURES
            if feature not in payload
        ]

        if missing_features:

            return jsonify(
                {
                    "error": "Missing required features.",
                    "missing_features": missing_features
                }
            ), 400

        # Convert the single JSON record into a DataFrame
        input_data = pd.DataFrame(
            [payload]
        )

        # Keep the model features in the expected order
        input_data = input_data[
            EXPECTED_FEATURES
        ]

        # Generate the sales prediction
        prediction = model.predict(
            input_data
        )[0]

        # Return the prediction as JSON
        return jsonify(
            {
                "prediction": float(prediction)
            }
        )

    except Exception as error:

        return jsonify(
            {
                "error":
                "The prediction request could not be processed."
            }
        ), 500


# ---------------------------------------------------------
# Batch prediction endpoint
# ---------------------------------------------------------

@superkart_api.post("/v1/predictbatch")
def predict_batch():
    """
    Accept a CSV file containing multiple observations
    and return one prediction for every row.
    """

    try:

        # Check that the request contains a file
        if "file" not in request.files:

            return jsonify(
                {
                    "error":
                    "A CSV file must be supplied using the 'file' field."
                }
            ), 400

        # Get the uploaded CSV file
        uploaded_file = request.files[
            "file"
        ]

        # Read the CSV into a Pandas DataFrame
        batch_data = pd.read_csv(
            uploaded_file
        )

        # Check for missing required model features
        missing_features = [
            feature
            for feature in EXPECTED_FEATURES
            if feature not in batch_data.columns
        ]

        if missing_features:

            return jsonify(
                {
                    "error": "Missing required features.",
                    "missing_features": missing_features
                }
            ), 400

        # Keep only the expected model features
        batch_data = batch_data[
            EXPECTED_FEATURES
        ]

        # Generate predictions for all rows
        predictions = model.predict(
            batch_data
        )

        # Return predictions as:
        # {"0": prediction, "1": prediction, ...}
        prediction_results = {
            str(index): float(prediction)
            for index, prediction
            in enumerate(predictions)
        }

        return jsonify(
            prediction_results
        )

    except Exception as error:

        return jsonify(
            {
                "error":
                "The batch prediction request could not be processed."
            }
        ), 500


# ---------------------------------------------------------
# Development server
# ---------------------------------------------------------

if __name__ == "__main__":

    superkart_api.run(
        host="0.0.0.0",
        port=7860
    )
