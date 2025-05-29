"""
Calorie Calculator Module

This module provides functionality for calculating daily calorie needs based on:
1. Personal metrics (age, weight, height, gender)
2. Activity level
3. Fitness goals

The calculations are based on the Mifflin-St Jeor Equation and activity multipliers.
"""

from typing import Tuple, Dict, Union
import numbers

# Activity level multipliers for different activity levels
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extra_active": 1.9
}

def calculate_daily_calories(
    weight: Union[int, float],
    height: Union[int, float],
    age: int,
    gender: str,
    activity_level: str
) -> float:
    """
    Calculate daily calorie needs using the Mifflin-St Jeor Equation.
    
    Args:
        weight: Weight in kilograms (must be between 20 and 300)
        height: Height in centimeters (must be between 100 and 250)
        age: Age in years (must be between 15 and 100)
        gender: "male" or "female"
        activity_level: One of the keys from ACTIVITY_MULTIPLIERS
        
    Returns:
        float: Estimated daily calorie needs
        
    Raises:
        ValueError: If any input parameter is invalid
        TypeError: If input types are incorrect
    """
    # Validate input types
    if not isinstance(weight, (int, float)) or not isinstance(height, (int, float)):
        raise TypeError("Weight and height must be numbers")
    if not isinstance(age, int):
        raise TypeError("Age must be an integer")
    if not isinstance(gender, str) or not isinstance(activity_level, str):
        raise TypeError("Gender and activity_level must be strings")
    
    # Validate input values
    is_valid, error_message = validate_inputs(weight, height, age, gender, activity_level)
    if not is_valid:
        raise ValueError(error_message)
    
    # Base metabolic rate calculation using Mifflin-St Jeor Equation
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Apply activity multiplier
    activity_multiplier = ACTIVITY_MULTIPLIERS.get(activity_level.lower(), 1.2)
    daily_calories = bmr * activity_multiplier
    
    return round(daily_calories, 2)  # Round to 2 decimal places for readability

def validate_inputs(
    weight: Union[int, float],
    height: Union[int, float],
    age: int,
    gender: str,
    activity_level: str
) -> Tuple[bool, str]:
    """
    Validate user inputs for calorie calculation.
    
    Args:
        weight: Weight in kilograms
        height: Height in centimeters
        age: Age in years
        gender: "male" or "female"
        activity_level: One of the keys from ACTIVITY_MULTIPLIERS
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Validate weight
    if not isinstance(weight, (int, float)) or not 20 <= weight <= 300:
        return False, "Weight must be a number between 20 and 300 kg"
    
    # Validate height
    if not isinstance(height, (int, float)) or not 100 <= height <= 250:
        return False, "Height must be a number between 100 and 250 cm"
    
    # Validate age
    if not isinstance(age, int) or not 15 <= age <= 100:
        return False, "Age must be an integer between 15 and 100 years"
    
    # Validate gender
    if not isinstance(gender, str) or gender.lower() not in ["male", "female"]:
        return False, "Gender must be either 'male' or 'female'"
    
    # Validate activity level
    if not isinstance(activity_level, str) or activity_level.lower() not in ACTIVITY_MULTIPLIERS:
        return False, f"Activity level must be one of: {', '.join(ACTIVITY_MULTIPLIERS.keys())}"
    
    return True, "" 