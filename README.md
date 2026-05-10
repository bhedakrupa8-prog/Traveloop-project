# Traveloop-project

Traveloop is a modern AI-powered travel planning platform that helps users create personalized multi-city itineraries, manage budgets, discover activities, organize packing checklists, and share travel experiences seamlessly. A premium, modern travel planning web application built with Flask and Bootstrap 5.

## Features
- **User Authentication**: Secure sign up, login, and session management.
- **Trip Management**: Create and manage multiple trips with dates and descriptions.
- **Itinerary Builder**: Add cities, dates, and build a visual timeline.
- **Budget Tracker**: Track estimated vs actual costs with interactive Chart.js visualizations.
- **Packing List**: Create categories and tick off items as you pack.
- **Premium UI**: Clean, minimal, and responsive interface resembling a startup MVP.

## Tech Stack
- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Migrate
- **Database**: MySQL (PyMySQL)
- **Frontend**: HTML5, CSS3, Bootstrap 5, Jinja2, Vanilla JS, Chart.js

## Setup Instructions

1. **Clone the repository / navigate to folder**
   ```bash
   cd traveloop
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Configuration**
   - Ensure MySQL is running on your local machine.
   - Create a database named `traveloop`:
     ```sql
     CREATE DATABASE traveloop;
     ```
   - Update the `DATABASE_URL` in your `.env` file if your MySQL credentials differ from `root:password`.

5. **Initialize Database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```

6. **Seed Sample Data (Optional)**
   ```bash
   python seed.py
   ```

7. **Run the Application**
   ```bash
   python run.py
   ```
   Open `http://localhost:5000` in your browser.
