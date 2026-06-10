from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import pickle

app = FastAPI(title="Sri Lankan Car Price Predictor API")

# Enable CORS so your Vercel frontend can talk to this Railway backend safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to hold our model and encoder
model = None
encoder = None

# Load machine learning files on startup
@app.on_event("startup")
def load_artifacts():
    global model, encoder
    try:
        with open('car_price_model.pkl', 'rb') as model_file:
            model = pickle.load(model_file)
        with open('target_encoder.pkl', 'rb') as encoder_file:
            encoder = pickle.load(encoder_file)
        print("🤖 ML Model and Encoder loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading pickle files: {str(e)}")

# Define the structured schema for incoming JSON data (Pydantic model)
class CarFeatures(BaseModel):
    brand: str
    model_name: str
    engine_cc: int
    mileage: int
    town: str
    car_age: int
    fuel_type: str
    gear_type: str

# Load index.html as the main page
@app.get("/", response_class=HTMLResponse)
def root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/predict")
def predict_price(car: CarFeatures):
    if model is None or encoder is None:
        raise HTTPException(status_code=500, detail="Model assets are not loaded properly on the server.")
        
    try:
        # 1. Structure the input JSON into training data format
        input_data = {
            'Brand': [car.brand],
            'Model': [car.model_name],
            'Engine (cc)': [car.engine_cc],
            'Millage(KM)': [car.mileage],
            'Town': [car.town],
            'Car_Age': [car.car_age],
            'Fuel Type_Hybrid': [1 if car.fuel_type.lower() == 'hybrid' else 0],
            'Fuel Type_Petrol': [1 if car.fuel_type.lower() == 'petrol' else 0],
            'Gear_Manual': [1 if car.gear_type.lower() == 'manual' else 0]
        }
        
        # 2. Convert to DataFrame
        df_input = pd.DataFrame(input_data)
        
        # 3. Transform using the Pre-trained Target Encoder
        df_input[['Brand', 'Model', 'Town']] = encoder.transform(df_input[['Brand', 'Model', 'Town']])
        
        # 4. Predict the price using Random Forest Model
        predicted_price = model.predict(df_input)[0]
        
        # 5. Return JSON Response to Frontend
        return {
            "status": "success",
            "predicted_price_lakhs": round(predicted_price, 2),
            "estimated_lkr": int(predicted_price * 100000)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed. Check inputs or spellings. Error: {str(e)}")
    
    # html load for first page
@app.get("/", response_class=HTMLResponse)
def root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# CSS and JS file Link
app.mount("/", StaticFiles(directory="."), name="static")
