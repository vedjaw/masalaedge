import pandas as pd
import random
from tqdm import tqdm

# --- 1. CONFIGURATION ---

# --- FILE PATHS ---
# Input: Your tagged dish data
TAGGED_DISHES_PATH = 'dishes_with_tags_fuzzy.xlsx'
# Input: Your original file with image URLs
ORIGINAL_DATA_PATH = 'dish_names.xlsx' # Make sure this is the correct name
# Output: The final CSV for model training
OUTPUT_DATASET_PATH = 'finetuning_dataset.csv'

# Number of varied text queries to generate for each image
QUERIES_PER_IMAGE = 8


# --- 2. QUERY TEMPLATES ---
# The script will use these templates. The keys MUST match your tags.
TAG_TO_TEMPLATES = {
    # --- Dietary ---
    'vegetarian': [
        "Show me some vegetarian options.",
        "I'm looking for a good veggie dish.",
        "What vegetarian food do you have?",
        "What are the non-meat options?",
        "I'm purely vegetarian."
    ],
    'non_vegetarian': [
        "What are your non-veg specialties?",
        "I'm in the mood for chicken or meat.",
        "Show me the non-vegetarian menu.",
        "What meat dishes do you have?",
        "I'm not vegetarian, what do you recommend?"
    ],
    'healthy': [
        "I need a light and healthy meal.",
        "What's a nutritious option?",
        "Show me your healthy choices.",
        "Suggest something healthy but tasty.",
        "What's a good guilt-free option?"
    ],
    'light_meal': [
        "I want something light, not too heavy.",
        "Suggest a light meal.",
        "Looking for a small, light dish.",
        "I'm not very hungry, just something light.",
        "What are some of your lighter options?"
    ],

    # --- Meal Type ---
    'main_course': [
        "I'm looking for a main course.",
        "What's a good idea for dinner?",
        "Suggest a filling main dish.",
        "I'm ready for the main event.",
        "What's a good entree?"
    ],
    'breakfast': [
        "What's a good breakfast option?",
        "Suggest a light and healthy breakfast.",
        "What do you have for breakfast?",
        "What's on the breakfast menu?",
        "I'd like to order breakfast."
    ],
    'snack': [
        "What's a good evening snack?",
        "I need a light bite.",
        "Suggest a quick snack.",
        "I'm feeling a bit hungry, need a snack.",
        "Just a small bite to eat."
    ],
    'dessert': [
        "I have a massive sweet tooth right now.",
        "What's for dessert?",
        "Show me the dessert menu.",
        "Craving something sweet.",
        "I'm ready for something sweet."
    ],
    'beverage': [
        "I'm thirsty, what drinks do you have?",
        "Can I get a beverage?",
        "What's good to drink?",
        "What are the drink options?",
        "Can I see the beverage list?"
    ],
    'appetizer': [
        "What are some good appetizers?",
        "Let's start with an appetizer.",
        "Show me the starters.",
        "What should we get for a starter?",
        "Let's get something to share before the main."
    ],

    # --- Cuisine / Style ---
    'north_indian': [
        "I'm in the mood for North Indian food.",
        "What North Indian dishes do you recommend?",
        "Craving North Indian curry.",
        "Do you have any tandoori food?",
        "Show me the North Indian specialties."
    ],
    'south_indian': [
        "I feel like having South Indian food.",
        "Show me your South Indian specialties.",
        "I'd like a dosa or idli.",
        "What's on the South Indian menu?",
        "I want something light like South Indian food."
    ],
    'punjabi': [
        "Do you have any Punjabi dishes?",
        "I want some rich Punjabi food.",
        "I want some rich, buttery Punjabi food.",
        "What's your best Punjabi curry?",
        "Craving some chole or rajma."
    ],
    'indian_cuisine': [
        "I'm looking for Indian food.",
        "What's your most popular Indian dish?",
        "What's your house special Indian dish?",
        "I'm in the mood for some desi food.",
        "Do you have classic Indian curries?"
    ],
    'chinese_cuisine': [
        "I'm craving Chinese food.",
        "What Chinese dishes do you have?",
        "Feel like having some Indo-Chinese.",
        "I feel like some noodles or fried rice.",
        "What's on the Chinese menu?"
    ],
    'japanese_cuisine': [
        "Do you have any Japanese food?",
        "I'd like to try some Japanese cuisine.",
        "I'm in the mood for sushi.",
        "Do you have ramen or teriyaki?",
        "Show me the Japanese options."
    ],
    'asian_cuisine': [
        "What kind of Asian food do you serve?",
        "I'm in the mood for something Asian.",
        "Looking for Thai, Chinese, or Japanese.",
        "What's a good pan-Asian dish?",
        "I want something with Asian flavors."
    ],
    'western_cuisine': [
        "I'm looking for some Western food.",
        "What's on the continental menu?",
        "I want a burger or pasta.",
        "I'm not in the mood for Indian, what else do you have?",
        "I'll have a sandwich or a burger."
    ],
    'street_food': [
        "I feel like eating some street food.",
        "Suggest a popular street food item.",
        "Craving some chaat or something.",
        "I want something quick and chatpata.",
        "What's your best street-style dish?"
    ],

    # --- Flavor / Texture ---
    'creamy': [
        "I want something rich and creamy.",
        "What's your creamiest dish?",
        "Suggest a dish with a rich, creamy gravy.",
        "I want a malai or korma dish.",
        "What's something creamy and comforting?"
    ],
    'savory': [
        "I'm in the mood for something savory.",
        "Not sweet, I want a savory dish.",
        "I want a savory main course.",
        "Something salty and savory, not sweet.",
        "What's your best savory snack?"
    ],
    'rich': [
        "I want something rich and decadent.",
        "Suggest a heavy, rich meal.",
        "I'm celebrating, give me something rich.",
        "Looking for a heavy, decadent meal.",
        "What's a rich, Mughlai-style dish?"
    ],
    'sweet': [
        "I have a sweet tooth.",
        "Show me something sweet.",
        "I'm craving sugar.",
        "What's your most popular sweet dish?",
        "I need a sweet treat."
    ],
    'spicy': [
        "I'm craving something hot and spicy.",
        "What's the spiciest dish you have?",
        "Make it spicy.",
        "I want something really hot, extra spicy.",
        "What's a fiery dish I can try?"
    ],
    'tangy': [
        "I want something tangy and chatpata.",
        "What's a good tangy dish?",
        "I want a chaat-style tangy dish.",
        "Something with a sour and tangy flavor.",
        "Give me something with tamarind or lemon."
    ],
    'raw': [
        "Do you have any raw options, like sashimi?",
        "I'm looking for something raw and fresh.",
        "I'm looking for a fresh, uncooked dish.",
        "What salads or raw fish do you have?",
        "A simple raw appetizer would be great."
    ],

    # --- Cooking Method ---
    'fried': [
        "I'm craving something fried and crunchy.",
        "What's a popular deep-fried dish?",
        "Suggest a crispy snack.",
        "I want some deep-fried goodness.",
        "What's your crispiest dish?"
    ],
    'grilled': [
        "I want something grilled.",
        "What's healthy and grilled?",
        "Show me the grilled options.",
        "What's on the grill today?",
        "I'd like a grilled appetizer."
    ],
    'baked': [
        "Do you have any baked goods?",
        "I'm looking for something baked, not fried.",
        "Do you have any baked snacks?",
        "I'm looking for a baked dessert.",
        "Show me the items from the oven."
    ],
    'steamed': [
        "I want a light, steamed dish.",
        "What are your steamed options?",
        "Suggest something healthy and steamed.",
        "I'm on a diet, what's steamed?",
        "I'd like some steamed dumplings."
    ],
    'curry': [
        "I feel like a good curry.",
        "What's your best curry?",
        "Show me the list of curries.",
        "Suggest a good curry.",
        "What curries go well with naan?"
    ],
    'tandoori': [
        "I want something from the tandoor.",
        "What are your tandoori specialties?",
        "What's fresh from the tandoor?",
        "I'd like a tandoori platter.",
        "Show me the tandoori breads and appetizers."
    ],
    'stew': [
        "I want a hearty stew.",
        "Do you have any slow-cooked stews?",
        "What's a good slow-cooked meal?",
        "I want a hearty stew for this cold weather.",
        "Do you have any stews or casseroles?"
    ],

    # --- Key Ingredient / Dish Type ---
    'bread': [
        "What types of bread do you have?",
        "Can I get some bread with this?",
        "What kind of Indian breads do you have?",
        "I need some bread to go with my curry.",
        "Can I see the bread basket options?"
    ],
    'rice_dish': [
        "I'm in the mood for a rice dish.",
        "What are your rice-based meals?",
        "I want biryani or pulao.",
        "What are my options for rice?",
        "I'll have a rice-based main."
    ],
    'noodle': [
        "I want to eat noodles.",
        "What kind of noodle dishes do you have?",
        "I'm craving a bowl of noodles.",
        "What's your best noodle dish?",
        "Do you have Hakka noodles?"
    ],
    'seafood': [
        "What's your best seafood dish?",
        "I'm in the mood for fish or shrimp.",
        "Show me the seafood menu.",
        "What's the catch of the day?",
        "I want to eat some fish."
    ],
    'beef': [
        "I'm looking for a beef dish.",
        "What are your beef options?",
        "What are your beef curries?",
        "I'll have a beef steak.",
        "How is the beef prepared?"
    ],
    'pork': [
        "Do you serve pork?",
        "What pork dishes do you have?",
        "What's your most popular pork dish?",
        "I'm in the mood for pork ribs.",
        "Do you have any pork-based appetizers?"
    ],
    'egg': [
        "What do you have with eggs?",
        "I'd like an egg dish for breakfast.",
        "I'll have an omelette.",
        "What egg curries do you have?",
        "What are the egg-based breakfast options?"
    ],
    'dumpling': [
        "I feel like having dumplings.",
        "What kind of dumplings are on the menu?",
        "I want momos.",
        "What's in the dumplings?",
        "Can I get a plate of steamed dumplings?"
    ],
    'sushi': [
        "I'm craving sushi.",
        "What are your sushi roll options?",
        "Show me the sushi menu.",
        "What are your maki roll options?",
        "I'd like a sushi platter."
    ],
    'sandwich': [
        "Can I get a sandwich?",
        "What's a good quick sandwich?",
        "I just want a simple sandwich.",
        "What's in the club sandwich?",
        "Do you have any grilled sandwiches?"
    ],
    'platter': [
        "I'm with a group, do you have any platters?",
        "What's on the assorted platter?",
        "What's in the mixed platter?",
        "We're a group, suggest a good sharing platter.",
        "I'll get the tandoori platter."
    ],
    'fruit': [
        "I'd like some fresh fruit.",
        "Do you have a fruit platter or fruit salad?",
        "What's in the fruit bowl?",
        "Can I get a side of fresh fruits?",
        "I'd like a fruit juice, fresh."
    ],

    # --- Occasion / Feeling ---
    'comfort_food': [
        "Long day at work, I need some comfort food.",
        "Suggest something to cheer me up.",
        "What's a good, comforting meal?",
        "I need something hearty and comforting.",
        "What's a good home-style meal?"
    ],
    'celebratory': [
        "I'm celebrating! Suggest something special.",
        "What's a good dish for a party?",
        "We're looking for a festive meal.",
        "It's my birthday, suggest a special dish.",
        "We want to order something fancy."
    ],
    'quick_and_easy': [
        "I'm in a hurry, what's quick?",
        "What's a quick and easy option?",
        "I need food, fast.",
        "I'm really hungry, what's the fastest dish?",
        "I don't have much time, what's ready to go?"
    ],
    'rainy_day': [
        "It's a classic rainy day, what's a good snack?",
        "Feeling cozy because of the rain, suggest something warm.",
        "What's the perfect food for this gloomy weather?",
        "It's raining, I want something hot.",
        "What's a good snack for this rainy weather?"
    ],
    'summer_food': [
        "It's so hot, I need something cooling.",
        "What's a good summer dish?",
        "Suggest something refreshing for this heat.",
        "It's boiling outside, I need a cold drink.",
        "What's a good light meal for this summer?"
    ]
}


def generate_final_dataset():
    """
    Generates the final (text, image_url, dish_name) dataset from the tagged dishes.
    """
    try:
        # Load the tagged dishes
        df_tagged = pd.read_excel(TAGGED_DISHES_PATH)
        # Load the original data (assuming it has 'dish_name' and 'image_url')
        df_original = pd.read_excel(ORIGINAL_DATA_PATH)
    except FileNotFoundError as e:
        print(f"Error: Could not find a required file. {e}")
        return
    
    # 1. Filter out untagged dishes
    df_tagged = df_tagged.dropna(subset=['tags'])
    df_tagged = df_tagged[df_tagged['tags'] != '']
    print(f"Found {len(df_tagged)} successfully tagged rows.")

    # Keep only the first set of tags for each unique dish name
    df_tagged = df_tagged.drop_duplicates(subset=['dish_name'])
    print(f"Working with {len(df_tagged)} unique tagged dishes.")
    
    # 2. Merge with original data to get image_url
    # Assuming 'dish_name' is the common key
    df_merged = pd.merge(df_original, df_tagged, on='dish_name', how='inner')
    
    if 'image_url' not in df_merged.columns:
        print("Error: 'image_url' column not found in the merged data.")
        print("Please ensure your original data file has 'dish_name' and 'image_url' columns.")
        return
        
    print(f"Found {len(df_merged)} images to process.")

    final_data = []

    # 3. Iterate and generate queries
    for _, row in tqdm(df_merged.iterrows(), total=df_merged.shape[0], desc="Generating Text Queries"):
        image_url = row['image_url']
        dish_name = row['dish_name']
        tags = row['tags'].split('|')
        
        possible_queries = set()
        
        # Add direct queries
        possible_queries.add(f"I want to eat {dish_name}.")
        possible_queries.add(f"Show me pictures of {dish_name}.")
        
        # Add queries from templates
        for tag in tags:
            if tag in TAG_TO_TEMPLATES:
                possible_queries.update(TAG_TO_TEMPLATES[tag])
        
        # Sample queries
        num_to_sample = min(QUERIES_PER_IMAGE, len(possible_queries))
        if num_to_sample > 0:
            sampled_queries = random.sample(list(possible_queries), num_to_sample)
            for query in sampled_queries:
                # --- THIS IS THE MODIFIED LINE ---
                # Add dish_name to the dictionary
                final_data.append({'text': query, 'image_url': image_url, 'dish_name': dish_name})

    df_final = pd.DataFrame(final_data)
    
    if df_final.empty:
        print("No data was generated. Check your file paths and column names.")
        return

    # 4. Save the final dataset
    df_final.to_csv(OUTPUT_DATASET_PATH, index=False)
    
    print(f"\nSuccessfully generated {len(df_final)} (text, image_url, dish_name) pairs.")
    print(f"Final training dataset saved to '{OUTPUT_DATASET_PATH}'")
    print("\nSample of the generated data:")
    # Re-order columns for better display in the sample
    print(df_final.sample(5)[['text', 'dish_name', 'image_url']])

if __name__ == '__main__':
    generate_final_dataset()