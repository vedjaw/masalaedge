import pandas as pd
from collections import Counter

# --- CONFIGURATION ---
INPUT_FILE = 'dishes_with_tags_fuzzy.xlsx'
# We will find the top N most common words to consider as new keywords
TOP_N_WORDS = 50
# Words to ignore (common, non-descriptive words)
STOP_WORDS = {'and', 'with', 'in', 'recipe', 'style', 'masala', 'fry'}

def analyze_untagged_dishes():
    """
    Analyzes the untagged dishes and suggests new keywords.
    """
    try:
        df = pd.read_excel(INPUT_FILE)
    except FileNotFoundError:
        print(f"FATAL: Input file not found at '{INPUT_FILE}'.")
        return

    # Filter for rows where the 'tags' column is empty/NaN
    df_untagged = df[df['tags'].isnull() | (df['tags'] == '')]

    if df_untagged.empty:
        print("✅ No untagged dishes found. Great job!")
        return

    print(f"Found {len(df_untagged)} untagged dishes. Analyzing for common words...")

    all_words = []
    # Tokenize the dish names into individual words
    for dish_name in df_untagged['dish_name']:
        words = str(dish_name).lower().split()
        all_words.extend([word for word in words if word not in STOP_WORDS])
    
    # Count the frequency of each word
    word_counts = Counter(all_words)

    print(f"\n--- Top {TOP_N_WORDS} Potential New Keywords ---")
    for word, count in word_counts.most_common(TOP_N_WORDS):
        print(f"{word:<20} (appeared {count} times)")

if __name__ == '__main__':
    analyze_untagged_dishes()