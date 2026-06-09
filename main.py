import os
import urllib.request
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import pickle

app = FastAPI()

# Enable CORS so Frontend can talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Drive Direct Download Links
MODEL_URL = "https://docs.google.com/uc?export=download&id=1fQlUaIG9PKujWzAvton1ZC7Q7X0k5JQ7"
ENCODER_URL = "https://docs.google.com/uc?export=download&id=1yQWYN51Pe95eJalPKxlWBDmjiJTOpZhV"

MODEL_PATH = "car_price_model.pkl"
ENCODER_PATH = "target_encoder.pkl"

# Function to download files from Google Drive if they don't exist
def download_file(url, path):
    if not os.path.exists(path):
        print(f"Downloading {path} from Google Drive...")
        urllib.request.urlretrieve(url, path)
        print(f"{path} downloaded successfully!")

# Download models before starting the API
download_file(MODEL_URL, MODEL_PATH)
download_file(ENCODER_URL, ENCODER_PATH)

# Load the trained Model and Target Encoder
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(ENCODER_PATH, "rb") as f:
    target_encoder = pickle.load(f)

# Define Input Data Format
class CarInput(BaseModel):
    brand: str
    model_name: str
    engine_cc: float
    mileage: float
    town: str
    car_age: float
    fuel_type: str
    gear_type: str

@app.get("/")
def home():
    return {"message": "Sri Lankan Car Price Predictor API is running!"}

@app.post("/predict")
def predict_price(data: CarInput):
    try:
        # Convert input data to Dictionary
        input_dict = data.dict()
        df = pd.DataFrame([input_dict])

        # Target Encode Categorical Columns
        categorical_cols = ['brand', 'model_name', 'town', 'fuel_type', 'gear_type']
        df[categorical_cols] = target_encoder.transform(df[categorical_cols])

        # Make Prediction (Model outputs price in Lakhs)
        predicted_lakhs = model.predict(df)[0]
        
        # Convert Lakhs to Full LKR Price (1 Lakh = 100,000 LKR)
        predicted_lkr = predicted_lakhs * 100000

        return {
            "status": "success",
            "price_lakhs": f"Rs. {round(predicted_lakhs, 2)} Lakhs",
            "price_lkr": f"Rs. {int(predicted_lkr):,}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))