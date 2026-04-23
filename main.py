from pathlib import Path
import re

from fastapi import FastAPI, Query

from meal_steps import MEAL_STEPS
from fastapi.responses import HTMLResponse
import random

app = FastAPI()

NON_GF_INGREDIENT_KEYWORDS = {
    "wheat",
    "flour",
    "bread",
    "pasta",
    "noodle",
    "tortilla",
    "wrap",
    "wonton",
    # Regular wheat-based soy sauce is not listed here; recipes use certified gf soya sauce / tamari by name.
    "hoisin",
    "granola",
}

MEALS = [
    {"name": "One Pot Chicken Rice", "type": "Dinner", "ingredients": ["chicken", "rice", "garlic", "onion", "chicken broth", "water", "salt", "black pepper", "vegetable oil"]},
    {"name": "Chicken Lettuce Wrap", "type": "Lunch", "ingredients": ["ground chicken", "lettuce", "hoisin sauce", "gf soya sauce", "garlic", "sesame oil", "green onions", "salt", "vegetable oil"]},
    {"name": "Chicken Wings", "type": "Dinner", "ingredients": ["chicken wings", "garlic powder", "paprika", "oil", "hot sauce", "salt", "black pepper", "baking powder"]},
    {"name": "Vegetable Stir-Fry", "type": "Dinner", "ingredients": ["broccoli", "bell peppers", "carrots", "gf soya sauce", "garlic", "vegetable oil", "ginger", "sesame oil", "salt", "cornstarch"]},
    {"name": "Green Curry Chicken Thai", "type": "Dinner", "ingredients": ["chicken", "green curry paste", "coconut milk", "bell peppers", "basil", "fish sauce", "lime", "brown sugar", "vegetable oil", "salt"]},
    {"name": "Pasta", "type": "Dinner", "ingredients": ["pasta", "tomato sauce", "garlic", "olive oil", "parmesan cheese", "salt", "black pepper", "red pepper flakes", "fresh basil"]},
    {"name": "Burrito Bowls", "type": "Lunch", "ingredients": ["rice", "chicken", "black beans", "corn", "avocado", "lime", "cilantro", "cumin", "chili powder", "salt", "olive oil", "sour cream"]},
    {"name": "Tacos", "type": "Lunch", "ingredients": ["tortillas", "ground turkey", "lettuce", "cheese", "salsa", "onion", "cumin", "chili powder", "garlic powder", "salt", "vegetable oil", "lime"]},
    {"name": "Veggie Fried Rice", "type": "Dinner", "ingredients": ["rice", "eggs", "carrots", "peas", "gf soya sauce", "vegetable oil", "garlic", "green onions", "sesame oil", "salt", "black pepper"]},
    {"name": "Coconut Chickpea Curry", "type": "Dinner", "ingredients": ["chickpeas", "coconut milk", "curry powder", "tomatoes", "onion", "garlic", "ginger", "vegetable oil", "salt", "spinach"]},
    {"name": "Chicken Stir Fry", "type": "Dinner", "ingredients": ["chicken", "broccoli", "gf soya sauce", "garlic", "bell peppers", "vegetable oil", "ginger", "cornstarch", "sesame oil", "salt", "green onions"]},
    {"name": "Shrimp Garlic Butter Pasta", "type": "Dinner", "ingredients": ["shrimp", "pasta", "garlic", "butter", "parsley", "salt", "black pepper", "lemon", "olive oil", "white wine"]},
    {"name": "Vegetable Fried Rice", "type": "Lunch", "ingredients": ["rice", "eggs", "carrots", "peas", "gf soya sauce", "vegetable oil", "garlic", "green onions", "sesame oil", "salt", "black pepper"]},
    {"name": "Chicken Burrito Bowl", "type": "Lunch", "ingredients": ["chicken", "rice", "black beans", "corn", "avocado", "lime", "cilantro", "cumin", "salt", "olive oil", "sour cream", "shredded cheese"]},
    {"name": "Grilled Salmon Bowl", "type": "Dinner", "ingredients": ["salmon", "rice", "cucumber", "avocado", "gf soya sauce", "sesame oil", "rice vinegar", "salt", "black pepper", "sesame seeds", "green onions"]},
    {"name": "Veggie Omelette", "type": "Breakfast", "ingredients": ["eggs", "spinach", "cheese", "mushrooms", "onion", "butter", "salt", "black pepper", "milk"]},
    {"name": "Chicken Caesar Wrap", "type": "Lunch", "ingredients": ["chicken", "tortilla", "lettuce", "caesar dressing", "parmesan", "salt", "black pepper", "lemon juice", "olive oil"]},
    {"name": "Garlic Butter Shrimp Rice", "type": "Dinner", "ingredients": ["shrimp", "rice", "garlic", "butter", "lemon", "chicken broth", "salt", "black pepper", "parsley", "white wine"]},
    {"name": "Chickpea Curry", "type": "Dinner", "ingredients": ["chickpeas", "coconut milk", "curry powder", "tomatoes", "onion", "garlic", "ginger", "vegetable oil", "salt", "spinach"]},
    {"name": "Chicken Noodle Soup", "type": "Dinner", "ingredients": ["chicken", "noodles", "carrots", "celery", "chicken broth", "onion", "garlic", "bay leaves", "salt", "black pepper", "fresh parsley"]},
    {"name": "Avocado Toast with Egg", "type": "Breakfast", "ingredients": ["bread", "avocado", "eggs", "lemon", "olive oil", "salt", "black pepper", "red pepper flakes"]},
    {"name": "Shrimp Tacos", "type": "Dinner", "ingredients": ["shrimp", "tortillas", "cabbage", "lime", "sauce", "garlic", "cumin", "chili powder", "salt", "olive oil", "cilantro", "sour cream"]},
    {"name": "Vegetable Pasta", "type": "Dinner", "ingredients": ["pasta", "zucchini", "tomato sauce", "garlic", "olive oil", "salt", "black pepper", "red pepper flakes", "parmesan cheese", "fresh basil"]},
    {"name": "Chicken Lettuce Wraps", "type": "Lunch", "ingredients": ["ground chicken", "lettuce", "hoisin sauce", "gf soya sauce", "garlic", "sesame oil", "green onions", "salt", "vegetable oil", "water chestnuts"]},
    {"name": "Fried Egg Rice Bowl", "type": "Lunch", "ingredients": ["rice", "egg", "green onions", "gf soya sauce", "sesame oil", "vegetable oil", "garlic", "salt", "black pepper"]},
    {"name": "Baked Salmon and Veggies", "type": "Dinner", "ingredients": ["salmon", "broccoli", "carrots", "olive oil", "lemon", "garlic", "salt", "black pepper", "dill"]},
    {"name": "Caprese Salad", "type": "Lunch", "ingredients": ["tomatoes", "mozzarella", "basil", "olive oil", "balsamic", "salt", "black pepper", "flaky sea salt"]},
    {"name": "Chicken Alfredo Pasta", "type": "Dinner", "ingredients": ["chicken", "pasta", "cream", "garlic", "parmesan", "butter", "salt", "black pepper", "nutmeg", "parsley"]},
    {"name": "Veggie Quesadilla", "type": "Lunch", "ingredients": ["tortilla", "cheese", "bell peppers", "onion", "corn", "butter", "cumin", "salt", "black pepper", "sour cream"]},
    {"name": "Shrimp Fried Rice", "type": "Dinner", "ingredients": ["rice", "shrimp", "egg", "peas", "gf soya sauce", "vegetable oil", "garlic", "green onions", "sesame oil", "salt", "black pepper"]},
    {"name": "Blueberry Pancakes", "type": "Breakfast", "ingredients": ["flour", "milk", "eggs", "blueberries", "baking powder", "sugar", "salt", "butter", "vanilla extract"]},
    {"name": "Strawberry Banana Smoothie Bowl", "type": "Breakfast", "ingredients": ["strawberries", "banana", "yogurt", "granola", "honey", "ice", "milk", "chia seeds"]},
    {"name": "Egg and Cheese Breakfast Sandwich", "type": "Breakfast", "ingredients": ["bread", "eggs", "cheese", "butter", "milk", "salt", "black pepper", "mayonnaise"]},
    {"name": "Apple Cinnamon Oatmeal", "type": "Breakfast", "ingredients": ["oats", "apple", "cinnamon", "milk", "maple syrup", "salt", "butter", "vanilla extract"]},
    {"name": "Spinach Feta Breakfast Wrap", "type": "Breakfast", "ingredients": ["tortilla", "spinach", "feta cheese", "eggs", "olive oil", "salt", "black pepper", "red onion"]},
    {"name": "Peanut Butter Banana Toast", "type": "Breakfast", "ingredients": ["bread", "peanut butter", "banana", "honey", "chia seeds", "cinnamon", "salt"]},
    {"name": "Breakfast Burrito", "type": "Breakfast", "ingredients": ["tortilla", "eggs", "potatoes", "cheese", "salsa", "butter", "salt", "black pepper", "cumin", "sour cream"]},
    {"name": "Chocolate Chip Waffles", "type": "Breakfast", "ingredients": ["flour", "milk", "eggs", "chocolate chips", "butter", "baking powder", "sugar", "salt", "vanilla extract"]},
    {"name": "Mango Yogurt Bowl", "type": "Breakfast", "ingredients": ["yogurt", "mango", "granola", "honey", "coconut flakes", "lime", "chia seeds"]},
    {"name": "Egg Muffins", "type": "Breakfast", "ingredients": ["eggs", "spinach", "cheese", "bell peppers", "milk", "salt", "black pepper", "onion powder"]},
    {"name": "French Toast", "type": "Breakfast", "ingredients": ["bread", "eggs", "milk", "cinnamon", "maple syrup", "butter", "vanilla extract", "salt", "nutmeg"]},
    {"name": "Chia Seed Pudding", "type": "Breakfast", "ingredients": ["chia seeds", "milk", "honey", "vanilla", "berries", "maple syrup", "cinnamon"]},
    {"name": "Breakfast Quesadilla", "type": "Breakfast", "ingredients": ["tortilla", "eggs", "cheese", "spinach", "butter", "salt", "black pepper", "salsa"]},
    {"name": "Avocado Egg Bowl", "type": "Breakfast", "ingredients": ["avocado", "eggs", "rice", "green onions", "gf soya sauce", "sesame oil", "salt", "sesame seeds", "lime"]},
    {"name": "Cinnamon Roll Oatmeal", "type": "Breakfast", "ingredients": ["oats", "milk", "cinnamon", "brown sugar", "cream cheese", "salt", "butter", "vanilla extract"]},
    {"name": "Berry Protein Smoothie", "type": "Breakfast", "ingredients": ["berries", "protein powder", "milk", "banana", "honey", "ice", "yogurt", "chia seeds"]},
    {"name": "Ham and Cheese Omelette", "type": "Breakfast", "ingredients": ["eggs", "ham", "cheese", "milk", "butter", "salt", "black pepper", "chives"]},
    {"name": "Granola with Milk", "type": "Breakfast", "ingredients": ["granola", "milk", "berries", "honey", "nuts", "banana", "cinnamon"]},
    {"name": "Savory Breakfast Rice Bowl", "type": "Breakfast", "ingredients": ["rice", "eggs", "gf soya sauce", "green onions", "sesame oil", "vegetable oil", "garlic", "salt", "sesame seeds"]},
    {"name": "Almond Butter Toast with Berries", "type": "Breakfast", "ingredients": ["bread", "almond butter", "strawberries", "honey", "chia seeds", "cinnamon", "sea salt"]},
    {"name": "Greek Yogurt Berry Parfait", "type": "Breakfast", "ingredients": ["yogurt", "berries", "honey", "chia seeds", "almonds", "vanilla extract", "granola"]},
    {"name": "Spinach Mushroom Frittata", "type": "Breakfast", "ingredients": ["eggs", "spinach", "mushrooms", "onion", "cheese", "olive oil", "salt", "black pepper", "garlic", "milk"]},
    {"name": "Coconut Chia Mango Bowl", "type": "Breakfast", "ingredients": ["chia seeds", "coconut milk", "mango", "honey", "coconut flakes", "vanilla extract", "lime"]},
    {"name": "Tomato Basil Omelette", "type": "Breakfast", "ingredients": ["eggs", "tomatoes", "basil", "cheese", "olive oil", "salt", "black pepper", "butter", "garlic"]},
    {"name": "Breakfast Sweet Potato Hash", "type": "Breakfast", "ingredients": ["sweet potato", "eggs", "onion", "bell peppers", "olive oil", "garlic", "salt", "black pepper", "paprika", "fresh parsley"]},
    {"name": "Lemon Herb Salmon", "type": "Dinner", "ingredients": ["salmon", "lemon", "garlic", "olive oil", "parsley", "salt", "black pepper", "dill", "butter"]},
    {"name": "Garlic Shrimp Quinoa Bowl", "type": "Dinner", "ingredients": ["shrimp", "quinoa", "garlic", "spinach", "lemon", "butter", "salt", "black pepper", "chicken broth", "red pepper flakes"]},
    {"name": "Stuffed Bell Peppers", "type": "Dinner", "ingredients": ["bell peppers", "ground turkey", "rice", "tomatoes", "onion", "garlic", "tomato sauce", "Italian seasoning", "salt", "black pepper", "mozzarella cheese", "chicken broth"]},
    {"name": "Chicken Cauliflower Rice Bowl", "type": "Dinner", "ingredients": ["chicken", "cauliflower rice", "broccoli", "garlic", "olive oil", "gf soya sauce", "ginger", "salt", "black pepper", "green onions", "sesame oil"]},
    {"name": "Zucchini Turkey Skillet", "type": "Dinner", "ingredients": ["ground turkey", "zucchini", "tomatoes", "garlic", "onion", "olive oil", "Italian seasoning", "salt", "black pepper", "parmesan cheese", "red pepper flakes"]},
    {"name": "Lentil Coconut Stew", "type": "Dinner", "ingredients": ["lentils", "coconut milk", "tomatoes", "onion", "curry powder", "garlic", "ginger", "vegetable broth", "salt", "spinach", "vegetable oil"]},
    {"name": "Baked Cod with Veggies", "type": "Dinner", "ingredients": ["cod", "broccoli", "carrots", "lemon", "olive oil", "garlic", "salt", "black pepper", "paprika", "butter", "fresh parsley"]},
    {"name": "Chicken Tomato Basil Bake", "type": "Dinner", "ingredients": ["chicken", "tomatoes", "basil", "mozzarella", "olive oil", "garlic", "salt", "black pepper", "balsamic vinegar", "Italian seasoning"]},
    {"name": "Avocado Tuna Salad Bowl", "type": "Lunch", "ingredients": ["tuna", "avocado", "cucumber", "lemon", "olive oil", "red onion", "mayonnaise", "salt", "black pepper", "cilantro", "celery"]},
    {"name": "Quinoa Chickpea Salad", "type": "Lunch", "ingredients": ["quinoa", "chickpeas", "cucumber", "tomatoes", "olive oil", "lemon juice", "red onion", "salt", "black pepper", "fresh parsley", "feta cheese"]},
    {"name": "Egg Salad Lettuce Cups", "type": "Lunch", "ingredients": ["eggs", "lettuce", "mustard", "olive oil", "green onions", "mayonnaise", "salt", "black pepper", "paprika", "celery", "lemon juice"]},
    {"name": "Turkey Rice Bowl", "type": "Lunch", "ingredients": ["ground turkey", "rice", "spinach", "carrots", "garlic", "gf soya sauce", "sesame oil", "ginger", "salt", "green onions", "vegetable oil"]},
    {"name": "Mediterranean Chicken Salad", "type": "Lunch", "ingredients": ["chicken", "cucumber", "tomatoes", "feta cheese", "olive oil", "lemon juice", "red onion", "oregano", "salt", "black pepper", "kalamata olives", "fresh mint"]},
    {"name": "Black Bean Corn Rice Bowl", "type": "Lunch", "ingredients": ["black beans", "corn", "rice", "avocado", "lime", "cilantro", "salt", "olive oil", "cumin", "chili powder", "tomatoes", "red onion"]},
    {"name": "Shrimp Avocado Cucumber Salad", "type": "Lunch", "ingredients": ["shrimp", "avocado", "cucumber", "lime", "olive oil", "salt", "black pepper", "cilantro", "red onion", "jalapeño", "garlic"]},
    # Snacks: Lean Green Bean roundup-inspired (below) + PureWow “48 Easy Snacks” (after; no red meat).
    # TLG: https://www.theleangreenbean.com/homemade-snacks-to-make/
    {"name": "Lemon Oat Energy Balls", "type": "Snack", "ingredients": ["oats", "medjool dates", "lemon", "coconut flakes", "honey", "vanilla extract", "salt", "chia seeds"]},
    {"name": "Chewy Homemade Granola Bars", "type": "Snack", "ingredients": ["oats", "honey", "butter", "brown sugar", "vanilla extract", "salt", "cinnamon", "chopped almonds"]},
    {"name": "Greek Yogurt Ranch Dip", "type": "Snack", "ingredients": ["greek yogurt", "dried dill", "garlic powder", "onion powder", "lemon juice", "salt", "black pepper", "chives"]},
    {"name": "Berry Yogurt Smoothie Snack", "type": "Snack", "ingredients": ["mixed berries", "banana", "greek yogurt", "milk", "honey", "ice", "vanilla extract"]},
    {"name": "Turkey Cheese Apple Skewers", "type": "Snack", "ingredients": ["turkey breast", "cheddar cheese", "apple", "lemon juice", "salt", "black pepper"]},
    {"name": "Chocolate Avocado Pudding Cups", "type": "Snack", "ingredients": ["avocado", "cocoa powder", "medjool dates", "maple syrup", "vanilla extract", "salt", "almond milk"]},
    {"name": "Ranch Popcorn Snack", "type": "Snack", "ingredients": ["popcorn kernels", "butter", "nutritional yeast", "garlic powder", "onion powder", "dried parsley", "salt", "black pepper"]},
    {"name": "Microwave Egg Snack Sandwich", "type": "Snack", "ingredients": ["eggs", "english muffin", "cheddar cheese", "butter", "spinach", "salt", "black pepper"]},
    {"name": "Turkey Cheddar Lettuce Roll Ups", "type": "Snack", "ingredients": ["turkey slices", "cheddar cheese", "lettuce", "mustard", "mayonnaise", "salt", "black pepper"]},
    {"name": "Quick Yogurt Snack Bowl", "type": "Snack", "ingredients": ["greek yogurt", "mixed berries", "honey", "walnuts", "cinnamon", "mini chocolate chips"]},
    {"name": "Veggie Black Bean Nachos", "type": "Snack", "ingredients": ["corn chips", "black beans", "cheddar cheese", "jalapeño", "salsa", "sour cream", "green onions", "cumin", "lime"]},
    {"name": "Sweet Potato White Bean Squares", "type": "Snack", "ingredients": ["sweet potato", "cannellini beans", "oats", "eggs", "maple syrup", "cinnamon", "vanilla extract", "salt", "baking powder"]},
    {"name": "Overnight Oats Snack Jars", "type": "Snack", "ingredients": ["oats", "milk", "chia seeds", "greek yogurt", "berries", "honey", "vanilla extract", "salt"]},
    {"name": "Homemade Trail Mix", "type": "Snack", "ingredients": ["almonds", "pumpkin seeds", "dried cranberries", "dark chocolate chips", "coconut flakes", "salt"]},
    {"name": "Hard-Boiled Egg Snack Pack", "type": "Snack", "ingredients": ["eggs", "everything bagel seasoning", "salt", "cherry tomatoes", "cucumber"]},
    {"name": "Baked Blueberry Oatmeal Bars", "type": "Snack", "ingredients": ["oats", "milk", "eggs", "maple syrup", "blueberries", "baking powder", "vanilla extract", "salt", "cinnamon"]},
    {"name": "Apple Peanut Butter Nachos", "type": "Snack", "ingredients": ["apples", "peanut butter", "granola", "honey", "mini chocolate chips", "cinnamon"]},
    {"name": "Silver Dollar Pancake Snacks", "type": "Snack", "ingredients": ["flour", "milk", "eggs", "baking powder", "sugar", "salt", "butter", "maple syrup", "berries"]},
    {"name": "Cottage Cheese Snack Bowl", "type": "Snack", "ingredients": ["cottage cheese", "cherry tomatoes", "cucumber", "olive oil", "salt", "black pepper", "fresh basil"]},
    {"name": "Chicken Salad Snack Box", "type": "Snack", "ingredients": ["chicken breast", "greek yogurt", "mayonnaise", "celery", "red grapes", "lemon juice", "salt", "black pepper", "rice cakes"]},
    {"name": "Pumpkin Peanut Butter Oat Squares", "type": "Snack", "ingredients": ["pumpkin puree", "peanut butter", "oats", "honey", "cinnamon", "vanilla extract", "salt", "nutmeg"]},
    {"name": "Air Fryer Chicken Bites", "type": "Snack", "ingredients": ["chicken tenders", "olive oil", "paprika", "garlic powder", "salt", "black pepper", "gf soya sauce", "honey"]},
    {"name": "Homemade Fruit Leather", "type": "Snack", "ingredients": ["apples", "strawberries", "honey", "lemon juice", "cinnamon", "water"]},
    {"name": "Turkey Lettuce Snack Wraps", "type": "Snack", "ingredients": ["turkey breast", "butter lettuce", "bell peppers", "italian dressing", "provolone cheese", "salt", "black pepper"]},
    {"name": "Crispy Sweet Potato Chips", "type": "Snack", "ingredients": ["sweet potato", "olive oil", "cornstarch", "salt", "paprika", "garlic powder", "black pepper"]},
    {"name": "Frozen Yogurt Fruit Tubes", "type": "Snack", "ingredients": ["greek yogurt", "mixed berries", "honey", "vanilla extract", "lemon juice"]},
    # Snacks from PureWow "48 Easy Snacks" — red-meat items omitted (prosciutto, bacon, pork, chorizo).
    {"name": "Chocolate-Strawberry Energy Bites", "type": "Snack", "ingredients": ["oats", "peanut butter", "dark chocolate", "freeze-dried strawberries", "honey", "vanilla extract", "salt", "chia seeds"]},
    {"name": "Garlic Parmesan Popcorn", "type": "Snack", "ingredients": ["popcorn", "butter", "garlic", "parmesan cheese", "salt", "black pepper", "olive oil"]},
    {"name": "Lemon-y Avocado Toast", "type": "Snack", "ingredients": ["bread", "avocado", "lemon", "salt", "olive oil", "red pepper flakes", "black pepper"]},
    {"name": "15-Minute Mezze Plate with Za'atar Pita", "type": "Snack", "ingredients": ["pita bread", "hummus", "marinated artichoke hearts", "roasted red peppers", "olives", "za'atar", "olive oil", "lemon", "cucumber", "feta cheese"]},
    {"name": "Roasted Veggie Chips", "type": "Snack", "ingredients": ["sweet potato", "olive oil", "salt", "herbs", "black pepper", "garlic powder", "paprika"]},
    {"name": "Crudi-Tots Platter", "type": "Snack", "ingredients": ["tater tots", "carrots", "cucumber", "bell peppers", "dip", "ranch dressing", "salt", "cherry tomatoes"]},
    {"name": "Easy Homemade Pickles", "type": "Snack", "ingredients": ["cucumbers", "vinegar", "water", "salt", "sugar", "garlic", "dill", "mustard seeds", "black peppercorns"]},
    {"name": "Italian Deli Pinwheels (Turkey)", "type": "Snack", "ingredients": ["flour tortillas", "turkey", "cheese", "lettuce", "mayonnaise", "salt", "black pepper", "Italian seasoning", "tomatoes"]},
    {"name": "Cinnamon Roll Snowmen", "type": "Snack", "ingredients": ["cinnamon roll dough", "icing", "sprinkles", "candy eyes", "food coloring", "butter", "powdered sugar"]},
    {"name": "Gwyneth Paltrow Blueberry Cauliflower Smoothie", "type": "Snack", "ingredients": ["blueberries", "cauliflower", "almond milk", "protein powder", "ice", "banana", "honey", "cinnamon"]},
    {"name": "Ants on a Log", "type": "Snack", "ingredients": ["celery", "peanut butter", "raisins", "honey", "salt", "cinnamon"]},
    {"name": "Roasted Pumpkin Seeds", "type": "Snack", "ingredients": ["pumpkin seeds", "olive oil", "salt", "curry powder", "paprika", "garlic powder", "cayenne"]},
    {"name": "Rainbow Snack Mix", "type": "Snack", "ingredients": ["white chocolate", "pretzels", "chex cereal", "roasted nuts", "dried berries", "coconut oil", "salt", "vanilla extract"]},
    {"name": "Watermelon Salsa", "type": "Snack", "ingredients": ["watermelon", "jalapeño", "lime", "cilantro", "red onion", "salt", "black pepper", "cumin", "olive oil"]},
    {"name": "Baked Bananas", "type": "Snack", "ingredients": ["bananas", "cinnamon", "honey", "nut butter", "salt", "butter", "vanilla extract"]},
    {"name": "One-Ingredient Watermelon Sorbet", "type": "Snack", "ingredients": ["watermelon", "fresh mint", "lime juice"]},
    {"name": "Salted Peanut Butter Cup Smoothie", "type": "Snack", "ingredients": ["peanut butter", "cocoa powder", "almond milk", "banana", "sea salt", "ice", "honey", "vanilla extract"]},
    {"name": "Broiler S'mores", "type": "Snack", "ingredients": ["graham crackers", "marshmallows", "chocolate", "butter", "salt", "cinnamon"]},
    {"name": "Golden Oreo Truffles", "type": "Snack", "ingredients": ["golden oreos", "cream cheese", "melted chocolate", "vanilla", "salt", "powdered sugar", "coconut oil"]},
    {"name": "Sweet Potato Fries", "type": "Snack", "ingredients": ["sweet potato", "olive oil", "salt", "paprika", "garlic powder", "cornstarch", "black pepper", "ketchup"]},
    {"name": "Cinnamon Toast Crunch Muffins", "type": "Snack", "ingredients": ["spice cake mix", "pumpkin puree", "cinnamon toast crunch", "brown sugar", "butter", "eggs", "water", "vegetable oil"]},
    {"name": "Jammy Soft-Boiled Eggs", "type": "Snack", "ingredients": ["eggs", "ice water", "salt", "gf soya sauce", "sesame seeds", "green onions", "rice vinegar"]},
    {"name": "Pizza Trail Mix", "type": "Snack", "ingredients": ["nuts", "sun-dried tomatoes", "cheese crisps", "italian seasoning", "olive oil", "garlic powder", "salt", "black pepper", "parmesan cheese"]},
    {"name": "Peanut Toffee Chocolate Clusters", "type": "Snack", "ingredients": ["peanuts", "chocolate", "toffee bits", "butter", "salt", "vanilla extract", "corn syrup"]},
    {"name": "Roasted Chickpeas", "type": "Snack", "ingredients": ["chickpeas", "olive oil", "smoked paprika", "garlic powder", "sumac", "salt", "cumin", "lemon juice"]},
    {"name": "Chocolate Granola", "type": "Snack", "ingredients": ["oats", "brown sugar", "cocoa powder", "almonds", "chocolate chunks", "honey", "coconut oil", "salt", "vanilla extract", "cinnamon"]},
    {"name": "Easy Cherry Almond Granola Bars", "type": "Snack", "ingredients": ["oats", "dried cherries", "almonds", "honey", "butter", "brown sugar", "vanilla extract", "salt", "cinnamon"]},
    {"name": "Tater Tot Nachos (Black Bean)", "type": "Snack", "ingredients": ["tater tots", "black beans", "cheese", "salsa", "jalapeño", "sour cream", "green onions", "cumin", "lime", "olive oil"]},
    {"name": "Spicy Avocado Hummus", "type": "Snack", "ingredients": ["chickpeas", "avocado", "tahini", "garlic", "cayenne", "lemon juice", "olive oil", "salt", "cumin", "paprika"]},
    {"name": "Five-Ingredient Golden Milk Snack Bites", "type": "Snack", "ingredients": ["cashew butter", "turmeric", "maple syrup", "coconut flakes", "dates", "cinnamon", "black pepper", "salt", "vanilla extract"]},
    {"name": "Fresh Fruit Ice Pops", "type": "Snack", "ingredients": ["fruit juice", "fresh fruit", "honey", "water", "vanilla", "lemon juice", "mint"]},
    {"name": "Thick Italian Hot Chocolate", "type": "Snack", "ingredients": ["milk", "bittersweet chocolate", "cornstarch", "sugar", "vanilla", "salt", "cinnamon", "whipped cream"]},
    {"name": "Roasted Edamame", "type": "Snack", "ingredients": ["edamame", "olive oil", "smoked paprika", "lemon zest", "salt", "garlic powder", "sesame seeds", "gf soya sauce"]},
    {"name": "Buffalo Chicken Brie Bites", "type": "Snack", "ingredients": ["chicken", "brie", "buffalo sauce", "puff pastry", "green onions", "egg", "salt", "black pepper", "blue cheese crumbles"]},
    {"name": "Cajun Shrimp Guacamole Bites", "type": "Snack", "ingredients": ["shrimp", "avocado", "lime", "cajun seasoning", "cilantro", "red onion", "salt", "garlic", "tomato", "tortilla chips"]},
    {"name": "Grilled Cheese Crostini", "type": "Snack", "ingredients": ["bread", "brie", "strawberries", "balsamic vinegar", "mint", "butter", "honey", "salt", "black pepper"]},
    {"name": "Sourdough with Whipped Cottage Cheese and Raspberry Chia Jam", "type": "Snack", "ingredients": ["sourdough bread", "cottage cheese", "raspberries", "chia seeds", "honey", "lemon juice", "vanilla extract", "salt", "butter"]},
    {"name": "Mini Yogurt Cheesecakes", "type": "Snack", "ingredients": ["graham crackers", "greek yogurt", "cream cheese", "eggs", "vanilla", "sugar", "salt", "butter", "lemon zest"]},
    {"name": "Vegan Banana Bread", "type": "Snack", "ingredients": ["bananas", "flour", "flax egg", "walnuts", "plant milk", "baking soda", "baking powder", "salt", "sugar", "vanilla extract", "coconut oil"]},
    {"name": "Smoky Savory Fire Crackers", "type": "Snack", "ingredients": ["saltine crackers", "vegetable oil", "ranch seasoning", "red pepper flakes", "garlic powder", "onion powder", "paprika", "salt"]},
    {"name": "3-Ingredient Shredded Chicken Flautas", "type": "Snack", "ingredients": ["chicken", "flour tortillas", "cheese", "sour cream", "salsa", "vegetable oil", "cumin", "salt", "green onions"]},
    {"name": "Homemade Cheese Crackers", "type": "Snack", "ingredients": ["cheddar cheese", "parmesan cheese", "flour", "butter", "salt", "ice water", "black pepper", "paprika"]},
    {"name": "Grated Egg Toast", "type": "Snack", "ingredients": ["bread", "avocado", "eggs", "salt", "black pepper", "olive oil", "lemon juice", "red pepper flakes", "microgreens"]},
]

# Approximate active prep + cook time (rough estimates).
PREP_TIME_BY_NAME: dict[str, str] = {
    "One Pot Chicken Rice": "~ 40 min",
    "Chicken Lettuce Wrap": "~ 25 min",
    "Chicken Wings": "~ 50 min",
    "Vegetable Stir-Fry": "~ 25 min",
    "Green Curry Chicken Thai": "~ 35 min",
    "Pasta": "~ 30 min",
    "Burrito Bowls": "~ 30 min",
    "Tacos": "~ 20 min",
    "Veggie Fried Rice": "~ 25 min",
    "Coconut Chickpea Curry": "~ 40 min",
    "Chicken Stir Fry": "~ 25 min",
    "Shrimp Garlic Butter Pasta": "~ 30 min",
    "Vegetable Fried Rice": "~ 25 min",
    "Chicken Burrito Bowl": "~ 25 min",
    "Grilled Salmon Bowl": "~ 30 min",
    "Veggie Omelette": "~ 15 min",
    "Chicken Caesar Wrap": "~ 15 min",
    "Garlic Butter Shrimp Rice": "~ 20 min",
    "Chickpea Curry": "~ 35 min",
    "Chicken Noodle Soup": "~ 50 min",
    "Avocado Toast with Egg": "~ 10 min",
    "Shrimp Tacos": "~ 20 min",
    "Vegetable Pasta": "~ 30 min",
    "Chicken Lettuce Wraps": "~ 20 min",
    "Fried Egg Rice Bowl": "~ 20 min",
    "Baked Salmon and Veggies": "~ 35 min",
    "Caprese Salad": "~ 10 min",
    "Chicken Alfredo Pasta": "~ 35 min",
    "Veggie Quesadilla": "~ 15 min",
    "Shrimp Fried Rice": "~ 20 min",
    "Blueberry Pancakes": "~ 25 min",
    "Strawberry Banana Smoothie Bowl": "~ 5 min",
    "Egg and Cheese Breakfast Sandwich": "~ 15 min",
    "Apple Cinnamon Oatmeal": "~ 10 min",
    "Spinach Feta Breakfast Wrap": "~ 15 min",
    "Peanut Butter Banana Toast": "~ 5 min",
    "Breakfast Burrito": "~ 20 min",
    "Chocolate Chip Waffles": "~ 20 min",
    "Mango Yogurt Bowl": "~ 5 min",
    "Egg Muffins": "~ 30 min",
    "French Toast": "~ 15 min",
    "Chia Seed Pudding": "~ 10 min",
    "Breakfast Quesadilla": "~ 15 min",
    "Avocado Egg Bowl": "~ 20 min",
    "Cinnamon Roll Oatmeal": "~ 10 min",
    "Berry Protein Smoothie": "~ 5 min",
    "Ham and Cheese Omelette": "~ 15 min",
    "Granola with Milk": "~ 3 min",
    "Savory Breakfast Rice Bowl": "~ 20 min",
    "Almond Butter Toast with Berries": "~ 5 min",
    "Greek Yogurt Berry Parfait": "~ 5 min",
    "Spinach Mushroom Frittata": "~ 30 min",
    "Coconut Chia Mango Bowl": "~ 10 min",
    "Tomato Basil Omelette": "~ 12 min",
    "Breakfast Sweet Potato Hash": "~ 35 min",
    "Lemon Herb Salmon": "~ 25 min",
    "Garlic Shrimp Quinoa Bowl": "~ 25 min",
    "Stuffed Bell Peppers": "~ 50 min",
    "Chicken Cauliflower Rice Bowl": "~ 25 min",
    "Zucchini Turkey Skillet": "~ 30 min",
    "Lentil Coconut Stew": "~ 45 min",
    "Baked Cod with Veggies": "~ 30 min",
    "Chicken Tomato Basil Bake": "~ 40 min",
    "Avocado Tuna Salad Bowl": "~ 15 min",
    "Quinoa Chickpea Salad": "~ 25 min",
    "Egg Salad Lettuce Cups": "~ 20 min",
    "Turkey Rice Bowl": "~ 30 min",
    "Mediterranean Chicken Salad": "~ 20 min",
    "Black Bean Corn Rice Bowl": "~ 20 min",
    "Shrimp Avocado Cucumber Salad": "~ 20 min",
    "Lemon Oat Energy Balls": "~ 20 min",
    "Chewy Homemade Granola Bars": "~ 35 min",
    "Greek Yogurt Ranch Dip": "~ 10 min",
    "Berry Yogurt Smoothie Snack": "~ 5 min",
    "Turkey Cheese Apple Skewers": "~ 15 min",
    "Chocolate Avocado Pudding Cups": "~ 15 min",
    "Ranch Popcorn Snack": "~ 12 min",
    "Microwave Egg Snack Sandwich": "~ 10 min",
    "Turkey Cheddar Lettuce Roll Ups": "~ 15 min",
    "Quick Yogurt Snack Bowl": "~ 5 min",
    "Veggie Black Bean Nachos": "~ 12 min",
    "Sweet Potato White Bean Squares": "~ 45 min",
    "Overnight Oats Snack Jars": "~ 8 hr",
    "Homemade Trail Mix": "~ 10 min",
    "Hard-Boiled Egg Snack Pack": "~ 25 min",
    "Baked Blueberry Oatmeal Bars": "~ 40 min",
    "Apple Peanut Butter Nachos": "~ 8 min",
    "Silver Dollar Pancake Snacks": "~ 25 min",
    "Cottage Cheese Snack Bowl": "~ 8 min",
    "Chicken Salad Snack Box": "~ 25 min",
    "Pumpkin Peanut Butter Oat Squares": "~ 30 min",
    "Air Fryer Chicken Bites": "~ 18 min",
    "Homemade Fruit Leather": "~ 4 hr",
    "Turkey Lettuce Snack Wraps": "~ 12 min",
    "Crispy Sweet Potato Chips": "~ 35 min",
    "Frozen Yogurt Fruit Tubes": "~ 4 hr",
    "Chocolate-Strawberry Energy Bites": "~ 10 min",
    "Garlic Parmesan Popcorn": "~ 10 min",
    "Lemon-y Avocado Toast": "~ 13 min",
    "15-Minute Mezze Plate with Za'atar Pita": "~ 15 min",
    "Roasted Veggie Chips": "~ 40 min",
    "Crudi-Tots Platter": "~ 40 min",
    "Easy Homemade Pickles": "~ 48 hr",
    "Italian Deli Pinwheels (Turkey)": "~ 25 min",
    "Cinnamon Roll Snowmen": "~ 24 min",
    "Gwyneth Paltrow Blueberry Cauliflower Smoothie": "~ 5 min",
    "Ants on a Log": "~ 5 min",
    "Roasted Pumpkin Seeds": "~ 45 min",
    "Rainbow Snack Mix": "~ 30 min",
    "Watermelon Salsa": "~ 15 min",
    "Baked Bananas": "~ 20 min",
    "One-Ingredient Watermelon Sorbet": "~ 4 hr",
    "Salted Peanut Butter Cup Smoothie": "~ 10 min",
    "Broiler S'mores": "~ 30 min",
    "Golden Oreo Truffles": "~ 1.5 hr",
    "Sweet Potato Fries": "~ 40 min",
    "Cinnamon Toast Crunch Muffins": "~ 27 min",
    "Jammy Soft-Boiled Eggs": "~ 40 min",
    "Pizza Trail Mix": "~ 20 min",
    "Peanut Toffee Chocolate Clusters": "~ 1 hr",
    "Roasted Chickpeas": "~ 1 hr",
    "Chocolate Granola": "~ 1 hr 20 min",
    "Easy Cherry Almond Granola Bars": "~ 25 min",
    "Tater Tot Nachos (Black Bean)": "~ 50 min",
    "Spicy Avocado Hummus": "~ 10 min",
    "Five-Ingredient Golden Milk Snack Bites": "~ 20 min",
    "Fresh Fruit Ice Pops": "~ 3 hr",
    "Thick Italian Hot Chocolate": "~ 15 min",
    "Roasted Edamame": "~ 25 min",
    "Buffalo Chicken Brie Bites": "~ 38 min",
    "Cajun Shrimp Guacamole Bites": "~ 35 min",
    "Grilled Cheese Crostini": "~ 45 min",
    "Sourdough with Whipped Cottage Cheese and Raspberry Chia Jam": "~ 25 min",
    "Mini Yogurt Cheesecakes": "~ 1.5 hr",
    "Vegan Banana Bread": "~ 1 hr 5 min",
    "Smoky Savory Fire Crackers": "~ 45 min",
    "3-Ingredient Shredded Chicken Flautas": "~ 20 min",
    "Homemade Cheese Crackers": "~ 35 min",
    "Grated Egg Toast": "~ 25 min",
}


def get_prep_time(meal_name: str) -> str:
    return PREP_TIME_BY_NAME.get(meal_name, "~ 30 min")


_LAND_PROTEIN_MARKERS = (
    "chicken",
    "beef",
    "pork",
    "turkey",
    "ham",
    "lamb",
    "duck",
    "sausage",
    "steak",
    "bacon",
    "pepperoni",
    "salami",
    "chorizo",
    "ground beef",
    "ground turkey",
    "ground chicken",
    "meatball",
    "chicken broth",
    "beef broth",
)
_SEAFOOD_MARKERS = (
    "shrimp",
    "salmon",
    "tuna",
    "cod",
    "crab",
    "lobster",
    "scallop",
    "mussel",
    "anchovy",
    "sardine",
    "seafood",
    "calamari",
    "squid",
)


def _ingredient_blob(ingredients: list[str]) -> str:
    return " ".join(i.lower() for i in ingredients)


def food_vibe_for_meal(meal_name: str, ingredients: list[str]) -> dict[str, str]:
    """Cute meat / seafood / mixed / veggie badge for the UI (stable per meal name)."""
    b = _ingredient_blob(ingredients)
    land = any(m in b for m in _LAND_PROTEIN_MARKERS)
    sea = any(m in b for m in _SEAFOOD_MARKERS) or ("fish" in b and "goldfish" not in b)
    h = sum(ord(c) for c in meal_name) % 1000

    def pick(seq: tuple[str, ...]) -> str:
        return seq[h % len(seq)]

    if land and sea:
        return {
            "kind": "mixed",
            "emoji": pick(("🍱", "🌊", "✨", "🥢")),
            "label": pick(("Surf + turf party", "Land meets sea", "Best of both worlds", "Flavor combo mode")),
        }
    if land:
        return {
            "kind": "meat",
            "emoji": pick(("🍖", "🍗", "🥩", "🐔", "🍳")),
            "label": pick(("Protein pals", "Grill squad", "Meaty marvel", "Savory superstar", "Filling")),
        }
    if sea:
        return {
            "kind": "seafood",
            "emoji": pick(("🦐", "🐟", "🦞", "🍤", "🐠")),
            "label": pick(("Ocean nibbles", "Sea snackers", "From the briny yum", "Catch of the day", "Splashy bites")),
        }
    if "egg" in b:
        return {
            "kind": "veggie",
            "emoji": pick(("🥚", "🍳", "🐣", "✨")),
            "label": pick(("Eggstra cute", "Sunny-side squad", "Yolk around", "Cluck-free crunch", "Whisk it good")),
        }
    return {
        "kind": "veggie",
        "emoji": pick(("🥦", "🥕", "🌽", "🍄", "🥬", "🫛", "🌱", "🍅")),
        "label": pick(("Plant party", "Veggie joy", "Garden goodies", "Leafy legends", "Rainbow fuel")),
    }


def steps_for_meal(name: str, ingredients: list[str], meal_type: str) -> list[str]:
    """Cooking steps from meal_steps.MEAL_STEPS (regenerate via python3 build_meal_steps.py)."""
    if name in MEAL_STEPS:
        return MEAL_STEPS[name]
    ing_list = ", ".join(ingredients)
    return [
        f"Gather and prep: {ing_list}. Wash produce, trim proteins, and measure before you turn on the heat.",
        "Cook in logical order so everything finishes together; taste and adjust salt and acid at the end.",
        "Plate while hot (or chill if meant cold) and enjoy!",
    ]


def meal_api_dict(meal: dict) -> dict:
    return {
        "meal": meal["name"],
        "type": meal["type"],
        "prep_time": get_prep_time(meal["name"]),
        "ingredients": meal["ingredients"],
        "food_vibe": food_vibe_for_meal(meal["name"], meal["ingredients"]),
        "steps": steps_for_meal(meal["name"], meal["ingredients"], meal["type"]),
    }


def is_gluten_free_ingredients(ingredients: list[str]) -> bool:
    ingredient_text = " ".join(item.lower() for item in ingredients)
    return not any(keyword in ingredient_text for keyword in NON_GF_INGREDIENT_KEYWORDS)

@app.get("/meal")
def get_meal(
    ingredients: str = Query(""),
    meal_type: str = Query("All"),
    gluten_free: bool = Query(False),
):
    user_ingredients = [i.strip().lower() for i in ingredients.split(",") if i.strip()]
    matches = []

    for meal in MEALS:
        if gluten_free and not is_gluten_free_ingredients(meal["ingredients"]):
            continue

        if meal_type != "All" and meal["type"].lower() != meal_type.lower():
            continue

        meal_ingredients = [item.lower() for item in meal["ingredients"]]
        if user_ingredients and not all(
            any(
                user_ingredient in meal_ingredient or meal_ingredient in user_ingredient
                for meal_ingredient in meal_ingredients
            )
            for user_ingredient in user_ingredients
        ):
            continue

        matches.append(meal_api_dict(meal))

    return {"meals": matches}


@app.get("/surprise")
def surprise_meal(meal_type: str = Query("All"), gluten_free: bool = Query(False)):
    options = [
        meal for meal in MEALS
        if (meal_type == "All" or meal["type"].lower() == meal_type.lower())
        and (not gluten_free or is_gluten_free_ingredients(meal["ingredients"]))
    ]
    if not options:
        return {"meal": None}

    selected = random.choice(options)
    return {"meal": meal_api_dict(selected)}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Eat?</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet" />
        <style>
            :root {
                --font-title: "Playfair Display", Georgia, "Times New Roman", serif;
                --font-body: var(--font-title);
                --bg: #EDE4D8;
                --card: #FFFFFF;
                --peach: #FFB38A;
                --butter: #FFE08A;
                --sage: #B7D7C0;
                --beige: #F3E5D8;
                --text: #4B3A2F;
                --text-soft: rgba(75, 58, 47, 0.72);
                --peach-deep: #e89670;
                --sage-deep: #8fb9a0;
            }
            body {
                font-family: var(--font-body);
                margin: 0;
                min-height: 100vh;
                color: var(--text);
                background-color: var(--bg);
                background-image:
                    radial-gradient(ellipse 120% 80% at 100% 0%, rgba(255, 179, 138, 0.32) 0%, transparent 55%),
                    radial-gradient(ellipse 90% 70% at 0% 100%, rgba(255, 224, 138, 0.36) 0%, transparent 50%),
                    radial-gradient(ellipse 70% 50% at 50% 50%, rgba(183, 215, 192, 0.2) 0%, transparent 60%);
            }
            .nav-fab {
                position: fixed;
                top: 22px;
                left: 22px;
                z-index: 260;
                width: 56px;
                height: 56px;
                padding: 0;
                border: none;
                border-radius: 18px;
                cursor: pointer;
                background: linear-gradient(145deg, var(--card) 0%, var(--butter) 45%, var(--peach) 100%);
                color: var(--text);
                box-shadow: 0 8px 22px rgba(75, 58, 47, 0.12), 0 2px 8px rgba(255, 179, 138, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.85);
                transition: transform 0.22s ease, box-shadow 0.22s ease, background 0.25s ease, color 0.25s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .nav-fab:hover {
                transform: scale(1.06);
                box-shadow: 0 12px 28px rgba(75, 58, 47, 0.14), 0 4px 14px rgba(183, 215, 192, 0.45);
            }
            .nav-fab:active {
                transform: scale(0.98);
            }
            body.drawer-open .nav-fab {
                background: linear-gradient(145deg, var(--sage-deep) 0%, var(--sage) 55%, var(--butter) 100%);
                color: var(--text);
                box-shadow: 0 8px 24px rgba(75, 58, 47, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.5);
            }
            .nav-fab-icon {
                width: 26px;
                height: 26px;
                display: block;
            }
            .nav-fab-badge {
                position: absolute;
                top: -2px;
                right: -2px;
                min-width: 20px;
                height: 20px;
                padding: 0 5px;
                border-radius: 999px;
                background: linear-gradient(135deg, var(--peach), var(--peach-deep));
                color: var(--text);
                font-size: 11px;
                font-weight: 700;
                font-family: var(--font-body);
                display: none;
                align-items: center;
                justify-content: center;
                line-height: 1;
                border: 2px solid var(--card);
                box-shadow: 0 2px 8px rgba(232, 150, 112, 0.5);
            }
            .nav-fab-badge.has-count {
                display: flex;
            }
            .nav-backdrop {
                position: fixed;
                inset: 0;
                z-index: 180;
                /* No backdrop-filter — it repaints the whole page every frame and feels slow */
                background: rgba(75, 58, 47, 0.38);
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.12s ease-out;
                will-change: opacity;
            }
            body.drawer-open .nav-backdrop {
                opacity: 1;
                pointer-events: auto;
            }
            .nav-drawer {
                position: fixed;
                top: 0;
                left: 0;
                z-index: 200;
                width: min(300px, 88vw);
                height: 100%;
                max-height: 100vh;
                background: linear-gradient(180deg, var(--card) 0%, var(--beige) 55%, rgba(255, 224, 138, 0.25) 100%);
                box-shadow: 16px 0 40px rgba(75, 58, 47, 0.12);
                transform: translate3d(-105%, 0, 0);
                transition: transform 0.2s cubic-bezier(0.22, 1, 0.36, 1);
                border-radius: 0 28px 28px 0;
                border-right: 2px solid rgba(255, 179, 138, 0.45);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                will-change: transform;
                contain: layout paint;
            }
            body.drawer-open .nav-drawer {
                transform: translate3d(0, 0, 0);
            }
            .nav-drawer-head {
                position: relative;
                padding: 26px 52px 20px 22px;
                background: linear-gradient(125deg, var(--sage) 0%, var(--butter) 50%, var(--peach) 100%);
                color: var(--text);
                text-align: left;
                box-shadow: 0 4px 18px rgba(75, 58, 47, 0.08);
            }
            .nav-drawer-head h2 {
                margin: 0;
                font-family: var(--font-title);
                font-size: 22px;
                font-weight: 700;
                letter-spacing: 0.02em;
            }
            .nav-drawer-head p {
                margin: 6px 0 0;
                font-size: 14px;
                opacity: 0.88;
                color: var(--text-soft);
            }
            .nav-drawer-close {
                position: absolute;
                top: 18px;
                right: 14px;
                width: 40px;
                height: 40px;
                border: none;
                border-radius: 12px;
                background: rgba(255, 255, 255, 0.55);
                color: var(--text);
                font-size: 26px;
                line-height: 1;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.2s ease, transform 0.15s ease;
            }
            .nav-drawer-close:hover {
                background: rgba(255, 255, 255, 0.85);
            }
            .nav-drawer-nav {
                padding: 18px 14px 24px;
                display: flex;
                flex-direction: column;
                gap: 10px;
                flex: 1;
                overflow-y: auto;
            }
            .drawer-link {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 14px 16px;
                border-radius: 16px;
                text-decoration: none;
                color: var(--text);
                font-family: var(--font-body);
                font-weight: 700;
                font-size: 17px;
                border: 2px solid transparent;
                background: rgba(255, 255, 255, 0.85);
                box-shadow: 0 2px 8px rgba(75, 58, 47, 0.05);
                transition: background 0.2s ease, border-color 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
            }
            .drawer-link:hover {
                background: var(--card);
                border-color: var(--peach);
                box-shadow: 0 4px 14px rgba(255, 179, 138, 0.25);
                transform: translateX(2px);
            }
            .drawer-link.current {
                background: linear-gradient(135deg, rgba(183, 215, 192, 0.55), rgba(255, 224, 138, 0.45));
                border-color: var(--sage-deep);
                color: var(--text);
            }
            .drawer-link-icon {
                font-size: 22px;
                width: 32px;
                text-align: center;
            }
            .drawer-link .fav-count {
                margin-left: auto;
                font-size: 14px;
                font-weight: 700;
                color: var(--text-soft);
            }
            .drawer-link.current .fav-count {
                color: var(--peach-deep);
            }
            .app-main {
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 28px 20px 24px;
                min-height: 100vh;
                box-sizing: border-box;
            }
            .card {
                background: var(--card);
                padding: 34px;
                border-radius: 24px;
                border: 2px solid rgba(183, 215, 192, 0.65);
                box-shadow:
                    0 12px 36px rgba(75, 58, 47, 0.08),
                    0 0 0 1px rgba(255, 179, 138, 0.2) inset,
                    0 1px 0 rgba(255, 255, 255, 0.9) inset;
                width: 900px;
                text-align: center;
                max-height: 86vh;
                overflow-y: auto;
                overflow-x: hidden;
                scrollbar-width: none;
                transition: box-shadow 0.25s ease, transform 0.25s ease, border-color 0.25s ease;
            }
            .card.is-scrolling {
                scrollbar-width: thin;
                scrollbar-color: var(--sage) var(--beige);
            }
            .card::-webkit-scrollbar {
                width: 0;
                height: 0;
            }
            .card.is-scrolling::-webkit-scrollbar {
                width: 10px;
            }
            .card.is-scrolling::-webkit-scrollbar-track {
                background: var(--beige);
                border-radius: 0 20px 20px 0;
            }
            .card.is-scrolling::-webkit-scrollbar-thumb {
                background: linear-gradient(180deg, var(--sage), var(--sage-deep));
                border-radius: 8px;
                border: 2px solid var(--beige);
            }
            .card:hover {
                box-shadow:
                    0 20px 48px rgba(75, 58, 47, 0.1),
                    0 0 0 1px rgba(255, 224, 138, 0.35) inset;
                transform: translateY(-2px);
                border-color: rgba(255, 179, 138, 0.55);
            }
            h1 {
                margin-bottom: 8px;
                font-family: var(--font-title);
                font-size: 42px;
                font-weight: 700;
                letter-spacing: 0.3px;
                color: var(--text);
                text-shadow: 0 1px 0 rgba(255, 255, 255, 0.8);
            }
            p {
                color: var(--text-soft);
                font-size: 17px;
                margin-top: 0;
            }
            .controls {
                display: grid;
                grid-template-columns: 1fr 180px;
                gap: 10px;
                margin-top: 14px;
            }
            input, select {
                width: 100%;
                padding: 12px;
                border-radius: 12px;
                border: 1px solid rgba(183, 215, 192, 0.85);
                font-size: 16px;
                box-sizing: border-box;
                font-family: var(--font-body);
                background: rgba(255, 255, 255, 0.92);
                color: var(--text);
                box-shadow: 0 2px 8px rgba(75, 58, 47, 0.04);
                transition: box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease;
            }
            input:focus, select:focus {
                outline: none;
                border-color: var(--peach);
                background: var(--card);
                box-shadow: 0 0 0 3px rgba(255, 179, 138, 0.35), 0 4px 14px rgba(183, 215, 192, 0.25);
            }
            .actions {
                display: flex;
                gap: 10px;
                justify-content: center;
                margin-top: 12px;
            }
            button {
                padding: 12px 20px;
                border: none;
                border-radius: 12px;
                background: linear-gradient(165deg, var(--sage) 0%, var(--sage-deep) 100%);
                color: var(--text);
                font-size: 16px;
                cursor: pointer;
                font-family: var(--font-title);
                font-weight: 700;
                box-shadow: 0 4px 14px rgba(75, 58, 47, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.45);
                transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
            }
            button:hover {
                background: linear-gradient(165deg, #c5e4cf 0%, var(--sage) 100%);
                box-shadow: 0 8px 22px rgba(143, 185, 160, 0.35);
                transform: translateY(-2px);
            }
            button:active {
                transform: translateY(0);
            }
            .secondary {
                background: linear-gradient(165deg, var(--beige) 0%, #e8d8c8 100%);
                color: var(--text);
                box-shadow: 0 4px 12px rgba(75, 58, 47, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.6);
            }
            .secondary:hover {
                background: linear-gradient(165deg, #faf3eb 0%, var(--beige) 100%);
                box-shadow: 0 8px 20px rgba(75, 58, 47, 0.1);
            }
            .toggle {
                background: linear-gradient(165deg, #e8dfd5, #cfc4b8);
                color: var(--text);
            }
            .toggle.active {
                background: linear-gradient(165deg, var(--butter) 0%, var(--peach) 100%);
                color: var(--text);
            }
            .toggle.active:hover {
                background: linear-gradient(165deg, #fff0b0 0%, #ffc9a8 100%);
            }
            .result {
                margin-top: 20px;
                padding: 14px;
                background: linear-gradient(180deg, rgba(243, 229, 216, 0.65) 0%, rgba(237, 228, 216, 0.92) 100%);
                border-radius: 18px;
                border: 1px solid rgba(255, 179, 138, 0.35);
                min-height: 50px;
                text-align: left;
                color: var(--text-soft);
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75), 0 4px 16px rgba(75, 58, 47, 0.05);
            }
            .meal-card {
                background: linear-gradient(145deg, var(--card) 0%, rgba(255, 224, 138, 0.12) 55%, rgba(183, 215, 192, 0.18) 100%);
                border: 1px solid rgba(183, 215, 192, 0.5);
                border-left: 5px solid var(--peach);
                border-radius: 16px;
                padding: 14px 16px;
                margin-bottom: 12px;
                box-shadow: 0 6px 18px rgba(75, 58, 47, 0.06), 0 2px 8px rgba(255, 179, 138, 0.08);
                transition: box-shadow 0.25s ease, transform 0.25s ease, border-color 0.25s ease;
            }
            .meal-card:hover {
                box-shadow: 0 12px 28px rgba(75, 58, 47, 0.09), 0 4px 14px rgba(183, 215, 192, 0.35);
                transform: translateY(-3px);
                border-color: rgba(255, 179, 138, 0.45);
            }
            .meal-card-header {
                display: flex;
                flex-direction: row;
                align-items: flex-start;
                justify-content: space-between;
                gap: 12px;
                margin-bottom: 4px;
            }
            .meal-card-main {
                flex: 1;
                min-width: 0;
            }
            .fav-heart {
                flex-shrink: 0;
                width: 38px;
                height: 38px;
                border: none;
                background: transparent;
                border-radius: 0;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.2s ease, transform 0.2s ease, filter 0.2s ease;
                box-shadow: none;
            }
            .fav-heart:hover {
                background: rgba(255, 255, 255, 0.55);
                border-radius: 14px;
                transform: scale(1.06);
                box-shadow: none;
            }
            .fav-heart svg {
                width: 30px;
                height: 30px;
                display: block;
                margin: 0;
                overflow: visible;
            }
            /* Outline heart — not saved */
            .fav-heart .heart-path {
                fill: none;
                stroke: var(--peach-deep);
                stroke-width: 1.85;
                stroke-linecap: round;
                stroke-linejoin: round;
            }
            /* Filled heart — saved (warm peach, not loud red) */
            .fav-heart.is-fav .heart-path {
                fill: var(--peach-deep);
                stroke: #c86b4a;
                stroke-width: 0.55;
            }
            .fav-heart.is-fav {
                background: transparent;
                box-shadow: none;
                filter: drop-shadow(0 2px 5px rgba(232, 150, 112, 0.45));
            }
            .fav-heart.is-fav:hover {
                filter: drop-shadow(0 3px 8px rgba(232, 150, 112, 0.55));
            }
            .meal-title-row {
                display: flex;
                flex-wrap: wrap;
                align-items: baseline;
                gap: 10px 14px;
                margin-bottom: 4px;
            }
            .meal-title {
                margin: 0;
                font-family: var(--font-title);
                font-weight: 700;
                font-size: 22px;
                color: var(--text);
            }
            .meal-prep {
                color: var(--sage-deep);
                font-size: 20px;
                font-weight: 700;
            }
            .meal-meta {
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 8px 10px;
                margin-bottom: 10px;
            }
            .meal-vibe {
                display: inline-flex;
                align-items: center;
                gap: 5px;
                font-size: 11px;
                font-weight: 700;
                color: var(--text);
                /* Rounded stamp — reads as “meta badge”, not an ingredient chip */
                border-radius: 8px;
                padding: 4px 10px 4px 8px;
                border: 1.5px solid rgba(75, 58, 47, 0.16);
                box-shadow: 0 1px 0 rgba(255, 255, 255, 0.65) inset, 0 2px 6px rgba(75, 58, 47, 0.06);
            }
            .meal-vibe-ico {
                font-size: 15px;
                line-height: 1;
            }
            .vibe-meat {
                background: linear-gradient(135deg, rgba(255, 179, 138, 0.55), rgba(255, 224, 138, 0.35));
            }
            .vibe-seafood {
                background: linear-gradient(135deg, rgba(183, 215, 192, 0.65), rgba(255, 224, 138, 0.4));
            }
            .vibe-mixed {
                background: linear-gradient(135deg, rgba(255, 224, 138, 0.7), rgba(255, 179, 138, 0.45));
            }
            .vibe-veggie {
                background: linear-gradient(135deg, rgba(183, 215, 192, 0.5), rgba(243, 229, 216, 0.95));
            }
            .meal-type {
                display: inline-block;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.02em;
                text-transform: none;
                color: var(--text);
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.55), rgba(243, 229, 216, 0.95));
                border: 1.5px solid rgba(75, 58, 47, 0.2);
                border-radius: 6px;
                padding: 4px 10px;
                margin-bottom: 0;
                box-shadow: 0 1px 0 rgba(255, 255, 255, 0.8) inset;
            }
            ul.meal-ingredients {
                display: flex;
                flex-wrap: wrap;
                gap: 8px 10px;
                margin: 12px 0 0;
                padding: 0;
                list-style: none;
                color: var(--text);
            }
            ul.meal-ingredients > li.ingredient-tag {
                margin: 0;
                font-size: 14px;
                font-weight: 600;
                line-height: 1.25;
                letter-spacing: 0.01em;
                text-transform: none;
                /* Full pill + dashed ring = “pantry list”, distinct from meal-type / vibe stamps */
                border-radius: 999px;
                padding: 6px 13px;
                border: 1px dashed rgba(75, 58, 47, 0.22);
                box-shadow: 0 1px 4px rgba(75, 58, 47, 0.05);
                background: rgba(255, 255, 255, 0.92);
            }
            ul.meal-ingredients > li.ingredient-tag:nth-child(4n + 1) {
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(255, 224, 138, 0.35));
                border-color: rgba(255, 179, 138, 0.42);
                border-style: dashed;
            }
            ul.meal-ingredients > li.ingredient-tag:nth-child(4n + 2) {
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(183, 215, 192, 0.4));
                border-color: rgba(143, 185, 160, 0.5);
                border-style: dashed;
            }
            ul.meal-ingredients > li.ingredient-tag:nth-child(4n + 3) {
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(243, 229, 216, 0.85));
                border-color: rgba(75, 58, 47, 0.2);
                border-style: dashed;
            }
            ul.meal-ingredients > li.ingredient-tag:nth-child(4n) {
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(255, 224, 138, 0.22));
                border-color: rgba(183, 215, 192, 0.55);
                border-style: dashed;
            }
            .meal-card-footer {
                margin-top: 14px;
                padding-top: 12px;
                border-top: 1px solid rgba(183, 215, 192, 0.45);
            }
            .meal-steps-btn {
                font-family: var(--font-title);
                font-size: 15px;
                font-weight: 800;
                letter-spacing: 0.04em;
                color: var(--text);
                padding: 9px 20px;
                border-radius: 999px;
                border: 2px solid rgba(143, 185, 160, 0.85);
                background: linear-gradient(145deg, var(--sage) 0%, rgba(255, 224, 138, 0.75) 55%, rgba(255, 179, 138, 0.55) 100%);
                cursor: pointer;
                box-shadow:
                    0 4px 14px rgba(75, 58, 47, 0.1),
                    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
                transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease, border-color 0.2s ease;
            }
            .meal-steps-btn:hover {
                background: linear-gradient(145deg, #c5e4cf 0%, var(--butter) 50%, var(--peach) 100%);
                border-color: var(--peach-deep);
                transform: translateY(-2px);
                box-shadow: 0 8px 22px rgba(255, 179, 138, 0.35), 0 0 0 1px rgba(255, 255, 255, 0.55) inset;
            }
            .meal-steps-btn[aria-expanded="true"] {
                background: linear-gradient(145deg, var(--peach) 0%, var(--butter) 100%);
                border-color: rgba(75, 58, 47, 0.22);
                box-shadow: 0 4px 16px rgba(232, 150, 112, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.45);
            }
            .meal-steps-btn:focus-visible {
                outline: none;
                box-shadow: 0 0 0 3px rgba(255, 179, 138, 0.55), 0 4px 14px rgba(75, 58, 47, 0.12);
            }
            .meal-steps-panel {
                display: none;
                margin-top: 12px;
                padding: 14px 16px;
                border-radius: 14px;
                background: rgba(255, 255, 255, 0.88);
                border: 1px solid rgba(183, 215, 192, 0.55);
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
            }
            .meal-steps-panel.is-open {
                display: block;
            }
            .meal-steps-list {
                margin: 0;
                padding-left: 1.35rem;
                color: var(--text);
                font-family: var(--font-body);
                line-height: 1.55;
                font-size: 15px;
            }
            .meal-steps-list li {
                margin-bottom: 8px;
            }
            .meal-steps-list li:last-child {
                margin-bottom: 0;
            }
            .fav-empty {
                color: var(--text-soft);
                text-align: center;
                padding: 24px 12px;
                font-size: 18px;
                margin: 0;
            }
        </style>
    </head>
    <body>
        <button type="button" class="nav-fab" id="navFab" aria-label="Open menu" aria-expanded="false" aria-controls="navDrawer">
            <svg class="nav-fab-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 7h16v2H4V7zm0 5h16v2H4v-2zm0 5h16v2H4v-2z"/></svg>
            <span class="nav-fab-badge" id="navFabBadge"></span>
        </button>
        <div class="nav-backdrop" id="navBackdrop" aria-hidden="true"></div>
        <aside class="nav-drawer" id="navDrawer" role="dialog" aria-labelledby="navDrawerTitle" aria-hidden="true">
            <div class="nav-drawer-head">
                <button type="button" class="nav-drawer-close" id="navDrawerClose" aria-label="Close menu">×</button>
                <h2 id="navDrawerTitle">Eat?</h2>
                <p>Where to next?</p>
            </div>
            <nav class="nav-drawer-nav" aria-label="Main">
                <a class="drawer-link current" href="/"><span class="drawer-link-icon">🔍</span> Search</a>
                <a class="drawer-link" href="/favorites"><span class="drawer-link-icon">💝</span> Favourites <span class="fav-count" id="sideFavCount">(0)</span></a>
            </nav>
        </aside>
        <div class="app-main">
        <div class="card" id="mainCard">
            <h1>🍽️ Eat?</h1>
            <p>Find meal ideas from your ingredients in seconds!</p>
            <form class="controls" id="searchForm" action="#" method="get" onsubmit="event.preventDefault(); findMeals();">
                <input id="ingredients" name="ingredients" placeholder="e.g. chicken, rice, garlic" autocomplete="off" />
                <select id="mealType" name="meal_type">
                    <option value="All">🌟 All bites</option>
                    <option value="Breakfast">🧇 Breakfast</option>
                    <option value="Lunch">🥙 Lunch</option>
                    <option value="Dinner">🍝 Dinner</option>
                    <option value="Snack">🍿 Snacks</option>
                </select>
            </form>
            <div class="actions">
                <button onclick="findMeals()">🔎 Find Meals</button>
                <button class="secondary" onclick="surpriseMe()">🎲 Surprise Me</button>
                <button id="gfToggle" class="toggle" onclick="toggleGlutenFree()">🌾 Gluten Free: Off</button>
            </div>
            <div class="result" id="result">hmmm...</div>
        </div>
        </div>

        <script>
            let glutenFreeOnly = false;
            const HEART_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path class="heart-path" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>';
            const FAV_KEY = "eatFavMealsV1";

            function escapeHtml(s) {
                if (s == null) return "";
                return String(s)
                    .replace(/&/g, "&amp;")
                    .replace(/</g, "&lt;")
                    .replace(/>/g, "&gt;")
                    .replace(/"/g, "&quot;");
            }
            function getFavorites() {
                try {
                    const raw = localStorage.getItem(FAV_KEY);
                    if (!raw) return [];
                    const a = JSON.parse(raw);
                    return Array.isArray(a) ? a : [];
                } catch (e) { return []; }
            }
            function setFavorites(arr) {
                localStorage.setItem(FAV_KEY, JSON.stringify(arr));
                updateFavCount();
            }
            function isFavoriteName(name) {
                return getFavorites().some((f) => f.meal === name);
            }
            function updateFavCount() {
                const n = getFavorites().length;
                const el = document.getElementById("sideFavCount");
                if (el) el.textContent = "(" + n + ")";
                const badge = document.getElementById("navFabBadge");
                if (badge) {
                    badge.textContent = n > 99 ? "99+" : (n > 0 ? String(n) : "");
                    badge.classList.toggle("has-count", n > 0);
                }
            }
            function initNavDrawer() {
                const fab = document.getElementById("navFab");
                const backdrop = document.getElementById("navBackdrop");
                const drawer = document.getElementById("navDrawer");
                const closeBtn = document.getElementById("navDrawerClose");
                if (!fab || !backdrop || !drawer) return;
                function openDrawer() {
                    document.body.classList.add("drawer-open");
                    fab.setAttribute("aria-expanded", "true");
                    drawer.setAttribute("aria-hidden", "false");
                    backdrop.setAttribute("aria-hidden", "false");
                }
                function closeDrawer() {
                    document.body.classList.remove("drawer-open");
                    fab.setAttribute("aria-expanded", "false");
                    drawer.setAttribute("aria-hidden", "true");
                    backdrop.setAttribute("aria-hidden", "true");
                }
                function toggleDrawer(e) {
                    e.stopPropagation();
                    if (document.body.classList.contains("drawer-open")) closeDrawer();
                    else openDrawer();
                }
                fab.addEventListener("click", toggleDrawer);
                backdrop.addEventListener("click", closeDrawer);
                if (closeBtn) closeBtn.addEventListener("click", closeDrawer);
                document.addEventListener("keydown", function (ev) {
                    if (ev.key === "Escape") closeDrawer();
                });
                drawer.querySelectorAll(".drawer-link").forEach(function (a) {
                    a.addEventListener("click", closeDrawer);
                });
            }
            function toggleFavoritePayload(payload) {
                let list = getFavorites();
                const i = list.findIndex((f) => f.meal === payload.meal);
                if (i >= 0) list.splice(i, 1);
                else list.push(payload);
                setFavorites(list);
            }

            (function () {
                const mainCard = document.getElementById("mainCard");
                let scrollHideTimer;
                mainCard.addEventListener("scroll", function () {
                    mainCard.classList.add("is-scrolling");
                    clearTimeout(scrollHideTimer);
                    scrollHideTimer = setTimeout(function () {
                        mainCard.classList.remove("is-scrolling");
                    }, 700);
                });
            })();

            document.getElementById("result").addEventListener("click", function (e) {
                const stepsBtn = e.target.closest(".meal-steps-btn");
                if (stepsBtn) {
                    e.preventDefault();
                    const card = stepsBtn.closest(".meal-card");
                    const panel = card && card.querySelector(".meal-steps-panel");
                    if (!panel) return;
                    const open = panel.classList.toggle("is-open");
                    stepsBtn.setAttribute("aria-expanded", open ? "true" : "false");
                    panel.setAttribute("aria-hidden", open ? "false" : "true");
                    stepsBtn.textContent = open ? "Hide steps" : "Steps?";
                    return;
                }
                const btn = e.target.closest(".fav-heart");
                if (!btn) return;
                e.preventDefault();
                const enc = btn.getAttribute("data-fav");
                if (!enc) return;
                let p;
                try { p = JSON.parse(decodeURIComponent(enc)); } catch (err) { return; }
                toggleFavoritePayload(p);
                btn.classList.toggle("is-fav", isFavoriteName(p.meal));
            });

            document.addEventListener("DOMContentLoaded", function () {
                updateFavCount();
                initNavDrawer();
            });

            function toggleGlutenFree() {
                glutenFreeOnly = !glutenFreeOnly;
                const button = document.getElementById("gfToggle");
                if (glutenFreeOnly) {
                    button.classList.add("active");
                    button.innerText = "🌾 Gluten Free: On";
                } else {
                    button.classList.remove("active");
                    button.innerText = "🌾 Gluten Free: Off";
                }
            }

            function foodVibeFromIngredients(mealName, ingredients) {
                const b = (ingredients || []).map(function (x) { return String(x).toLowerCase(); }).join(" ");
                const landM = ["chicken","beef","pork","turkey","ham","lamb","duck","sausage","steak","bacon","pepperoni","salami","chorizo","ground beef","ground turkey","ground chicken","meatball","chicken broth","beef broth"];
                const seaM = ["shrimp","salmon","tuna","cod","crab","lobster","scallop","mussel","anchovy","sardine","seafood","calamari","squid"];
                function hits(arr) { return arr.some(function (m) { return b.indexOf(m) >= 0; }); }
                const land = hits(landM);
                let sea = hits(seaM);
                if (!sea && b.indexOf("fish") >= 0 && b.indexOf("goldfish") < 0) sea = true;
                const h = mealName.split("").reduce(function (a, c) { return a + c.charCodeAt(0); }, 0) % 1000;
                function pick(seq) { return seq[h % seq.length]; }
                if (land && sea) {
                    return { kind: "mixed", emoji: pick(["🍱","🌊","✨","🥢"]), label: pick(["Surf + turf party","Land meets sea","Best of both worlds","Flavor combo mode"]) };
                }
                if (land) {
                    return { kind: "meat", emoji: pick(["🍖","🍗","🥩","🐔","🍳"]), label: pick(["Protein pals","Grill squad","Meaty marvel","Savory superstar","Filling"]) };
                }
                if (sea) {
                    return { kind: "seafood", emoji: pick(["🦐","🐟","🦞","🍤","🐠"]), label: pick(["Ocean nibbles","Sea snackers","From the briny yum","Catch of the day","Splashy bites"]) };
                }
                if (b.indexOf("egg") >= 0) {
                    return { kind: "veggie", emoji: pick(["🥚","🍳","🐣","✨"]), label: pick(["Eggstra cute","Sunny-side squad","Yolk around","Cluck-free crunch","Whisk it good"]) };
                }
                return { kind: "veggie", emoji: pick(["🥦","🥕","🌽","🍄","🥬","🫛","🌱","🍅"]), label: pick(["Plant party","Veggie joy","Garden goodies","Leafy legends","Rainbow fuel"]) };
            }

            function vibeClass(kind) {
                return ["meat","seafood","mixed","veggie"].indexOf(kind) >= 0 ? kind : "veggie";
            }

            function fallbackSteps(meal) {
                const ing = meal.ingredients || [];
                return [
                    "Gather and prep: " + ing.join(", ") + ". Wash produce, trim proteins, and chop or measure before you turn on the heat.",
                    "Heat your main pan, pot, or oven to the right level for this dish before adding oil or butter.",
                    "Cook in logical order—browning proteins or hardy veg first—so everything finishes together.",
                    "Combine, simmer, or toss as the dish needs; taste and adjust salt, acid, or heat at the end.",
                    "Plate while hot (or chill if meant cold) and enjoy!",
                ];
            }

            function renderMeals(meals, emptyHtml) {
                const resultBox = document.getElementById("result");
                if (!meals.length) {
                    resultBox.innerHTML =
                        emptyHtml != null ? emptyHtml : "No meal turned up—try another meal type or filters.";
                    return;
                }

                resultBox.innerHTML = meals.map((meal) => {
                    const vibe = meal.food_vibe || foodVibeFromIngredients(meal.meal, meal.ingredients);
                    const vk = vibeClass(vibe.kind);
                    const stepsArr = meal.steps && meal.steps.length ? meal.steps : fallbackSteps(meal);
                    const payload = {
                        meal: meal.meal,
                        type: meal.type,
                        prep_time: meal.prep_time || "",
                        ingredients: meal.ingredients,
                        food_vibe: vibe,
                        steps: stepsArr,
                    };
                    const enc = encodeURIComponent(JSON.stringify(payload));
                    const fav = isFavoriteName(meal.meal) ? " is-fav" : "";
                    return `
                    <div class="meal-card">
                        <div class="meal-card-header">
                            <div class="meal-card-main">
                                <div class="meal-title-row">
                                    <span class="meal-title">${escapeHtml(meal.meal)}</span>
                                    <span class="meal-prep">${escapeHtml(meal.prep_time || "")}</span>
                                </div>
                                <div class="meal-meta">
                                    <span class="meal-vibe vibe-${vk}"><span class="meal-vibe-ico" aria-hidden="true">${vibe.emoji}</span>${escapeHtml(vibe.label)}</span>
                                    <span class="meal-type">${escapeHtml(meal.type)}</span>
                                </div>
                            </div>
                            <button type="button" class="fav-heart${fav}" data-fav="${enc}" aria-label="Toggle favourite">${HEART_SVG}</button>
                        </div>
                        <ul class="meal-ingredients" aria-label="Ingredients">
                            ${meal.ingredients.map((ingredient) => '<li class="ingredient-tag">' + escapeHtml(ingredient) + "</li>").join("")}
                        </ul>
                        <div class="meal-card-footer">
                            <button type="button" class="meal-steps-btn" aria-expanded="false">Steps?</button>
                        </div>
                        <div class="meal-steps-panel" aria-hidden="true">
                            <ol class="meal-steps-list">
                                ${stepsArr.map((s) => "<li>" + escapeHtml(s) + "</li>").join("")}
                            </ol>
                        </div>
                    </div>`;
                }).join("");
                updateFavCount();
            }

            async function findMeals() {
                const ingredients = document.getElementById("ingredients").value;
                const mealType = document.getElementById("mealType").value;
                const resultBox = document.getElementById("result");
                resultBox.innerText = "Loading meals...";
                const response = await fetch(
                    `/meal?ingredients=${encodeURIComponent(ingredients)}&meal_type=${encodeURIComponent(mealType)}&gluten_free=${glutenFreeOnly}`
                );
                const data = await response.json();
                renderMeals(data.meals || [], "umm... I'm not exactly sure");
            }

            async function surpriseMe() {
                const mealType = document.getElementById("mealType").value;
                const resultBox = document.getElementById("result");
                resultBox.innerText = "Picking a surprise...";
                const response = await fetch(`/surprise?meal_type=${encodeURIComponent(mealType)}&gluten_free=${glutenFreeOnly}`);
                const data = await response.json();
                if (!data.meal) {
                    renderMeals([]);
                    return;
                }
                renderMeals([data.meal]);
            }
        </script>
    </body>
    </html>
    """


def _app_css_from_home_template() -> str:
    text = Path(__file__).read_text(encoding="utf-8")
    m = re.search(r"<style>\s*([\s\S]*?)\s*</style>", text)
    return m.group(1) if m else ""


@app.get("/favorites", response_class=HTMLResponse)
def favorites_page():
    css = _app_css_from_home_template()
    return (
        """<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>Favourites - Eat?</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet" />
        <style>"""
        + css
        + """
        </style>
    </head>
    <body>
        <button type="button" class="nav-fab" id="navFab" aria-label="Open menu" aria-expanded="false" aria-controls="navDrawer">
            <svg class="nav-fab-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 7h16v2H4V7zm0 5h16v2H4v-2zm0 5h16v2H4v-2z"/></svg>
            <span class="nav-fab-badge" id="navFabBadge"></span>
        </button>
        <div class="nav-backdrop" id="navBackdrop" aria-hidden="true"></div>
        <aside class="nav-drawer" id="navDrawer" role="dialog" aria-labelledby="navDrawerTitle" aria-hidden="true">
            <div class="nav-drawer-head">
                <button type="button" class="nav-drawer-close" id="navDrawerClose" aria-label="Close menu">×</button>
                <h2 id="navDrawerTitle">Eat?</h2>
                <p>Where to next?</p>
            </div>
            <nav class="nav-drawer-nav" aria-label="Main">
                <a class="drawer-link" href="/"><span class="drawer-link-icon">🔍</span> Search</a>
                <a class="drawer-link current" href="/favorites"><span class="drawer-link-icon">💝</span> Favourites <span class="fav-count" id="sideFavCount">(0)</span></a>
            </nav>
        </aside>
        <div class="app-main">
        <div class="card" id="mainCard">
            <h1>💝 Favourites</h1>
            <p>Meals you saved with the heart button on the search page.</p>
            <div class="result" id="favList">Loading…</div>
        </div>
        </div>
        <script>
            const HEART_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path class="heart-path" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>';
            const FAV_KEY = "eatFavMealsV1";
            function escapeHtml(s) {
                if (s == null) return "";
                return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
            }
            function getFavorites() {
                try {
                    const raw = localStorage.getItem(FAV_KEY);
                    if (!raw) return [];
                    const a = JSON.parse(raw);
                    return Array.isArray(a) ? a : [];
                } catch (e) { return []; }
            }
            function setFavorites(arr) {
                localStorage.setItem(FAV_KEY, JSON.stringify(arr));
                updateFavCount();
            }
            function isFavoriteName(name) {
                return getFavorites().some((f) => f.meal === name);
            }
            function updateFavCount() {
                const n = getFavorites().length;
                const el = document.getElementById("sideFavCount");
                if (el) el.textContent = "(" + n + ")";
                const badge = document.getElementById("navFabBadge");
                if (badge) {
                    badge.textContent = n > 99 ? "99+" : (n > 0 ? String(n) : "");
                    badge.classList.toggle("has-count", n > 0);
                }
            }
            function initNavDrawer() {
                const fab = document.getElementById("navFab");
                const backdrop = document.getElementById("navBackdrop");
                const drawer = document.getElementById("navDrawer");
                const closeBtn = document.getElementById("navDrawerClose");
                if (!fab || !backdrop || !drawer) return;
                function openDrawer() {
                    document.body.classList.add("drawer-open");
                    fab.setAttribute("aria-expanded", "true");
                    drawer.setAttribute("aria-hidden", "false");
                    backdrop.setAttribute("aria-hidden", "false");
                }
                function closeDrawer() {
                    document.body.classList.remove("drawer-open");
                    fab.setAttribute("aria-expanded", "false");
                    drawer.setAttribute("aria-hidden", "true");
                    backdrop.setAttribute("aria-hidden", "true");
                }
                function toggleDrawer(e) {
                    e.stopPropagation();
                    if (document.body.classList.contains("drawer-open")) closeDrawer();
                    else openDrawer();
                }
                fab.addEventListener("click", toggleDrawer);
                backdrop.addEventListener("click", closeDrawer);
                if (closeBtn) closeBtn.addEventListener("click", closeDrawer);
                document.addEventListener("keydown", function (ev) {
                    if (ev.key === "Escape") closeDrawer();
                });
                drawer.querySelectorAll(".drawer-link").forEach(function (a) {
                    a.addEventListener("click", closeDrawer);
                });
            }
            function toggleFavoritePayload(payload) {
                var list = getFavorites();
                const i = list.findIndex((f) => f.meal === payload.meal);
                if (i >= 0) list.splice(i, 1);
                else list.push(payload);
                setFavorites(list);
            }
            function foodVibeFromIngredients(mealName, ingredients) {
                const b = (ingredients || []).map(function (x) { return String(x).toLowerCase(); }).join(" ");
                const landM = ["chicken","beef","pork","turkey","ham","lamb","duck","sausage","steak","bacon","pepperoni","salami","chorizo","ground beef","ground turkey","ground chicken","meatball","chicken broth","beef broth"];
                const seaM = ["shrimp","salmon","tuna","cod","crab","lobster","scallop","mussel","anchovy","sardine","seafood","calamari","squid"];
                function hits(arr) { return arr.some(function (m) { return b.indexOf(m) >= 0; }); }
                const land = hits(landM);
                var sea = hits(seaM);
                if (!sea && b.indexOf("fish") >= 0 && b.indexOf("goldfish") < 0) sea = true;
                const h = mealName.split("").reduce(function (a, c) { return a + c.charCodeAt(0); }, 0) % 1000;
                function pick(seq) { return seq[h % seq.length]; }
                if (land && sea) {
                    return { kind: "mixed", emoji: pick(["🍱","🌊","✨","🥢"]), label: pick(["Surf + turf party","Land meets sea","Best of both worlds","Flavor combo mode"]) };
                }
                if (land) {
                    return { kind: "meat", emoji: pick(["🍖","🍗","🥩","🐔","🍳"]), label: pick(["Protein pals","Grill squad","Meaty marvel","Savory superstar","Filling"]) };
                }
                if (sea) {
                    return { kind: "seafood", emoji: pick(["🦐","🐟","🦞","🍤","🐠"]), label: pick(["Ocean nibbles","Sea snackers","From the briny yum","Catch of the day","Splashy bites"]) };
                }
                if (b.indexOf("egg") >= 0) {
                    return { kind: "veggie", emoji: pick(["🥚","🍳","🐣","✨"]), label: pick(["Eggstra cute","Sunny-side squad","Yolk around","Cluck-free crunch","Whisk it good"]) };
                }
                return { kind: "veggie", emoji: pick(["🥦","🥕","🌽","🍄","🥬","🫛","🌱","🍅"]), label: pick(["Plant party","Veggie joy","Garden goodies","Leafy legends","Rainbow fuel"]) };
            }
            function vibeClass(kind) {
                return ["meat","seafood","mixed","veggie"].indexOf(kind) >= 0 ? kind : "veggie";
            }
            function fallbackSteps(meal) {
                const ing = meal.ingredients || [];
                return [
                    "Gather and prep: " + ing.join(", ") + ". Wash produce, trim proteins, and chop or measure before you turn on the heat.",
                    "Heat your main pan, pot, or oven to the right level for this dish before adding oil or butter.",
                    "Cook in logical order—browning proteins or hardy veg first—so everything finishes together.",
                    "Combine, simmer, or toss as the dish needs; taste and adjust salt, acid, or heat at the end.",
                    "Plate while hot (or chill if meant cold) and enjoy!",
                ];
            }
            function mealCardFromPayload(meal, forceFav) {
                const vibe = meal.food_vibe || foodVibeFromIngredients(meal.meal, meal.ingredients);
                const vk = vibeClass(vibe.kind);
                const stepsArr = meal.steps && meal.steps.length ? meal.steps : fallbackSteps(meal);
                const payload = {
                    meal: meal.meal,
                    type: meal.type,
                    prep_time: meal.prep_time || "",
                    ingredients: meal.ingredients,
                    food_vibe: vibe,
                    steps: stepsArr,
                };
                const enc = encodeURIComponent(JSON.stringify(payload));
                const fav = (forceFav || isFavoriteName(meal.meal)) ? " is-fav" : "";
                return (
                    '<div class="meal-card"><div class="meal-card-header"><div class="meal-card-main">' +
                    '<div class="meal-title-row"><span class="meal-title">' + escapeHtml(meal.meal) + '</span>' +
                    '<span class="meal-prep">' + escapeHtml(meal.prep_time || "") + '</span></div>' +
                    '<div class="meal-meta"><span class="meal-vibe vibe-' + vk + '"><span class="meal-vibe-ico" aria-hidden="true">' + vibe.emoji + '</span>' + escapeHtml(vibe.label) + '</span>' +
                    '<span class="meal-type">' + escapeHtml(meal.type) + '</span></div></div>' +
                    '<button type="button" class="fav-heart' + fav + '" data-fav="' + enc + '" aria-label="Toggle favourite">' + HEART_SVG + '</button></div>' +
                    '<ul class="meal-ingredients" aria-label="Ingredients">' +
                    meal.ingredients.map(function (ing) { return '<li class="ingredient-tag">' + escapeHtml(ing) + "</li>"; }).join("") +
                    "</ul>" +
                    '<div class="meal-card-footer"><button type="button" class="meal-steps-btn" aria-expanded="false">Steps?</button></div>' +
                    '<div class="meal-steps-panel" aria-hidden="true"><ol class="meal-steps-list">' +
                    stepsArr.map(function (s) { return "<li>" + escapeHtml(s) + "</li>"; }).join("") +
                    "</ol></div></div>"
                );
            }
            function renderFavorites() {
                const box = document.getElementById("favList");
                const list = getFavorites();
                if (!list.length) {
                    box.innerHTML = '<p class="fav-empty">No favourites yet. Go to Search and tap the heart on a meal to save it here.</p>';
                    updateFavCount();
                    return;
                }
                box.innerHTML = list.map((m) => mealCardFromPayload(m, true)).join("");
                updateFavCount();
            }
            (function () {
                const mainCard = document.getElementById("mainCard");
                const scrollHideTimer = { t: 0 };
                mainCard.addEventListener("scroll", function () {
                    mainCard.classList.add("is-scrolling");
                    clearTimeout(scrollHideTimer.t);
                    scrollHideTimer.t = setTimeout(function () {
                        mainCard.classList.remove("is-scrolling");
                    }, 700);
                });
            })();
            document.getElementById("favList").addEventListener("click", function (e) {
                const stepsBtn = e.target.closest(".meal-steps-btn");
                if (stepsBtn) {
                    e.preventDefault();
                    const card = stepsBtn.closest(".meal-card");
                    const panel = card && card.querySelector(".meal-steps-panel");
                    if (!panel) return;
                    const open = panel.classList.toggle("is-open");
                    stepsBtn.setAttribute("aria-expanded", open ? "true" : "false");
                    panel.setAttribute("aria-hidden", open ? "false" : "true");
                    stepsBtn.textContent = open ? "Hide steps" : "Steps?";
                    return;
                }
                const btn = e.target.closest(".fav-heart");
                if (!btn) return;
                e.preventDefault();
                const enc = btn.getAttribute("data-fav");
                if (!enc) return;
                let p;
                try { p = JSON.parse(decodeURIComponent(enc)); } catch (err) { return; }
                toggleFavoritePayload(p);
                renderFavorites();
            });
            document.addEventListener("DOMContentLoaded", function () {
                renderFavorites();
                initNavDrawer();
            });
        </script>
    </body>
    </html>"""
    )