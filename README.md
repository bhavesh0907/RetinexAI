# 🚀 RetinexAI

### Automated Ophthalmic Disease Detection using Deep Learning

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)
![React](https://img.shields.io/badge/React-Admin--Dashboard-blue)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange)
![Deep Learning](https://img.shields.io/badge/CNN-ResNet50-important)
![Status](https://img.shields.io/badge/Status-Completed-success)

---

## 📌 Overview

RetinexAI is a full-stack AI system for automated retinal disease detection from fundus images. It integrates deep learning models with a scalable backend, interactive frontend, and database-driven analytics dashboard.

---

## 🎯 Objectives

* Automate retinal disease screening
* Compare CNN architectures (ResNet50, ResNet101, DenseNet121)
* Improve generalization under class imbalance
* Provide explainable AI outputs (Grad-CAM)
* Build a deployable full-stack system

---

## 🧠 Diseases Detected

* Diabetic Retinopathy
* Cataract
* Glaucoma
* Normal

---

## 🤖 Models Used

### ResNet50 (Best Model)

* Transfer learning (ImageNet pretrained)
* Fine-tuned on retinal dataset

**Performance:**

* Train Accuracy: 98.14%
* Validation Accuracy: 93.48%
* Test Accuracy: 94%

---

### ResNet101

* Deeper architecture
* Slight overfitting observed

**Performance:**

* Train: 98.23%
* Validation: 94.02%
* Test: 93%

---

### DenseNet121

* Dense connectivity improves feature reuse
* Better generalization but slightly lower accuracy

**Performance:**

* Train: 95.67%
* Validation: 94.41%
* Test: 93%

---

## 🔬 Training Configuration (CRITICAL)

* Input Size: **224 × 224 × 3**
* Batch Size: **32**
* Epochs: **25–30**
* Optimizer: **Adam**
* Learning Rate: **0.0001**
* Loss Function: **Categorical Crossentropy**
* Activation: **Softmax**
* Transfer Learning: Enabled

### Regularization Techniques

* Data Augmentation
* Early Stopping
* Dropout layers
* Class balancing (weighted loss / augmentation)

---

## 📊 Evaluation Metrics

* Accuracy
* Precision
* Recall
* F1-score
* Confusion Matrix
* Normalized Confusion Matrix

---

## 🧪 Key Observations

* Diabetic Retinopathy → highest detection accuracy
* Cataract → strong performance
* Glaucoma → lowest recall (challenging class)
* Model depth increase ≠ performance improvement

---

## 🧠 Explainability

* Grad-CAM used for visualization
* Highlights disease-relevant retinal regions
* Improves model interpretability

---

## ⚙️ Tech Stack

### Machine Learning

* TensorFlow / Keras
* OpenCV
* NumPy, Pandas
* Matplotlib

### Backend

* FastAPI
* Uvicorn
* SQLAlchemy
* Pydantic

### Frontend

* Streamlit (User App)
* React.js + Vite (Admin Dashboard)
* Axios

### Database

* MySQL

### Tools

* Git, GitHub
* Postman
* VS Code

---

## 🏗️ System Architecture

```text
User → Streamlit UI → FastAPI Backend → CNN Model  
                                      ↓  
                                 MySQL Database  
                                      ↓  
                           React Admin Dashboard
```

---

## 🔌 API Layer (Important)

### Core Endpoints

* `/predict` → image inference
* `/login` → authentication
* `/register` → user creation
* `/patients` → patient data
* `/reports` → report generation

---

## 🔄 Workflow

1. User registers / logs in
2. Uploads retinal image
3. Backend processes image
4. Model generates prediction
5. Confidence score computed
6. Grad-CAM visualization generated
7. Report created (PDF)
8. Data stored in database
9. Admin monitors via dashboard

---

## 🧪 ML Pipeline

1. Image preprocessing (resize, normalization)
2. CNN inference
3. Softmax classification
4. Confidence scoring
5. Grad-CAM visualization
6. Output generation

---

## 📸 Screenshots

(Add your images in `/assets`)

---

## 📂 Project Structure

```text
AI-RetinoCare/
├── backend/
├── admin-frontend/
├── app.py
├── requirements.txt
└── README.md
```

---

## 📦 Dataset

👉 https://www.kaggle.com/datasets/gunavenkatdoddi/eye-diseases-classification

* Multi-class retinal dataset
* Classes: DR, Cataract, Glaucoma, Normal

### Preprocessing

* Resizing
* Normalization
* Augmentation (flip, rotate, zoom, brightness)

⚠️ Not included in repo

---

## 📦 Model Weights

[(Add Drive link)](https://drive.google.com/file/d/1h7B6wTA5ptoCNq6PUtQJp7ZtidYmUqZp/view?usp=share_link)

---

## ⚡ Installation

```bash
git clone https://github.com/bhavesh0907/RetinexAI.git
cd RetinexAI
```

---

## 🔧 Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

---

## ▶️ Run Backend

```bash
cd backend
uvicorn app.backend_main:app --reload
```

---

## ▶️ Run Frontend

```bash
streamlit run app.py
```

---

## ▶️ Run Admin Dashboard

```bash
cd admin-frontend
npm install
npm run dev
```

---

## 🗄️ Database Setup

```sql
CREATE DATABASE retinex_ai;
```

---

## ⚠️ Limitations

* Dataset size limitations
* Glaucoma detection difficulty
* No clinical validation

---

## 🚀 Future Work

* Vision Transformers
* Ensemble learning
* Larger dataset
* Cloud deployment

---

## 👨‍💻 Contributors

* Bhavesh Mishra
* Yugam Shah

---

## 🏁 Conclusion

RetinexAI demonstrates a complete AI-driven healthcare pipeline combining deep learning with scalable system design.

---
