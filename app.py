import requests
from flask import Flask, render_template, request

app = Flask(__name__)
USDA_API_KEY = "BvFgr3AWAcsz4I85OTGucCzX9rVTaPcPAuP1s6S3"
MEALDB_BASE = "https://www.themealdb.com/api/json/v1/1"
USDA_BASE = "https://api.nal.usda.gov/fdc/v1"

INGREDIENT_ALIASES = {
    'ground beef':'beef mince',
    'minced beef':'beef mince',
    'green onion':'spring onions',
    'scallion':'spring onions',
    'bell pepper':'red pepper',
    'heavy cream':'double cream',
    'cilantro':'coriander',
    'eggplant':'aubergine',
    'zucchini':'courgette',
    'shrimp':'prawns',
    'ground pork':'pork mince',
    'corn starch':'cornflour',
    'starch':'cornflour',
    'scallions':'spring onions',
    'chili':'red chilli',
    'chilli':'red chilli',
    'hot pepper':'red chilli',
}
STRIP_PREFIXES = ['chopped ', 'minced ', 'sliced ', 'diced ', 'crushed ', 'fresh ', 'dried ', 'cooked ', 'frozen ', 'ground ']

def singularize(word):
    if word.endswith('ves'):
        return word[:-3] + 'f'
    if word.endswith('ies'):
        return word[:-3] + 'y'
    if word.endswith('s') and not word.endswith('ss') and len(word) > 3:
        return word[:-1]
    return word

def normalize_ingredient(name):
    key = name.strip().lower()
    if key in INGREDIENT_ALIASES:
        return INGREDIENT_ALIASES[key]
    for prefix in STRIP_PREFIXES:
        if key.startswith(prefix):
            stripped = key[len(prefix):]
            if stripped in INGREDIENT_ALIASES:
                return INGREDIENT_ALIASES[stripped]
            return stripped
    if key.endswith('s') and len(key) > 3:
        return key
    return key

def search_by_ingredient(ingredient) :
    url = f"{MEALDB_BASE}/filter.php"
    try:
        r = requests.get(url, params={"i": ingredient}, timeout=6)
        return r.json().get("meals") or []
    except Exception:
        return []
    
def get_meal_detail(meal_id):
    url = f"{MEALDB_BASE}/lookup.php"
    try:
        r = requests.get(url, params={"i": meal_id}, timeout=8)
        meals = r.json().get("meals")
        return meals[0] if meals else None
    except Exception:
        return None
    
def extract_ingredients(meal):
    ingredients = []
    for i in range(1, 21):
        name = (meal.get(f"strIngredient{i}") or "").strip()
        measure = (meal.get(f"strMeasure{i}")    or "").strip()
        if name:
            ingredients.append({"name": name.lower(), "measure": measure})
    return ingredients

_calorie_cache = {}

def fetch_calories(ingredient_name):
    if ingredient_name in _calorie_cache:
        return _calorie_cache[ingredient_name]
    try:
        r = requests.get(
            f"{USDA_BASE}/foods/search",
            params={
                "query": ingredient_name,
                "pageSize": 1,
                "api_key": USDA_API_KEY,
            },
            timeout=5,
        )
        foods = r.json().get("foods", [])
        if not foods:
            return 0.0
        for n in foods[0].get("foodNutrients", []):
            if "Energy" in n.get("nutrientName", ""):
                val = n.get("value", 0) or 0
                _calorie_cache[ingredient_name] = val
                return val
    except Exception:
        pass
    return 0.0

def estimate_recipe_calories(ingredients):
    total = 0.0
    for ing in ingredients:
        total += fetch_calories(ing["name"])
    return round(total)

def find_recipes(user_ingredients, sort_by="best_match"):
    user_set = {i.strip().lower() for i in user_ingredients if i.strip()}
    meal_id_set: set[str] = set()
    for ing in user_set:
        stubs = search_by_ingredient(ing)
        for stub in stubs[:15]:
            meal_id_set.add(stub["idMeal"])
    results = []
    for meal_id in list(meal_id_set)[:30]:
        detail = get_meal_detail(meal_id)
        if not detail:
            continue
        ingredients = extract_ingredients(detail)
        recipe_ing_names = {i["name"] for i in ingredients}
        matched = recipe_ing_names & user_set
        missing = recipe_ing_names - user_set
        match_count = len(matched)
        total_count = len(recipe_ing_names)
        match_pct = round(match_count / total_count * 100) if total_count else 0
        calories = estimate_recipe_calories(ingredients)
        results.append({
            "id": meal_id,
            "title": detail.get("strMeal", ""),
            "image": detail.get("strMealThumb", ""),
            "category": detail.get("strCategory", ""),
            "area": detail.get("strArea", ""),
            "instructions": detail.get("strInstructions", ""),
            "url": detail.get("strSource", "") or f"https://www.themealdb.com/meal/{meal_id}",
            "youtube": detail.get("strYoutube", ""),
            "ingredients": ingredients,
            "matched": sorted(matched),
            "missing": sorted(missing),
            "match_count": match_count,
            "total_count": total_count,
            "match_pct": match_pct,
            "calories": calories,
        })
    if sort_by == "calories":
        results.sort(key=lambda r: r["calories"])
    elif sort_by == "fewest_missing":
        results.sort(key=lambda r: len(r["missing"]))
    else:
        results.sort(key=lambda r: r["match_pct"], reverse=True)

    return results

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/results", methods=["POST"])
def results():
    raw = request.form.get("ingredients", "")
    sort_by = request.form.get("sort_by", "best_match")
    user_ingredients = [i.strip() for i in raw.split(",") if i.strip()]
    if not user_ingredients:
        return render_template("index.html", error="Please enter at least one ingredient.")
    recipes = find_recipes(user_ingredients, sort_by)
    return render_template(
        "results.html",
        recipes=recipes,
        user_ingredients=user_ingredients,
        sort_by=sort_by,
    )

@app.route("/recipe/<meal_id>")
def recipe_detail(meal_id):
    user_ingredients_raw = request.args.get("ingredients", "")
    user_ingredients = [i.strip().lower() for i in user_ingredients_raw.split(",") if i.strip()]
    user_set = set(user_ingredients)

    detail = get_meal_detail(meal_id)
    if not detail:
        return render_template("index.html", error="Recipe not found.")

    ingredients = extract_ingredients(detail)
    matched = {i["name"] for i in ingredients if i["name"] in user_set}
    missing = {i["name"] for i in ingredients if i["name"] not in user_set}
    calories = estimate_recipe_calories(ingredients)

    return render_template(
        "recipe.html",
        meal=detail,
        ingredients=ingredients,
        matched=matched,
        missing=missing,
        calories=calories,
        user_ingredients_raw=user_ingredients_raw,
    )

if __name__ == "__main__":
    app.run(debug=True)