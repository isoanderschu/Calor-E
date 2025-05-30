"""
Meal Planner Module

This module provides functionality for generating personalized meal plans using
the Spoonacular API. It includes:
1. Meal plan generation based on calorie goals and dietary preferences
2. Dietary restriction handling
3. Allergy management
4. Macro distribution calculations

The module uses the Spoonacular API to:
- Generate meal plans based on calorie targets and macro distributions
- Get detailed nutrition information for recipes
- Handle dietary restrictions and allergies
- Calculate and validate macro distributions

Key Features:
- Dynamic meal distribution across breakfast, lunch, and dinner
- Automatic nutrition calculation and macro distribution
- Support for various dietary restrictions and allergies
- Error handling for API limitations and rate limits
"""

import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MealPlanner:
    """
    A class to handle meal planning using the Spoonacular API.
    
    This class provides methods for:
    - Generating personalized meal plans
    - Managing dietary restrictions
    - Handling allergies
    - Calculating macro distributions
    
    The class uses the Spoonacular API to generate meal plans that match:
    - Daily calorie targets
    - Macro distribution goals (protein, fat, carbs)
    - Dietary restrictions
    - Allergy considerations
    
    Attributes:
        api_key (str): The Spoonacular API key loaded from environment variables
        BASE_URL (str): Base URL for the meal planner API endpoint
        RECIPE_NUTRITION_URL (str): URL template for getting recipe nutrition info
        IMAGE_BASE_URL (str): Base URL for recipe images
    """
    
    # Base URLs for different Spoonacular API endpoints
    BASE_URL = "https://api.spoonacular.com/mealplanner/generate"
    RECIPE_NUTRITION_URL = "https://api.spoonacular.com/recipes/{id}/nutritionWidget.json"
    IMAGE_BASE_URL = "https://spoonacular.com/recipeImages/"
    
    def __init__(self):
        """
        Initialize the MealPlanner with API credentials.
        
        Loads the Spoonacular API key from environment variables and sets up
        the base URLs for API endpoints.
        
        Raises:
            ValueError: If the Spoonacular API key is not set in the environment variables.
        """
        self.api_key = os.getenv('SPOONACULAR_API_KEY')
        if not self.api_key:
            raise ValueError("Spoonacular API key not found. Please set SPOONACULAR_API_KEY in your .env file.")
    
    def get_recipe_nutrition(self, recipe_id: int) -> Dict:
        """
        Get detailed nutrition information for a specific recipe.
        
        This method fetches nutrition data for a specific recipe from the Spoonacular API,
        including calories, macronutrients, and other nutritional information.
        
        Args:
            recipe_id: The Spoonacular recipe ID to get nutrition info for
            
        Returns:
            Dict containing nutrition information including:
            - Calories
            - Macronutrients (protein, fat, carbs)
            - Other nutritional information
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        url = self.RECIPE_NUTRITION_URL.format(id=recipe_id)
        params = {
            "apiKey": self.api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def generate_meal_plan(
        self,
        target_calories: int,
        diet: Optional[str] = None,
        exclude: Optional[str] = None,
        time_frame: str = "day"
    ) -> Dict[str, Any]:
        """
        Generate a meal plan using the Spoonacular API.
        
        This method creates a personalized meal plan based on the user's calorie goals,
        dietary restrictions, and allergies. It handles API rate limits and errors
        gracefully, providing clear error messages for common issues.
        
        Args:
            target_calories: Target daily calorie intake
            diet: Optional dietary restrictions (e.g., "vegetarian", "vegan")
            exclude: Optional ingredients to exclude (e.g., "shellfish", "nuts")
            time_frame: Time frame for the meal plan ("day" or "week")
            
        Returns:
            Dict containing the generated meal plan with:
            - List of meals with their details
            - Total daily nutrition information
            - Macro distribution
            
        Raises:
            ValueError: If the API request fails or returns invalid data
            requests.exceptions.RequestException: If there's an error with the API request
        """
        # Set up API request parameters
        params = {
            "apiKey": self.api_key,
            "timeFrame": time_frame,
            "targetCalories": target_calories,
            "number": 3,  # Get three meals
            "addRecipeInformation": True
        }
        
        # Add optional parameters if provided
        if diet:
            params["diet"] = diet
        if exclude:
            params["exclude"] = exclude
        
        try:
            # Make API request
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            # Process response
            data = response.json()
            if not data.get("meals"):
                raise ValueError("Could not generate a meal plan with the given constraints")
            
            return self._process_meal_plan(data)
            
        except requests.exceptions.HTTPError as e:
            # Handle specific API errors
            if e.response.status_code == 402:
                raise ValueError("API quota exceeded. Please try again later or upgrade your plan.")
            elif e.response.status_code == 401:
                raise ValueError("Invalid API key. Please check your Spoonacular API key.")
            elif e.response.status_code == 429:
                raise ValueError("API rate limit exceeded. Please wait a few minutes before trying again.")
            else:
                raise ValueError(f"API request failed with status code {e.response.status_code}: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error making API request: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error generating meal plan: {str(e)}")
    
    def _process_meal_plan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the raw API response into a structured meal plan.
        
        This method takes the raw API response and organizes it into a structured
        meal plan with proper meal types (Breakfast, Lunch, Dinner), calculates
        total nutrition information, and formats the data for display.
        
        Args:
            data: Raw API response data containing meal information
            
        Returns:
            Dict containing the processed meal plan with:
            - Organized meals by type
            - Combined nutrition information
            - Total daily macros and calories
        """
        # Get meals from response
        meals = data.get("meals", [])
        
        # Initialize meal type containers
        meal_types = {
            "Breakfast": [],
            "Lunch": [],
            "Dinner": []
        }
        
        # Distribute meals across types
        for i, meal in enumerate(meals):
            meal_type = list(meal_types.keys())[i % len(meal_types)]
            meal_types[meal_type].append(meal)
        
        # Initialize tracking variables
        processed_meals = []
        total_daily_calories = 0
        total_daily_protein = 0
        total_daily_fat = 0
        total_daily_carbs = 0
        
        # Process each meal type
        for meal_type, type_meals in meal_types.items():
            if not type_meals:
                continue
                
            # Initialize nutrition totals for this meal type
            total_calories = 0
            total_protein = 0
            total_fat = 0
            total_carbs = 0
            
            # Calculate nutrition for each meal
            for meal in type_meals:
                nutrition = meal.get("nutrition", {})
                if not nutrition:
                    try:
                        # Get nutrition data from API if not in meal data
                        nutrition_data = self.get_recipe_nutrition(meal.get("id"))
                        calories = float(nutrition_data.get("calories", "0").replace("kcal", "").strip())
                        protein = float(nutrition_data.get("protein", "0").replace("g", "").strip())
                        fat = float(nutrition_data.get("fat", "0").replace("g", "").strip())
                        carbs = float(nutrition_data.get("carbs", "0").replace("g", "").strip())
                        
                        total_calories += calories
                        total_protein += protein
                        total_fat += fat
                        total_carbs += carbs
                    except Exception:
                        continue
                else:
                    # Use nutrition data from meal
                    total_calories += float(nutrition.get("calories", 0))
                    total_protein += float(nutrition.get("protein", 0))
                    total_fat += float(nutrition.get("fat", 0))
                    total_carbs += float(nutrition.get("carbs", 0))
            
            # Add to daily totals
            total_daily_calories += total_calories
            total_daily_protein += total_protein
            total_daily_fat += total_fat
            total_daily_carbs += total_carbs
            
            # Create processed meal entry
            processed_meals.append({
                "title": meal_type,
                "image": f"{self.IMAGE_BASE_URL}{type_meals[0].get('image', '')}" if type_meals else "",
                "readyInMinutes": sum(meal.get("readyInMinutes", 0) for meal in type_meals),
                "servings": sum(meal.get("servings", 0) for meal in type_meals),
                "sourceUrl": [meal.get("sourceUrl", "") for meal in type_meals if meal.get("sourceUrl")],
                "nutrition": {
                    "calories": round(total_calories, 2),
                    "protein": round(total_protein, 2),
                    "fat": round(total_fat, 2),
                    "carbs": round(total_carbs, 2)
                },
                "meals": type_meals
            })
        
        # Return processed meal plan with daily totals
        return {
            "meals": processed_meals,
            "nutrients": {
                "calories": round(total_daily_calories, 2),
                "protein": round(total_daily_protein, 2),
                "fat": round(total_daily_fat, 2),
                "carbs": round(total_daily_carbs, 2)
            }
        }
    
    def get_available_diets(self) -> List[str]:
        """
        Get a list of available dietary restrictions supported by the API.
        
        Returns:
            list: List of supported dietary restrictions including:
            - gluten-free
            - ketogenic
            - vegetarian
            - vegan
            - pescetarian
            - paleo
            - primal
            - whole30
        """
        return [
            "gluten-free",
            "ketogenic",
            "vegetarian",
            "vegan",
            "pescetarian",
            "paleo",
            "primal",
            "whole30"
        ]
    
    def get_common_allergies(self) -> List[str]:
        """
        Get a list of common food allergies that can be excluded from meal plans.
        
        Returns:
            list: List of common food allergies including:
            - dairy
            - egg
            - gluten
            - grain
            - peanut
            - seafood
            - sesame
            - shellfish
            - soy
            - sulfite
            - tree-nut
            - wheat
        """
        return [
            "dairy",
            "egg",
            "gluten",
            "grain",
            "peanut",
            "seafood",
            "sesame",
            "shellfish",
            "soy",
            "sulfite",
            "tree-nut",
            "wheat"
        ] 