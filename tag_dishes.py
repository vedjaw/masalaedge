import pandas as pd
from tqdm import tqdm
from thefuzz import fuzz # <-- Import the fuzzy matching library

# --- 1. CONFIGURATION ---

INPUT_EXCEL_PATH = 'dish_names.xlsx'
OUTPUT_EXCEL_PATH = 'dishes_with_tags_fuzzy.xlsx'
# We set a similarity threshold. Any match below this score will be ignored.
# 85 is a good starting point to avoid incorrect matches.
SIMILARITY_THRESHOLD = 65


# --- 2. THE "KNOWLEDGE BASE" (Your existing keyword dictionary) ---
# --- THE "KNOWLEDGE BASE" (Keyword-to-Tag Mapping) ---
# This expanded dictionary now covers a much wider range of dishes.
# Keywords are lowercase for consistent matching.
KEYWORD_TO_TAGS = {
    # --- Curries & Gravies ---
    'paneer': ['vegetarian', 'main_course', 'north_indian', 'creamy', 'savory', 'punjabi'],
    'kofta': ['vegetarian', 'main_course', 'north_indian', 'creamy', 'savory', 'rich'],
    'dal': ['vegetarian', 'main_course', 'healthy', 'comfort_food', 'curry'],
    'daal': ['vegetarian', 'main_course', 'healthy', 'comfort_food', 'curry'],
    'rajma': ['vegetarian', 'main_course', 'punjabi', 'healthy', 'comfort_food', 'curry'],
    'chole': ['main_course', 'punjabi', 'savory', 'vegetarian', 'comfort_food'],
    'curry': ['main_course', 'curry', 'savory'],
    
    # --- Breads ---
    'paratha': ['bread', 'north_indian', 'breakfast', 'vegetarian'],
    'naan': ['bread', 'north_indian', 'tandoori', 'vegetarian'],
    'roti': ['bread', 'healthy', 'vegetarian'],
    'chapati': ['bread', 'healthy', 'vegetarian'],
    'kulcha': ['bread', 'punjabi', 'vegetarian'],

    # --- Rice Dishes ---
    'biryani': ['main_course', 'celebratory', 'rich', 'savory', 'rice_dish'],
    'pulao': ['main_course', 'rice_dish', 'savory', 'light_meal'],
    'rice': ['rice_dish'], # Generic tag for fried rice, lemon rice etc.

    # --- South Indian ---
    'dosa': ['breakfast', 'south_indian', 'savory', 'light_meal', 'vegetarian'],
    'idli': ['breakfast', 'south_indian', 'steamed', 'healthy', 'light_meal', 'vegetarian'],
    'vada': ['snack', 'fried', 'south_indian', 'savory'],
    'uttapam': ['breakfast', 'south_indian', 'savory', 'vegetarian'],
    'sambar': ['south_indian', 'curry', 'healthy', 'vegetarian'],

    # --- Snacks & Street Food ---
    'samosa': ['snack', 'fried', 'savory', 'street_food', 'rainy_day', 'vegetarian'],
    'pakora': ['snack', 'fried', 'rainy_day', 'vegetarian'],
    'chaat': ['street_food', 'snack', 'tangy', 'savory'],
    'pav bhaji': ['street_food', 'main_course', 'vegetarian', 'comfort_food'],
    'kebab': ['appetizer', 'grilled', 'tandoori', 'snack'],
    'tikka': ['appetizer', 'grilled', 'tandoori', 'punjabi'],

    # --- Desserts ---
    'gulab jamun': ['dessert', 'sweet', 'celebratory', 'rich'],
    'kheer': ['dessert', 'sweet', 'celebratory', 'comfort_food'],
    'halwa': ['dessert', 'sweet', 'rich'],
    'jalebi': ['dessert', 'sweet', 'fried', 'street_food'],
    'barfi': ['dessert', 'sweet'],

    # --- Beverages ---
    'lassi': ['beverage', 'summer_food', 'sweet', 'healthy'],
    'coffee': ['beverage', 'quick_and_easy'],
    'tea': ['beverage', 'quick_and_easy', 'rainy_day'],
    'chai': ['beverage', 'quick_and_easy', 'rainy_day'],
    'sharbat': ['beverage', 'summer_food', 'sweet'],
    
    # --- Non-Vegetarian ---
    'chicken': ['non_vegetarian'],
    'mutton': ['non_vegetarian', 'rich'],
    'fish': ['non_vegetarian', 'healthy'],
    'egg': ['non_vegetarian', 'breakfast'],

    # --- Core Vegetables ---
    'aloo': ['vegetarian', 'savory'],
    'potato': ['vegetarian', 'savory'],
    'gobi': ['vegetarian', 'healthy'],
    'matar': ['vegetarian'],
    
    # --- Common International ---
    'noodles': ['chinese_cuisine', 'main_course', 'quick_and_easy'],
    'manchurian': ['chinese_cuisine', 'appetizer', 'savory'],
    'soup': ['appetizer', 'light_meal', 'healthy', 'comfort_food'],
    'pizza': ['quick_and_easy', 'snack', 'savory'],
    'pasta': ['main_course', 'quick_and_easy', 'savory'],
    'salad': ['healthy', 'light_meal', 'appetizer'],

    'meat': ['non_vegetarian'],
    'beef': ['non_vegetarian', 'beef'],
    'pork': ['non_vegetarian', 'pork'],
    'shrimp': ['non_vegetarian', 'seafood'],
    'seafood': ['non_vegetarian', 'seafood'],
    
    # --- Cooking Styles ---
    'stir-fried': ['fried', 'chinese_cuisine'],
    'stir-fry': ['fried', 'chinese_cuisine', 'main_course'],
    'grilled': ['grilled', 'healthy'],
    'braised': ['stew', 'comfort_food'],
    'baked': ['baked'],
    'roasted': ['baked'],
    'stew': ['stew', 'main_course', 'comfort_food'],

    # --- International Dish Types ---
    'dumplings': ['dumpling', 'snack', 'appetizer', 'asian_cuisine', 'steamed'],
    'sushi': ['japanese_cuisine', 'seafood', 'healthy', 'main_course'],
    'sandwich': ['sandwich', 'snack', 'quick_and_easy', 'western_cuisine'],
    'platter': ['platter', 'celebratory', 'appetizer'],
    'rolls': ['appetizer', 'snack'], # Could be spring rolls, sushi rolls, etc.

    # --- Desserts & Fruits ---
    'cake': ['dessert', 'sweet', 'baked'],
    'chocolate': ['dessert', 'sweet'],
    'fruit': ['healthy', 'snack', 'dessert'],
    'apple': ['healthy', 'snack', 'fruit'],
    'watermelon': ['healthy', 'snack', 'fruit', 'summer_food'],
    'strawberries': ['healthy', 'snack', 'fruit'],
    'lychee': ['healthy', 'snack', 'fruit'],
    'cream': ['dessert', 'sweet', 'creamy'],

    # --- Other Key Ingredients & Types ---
    'vegetable': ['vegetarian', 'healthy'],
    'vegetables': ['vegetarian', 'healthy'],
    'tofu': ['vegetarian', 'healthy', 'asian_cuisine'],
    'hot pot': ['main_course', 'celebratory', 'asian_cuisine'],
    'pot': ['main_course', 'celebratory', 'asian_cuisine'], # Catches "hot pot"
    'skewers': ['snack', 'appetizer', 'grilled', 'street_food'],

    'crawfish': ['non_vegetarian', 'seafood'],
    'crab': ['non_vegetarian', 'seafood'],
    'oysters': ['non_vegetarian', 'seafood'],
    'lobster': ['non_vegetarian', 'seafood', 'celebratory'],
    'salmon': ['non_vegetarian', 'seafood', 'healthy'],
    'sashimi': ['japanese_cuisine', 'seafood', 'healthy', 'raw'],
    'duck': ['non_vegetarian', 'rich'],
    'steak': ['non_vegetarian', 'western_cuisine', 'main_course'],
    'ribs': ['non_vegetarian', 'western_cuisine', 'main_course'],

    # --- Western & International Dishes ---
    'cheeseburger': ['western_cuisine', 'main_course', 'snack', 'beef', 'non_vegetarian'],
    'hamburger': ['western_cuisine', 'main_course', 'snack', 'beef', 'non_vegetarian'],
    'spaghetti': ['western_cuisine', 'main_course', 'pasta'],
    'ramen': ['japanese_cuisine', 'main_course', 'soup', 'noodle'],
    'pancakes': ['breakfast', 'sweet', 'western_cuisine'],
    'fries': ['snack', 'fried', 'western_cuisine'],
    'toast': ['breakfast', 'quick_and_easy', 'bread'],
    'meatballs': ['main_course', 'savory'],

    # --- Breads & Pastries ---
    'buns': ['bread', 'steamed', 'baked'],
    'flatbread': ['bread', 'healthy'],
    'pastry': ['dessert', 'snack', 'baked', 'sweet'],
    'cookies': ['dessert', 'snack', 'baked', 'sweet'],
    
    # --- Fruits & Vegetables ---
    'mango': ['fruit', 'healthy', 'dessert', 'summer_food'],
    'grapes': ['fruit', 'healthy', 'snack'],
    'durian': ['fruit', 'dessert'],
    'bananas': ['fruit', 'healthy', 'breakfast'],
    'peaches': ['fruit', 'healthy', 'dessert'],
    'cherries': ['fruit', 'healthy', 'dessert'],
    'tomatoes': ['vegetarian', 'healthy'],
    'corn': ['vegetarian', 'snack'],
    'cucumber': ['vegetarian', 'healthy', 'salad'],
    'beans': ['vegetarian', 'healthy', 'curry'],
    'peanuts': ['snack', 'vegetarian'],
    'nuts': ['snack', 'vegetarian', 'healthy'],

    # --- Desserts & Dairy ---
    'custard': ['dessert', 'sweet', 'creamy'],
    'tart': ['dessert', 'sweet', 'baked'],
    'yogurt': ['healthy', 'breakfast', 'creamy'],
    'coconut': ['dessert', 'creamy'],
    
    # --- Cooking Methods & Descriptors ---
    'stuffed': ['rich', 'savory'],
    'boiled': ['steamed', 'healthy'],
    'scrambled': ['breakfast', 'egg'],
    'sautéed': ['fried', 'healthy'],
    'cheese': ['savory', 'creamy', 'vegetarian'],

    'noodle': ['noodle', 'main_course', 'asian_cuisine'],
    'bun': ['bread', 'steamed', 'baked'],
    'peach': ['fruit', 'healthy', 'dessert'],
    'orange': ['fruit', 'healthy'],
    'strawberry': ['fruit', 'healthy', 'dessert'],
    'melon': ['fruit', 'healthy', 'summer_food'],
    'plum': ['fruit', 'healthy'],
    'blueberry': ['fruit', 'healthy', 'dessert'],
    'bean': ['vegetarian', 'healthy'],
}


def automate_tagging_fuzzy():
    """
    Reads an Excel file and adds a 'tags' column using fuzzy string matching.
    """
    try:
        df = pd.read_excel(INPUT_EXCEL_PATH)
    except FileNotFoundError:
        print(f"FATAL: Input file not found at '{INPUT_EXCEL_PATH}'.")
        return

    if 'dish_name' not in df.columns:
        print(f"FATAL: Column 'dish_name' not found in the Excel file.")
        return

    tqdm.pandas(desc="Tagging Dishes (Fuzzy Search)")

    # --- THIS IS THE MODIFIED FUNCTION ---
    def get_tags_for_dish(dish_name):
        found_tags = set()
        name_lower = str(dish_name).lower()
        
        for keyword, tags in KEYWORD_TO_TAGS.items():
            # Calculate the similarity score between the keyword and the dish name
            # partial_ratio is good for finding a short keyword within a longer dish name
            score = fuzz.token_set_ratio(keyword, name_lower)
            
            # If the score is above our threshold, we consider it a match
            if score >= SIMILARITY_THRESHOLD:
                found_tags.update(tags)
        
        return '|'.join(sorted(list(found_tags)))

    # Apply the new fuzzy function to create the 'tags' column
    df['tags'] = df['dish_name'].progress_apply(get_tags_for_dish)

    # Save the updated dataframe to a new Excel file
    df.to_excel(OUTPUT_EXCEL_PATH, index=False)

    # Report on untagged dishes
    untagged_count = df[df['tags'] == ''].shape[0]
    total_count = len(df)
    
    print(f"\nSuccessfully processed {total_count} dishes.")
    print(f"Tagged data saved to '{OUTPUT_EXCEL_PATH}'")
    if untagged_count > 0:
        print(f"⚠️  {untagged_count} out of {total_count} dishes remain untagged.")
        print("Consider adding more keywords for them or lowering the SIMILARITY_THRESHOLD.")
    else:
        print("✅ All dishes were successfully tagged!")

if __name__ == '__main__':
    automate_tagging_fuzzy()