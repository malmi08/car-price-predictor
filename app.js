document.getElementById('predictionForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const resultContainer = document.getElementById('resultContainer');
    
    // Change button text to processing and disable it to prevent multiple duplicate clicks
    submitBtn.innerText = "Processing..";
    submitBtn.disabled = true;

    // Correctly extract and format input data from the HTML form
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

    // URL endpoint of the locally running FastAPI backend server
    const BACKEND_URL = "/predict"; 

    try {
        // Send data to the Backend API via a POST Request
        const response = await fetch(BACKEND_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(carData)
        });

        const result = await response.json();

        if (response.ok && result.status === "success") {
            // Display the predicted prices from the backend inside the HTML elements
            document.getElementById('priceLakhs').innerText = `LKR ${result.predicted_price_lakhs} Lakhs`;
            document.getElementById('priceLkr').innerText = `Approx: LKR. ${result.estimated_lkr.toLocaleString()}`;
            
            // Make the result container visible by removing the hidden class
            resultContainer.classList.remove('hidden');
            
            // Smoothly scroll the screen down to focus on the displayed result
            resultContainer.scrollIntoView({ behavior: 'smooth' });
        } else {
            // Display an alert message if the backend returns a validation or validation error
            alert("Error from Server: " + (result.detail || "Prediction failed. Please check inputs."));
        }
    } catch (error) {
        // Log connection error and notify user if the server is offline
        console.error("Error connecting to API:", error);
        alert("Failed to connect to the Backend API. Make sure your FastAPI server is running locally (uvicorn main:app --reload)!");
    } finally {
        // Reset the button back to its initial state regardless of success or failure
        submitBtn.innerText = " Estimate Vehicle Price";
        submitBtn.disabled = false;
    }
});
