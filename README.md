Fridgely — Cook with What You Already Have

Fridgely is a recipe recommendation web app that helps users discover meals using ingredients already available in their fridge.
Instead of searching for recipes and then buying ingredients, users simply enter what they have at home, and Fridgely finds matching recipes, identifies missing ingredients, estimates calories, and provides cooking instructions.
Built with Flask, TheMealDB API, and USDA FoodData Central.

Features:  
Ingredient-based recipe search
Recipe match percentage calculation
Missing ingredient detection
Calorie estimation using USDA nutrition data
Multiple sorting options: Best Match, Fewest Missing Ingredients, Lowest Calories
Detailed recipe pages with: Ingredients, Cooking instructions, Recipe images, YouTube tutorials (when available)
Responsive UI with animated loading screens and interactive recipe cards

APIs:  
- TheMealDB
Recipe database used for: Recipe search, Ingredients, Images, Instructions, Video links
https://www.themealdb.com
- USDA FoodData Central
Nutrition database used for: Ingredient calorie lookup, Recipe calorie estimation
https://fdc.nal.usda.gov

Tech Stack:  
Backend: Python, Flask, Requests
Frontend: HTML, CSS, JavaScript
Data Sources: TheMealDB API, USDA FoodData Central API

Getting Started:  
Clone the repository
Install dependencies
Add your USDA API key in app.py: USDA_API_KEY = "YOUR_API_KEY"
Run the application
Open link: http://127.0.0.1:5000

Future Improvements:  
User accounts and saved recipes
Shopping list generation and directions to where can buy it
More dietary preference filters
More accurate nutrition calculations based on ingredient quantities

Motivation:  
I often find myself staring at the leftover ingredients in my fridge without knowing what to cook, and many of them end up going to waste. 
Fridgely was inspired by this everyday problem. The goal is to help people make better use of the ingredients they already have, 
discover new recipes, reduce food waste, and make cooking decisions easier.

Author： 
Yitong Liu
HCDE310 Spring 2026 Final Project
