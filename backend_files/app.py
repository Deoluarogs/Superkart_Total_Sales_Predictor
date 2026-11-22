# Import libraries
import __main__
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify  # For creating the Flask API

# Define custom preprocessing function used in the saved pipeline
def standardize_store_age(data):
    data = data.copy()
    if 'Store_Age_Years' not in data.columns:
        if 'Store_Establishment_Year' in data.columns:
            data['Store_Age_Years'] = 2026 - data['Store_Establishment_Year']
        else:
            raise ValueError("Input must contain either 'Store_Establishment_Year' or 'Store_Age_Years'.")
    if 'Store_Establishment_Year' in data.columns:
        data = data.drop(columns=['Store_Establishment_Year'])
    return data

# Registering the function on __main__ so joblib can unpickle it under Gunicorn
__main__.standardize_store_age = standardize_store_age

# Initializing the Flask application
superkart_sales_predictor_api = Flask("Superkart Sales Predictor")

# Loading the trained machine learning model
model = joblib.load("superkart_model_v1.joblib")

# Defining a route for the home page (GET request)
@superkart_sales_predictor_api.get('/')
def home():
    return "Welcome to the Superkart Store Sales Total Prediction API!"

# Defining an endpoint for single property prediction (POST request)
@superkart_sales_predictor_api.post('/v1/superkart')
def predict_superkart_sales():

    # Getting the JSON data from the request body
    superkart_sales = request.get_json()

    # Extracting relevant features from the JSON data
    sample = {
        'Product_Weight': superkart_sales['Product_Weight'],
        'Product_Sugar_Content': superkart_sales['Product_Sugar_Content'],
        'Product_Allocated_Area': superkart_sales['Product_Allocated_Area'],
        'Product_Type': superkart_sales['Product_Type'],
        'Product_MRP': superkart_sales['Product_MRP'],
        'Store_Establishment_Year': superkart_sales['Store_Establishment_Year'],
        'Store_Size': superkart_sales['Store_Size'],
        'Store_Location_City_Type': superkart_sales['Store_Location_City_Type'],
        'Store_Type': superkart_sales['Store_Type']
    }

    # Converting the extracted data into a Pandas DataFrame
    input_data = pd.DataFrame([sample])

    # Make prediction
    predicted_sales = model.predict(input_data)[0]

    # Converting predicted_sales to Python float
    predicted_sales = round(float(predicted_sales), 2)

    # Return the actual price
    return jsonify({'Prediction': predicted_sales})


# Defining an endpoint for batch prediction (POST request)
@superkart_sales_predictor_api.post('/v1/superkartbatch')
def predict_superkart_sales_batch():

    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No CSV file uploaded."}), 400

    try:
        input_data = pd.read_csv(file)
    except Exception as e:
        return jsonify({"error": f"Invalid CSV file: {str(e)}"}), 400

    # Defining expected schema (accepting either Store_Establishment_Year or Store_Age_Years)
    base_cols = {col for col in model.feature_names_in_ if col != "Store_Age_Years"}
    age_cols = {"Store_Establishment_Year", "Store_Age_Years"}
    id_cols = {"Product_Id", "Store_Id"}
    actual_cols = set(input_data.columns)

    missing_cols = base_cols - actual_cols
    if not (age_cols & actual_cols):
        missing_cols.add("Store_Establishment_Year or Store_Age_Years")
    extra_cols = actual_cols - (base_cols | age_cols | id_cols)

    if missing_cols or extra_cols:
        return jsonify({
            "error": "Invalid input columns.",
            "missing_columns": list(missing_cols),
            "unexpected_columns": list(extra_cols)
        }), 400

    # Extracting IDs before selecting model features
    store_ids = input_data['Store_Id'].tolist() if 'Store_Id' in input_data.columns else list(range(len(input_data)))
    product_ids = input_data['Product_Id'].tolist() if 'Product_Id' in input_data.columns else None

    # Pass valid feature columns to the pipeline (which handles age conversion internally)
    feature_cols = list(base_cols | (age_cols & actual_cols))
    predicted_sales = [round(float(val), 2) for val in model.predict(input_data[feature_cols])]

    # Returning row-level predictions so duplicate Store_Ids do not overwrite each other
    if product_ids:
        results = [{"Product_Id": p, "Store_Id": s, "predicted_sales": pred} for p, s, pred in zip(product_ids, store_ids, predicted_sales)]
    else:
        results = [{"Store_Id": s, "predicted_sales": pred} for s, pred in zip(store_ids, predicted_sales)]

    return jsonify({"predictions": results}), 200


# Run the Flask application in debug mode if this script is executed directly
if __name__ == '__main__':
    superkart_sales_predictor_api.run(debug=True)
