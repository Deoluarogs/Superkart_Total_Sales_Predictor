import requests
import streamlit as st
import pandas as pd

BACKEND_URL = "http://backend:7860"


st.title("Superkart Sales Predictor APP")

# Batch Prediction
st.subheader("Superkart Online Predictor")

# Input fields for customer data 
Product_Id = st.text_input("Product_Id", placeholder = 'AA9999')
Product_Weight = st.number_input("Product weight", min_value=1.00, max_value=100.00)
Product_Sugar_Content = st.selectbox("Product sugare content (Sugar content of the procuct)", ["No Sugar", "Low Sugar", "Regular"])
Product_Allocated_Area = st.number_input("Product_Allocated_Area (area allocated for product)", min_value=0.001, max_value=0.999)
Product_Type = st.selectbox("Product_Type (Product category type)", ["Frozen Foods", "Dairy", "Canned", "Baking Goods", "Health and Hygiene", "Snack Foods", "Meat", "Household", "Hard Drinks", "Fruits and Vegetables", "Breads", "Soft Drinks", "Breakfast", "Others", "Starchy Foods", "Seafood"])
Product_MRP = st.number_input("Prudcut MRP (maximum retail price of product)", min_value=1.00, max_value=1000.00)
Store_Id = st.text_input("Store ID", placeholder = 'AAA999')
Store_Establishment_Year = st.number_input("Store establishment year (year of store establishment)", min_value=1900, max_value=2026)
Store_Size = st.selectbox("Store size (size of the store)", ["Small", "Medium", "High"])
Store_Location_City_Type = st.selectbox("Store location city type", ["Tier 1", "Tier 2", "Tier 3"])
Store_Type = st.selectbox("Store type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])


store_data = {
    'Product_Weight': Product_Weight,
    'Product_Sugar_Content': Product_Sugar_Content,
    'Product_Allocated_Area': Product_Allocated_Area,
    'Product_Type': Product_Type,
    'Product_MRP': Product_MRP,
    'Store_Establishment_Year': Store_Establishment_Year,
    'Store_Size': Store_Size,
    'Store_Location_City_Type': Store_Location_City_Type,
    'Store_Type': Store_Type
}

if st.button("Predict", type='primary'):
    response = requests.post(f"{BACKEND_URL}/v1/superkart", json=store_data)
    if response.status_code == 200:
        result = response.json()
        sales_prediction = result["Prediction"]
        st.write(f"Based on the information provided, the store with ID {Store_Id} is likely to generate {sales_prediction} in sales.")
    else:
        st.error(f"Error in API request (Status {response.status_code}): {response.json()}")
#st.error("Error in API request")

# Batch Prediction
st.subheader("Batch Prediction")

file = st.file_uploader("Upload CSV file", type=["csv"])
if file is not None:
    if st.button("Predict for Batch", type='primary'):
        response = requests.post(f"{BACKEND_URL}/v1/superkartbatch", files={"file": file})  
        if response.status_code == 200:
            result = response.json()
            st.header("Batch Prediction Results")
            st.write(result)
        else:
            st.error(f"Error in API request (Status {response.status_code}): {response.json()}")         
