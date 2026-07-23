"""Seed data for miseBot — curated from 106 Wigle RC data + prep PDFs."""

SHOPPING_INGREDIENTS = [
    {"name": "Tomatoes", "category": "Produce", "default_unit": "lbs", "usage_rate_per_week": 5, "current_stock": 8, "min_stock": 3},
    {"name": "Potatoes", "category": "Produce", "default_unit": "lbs", "usage_rate_per_week": 10, "current_stock": 15, "min_stock": 5},
    {"name": "Onions", "category": "Produce", "default_unit": "lbs", "usage_rate_per_week": 4, "current_stock": 6, "min_stock": 2},
    {"name": "Lettuce", "category": "Produce", "default_unit": "ea", "usage_rate_per_week": 6, "current_stock": 10, "min_stock": 4},
    {"name": "Burger Buns", "category": "Baked Products", "default_unit": "ea", "usage_rate_per_week": 50, "current_stock": 30, "min_stock": 20},
    {"name": "Bacon", "category": "Meat", "default_unit": "lbs", "usage_rate_per_week": 3, "current_stock": 5, "min_stock": 2},
    {"name": "Ground Beef", "category": "Meat", "default_unit": "lbs", "usage_rate_per_week": 8, "current_stock": 12, "min_stock": 5},
    {"name": "Cheddar Cheese", "category": "Dairy", "default_unit": "lbs", "usage_rate_per_week": 3, "current_stock": 4, "min_stock": 1},
    {"name": "Heavy Cream", "category": "Dairy", "default_unit": "ml", "usage_rate_per_week": 1, "current_stock": 2, "min_stock": 1},
    {"name": "Eggs", "category": "Dairy", "default_unit": "ea", "usage_rate_per_week": 24, "current_stock": 36, "min_stock": 12},
    {"name": "Pickles", "category": "Dry Goods", "default_unit": "jar", "usage_rate_per_week": 1, "current_stock": 2, "min_stock": 1},
    {"name": "French Fries", "category": "Frozen", "default_unit": "lbs", "usage_rate_per_week": 6, "current_stock": 10, "min_stock": 3},
    {"name": "Canola Oil", "category": "Dry Goods", "default_unit": "L", "usage_rate_per_week": 1, "current_stock": 3, "min_stock": 1},
    {"name": "Salt", "category": "Dry Goods", "default_unit": "g", "usage_rate_per_week": 0.5, "current_stock": 1000, "min_stock": 500},
    {"name": "Black Pepper", "category": "Dry Goods", "default_unit": "g", "usage_rate_per_week": 0.2, "current_stock": 500, "min_stock": 200},
    {"name": "Coffee", "category": "Beverages", "default_unit": "bags", "usage_rate_per_week": 2, "current_stock": 1, "min_stock": 1},
    {"name": "Milk 2%", "category": "Dairy", "default_unit": "L", "usage_rate_per_week": 4, "current_stock": 6, "min_stock": 2},
    {"name": "All-Purpose Flour", "category": "Dry Goods", "default_unit": "lbs", "usage_rate_per_week": 2, "current_stock": 5, "min_stock": 2},
    {"name": "Granulated Sugar", "category": "Baking Supplies", "default_unit": "lbs", "usage_rate_per_week": 1, "current_stock": 3, "min_stock": 1},
    {"name": "Butter", "category": "Dairy", "default_unit": "lbs", "usage_rate_per_week": 2, "current_stock": 4, "min_stock": 1},
    {"name": "Garlic", "category": "Produce", "default_unit": "lbs", "usage_rate_per_week": 1, "current_stock": 2, "min_stock": 0.5},
    {"name": "Jalapeños", "category": "Produce", "default_unit": "lbs", "usage_rate_per_week": 0.5, "current_stock": 1, "min_stock": 0.5},
    {"name": "Cucumber", "category": "Produce", "default_unit": "lbs", "usage_rate_per_week": 2, "current_stock": 3, "min_stock": 1},
    {"name": "Lemons", "category": "Produce", "default_unit": "ea", "usage_rate_per_week": 8, "current_stock": 12, "min_stock": 4},
    {"name": "Rice", "category": "Dry Goods", "default_unit": "lbs", "usage_rate_per_week": 3, "current_stock": 5, "min_stock": 2},
]

PREP_ITEMS = [
    {"name": "Cinnamon Whipped Topping", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Creamy Coleslaw Dressing", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Croutons", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Garlic Aioli", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Marinara Sauce", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Meat Sauce", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Sweet Jerk Rub", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Tarter Sauce", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Arancini Balls", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Burger Meat (form patties)", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Buttermilk Chicken (marinate)", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Candied Jalapeño", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Coleslaw (pre-mix)", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Crispy Rice", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Crostini", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "French Fries (portion)", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "French Fries (side)", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "French Onion Soup (base)", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Lamb Slider Meat", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Pickled Cucumber", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Rice Cakes", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Risotto (base)", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Roasted Red Peppers", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Seasoned Chicken", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Whipped Feta", "category": "Sub-Recipe", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Toast Buns", "category": "Prep", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Warm Plates", "category": "Prep", "default_unit": "batch", "is_sub_ingredient": 1},
    {"name": "Cut Fries", "category": "Prep", "default_unit": "lbs", "is_sub_ingredient": 1},
]

MENU_ITEMS = [
    {"name": "Whipped Feta Burger", "prep_items": ["Whipped Feta", "Burger Meat (form patties)", "Toast Buns"]},
    {"name": "Smash Burger", "prep_items": ["Burger Meat (form patties)", "Toast Buns", "Pickled Cucumber"]},
    {"name": "Smash Dog", "prep_items": ["Toast Buns", "Pickled Cucumber"]},
    {"name": "Buttermilk Chicken Sandwich", "prep_items": ["Buttermilk Chicken (marinate)", "Coleslaw (pre-mix)", "Toast Buns"]},
    {"name": "Lamb Slider", "prep_items": ["Lamb Slider Meat", "Toast Buns", "Pickled Cucumber"]},
    {"name": "Arancini Plate", "prep_items": ["Arancini Balls", "Marinara Sauce"]},
    {"name": "French Onion Soup", "prep_items": ["French Onion Soup (base)", "Croutons"]},
]


def run_seed():
    from database import seed_ingredients, seed_menu_items
    all_ingredients = SHOPPING_INGREDIENTS + PREP_ITEMS
    seed_ingredients(all_ingredients)
    seed_menu_items(MENU_ITEMS)


if __name__ == "__main__":
    run_seed()
