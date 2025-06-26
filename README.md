# RetailBot: A Sophisticated Chatbot for Online mMobile Shotp


This repository contains the source code for **MobiAssist**, a sophisticated, AI-powered chatbot designed to enhance customer interaction within an online mobile phone store retail environment. Built using the Rasa Open Source framework, this project demonstrates a comprehensive approach to chatbot development, from NLU data creation and dialogue management to backend integration and front-end user interface design.

This project was developed as part of the "Advanced Conversational UI Design and Chatbot Development" module.

## ✨ Features

- **Order Management:** Allows users to track status of their orders in real-time and cancel recent orders.
- **Complaint Handling:** Guides users through a step-by-step process to file a complaint, offering troubleshooting tips or escalating to a human agent.
- **Product Inquiry:** Provides information on product availability, pricing, and features.
- **Purchase Workflow:** Assists users in placing new orders directly through the chat interface.
- **Natural Conversation:** Handles greetings, goodbyes, and digressions gracefully.

## 🛠️ Tech Stack

- **Conversational AI:** Rasa Open Source 3.6 (NLU and Core)
- **Backend API:** Flask
- **Database:** SQLite3
- **Frontend UI:** Streamlit
- **Programming Language:** Python 3.10

---

## 🚀 Getting Started

Follow these instructions to set up and run the chatbot on your local machine.

### 1. Prerequisites

- Python 3.10
- Pip (Python package installer)
- A virtual environment tool (like `venv`) is highly recommended.

### 2. Setup and Installation

**Step 1: Clone the repository**
```bash
git clone https://github.com/negilbabu/retail_bot.git
cd retail-bot
```

**Step 2: Create and activate a virtual environment for each directory**
```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Step 3: Install all required dependencies**
A `requirements.txt` file is included with all the necessary Python packages.
```bash
pip install -r requirements.txt
```
*(Note: If you don't have a `requirements.txt` file, you can create one with `pip freeze > requirements.txt` after installing rasa, flask, and streamlit manually.)*

**Step 4: Train the Rasa model**
This command will train the NLU and dialogue models based on the data in the `data/`, `domain.yml`, and `config.yml` files.
```bash
rasa train
```
Initialize Database from Flask API/ 
```bash
python python sample_data_seed.py
```
### 3. How to Run the Chatbot

You need to run **four** separate services in **four** separate terminals from the project's root directory.

**Terminal 1: Run the Rasa Action Server**
This server runs your custom Python code (`actions/actions.py`).
```bash
rasa run actions
```

**Terminal 2: Run the Flask API Server**
This server connects to the database.
```bash
# Assuming your flask app file is named 'api.py'
python main.py
```

**Terminal 3: Run the Rasa Server**
This server handles the main NLU and dialogue logic.
```bash
rasa run --enable-api --cors "*"
```

**Terminal 4: Run the Streamlit Frontend**
This starts the user interface.
```bash
# Assuming your streamlit app file is named 'app.py'
streamlit run app.py
```

Once all four services are running, a new tab should open in your browser with the Streamlit chat interface, ready to go!

---

## 📁 Project Structure

Retail Chatbot/
├── Flask API/
│   ├── app/
│   │   ├── models.py
│   │   ├── extensions.py
│   │   ├── routes.py
│   │   ├── config.py
│   │   ├── __init__.py
│   │   ├── utils.py
│   ├── instance/
│   │   ├── app.db
│   ├── migrations/
│   ├── sample_data_seed.py
│   ├── main.py (runs Flask app)
│   ├── requirements.txt
│   ├── wsgi.py
|── .env 
├── rasa/
│   ├── domain.yml
│   ├── data/
│   │   └── nlu.yml / stories.yml / rules.yml
│   ├── actions/
│   │   └── actions.py
│   ├── config.yml
│   ├── endpoints.yml
│   ├── domain.yml
│   ├── requirements.txt
│   └── credentials.yml
│
├── ui/                          # Frontend 
│   ├── app.py
│   ├──requirements.txt    
│
├── .env                         # Environment variables
├── README.md
└── .gitignore   

- Required ports:

    - `5005` (Rasa)

    - `5055` (Rasa Actions)

    - `3000` (Reflex)

    - `8000` (Reflex backend)

