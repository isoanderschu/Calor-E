"""
Nutrition API Handler

This module provides an interface to the USDA FoodData Central API for retrieving
nutritional information about foods. It handles:
1. Food searches
2. Detailed nutrition data retrieval
3. Unit conversions
4. Data formatting for display

The API requires a USDA API key to be set in the .env file.
"""

import os
import requests
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file
load_dotenv()

class NutritionAPI:
    """
    A class to handle interactions with the USDA FoodData Central API.
    
    This class provides methods for:
    - Searching foods
    - Getting detailed nutrition information
    - Converting between different units
    - Formatting nutrition data for display
    """
    
    def __init__(self):
        """
        Initialize the NutritionAPI with API key and base URL.
        
        Raises:
            ValueError: If the USDA API key is not set in the environment variables.
        """
        # Get API key from environment variables
        self.api_key = os.getenv('USDA_API_KEY')
        if not self.api_key:
            raise ValueError("USDA API key not found. Please set USDA_API_KEY in your .env file.")
        
        # Base URL for the USDA FoodData Central API
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
        
        # Define nutrient IDs for common nutrients
        self.NUTRIENT_IDS = {
            'energy': 1008,  # Energy (kcal)
            'protein': 1003,  # Protein (g)
            'fat': 1004,     # Total lipid (fat) (g)
            'carbs': 1005,   # Carbohydrate, by difference (g)
            'fiber': 1079,   # Fiber, total dietary (g)
            'sugar': 2000,   # Sugars, Total (g)
            'sodium': 1093,  # Sodium, Na (mg)
            'calcium': 1087, # Calcium, Ca (mg)
            'iron': 1089,    # Iron, Fe (mg)
            'vitamin_a': 1106, # Vitamin A, IU
            'vitamin_c': 1162, # Vitamin C, total ascorbic acid (mg)
            'vitamin_d': 1114, # Vitamin D (D2 + D3) (µg)
            'vitamin_e': 1158, # Vitamin E (alpha-tocopherol) (mg)
            'vitamin_k': 1185, # Vitamin K (phylloquinone) (µg)
            'vitamin_b6': 1175, # Vitamin B-6 (mg)
            'vitamin_b12': 1178, # Vitamin B-12 (µg)
            'folate': 1177,  # Folate, total (µg)
            'magnesium': 1090, # Magnesium, Mg (mg)
            'zinc': 1095,    # Zinc, Zn (mg)
            'potassium': 1092, # Potassium, K (mg)
            'water': 1051,   # Water (g)
            'alcohol': 1018, # Alcohol, ethyl (g)
            'caffeine': 1057, # Caffeine (mg)
            'cholesterol': 1253, # Cholesterol (mg)
            'saturated_fat': 1258, # Fatty acids, total saturated (g)
            'monounsaturated_fat': 1292, # Fatty acids, total monounsaturated (g)
            'polyunsaturated_fat': 1293, # Fatty acids, total polyunsaturated (g)
            'trans_fat': 1257, # Fatty acids, total trans (g)
        }
        
        # Define unit conversion factors (to grams)
        self.UNIT_CONVERSIONS = {
            "g": 1.0,        # 1 gram = 1 gram
            "oz": 28.35,     # 1 ounce = 28.35 grams
            "ml": 1.0,       # 1 ml = 1 gram (for water-based liquids)
            "fl_oz": 29.57   # 1 fluid ounce = 29.57 grams (for water-based liquids)
        }
    
    def search_foods(self, query, page_size=10):
        """
        Search for foods in the USDA database.
        
        Args:
            query (str): The food to search for
            page_size (int): Number of results to return (default: 10)
            
        Returns:
            dict: Search results from the API
            
        Raises:
            Exception: If the API request fails
        """
        # Construct the search URL
        url = f"{self.base_url}/foods/search"
        
        # Set up the search parameters
        params = {
            'api_key': self.api_key,
            'query': query,
            'pageSize': page_size,
            'dataType': ['Foundation', 'SR Legacy', 'Survey (FNDDS)']
        }
        
        try:
            # Make the API request
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error searching foods: {str(e)}")
    
    def get_food_details(self, fdc_id):
        """
        Get detailed nutrition information for a specific food.
        
        Args:
            fdc_id (int): The FoodData Central ID of the food
            
        Returns:
            dict: Detailed food information from the API
            
        Raises:
            Exception: If the API request fails
        """
        # Construct the details URL
        url = f"{self.base_url}/food/{fdc_id}"
        
        # Set up the request parameters
        params = {
            'api_key': self.api_key
        }
        
        try:
            # Make the API request
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error getting food details: {str(e)}")
    
    def convert_to_grams(self, amount, unit):
        """
        Convert a measurement to grams.
        
        Args:
            amount (float): The amount to convert
            unit (str): The unit of measurement ('g', 'oz', 'ml', or 'fl_oz')
            
        Returns:
            float: The converted amount in grams
            
        Raises:
            ValueError: If the unit is not supported
        """
        # Check if the unit is supported
        if unit not in self.UNIT_CONVERSIONS:
            raise ValueError(f"Unsupported unit: {unit}. Supported units are: {', '.join(self.UNIT_CONVERSIONS.keys())}")
        
        # Convert the amount to grams
        return amount * self.UNIT_CONVERSIONS[unit]
    
    def get_nutrition_data(self, food_data, amount_g):
        """
        Extract and format nutrition data from food details.
        
        Args:
            food_data (dict): The food details from the API
            amount_g (float): The amount in grams
            
        Returns:
            tuple: (success, data) where data is either the nutrition data or an error message
        """
        try:
            # Initialize nutrition data dictionary
            nutrition_data = {}
            
            # Extract nutrients from the food data
            for nutrient in food_data.get('foodNutrients', []):
                nutrient_id = nutrient.get('nutrient', {}).get('id')
                if nutrient_id in self.NUTRIENT_IDS.values():
                    # Get the nutrient name and amount
                    name = nutrient.get('nutrient', {}).get('name')
                    amount = nutrient.get('amount', 0)
                    
                    # Calculate the amount for the given quantity
                    adjusted_amount = (amount * amount_g) / 100
                    
                    # Store the nutrient data
                    nutrition_data[name] = {
                        'amount': adjusted_amount,
                        'unit': nutrient.get('nutrient', {}).get('unitName', 'g')
                    }
            
            return True, nutrition_data
        except Exception as e:
            return False, str(e)
    
    def create_nutrient_tables(self, food_data, amount_g):
        """
        Create formatted tables for displaying nutrition information.
        
        Args:
            food_data (dict): The food details from the API
            amount_g (float): The amount in grams
            
        Returns:
            tuple: (main_nutrients_df, additional_nutrients_df, pie_data)
        """
        # Get the nutrition data
        success, nutrition_data = self.get_nutrition_data(food_data, amount_g)
        
        if not success:
            raise ValueError(nutrition_data)
        
        # Define main nutrients to display
        main_nutrients = [
            'Energy',
            'Protein',
            'Total lipid (fat)',
            'Carbohydrate, by difference',
            'Fiber, total dietary',
            'Sugars, Total',
            'Water'
        ]
        
        # Create main nutrients table
        main_data = []
        for nutrient in main_nutrients:
            if nutrient in nutrition_data:
                data = nutrition_data[nutrient]
                main_data.append({
                    'Nutrient': nutrient,
                    'Amount': f"{data['amount']:.1f} {data['unit']}",
                    'Amount per 100g': f"{data['amount'] * 100 / amount_g:.1f} {data['unit']}"
                })
        
        # Create additional nutrients table
        additional_data = []
        for nutrient, data in nutrition_data.items():
            if nutrient not in main_nutrients:
                additional_data.append({
                    'Nutrient': nutrient,
                    'Amount': f"{data['amount']:.1f} {data['unit']}",
                    'Amount per 100g': f"{data['amount'] * 100 / amount_g:.1f} {data['unit']}"
                })
        
        # Create data for pie chart
        pie_data = []
        for nutrient in ['Protein', 'Total lipid (fat)', 'Carbohydrate, by difference']:
            if nutrient in nutrition_data:
                data = nutrition_data[nutrient]
                pie_data.append({
                    'Nutrient': nutrient,
                    'Amount per 100g': data['amount'] * 100 / amount_g
                })
        
        # Convert to DataFrames
        main_df = pd.DataFrame(main_data)
        additional_df = pd.DataFrame(additional_data)
        
        return main_df, additional_df, pie_data 
        