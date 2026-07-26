# Union Bank Web Application

A modern, responsive banking web application built with Python (Flask), SQLite, HTML, CSS, and JavaScript.

## Features
- Secure User Authentication (Register/Login/Logout)
- Dashboard with charts and summary
- Cash Deposit and Withdrawal
- Fund Transfer between accounts
- Transaction History (with PDF download)
- Profile management
- Dark/Light Mode

## Prerequisites
- Python 3.8+

## How to Run the Application Locally

1. **Navigate to the project directory** (if not already there):
   ```bash
   cd C:\Users\MEENAKSHI\.gemini\antigravity\scratch\union-bank-app
   ```

2. **(Optional) Create a virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask application**:
   ```bash
   python app.py
   ```
   The SQLite database will be automatically created in the `database` folder upon the first run.

5. **Access the application**:
   Open your web browser and go to: `http://127.0.0.1:5000`

## Default Usage
- Register a new account to test out the application.
- You will be assigned a random 10-digit account number.
- Try depositing money, transferring to another registered user, and downloading your transaction statement as a PDF.
