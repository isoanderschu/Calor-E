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
        
        Args:
            target_calories: Target daily calorie intake
            diet: Optional dietary restrictions (e.g., "vegetarian", "vegan")
            exclude: Optional ingredients to exclude
            time_frame: Time frame for the meal plan ("day" or "week")
            
        Returns:
            Dict containing the generated meal plan
            
        Raises:
            ValueError: If the API request fails or returns invalid data
            requests.exceptions.RequestException: If there's an error with the API request
        """
        # Prepare API request parameters
        params = {
            "apiKey": self.api_key,
            "timeFrame": time_frame,
            "targetCalories": target_calories,
            "number": 3,  # Number of meals per day
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
            response.raise_for_status()  # Raise exception for HTTP errors
            
            data = response.json()
            
            # Check if we got valid meal data
            if not data.get("meals"):
                raise ValueError("No meals found in API response")
            
            # Process and return meal plan
            return self._process_meal_plan(data)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 402:
                raise ValueError("API quota exceeded. Please try again later or upgrade your plan.")
            raise ValueError(f"API request failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error making API request: {str(e)}")
        except (KeyError, TypeError) as e:
            raise ValueError(f"Error processing API response: {str(e)}")
    
    def _process_meal_plan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the raw API response into a structured meal plan.
        
        Args:
            data: Raw API response data
            
        Returns:
            Dict containing the processed meal plan
        """
        meals = data.get("meals", [])
        nutrients = data.get("nutrients", {})
        
        # Group meals by type
        meal_types = {
            "Breakfast": [],
            "Lunch": [],
            "Dinner": []
        }
        
        # Distribute meals across types
        for i, meal in enumerate(meals):
            meal_type = list(meal_types.keys())[i % len(meal_types)]
            meal_types[meal_type].append(meal)
        
        # Process each meal type
        processed_meals = []
        for meal_type, type_meals in meal_types.items():
            if not type_meals:
                continue
                
            # Calculate combined nutrition info
            total_calories = sum(meal.get("nutrition", {}).get("calories", 0) for meal in type_meals)
            total_protein = sum(meal.get("nutrition", {}).get("protein", 0) for meal in type_meals)
            total_fat = sum(meal.get("nutrition", {}).get("fat", 0) for meal in type_meals)
            total_carbs = sum(meal.get("nutrition", {}).get("carbs", 0) for meal in type_meals)
            
            processed_meals.append({
                "title": f"{meal_type} ({len(type_meals)} {'meal' if len(type_meals) == 1 else 'meals'})",
                "image": f"{self.IMAGE_BASE_URL}{type_meals[0].get('image', '')}" if type_meals else "",
                "readyInMinutes": sum(meal.get("readyInMinutes", 0) for meal in type_meals),
                "servings": sum(meal.get("servings", 0) for meal in type_meals),
                "sourceUrl": [meal.get("sourceUrl", "") for meal in type_meals if meal.get("sourceUrl")],
                "nutrition": {
                    "calories": round(total_calories, 2),
                    "protein": round(total_protein, 2),
                    "fat": round(total_fat, 2),
                    "carbs": round(total_carbs, 2)
                }
            })
        
        return {
            "meals": processed_meals,
            "nutrients": {
                "calories": round(nutrients.get("calories", 0), 2),
                "protein": round(nutrients.get("protein", 0), 2),
                "fat": round(nutrients.get("fat", 0), 2),
                "carbs": round(nutrients.get("carbs", 0), 2)
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