"""
Calor-E

This is the main application file that creates a Streamlit web interface for:
1. Calculating daily calorie needs based on personal metrics
2. Looking up nutritional information for specific foods
3. Generating personalized meal plans

The app integrates with:
- USDA FoodData Central API for nutritional information
- Spoonacular API for meal planning
"""

import streamlit as st
from utils.calorie_calculator import (
    calculate_daily_calories,
    validate_inputs,
    ACTIVITY_MULTIPLIERS
)
from utils.nutrition_api import NutritionAPI
from utils.meal_planner import MealPlanner
import plotly.express as px
import requests

# Configure the Streamlit page with custom settings
st.set_page_config(
    page_title="Calor-E",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for a modern and consistent look
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        gap: 1rem;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border-radius: 4px 4px 0 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stNumberInput>div>div>input {
        border-radius: 5px;
    }
    .stSelectbox>div>div {
        border-radius: 5px;
    }
    .stRadio>div {
        border-radius: 5px;
    }
    .stSlider>div>div>div {
        border-radius: 5px;
    }
    .stExpander {
        border-radius: 5px;
    }
    .stDataFrame {
        border-radius: 5px;
    }
    .stPlotlyChart {
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for storing calorie goal
if "calorie_goal" not in st.session_state:
    st.session_state.calorie_goal = None

# Initialize session state for food lookup
if "is_liquid" not in st.session_state:
    st.session_state.is_liquid = False
if "selected_food_category" not in st.session_state:
    st.session_state.selected_food_category = None
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "selected_food" not in st.session_state:
    st.session_state.selected_food = None

# Title and description with custom styling
st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h1 style='color: #2E7D32; font-size: 3rem; margin-bottom: 1rem;'>🥗 Calor-E</h1>
        <p style='color: #666666; font-size: 1.2rem;'>
            Your personal nutrition assistant for a healthier lifestyle
        </p>
    </div>
""", unsafe_allow_html=True)

# Create tabs for different features
tab1, tab2, tab3 = st.tabs([
    "📊 Calorie Calculator",
    "🔍 Food Calorie Lookup",
    "🍽️ Meal Planner"
])

# Tab 1: Calorie Calculator
with tab1:
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h2 style='color: #2E7D32; font-size: 2rem; margin-bottom: 1rem;'>Daily Calorie Needs Calculator</h2>
            <p style='color: #666666; font-size: 1.1rem;'>
                Calculate your estimated daily calorie needs based on your personal data
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for input fields
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Personal Information")
        # Input fields for personal metrics
        age = st.number_input("Age (years)", min_value=1, max_value=120, value=30)
        weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=70.0)
        height = st.number_input("Height (cm)", min_value=1.0, max_value=300.0, value=170.0)
        gender = st.radio("Gender", ["male", "female"])
    
    with col2:
        st.markdown("### Activity Level")
        # Activity level selection with descriptions
        activity_level = st.radio(
            "Select your activity level:",
            options=list(ACTIVITY_MULTIPLIERS.keys()),
            format_func=lambda x: x.replace("_", " ").title(),
            help="Choose the option that best describes your daily activity level"
        )
    
    # Calculate button with validation and result display
    if st.button("Calculate Calorie Needs"):
        is_valid, error_message = validate_inputs(
            weight, height, age, gender, activity_level
        )
        
        if is_valid:
            daily_calories = calculate_daily_calories(
                weight, height, age, gender, activity_level
            )
            st.session_state.calorie_goal = daily_calories
            st.success(f"Your estimated daily calorie needs: **{daily_calories:.0f}** kcal")
        else:
            st.error(error_message)

# Tab 2: Food Calorie Lookup
with tab2:
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h2 style='color: #2E7D32; font-size: 2rem; margin-bottom: 1rem;'>Food Calorie Lookup</h2>
            <p style='color: #666666; font-size: 1.1rem;'>
                Look up the calorie content and nutritional information of any food item
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        # Initialize the nutrition API handler
        nutrition_api = NutritionAPI()
        
        # Create two columns for the input fields
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Food Details")
            # Input for food quantity
            quantity = st.number_input("Amount", min_value=1, max_value=1000, value=100, step=1)
            
            # Checkbox for liquid foods - only enabled if no food is selected
            if not st.session_state.selected_food:
                is_liquid = st.checkbox("This is a liquid (e.g., water, milk, juice)", value=st.session_state.is_liquid)
                st.session_state.is_liquid = is_liquid
            else:
                # Display the liquid status based on the selected food's category
                liquid_status = "a liquid" if st.session_state.is_liquid else "not a liquid"
                st.markdown(f"<div style='padding: 10px; border-radius: 5px; background-color: #f0f2f6;'>"
                          f"<strong>Food Type:</strong> {liquid_status}</div>", 
                          unsafe_allow_html=True)
            
            # Unit selection based on food type
            if st.session_state.is_liquid:
                unit = st.selectbox(
                    "Unit",
                    ["ml", "fl_oz"],
                    disabled=False  # Allow changing between ml and fl oz
                )
            else:
                unit = st.selectbox(
                    "Unit",
                    ["g", "oz"],
                    disabled=False  # Allow changing between g and oz
                )
        
        with col2:
            # Food name input
            st.markdown("### Search")
            food_name = st.text_input("Food Name", placeholder="e.g., apple, chicken breast, rice")
        
        # Search button with API integration
        if st.button("Search"):
            if food_name:
                try:
                    with st.spinner("Searching for foods..."):
                        # Search for foods using the USDA API
                        search_data = nutrition_api.search_foods(food_name)
                        foods = search_data.get("foods", [])
                        
                        if foods:
                            # Check if the first result is a liquid based on foodCategory
                            first_food = foods[0]
                            food_category = first_food.get('foodCategory', '').lower()
                            
                            # List of categories that indicate a liquid
                            liquid_categories = [
                                'beverages', 'drinks', 'juices', 'soups', 'broths', 'water',
                                'alcoholic', 'alcohol', 'beer', 'wine', 'spirits', 'cocktail',
                                'coffee', 'tea', 'soda', 'soft drink', 'carbonated'
                            ]
                            
                            # Check if the food category indicates a liquid
                            is_liquid_food = any(category in food_category for category in liquid_categories)
                            
                            # Also check the food description for liquid indicators
                            food_description = first_food.get('description', '').lower()
                            is_liquid_food = is_liquid_food or any(category in food_description for category in liquid_categories)
                            
                            # Update session state
                            st.session_state.is_liquid = is_liquid_food
                            st.session_state.selected_food_category = food_category
                            st.session_state.search_results = foods
                            st.session_state.selected_food = None
                            
                            # Show appropriate message
                            if is_liquid_food:
                                st.success(f"Found {len(foods)} results (liquid food detected)")
                            else:
                                st.success(f"Found {len(foods)} results")
                            
                            # Force a rerun to update the UI
                            st.rerun()
                        else:
                            st.warning("No results found. Try a different search term.")
                            
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("""
                    Tips for better results:
                    - Use specific food names (e.g., 'apple' instead of 'fruit')
                    - Check the spelling of the food name
                    """)
            else:
                st.warning("Please enter a food name")
        
        # Display search results if available
        if st.session_state.search_results:
            # Display search results as radio buttons
            food_options = [food.get('description') for food in st.session_state.search_results]
            selected_food = st.radio(
                "Select a food item:",
                options=food_options,
                key="food_selection",
                index=None  # No default selection
            )
            
            # Update selected food in session state
            if selected_food != st.session_state.selected_food:
                st.session_state.selected_food = selected_food
                # Get the selected food's category
                selected_food_data = next(
                    (food for food in st.session_state.search_results 
                     if food.get('description') == selected_food),
                    None
                )
                if selected_food_data:
                    food_category = selected_food_data.get('foodCategory', '').lower()
                    liquid_categories = ['beverages', 'drinks', 'juices', 'soups', 'broths', 'water']
                    st.session_state.is_liquid = any(category in food_category for category in liquid_categories)
                st.rerun()
            
            # Display details for selected food
            if st.session_state.selected_food:
                # Get the selected food's data
                selected_food_data = next(
                    (food for food in st.session_state.search_results 
                     if food.get('description') == st.session_state.selected_food),
                    None
                )
                
                if selected_food_data:
                    # Get detailed information from the API
                    details = nutrition_api.get_food_details(selected_food_data.get('fdcId'))
                    
                    # Convert the quantity to grams
                    grams = nutrition_api.convert_to_grams(quantity, unit)
                    
                    # Create nutrient tables
                    df_main, df_more, pie_data = nutrition_api.create_nutrient_tables(details, grams)
                    
                    # Create two columns for the display
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Display main nutrients
                        st.markdown("### Main Nutrients")
                        st.dataframe(df_main, hide_index=True)
                        
                        # Display additional nutrients in an expandable section
                        with st.expander("Show Vitamins and Minerals"):
                            st.dataframe(df_more, hide_index=True)
                    
                    with col2:
                        # Display pie chart for macronutrient distribution
                        st.markdown("### Macronutrient Distribution")
                        fig = px.pie(
                            pie_data,
                            values='Amount per 100g',
                            names='Nutrient',
                            title='Macronutrients per 100g',
                            hover_data=None
                        )
                        fig.update_traces(
                            hovertemplate=None,
                            hoverinfo='none'
                        )
                        fig.update_layout(
                            hovermode=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
    except ValueError as e:
        st.error(str(e))
        st.info("Please set up your USDA Food Database API key in the .env file")

# Tab 3: Meal Planner
with tab3:
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h2 style='color: #2E7D32; font-size: 2rem; margin-bottom: 1rem;'>Meal Plan Generator</h2>
            <p style='color: #666666; font-size: 1.1rem;'>
                Generate a personalized meal plan based on your preferences
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        # Initialize the meal planner
        meal_planner = MealPlanner()
        
        # Create two columns for the layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Get calorie goal
            st.markdown("### Calorie Goal")
            if st.session_state.calorie_goal:
                st.info(f"Using calculated calorie goal: {st.session_state.calorie_goal:.0f} kcal")
                calorie_goal = st.number_input(
                    "Daily calorie goal (kcal)",
                    min_value=1000,
                    max_value=10000,
                    value=int(st.session_state.calorie_goal),
                    step=100
                )
            else:
                calorie_goal = st.number_input(
                    "Daily calorie goal (kcal)",
                    min_value=1000,
                    max_value=10000,
                    value=2000,
                    step=100
                )
            
            if calorie_goal > 3000:
                st.info("Note: For calorie goals above 3000 kcal, we recommend splitting your goal into multiple meal plans. For example, if your goal is 5000 kcal, generate one meal plan for 3000 kcal and another for 2000 kcal, then combine the results.")
            
            # Macro distribution settings
            st.markdown("### Macro Distribution")
            
            # Add macro recommendations
            with st.expander("Recommended Macro Distributions"):
                st.markdown("""
                **Weight Loss & Muscle Gain:**
                - Protein: 40-50%
                - Fat: 20-30%
                - Carbs: 20-30%
                
                **Bulking:**
                - Protein: 30-35%
                - Fat: 20-25%
                - Carbs: 40-50%
                
                **Maintenance:**
                - Protein: 30%
                - Fat: 30%
                - Carbs: 40%
                """)
            
            # Macro distribution sliders
            protein_percent = st.slider("Protein (%)", 10, 50, 30)
            fat_percent = st.slider("Fat (%)", 10, 50, 25)
            carbs_percent = st.slider("Carbs (%)", 10, 70, 45)
            
            # Validate macro percentages
            total_percent = protein_percent + fat_percent + carbs_percent
            if total_percent != 100:
                st.warning(f"Macro percentages must sum to 100% (current: {total_percent}%)")
            
            # Dietary restrictions
            st.markdown("### Dietary Preferences")
            
            # Create checkboxes for dietary preferences
            dietary_preferences = meal_planner.get_available_diets()
            selected_diets = []
            
            # Create a grid of checkboxes
            cols = st.columns(2)
            for i, diet in enumerate(dietary_preferences):
                with cols[i % 2]:
                    if st.checkbox(diet.replace("-", " ").title()):
                        selected_diets.append(diet)
            
            # Allergies
            st.markdown("### Allergies (optional)")
            
            # Create checkboxes for allergies
            allergies = meal_planner.get_common_allergies()
            selected_allergies = []
            
            # Create a grid of checkboxes
            cols = st.columns(2)
            for i, allergy in enumerate(allergies):
                with cols[i % 2]:
                    if st.checkbox(allergy.replace("-", " ").title()):
                        selected_allergies.append(allergy)
        
        with col2:
            # Generate meal plan button
            if st.button("Generate Meal Plan"):
                try:
                    with st.spinner("Generating your personalized meal plan..."):
                        # Generate meal plan using the Spoonacular API
                        meal_plan = meal_planner.generate_meal_plan(
                            target_calories=calorie_goal,
                            diet=",".join(selected_diets) if selected_diets else None,
                            exclude=",".join(selected_allergies) if selected_allergies else None
                        )
                        
                        # Helper function to create macro distribution pie chart
                        def create_macro_pie_chart(values, title):
                            return px.pie(
                                values=values,
                                names=["Protein", "Fat", "Carbs"],
                                title=title,
                                color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'],
                                category_orders={"names": ["Protein", "Fat", "Carbs"]}
                            )
                        
                        # Display meal plan
                        for meal in meal_plan["meals"]:
                            st.markdown(f"### {meal['title']}")
                            
                            # Create two columns for the meal display
                            meal_col1, meal_col2 = st.columns([1, 2])
                            
                            with meal_col1:
                                try:
                                    # Try to load the image from URL
                                    if meal.get("image"):
                                        st.image(meal["image"], width=350)
                                    else:
                                        st.warning("No image available")
                                except Exception as e:
                                    st.warning("Image not available")
                            
                            with meal_col2:
                                # Display meal information
                                st.markdown(f"#### {meal.get('title', 'Unknown Meal')}")
                                st.markdown(f"⏱️ Ready in {meal.get('readyInMinutes', 0)} minutes")
                                st.markdown(f"🍽️ Servings: {meal.get('servings', 1)}")
                                
                                # Display multiple source URLs if available
                                if isinstance(meal.get('sourceUrl'), list):
                                    st.markdown("#### Recipe Links:")
                                    for url in meal.get('sourceUrl', []):
                                        if url:
                                            st.markdown(f"🔗 [View Recipe]({url})")
                                elif meal.get('sourceUrl'):
                                    st.markdown(f"🔗 [View Recipe]({meal['sourceUrl']})")
                                
                                # Display macros
                                st.markdown("#### Nutrition per serving:")
                                nutrition = meal.get('nutrition', {})
                                st.markdown(f"Calories: {nutrition.get('calories', 0):.0f} kcal")
                                st.markdown(f"Protein: {nutrition.get('protein', 0):.1f}g")
                                st.markdown(f"Fat: {nutrition.get('fat', 0):.1f}g")
                                st.markdown(f"Carbs: {nutrition.get('carbs', 0):.1f}g")
                            
                            st.markdown("---")
                        
                        # Display day summary
                        st.markdown("### Day Summary")
                        nutrients = meal_plan["nutrients"]
                        st.markdown(f"Total calories: **{nutrients.get('calories', 0):.0f}** kcal")
                        
                        # Create pie chart for target macro distribution
                        st.markdown("### Target Macro Distribution")
                        fig = create_macro_pie_chart(
                            values=[protein_percent, fat_percent, carbs_percent],
                            title='Target Macro Distribution'
                        )
                        fig.update_traces(
                            hovertemplate=None,
                            hoverinfo='none'
                        )
                        fig.update_layout(
                            hovermode=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Calculate actual macro distribution percentages
                        total_macros = nutrients.get('protein', 0) + nutrients.get('fat', 0) + nutrients.get('carbs', 0)
                        actual_protein = (nutrients.get('protein', 0) / total_macros * 100) if total_macros > 0 else 0
                        actual_fat = (nutrients.get('fat', 0) / total_macros * 100) if total_macros > 0 else 0
                        actual_carbs = (nutrients.get('carbs', 0) / total_macros * 100) if total_macros > 0 else 0
                        
                        # Create pie chart for actual macro distribution
                        st.markdown("### Actual Macro Distribution")
                        fig_actual = create_macro_pie_chart(
                            values=[actual_protein, actual_fat, actual_carbs],
                            title='Actual Macro Distribution'
                        )
                        fig_actual.update_traces(
                            hovertemplate=None,
                            hoverinfo='none'
                        )
                        fig_actual.update_layout(
                            hovermode=False
                        )
                        st.plotly_chart(fig_actual, use_container_width=True)
                        
                except ValueError as e:
                    error_message = str(e)
                    if "API daily limit reached" in error_message:
                        st.error("""
                        🚫 Daily API limit reached
                        
                        The free tier of the Spoonacular API has a daily limit. You can:
                        1. Try again tomorrow
                        2. Upgrade your API plan
                        3. Use a different API key
                        """)
                    elif "Invalid API key" in error_message:
                        st.error("""
                        🔑 Invalid API Key
                        
                        Please check your Spoonacular API key in the .env file:
                        ```
                        SPOONACULAR_API_KEY=your_api_key
                        ```
                        """)
                    elif "API rate limit exceeded" in error_message:
                        st.error("""
                        ⏳ API Rate Limit Exceeded
                        
                        Please wait a few minutes before trying again.
                        """)
                    else:
                        st.error(f"Error: {error_message}")
                        st.info("""
                        If you're seeing an error, please check:
                        1. Your Spoonacular API key is correctly set in the .env file
                        2. You have an active subscription to the Meal Planner API
                        3. Your API key has the necessary permissions
                        """)
                    
    except ValueError as e:
        st.error(str(e))
        st.info("""
        Please set up your Spoonacular API key in the .env file:
        ```
        SPOONACULAR_API_KEY=your_api_key
        ```
        """)

# Footer
st.markdown("""
    <div style='text-align: center; padding: 2rem; color: #666666;'>
        <p>Calor-E – Inspired by ChatGPT</p>
    </div>
""", unsafe_allow_html=True) 