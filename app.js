document.getElementById('predictionForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const resultContainer = document.getElementById('resultContainer');
    
    submitBtn.innerText = "Processing... ⏳";
    submitBtn.disabled = true;

    // Capture inputs
    const carData = {
        brand: document.getElementById('brand').value,
        model_name: document.getElementById('model_name').value,
        engine_cc: parseInt(document.getElementById('engine_cc').value),
        mileage: parseInt(document.getElementById('mileage').value),
        town: document.getElementById('town').value,
        car_age: parseInt(document.getElementById('car_age').value),
        fuel_type: document.getElementById('fuel_type').value,
        gear_type: document.getElementById('gear_type').value
    };

    // 🚨 සටහන: දැනට ලෝකල් මැෂින් එකේ ටෙස්ට් කරන්න http://127.0.0.1:8000/predict පාවිච්චි කරන්න.
    // Railway එකට දැම්මාට පස්සේ Railway URL එක මෙතනට දාන්න ඕනේ.
    const BACKEND_URL = "http://127.0.0.1:8000/predict"; 

    try {
        const response = await fetch(BACKEND_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(carData)
        });

        const result = await response.json();

        if (response.ok) {
            document.getElementById('priceLakhs').innerText = `LKR ${result.predicted_price_lakhs} Lakhs`;
            document.getElementById('priceLkr').innerText = `Approx: රු. ${result.estimated_lkr.toLocaleString()}`;
            resultContainer.classList.remove('hidden');
        } else {
            alert("Error: " + result.detail);
        }
    } catch (error) {
        console.error("Error connecting to API:", error);
        alert("Failed to connect to the Backend API. Make sure your FastAPI is running!");
    } finally {
        submitBtn.innerText = "🔮 Estimate Vehicle Price";
        submitBtn.disabled = false;
    }
});