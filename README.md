# RetinexAI

**Automated Ophthalmic Disease Detection using Deep Learning**

---

## Project Description

RetinexAI is a full-stack AI system that performs automated retinal disease screening from fundus images. The system leverages convolutional neural networks to classify multiple ophthalmic conditions and provides explainable predictions, structured reports, and an administrative analytics dashboard.

This project focuses on **model performance comparison, generalization behavior, and real-world system integration**, rather than only model training.

---

## Problem Statement

Manual retinal screening is:

* Time-consuming
* Dependent on expert availability
* Prone to variability

This system aims to:

* Automate disease detection
* Assist early diagnosis
* Provide consistent predictions

---

## Diseases Detected

* Diabetic Retinopathy
* Cataract
* Glaucoma
* Normal

---

## Models Used (Core Contribution)

### 1. ResNet50 (Primary Model)

* Transfer learning (ImageNet pretrained)
* Fine-tuned on retinal dataset
* Best performing model

**Performance:**

* Train Accuracy: 98.14%
* Validation Accuracy: 93.48%
* Test Accuracy: 94%

---

### 2. ResNet101

* Deeper architecture
* Higher capacity but slight overfitting

**Performance:**

* Train: 98.23%
* Validation: 94.02%
* Test: 93%

---

### 3. DenseNet121

* Dense connectivity for feature reuse
* Better generalization but lower peak accuracy

**Performance:**

* Train: 95.67%
* Validation: 94.41%
* Test: 93%

---

## Key Technical Insight

Increasing model depth **did NOT improve performance**.
ResNet50 achieved the best balance between:

* Accuracy
* Stability
* Generalization

---

## Explainability (Critical Feature)

* Grad-CAM used for visualization
* Highlights disease-relevant regions
* Improves interpretability of predictions

---

## Tech Stack (Complete)

### Machine Learning

* Python
* TensorFlow / Keras
* OpenCV
* NumPy, Pandas
* Matplotlib

### Deep Learning Concepts

* Transfer Learning
* Fine-Tuning
* Class Imbalance Handling
* Data Augmentation
* Feature Extraction

---

### Backend

* FastAPI
* Uvicorn
* SQLAlchemy
* Pydantic

---

### Frontend

* Streamlit (User App)
* React.js + Vite (Admin Dashboard)
* Axios (API communication)

---

### Database

* MySQL
* Relational schema (users, patients, screenings, sessions)

---

### Dev & Tools

* Git & GitHub
* VS Code
* Postman
* npm

---

## System Architecture

```text
User → Streamlit UI → FastAPI Backend → CNN Model  
                                      ↓  
                                 MySQL DB  
                                      ↓  
                           React Admin Dashboard
```

---

## Functional Modules

### 1. User Application

* Login / Registration
* Patient data input
* Image upload
* Real-time prediction
* Confidence score display
* Grad-CAM visualization
* Report generation

---

### 2. Backend Services

* Authentication APIs
* Screening APIs
* Model inference pipeline
* Report generation logic
* Database integration

---

### 3. Admin Dashboard

* Patient management
* Screening records
* Analytics & charts
* User management
* Session tracking

---

## ML Pipeline

1. Image Preprocessing

   * Resize
   * Normalization

2. Model Input

   * Tensor conversion

3. Prediction

   * Softmax classification

4. Post-processing

   * Confidence scoring
   * Risk categorization

5. Explainability

   * Grad-CAM heatmap

6. Output

   * UI display + Report

---

## Dataset

* Retinal fundus image dataset
* Multi-class classification

⚠️ Not included in repo (size constraint)

(Add dataset link here)

---

## Model Weights

(Add Drive link here)

Place inside:

```bash
models/
```

---

## Installation

```bash
git clone https://github.com/bhavesh0907/RetinexAI.git
cd RetinexAI
```

---

## Setup Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

---

## Run Backend

```bash
cd backend
uvicorn app.backend_main:app --reload
```

---

## Run Frontend (User App)

```bash
streamlit run app.py
```

---

## Run Admin Dashboard

```bash
cd admin-frontend
npm install
npm run dev
```

---

## Database Setup

```sql
CREATE DATABASE retinex_ai;
```

Update config in backend.

---

## Results Summary

| Metric         | Best Model  |
| -------------- | ----------- |
| Accuracy       | ResNet50    |
| Generalization | DenseNet121 |
| Stability      | ResNet50    |

---

## Observations

* Diabetic Retinopathy → easiest to detect
* Cataract → high accuracy
* Glaucoma → hardest (low recall)
* Normal → moderate confusion

---

## Limitations

* Limited dataset size
* Glaucoma detection complexity
* No clinical deployment validation

---

## Future Enhancements

* Vision Transformers
* Ensemble learning
* Larger dataset
* Cloud deployment
* Real-time hospital integration

---

## Contributors

* Bhavesh Mishra
* Yugam Shah
* Akshat Mittal
* Ritvik Rajvanshi

---

## Important Notes

* Do NOT upload datasets/models
* Use external storage (Drive/Kaggle)
* Use requirements.txt for setup

---

## Conclusion

RetinexAI demonstrates that optimized CNN architectures combined with proper system design can deliver reliable and scalable solutions for automated retinal disease detection.

---
