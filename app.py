import requests
from flask import Flask, render_template, request

app = Flask(__name__)
USDA_API_KEY = "BvFgr3AWAcsz4I85OTGucCzX9rVTaPcPAuP1s6S3"
MEALDB_BASE = "https://www.themealdb.com/api/json/v1/1"
USDA_BASE = "https://api.nal.usda.gov/fdc/v1"

def search_by_ingredient(ingredient: str) -> list[dict]:
    """Return meal stubs from MealDB for a single ingredient."""
    url = f"{MEALDB_BASE}/filter.php"
    try:
        r = requests.get(url, params={"i": ingredient}, timeout=8)
        data = r.json()
        return data.get("meals") or []
    except Exception:
        return []
    
def get_meal_detail(meal_id: str) -> dict | None:
    """Return full meal detail dict from MealDB."""
    url = f"{MEALDB_BASE}/lookup.php"
    try:
        r = requests.get(url, params={"i": meal_id}, timeout=8)
        data = r.json()
        meals = data.get("meals")
        return meals[0] if meals else None
    except Exception:
        return None
    
def extract_ingredients(meal: dict) -> list[str]:
    """Pull ingredient strings from MealDB meal detail dict."""
    ingredients = []
    for i in range(1, 21):
        name = meal.get(f"strIngredient{i}", "").strip()
        measure = meal.get(f"strMeasure{i}", "").strip()
        if name:
            ingredients.append({"name": name.lower(), "measure": measure})
    return ingredients