# 🥗 Calorie & Meal Planning App

A Streamlit web application that helps users manage their nutrition through calorie calculation, food lookup, and meal planning.

## Features

### 1. Daily Calorie Needs Calculator
- Calculate your daily calorie requirements using the Mifflin-St Jeor equation
- Input your personal data (age, gender, weight, height)
- Choose your activity level
- Get instant results with scientific accuracy

### 2. Food Calorie Lookup
- Look up the calorie content of any food item
- Powered by the Edamam Nutrition API
- Real-time results with accurate portion sizes
- Simple and intuitive interface

### 3. Meal Plan Generator
- Generate personalized daily meal plans
- Set your calorie goals
- Choose dietary preferences (vegetarian, vegan, high-protein, etc.)
- Get balanced meal suggestions for breakfast, lunch, dinner, and snacks

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd calorie_planner
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up the Edamam API credentials:
   - Sign up for a free account at [Edamam Developer Portal](https://developer.edamam.com/)
   - Create a new application to get your API credentials
   - Create a `.env` file in the project root with your credentials:
```
EDAMAM_APP_ID=your_app_id
EDAMAM_APP_KEY=your_app_key
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. Use the different features:
   - Calculate your daily calorie needs in the "Calorie Calculator" tab
   - Look up food calories in the "Food Calorie Lookup" tab
   - Generate meal plans in the "Meal Planner" tab

## Project Structure

```
calorie_planner/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env                  # API credentials (create this)
├── utils/
│   ├── __init__.py
│   ├── calorie_calculator.py    # Calorie calculation logic
│   ├── nutrition_api.py         # Edamam API integration
│   └── meal_planner.py          # Meal planning logic
└── data/                        # Data directory
```

## Technical Details

- Built with Python 3.8+
- Uses Streamlit for the web interface
- Implements the Mifflin-St Jeor equation for BMR calculation
- Integrates with Edamam Nutrition API for food data
- Includes a sample meal database with various dietary options

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 