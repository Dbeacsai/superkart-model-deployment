
# ---------------------------------------------------------
# Import required libraries
# ---------------------------------------------------------

import os

import pandas as pd
import requests
import streamlit as st


# ---------------------------------------------------------
# Configure the Streamlit page
# ---------------------------------------------------------

st.set_page_config(
    page_title="SuperKart Sales Forecast",
    page_icon="🛒",
    layout="wide"
)


# ---------------------------------------------------------
# Define the Flask backend location
# ---------------------------------------------------------

# When both containers are running on the same Docker
# network, "backend" will be the hostname of the
# Flask backend container.

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://backend:7860"
)

SINGLE_PREDICTION_URL = (
    BACKEND_URL + "/v1/predict"
)

BATCH_PREDICTION_URL = (
    BACKEND_URL + "/v1/predictbatch"
)


# ---------------------------------------------------------
# Application title and description
# ---------------------------------------------------------

st.title(
    "SuperKart Sales Forecasting Application"
)

st.write(
    """
    This application uses the deployed SuperKart
    machine learning model to estimate
    Product Store Sales Total from product and
    store characteristics.
    """
)


# ---------------------------------------------------------
# Create two tabs:
# Single Prediction and Batch Prediction
# ---------------------------------------------------------

single_tab, batch_tab = st.tabs(
    [
        "Single Prediction",
        "Batch Prediction"
    ]
)


# =========================================================
# SINGLE PREDICTION
# =========================================================

with single_tab:

    st.subheader(
        "Predict Sales for One Product-Store Observation"
    )

    st.write(
        """
        Enter the product and store characteristics
        below and click **Predict Sales**.
        """
    )

    # -----------------------------------------------------
    # Create the input form
    # -----------------------------------------------------

    with st.form(
        "single_prediction_form"
    ):

        col1, col2 = st.columns(2)

        # -----------------------------
        # Left column
        # -----------------------------

        with col1:

            product_weight = st.number_input(
                "Product Weight",
                min_value=0.0,
                value=12.66,
                step=0.01
            )

            product_sugar_content = st.selectbox(
                "Product Sugar Content",
                [
                    "Low Sugar",
                    "Regular",
                    "No Sugar"
                ]
            )

            product_allocated_area = st.number_input(
                "Product Allocated Area",
                min_value=0.0,
                value=0.027,
                step=0.001,
                format="%.3f"
            )

            product_mrp = st.number_input(
                "Product MRP",
                min_value=0.0,
                value=117.08,
                step=0.01
            )

            store_size = st.selectbox(
                "Store Size",
                [
                    "Medium",
                    "High",
                    "Small"
                ]
            )

        # -----------------------------
        # Right column
        # -----------------------------

        with col2:

            store_city_type = st.selectbox(
                "Store Location City Type",
                [
                    "Tier 1",
                    "Tier 2",
                    "Tier 3"
                ],
                index=1
            )

            store_type = st.selectbox(
                "Store Type",
                [
                    "Departmental Store",
                    "Supermarket Type1",
                    "Supermarket Type2",
                    "Food Mart"
                ],
                index=2
            )

            product_id_char = st.selectbox(
                "Product ID Category",
                [
                    "FD",
                    "NC",
                    "DR"
                ]
            )

            store_age_years = st.number_input(
                "Store Age in Years",
                min_value=0,
                value=16,
                step=1
            )

            product_type_category = st.selectbox(
                "Product Type Category",
                [
                    "Perishables",
                    "Non Perishables"
                ],
                index=1
            )

        # Submit button
        predict_button = st.form_submit_button(
            "Predict Sales"
        )


    # -----------------------------------------------------
    # Send single prediction request to Flask
    # -----------------------------------------------------

    if predict_button:

        payload = {
            "Product_Weight":
                product_weight,

            "Product_Sugar_Content":
                product_sugar_content,

            "Product_Allocated_Area":
                product_allocated_area,

            "Product_MRP":
                product_mrp,

            "Store_Size":
                store_size,

            "Store_Location_City_Type":
                store_city_type,

            "Store_Type":
                store_type,

            "Product_Id_char":
                product_id_char,

            "Store_Age_Years":
                store_age_years,

            "Product_Type_Category":
                product_type_category
        }

        try:

            response = requests.post(
                SINGLE_PREDICTION_URL,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:

                prediction = response.json()[
                    "prediction"
                ]

                st.success(
                    "Prediction generated successfully."
                )

                st.metric(
                    "Predicted Product Store Sales Total",
                    f"{prediction:,.2f}"
                )

            else:

                st.error(
                    "Prediction request failed."
                )

                st.write(
                    response.json()
                )

        except requests.exceptions.RequestException as error:

            st.error(
                "Unable to connect to the Flask backend."
            )

            st.write(
                str(error)
            )


# =========================================================
# BATCH PREDICTION
# =========================================================

with batch_tab:

    st.subheader(
        "Batch Sales Prediction"
    )

    st.write(
        """
        Upload a CSV file containing the ten model
        input features. The application will send the
        file to the Flask batch-prediction endpoint.
        """
    )

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:

            # Read the uploaded file for preview
            batch_data = pd.read_csv(
                uploaded_file
            )

            st.write(
                "Uploaded Data Preview"
            )

            st.dataframe(
                batch_data.head()
            )

            # -------------------------------------------------
            # Send the CSV file to the Flask batch endpoint
            # -------------------------------------------------

            if st.button(
                "Generate Batch Predictions"
            ):

                batch_file = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "text/csv"
                    )
                }

                response = requests.post(
                    BATCH_PREDICTION_URL,
                    files=batch_file,
                    timeout=60
                )

                if response.status_code == 200:

                    prediction_dictionary = (
                        response.json()
                    )

                    predictions = [
                        prediction_dictionary[
                            str(index)
                        ]
                        for index
                        in range(
                            len(batch_data)
                        )
                    ]

                    results = batch_data.copy()

                    results[
                        "Predicted_Product_Store_Sales_Total"
                    ] = predictions

                    st.success(
                        "Batch predictions generated successfully."
                    )

                    st.dataframe(
                        results
                    )

                    # Allow the user to save the results
                    csv_output = results.to_csv(
                        index=False
                    ).encode(
                        "utf-8"
                    )

                    st.download_button(
                        label="Download Predictions",
                        data=csv_output,
                        file_name=(
                            "superkart_predictions.csv"
                        ),
                        mime="text/csv"
                    )

                else:

                    st.error(
                        "Batch prediction request failed."
                    )

                    st.write(
                        response.json()
                    )

        except Exception as error:

            st.error(
                "The uploaded CSV could not be processed."
            )

            st.write(
                str(error)
            )


# ---------------------------------------------------------
# Footer information
# ---------------------------------------------------------

st.caption(
    "SuperKart Machine Learning Sales Forecasting System"
)
