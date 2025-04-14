

Bazaar Inventory - Stage 1 (Single Store Inventory System)

This is a basic inventory management system built using Flask and SQLite. It allows a single retail store to manage its product inventory through a simple web interface.

Requirements:

- Python 3.7 or above
- pip (Python package manager)

Steps to Run:

1. Download or clone the project to your computer.

2. Open a terminal or command prompt and navigate to the project folder.

3. (Optional) Create a virtual environment:
   - python -m venv venv
   - For Windows: venv\Scripts\activate
   - For Mac/Linux: source venv/bin/activate

4. Install required Python packages:
   - pip install flask

5. (Optional) Add your logo image:
   - Place your logo file (e.g., logo.png) in a folder called "static" inside the project directory.

6. Run the application:
   - python app.py

7. Open your browser and go to:
   - http://127.0.0.1:5000

Project Structure:

- app.py: Main application file
- inventory_stage1.db: Local database (created automatically)
- templates/: Contains HTML pages
- static/: Contains logo or static files

Functionality:

- Add new products
- View all products and current stock
- Stock in items
- Record sales
- Remove damaged or expired items

This version is designed for local use only (Stage 1). No user authentication is included. Future versions will include proper storage, multi-store support, and advanced analytics.