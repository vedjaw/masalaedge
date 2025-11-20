# Multimodal Culinary Instruction-Tuning Dataset
**Project Type:** Semester Group Project (LLM Fine-tuning)  
**Tech Stack:** Python, Pandas, TheFuzz, Fuzzy String Matching, Synthetic Data Generation

---

## 1. Executive Summary
The objective of this project was to build a high-quality, domain-specific dataset to fine-tune SigLip capable of acting as a culinary recommendation agent. 

Starting with a raw inventory of **~16,000 unique dishes** (approx. 100k total rows), I architected an iterative data engineering pipeline that enriched the data with semantic tags and expanded it via synthetic natural language generation. The final output was a robust dataset of **~800,000 training triplets** (`text_query`, `image_url`, `dish_name`), covering diverse user intents such as dietary restrictions, flavor profiles, and emotional context (e.g., "comfort food").

---

## 2. The Data Pipeline Architecture
The pipeline consisted of three distinct phases using a "Human-in-the-Loop" iterative approach to ensure high coverage and data quality.

### Phase 1: Semantic Enrichment (Fuzzy Tagging)
**Script:** `tag_dishes.py`

The raw data contained only dish names (e.g., *"Paneer Tikka Masala"*) and image URLs. To make this useful for an LLM, we needed to associate these names with concepts (e.g., *Vegetarian*, *Spicy*, *North Indian*).

* **The Knowledge Base:** I constructed a comprehensive dictionary (`KEYWORD_TO_TAGS`) mapping specific keywords to semantic tags.
* **Fuzzy Logic:** Instead of simple string matching, I utilized the **`thefuzz`** library. specifically `fuzz.token_set_ratio`. This allowed for robust matching even with noisy data (e.g., matching "Spicy Pneer Tika" to the "Paneer" keyword).
* **Process:**
    1.  Ingest raw Excel data (`dish_names.xlsx`).
    2.  Iterate through every dish name.
    3.  Calculate similarity scores against the knowledge base keywords.
    4.  Assign tags if the similarity score exceeded a threshold (Score > 65).

### Phase 2: Iterative Refinement (The Optimization Loop)
**Script:** `find_new_keywords.py`

After the initial tagging pass, many dishes remained untagged because the dictionary was incomplete. Instead of guessing new keywords, I wrote a script to analyze the data.

* **Frequency Analysis:** The script isolated all rows that received NO tags in Phase 1.
* **Tokenization:** It broke down the dish names into individual words, removed stop words (e.g., "and", "with", "recipe"), and used `collections.Counter` to find the most frequent unmapped words.
* **The Iterative Cycle:**
    1.  Run `tag_dishes.py`.
    2.  Run `find_new_keywords.py` to see what was missed (e.g., discovering that "Schezwan" appears 500 times but wasn't in the dictionary).
    3.  Manually update the `KEYWORD_TO_TAGS` dictionary in Phase 1 with these new terms.
    4.  **Repeat** until >95% of the dataset was successfully tagged.

### Phase 3: Synthetic Data Augmentation
**Script:** `generate_training_data.py`

Once the dishes were tagged with attributes (e.g., `['rainy_day', 'snack', 'fried']`), I needed to convert these structured tags into natural language prompts that a user would actually type.

* **Template Engineering:** I designed a mapping system (`TAG_TO_TEMPLATES`) to translate tags into human-like queries.
    * *Tag:* `rainy_day` $\rightarrow$ *Query:* "It's pouring outside, suggest a cozy snack."
    * *Tag:* `spicy` $\rightarrow$ *Query:* "I want something fiery and hot."
* **Combinatorial Expansion:** For every image, the system generated multiple unique text queries (up to 8 per image) based on its varied tags.
* **Multimodal Linking:** The script merged the generated text with the original `image_url` to create the final triplet structure required for the model.

---

## 3. Technical Implementation Details

### Key Libraries Used
* **`pandas`**: For high-performance data manipulation and merging of large CSV/Excel files.
* **`thefuzz`**: For approximate string matching (Levenshtein distance) to handle typos and variations in dish names.
* **`tqdm`**: To monitor processing speed and estimated time of arrival (ETA) during the processing of 100k+ rows.
* **`random`**: To sample queries stochastically, ensuring the model doesn't overfit to a specific sentence structure.

### The "Human-in-the-Loop" Logic
The success of this dataset relied on the interaction between `tag_dishes.py` and `find_new_keywords.py`. This prevented the "Black Box" problem where data engineers don't know why their data is poor. By mathematically identifying the most frequent missing terms, I rapidly scaled the dictionary from covering generic terms to covering niche culinary terms (e.g., *"Schezwan"*, *"Alfredo"*, *"Tandoori"*).

---

## 4. Final Results & Impact

| Metric | Initial State | Final State |
| :--- | :--- | :--- |
| **Entities** | ~16,000 Unique Dishes | ~16,000 Unique Dishes |
| **Total Rows** | ~100,000 Raw Rows | **~800,000 Training Samples** |
| **Data Type** | Raw Text + Images | **(Query, Image, Context) Triplets** |
| **Coverage** | N/A | Mood, Taste, Dietary, Cuisine, Texture |

**Key Achievements:**
1.  **Context Awareness:** The dataset goes beyond keyword search. It maps abstract concepts like "Comfort Food" or "Summer Food" to specific dishes, enabling the LLM to understand user *intent*.
2.  **Scale:** Successfully generated a dataset large enough for significant fine-tuning tasks (approaching 1M rows).
3.  **Data Quality:** By using fuzzy matching, the pipeline was resilient to spelling errors in the source data, a common issue in real-world scraped datasets.
