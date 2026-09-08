# AI-Driven Batch Process Dashboard

This is a full-stack ML application for predicting, explaining, and optimizing batch process parameters.

## Step-by-Step Instructions to Run the Program

### 1. Prerequisites
- Python 3.9+
- Node.js (v18 or higher) and npm

### 2. Setup the Backend (FastAPI + Machine Learning)
Open a terminal in the root of the project (`r:\mlprojectmini`).

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# 3. Install Python dependencies
pip install fastapi uvicorn scikit-learn xgboost shap optuna pandas numpy

# 4. Generate synthetic data
python backend/data_generator.py

# 5. Train the Machine Learning models
python backend/ml_pipeline.py

# 6. Start the FastAPI backend server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
The API will be available at `http://localhost:8000`. You can view the interactive documentation at `http://localhost:8000/docs`.

### 3. Setup the Frontend (React + Vite)
Open a **new separate terminal** in the `frontend` folder (`r:\mlprojectmini\frontend`).

```bash
# 1. Install Node.js dependencies
npm install

# 2. Start the React development server
npm run dev
```
The dashboard will open automatically in your browser, typically at `http://localhost:5173`.

---
**Note:** Make sure the backend server is running while you use the dashboard, as the frontend relies on the FastAPI endpoints (`/predict`, `/optimize`, `/anomaly`, `/explain`) to function.

#python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000