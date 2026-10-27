"""Sample catalogues for the market version.

These are illustrative, in-app catalogues (not a live marketplace):
sample vendors, products, themes, decor ideas, games and music.
Users can add their own vendors/products, and prices are in the
event's chosen currency unit — they are planning estimates, not quotes.
"""

from __future__ import annotations

THEMES = {
    "Space": {"colors": ["#3B115F", "#7A2A9E", "#FFD700", "#FFFFFF"],
              "ideas": ["Astronaut photo booth", "Planet cupcakes", "Star return gifts"]},
    "Garden": {"colors": ["#2E7D32", "#A5D6A7", "#FFF59D", "#FFFFFF"],
               "ideas": ["Flower arch", "Fairy lights in trees", "Herb favours"]},
    "Elegant Gold": {"colors": ["#1A1A1A", "#C9A227", "#FFF8E1", "#FFFFFF"],
                     "ideas": ["Gold centrepieces", "Candlelit tables", "Chandelier backdrop"]},
    "Rainbow / Fun": {"colors": ["#E91E63", "#FF9800", "#2196F3", "#4CAF50"],
                      "ideas": ["Balloon arch", "Colourful bunting", "Rainbow cake"]},
    "Traditional": {"colors": ["#B71C1C", "#FF8F00", "#FFF3E0", "#4E342E"],
                    "ideas": ["Marigold garlands", "Brass lamps", "Traditional music"]},
    "Minimalist": {"colors": ["#FAFAFA", "#9E9E9E", "#212121", "#FFFFFF"],
                   "ideas": ["Single floral arch", "White linen", "One focal backdrop"]},
    "Beach": {"colors": ["#0288D1", "#B3E5FC", "#FFF9C4", "#FFFFFF"],
              "ideas": ["Seashell centrepieces", "Fairy lights", "Barefoot photo corner"]},
    "Winter Wonderland": {"colors": ["#0D47A1", "#BBDEFB", "#FFFFFF", "#E0E0E0"],
                          "ideas": ["Snowflake decor", "White lights", "Hot chocolate station"]},
}

DECOR_SECTIONS = {
    "Balloon decoration": ["Balloon arch at entrance", "Balloon garland on stage", "Helium bunches per table"],
    "Flower decoration": ["Stage flowers", "Table centrepieces", "Entrance garlands"],
    "Stage decoration": ["Backdrop", "Stage lighting", "Name / theme board"],
    "Table decoration": ["Tablecloth + runner", "Centrepiece", "Place cards"],
    "Lighting": ["Fairy lights", "Spotlights for stage", "Candles / LED candles"],
    "Entrance decoration": ["Welcome sign", "Flower arch", "Photo corner"],
    "DIY ideas": ["Paper bunting", "Photo wall with prints", "Hand-painted welcome board"],
}

SAMPLE_VENDORS = [
    {"name": "Dream Venue Hall", "category": "Venue", "city": "Toronto", "rating": 4.7, "price_from": 50000, "available": "Weekends"},
    {"name": "Garden Banquet", "category": "Venue", "city": "Mumbai", "rating": 4.5, "price_from": 80000, "available": "All week"},
    {"name": "Tasty Bites Catering", "category": "Caterer", "city": "Toronto", "rating": 4.8, "price_from": 1200, "available": "All week"},
    {"name": "Sweet Layers Bakery", "category": "Baker", "city": "Toronto", "rating": 4.9, "price_from": 5000, "available": "Order 7 days ahead"},
    {"name": "Lens & Light Studio", "category": "Photographer", "city": "Mumbai", "rating": 4.6, "price_from": 25000, "available": "Weekends"},
    {"name": "DJ Beats", "category": "DJ", "city": "Toronto", "rating": 4.7, "price_from": 15000, "available": "Weekends"},
    {"name": "Bloom & Co Florist", "category": "Florist", "city": "Toronto", "rating": 4.8, "price_from": 8000, "available": "All week"},
    {"name": "Party Rentals Plus", "category": "Rental", "city": "Toronto", "rating": 4.4, "price_from": 10000, "available": "All week"},
    {"name": "Magic Moments Entertainer", "category": "Kids' Entertainer", "city": "Mumbai", "rating": 4.9, "price_from": 12000, "available": "Weekends"},
    {"name": "Elegant Decor Studio", "category": "Decorator", "city": "Toronto", "rating": 4.6, "price_from": 30000, "available": "All week"},
]

PRODUCTS = [
    {"name": "Balloon Arch Kit (100 pcs)", "category": "Decor", "price": 2500},
    {"name": "Fairy Lights (10m)", "category": "Decor", "price": 1200},
    {"name": "Photo Booth Props Set", "category": "Decor", "price": 1500},
    {"name": "Paper Plates (100 pcs)", "category": "Tableware", "price": 800},
    {"name": "Return Gift Bags (50 pcs)", "category": "Gifts", "price": 3000},
    {"name": "Cake Topper — Personalised", "category": "Cake", "price": 900},
    {"name": "Party Hats (50 pcs)", "category": "Decor", "price": 1000},
    {"name": "Craft Kit for Kids (20 sets)", "category": "Kids", "price": 4000},
]

GAMES_LIBRARY = [
    {"name": "Treasure Hunt", "age": "Kids", "place": "Outdoor", "duration": "20 min", "materials": "Clues, small prizes", "budget": "Low"},
    {"name": "Musical Chairs", "age": "Kids", "place": "Indoor", "duration": "15 min", "materials": "Chairs, music", "budget": "Low"},
    {"name": "Team Trivia", "age": "Adults", "place": "Indoor", "duration": "20 min", "materials": "Questions, buzzer/app", "budget": "Low"},
    {"name": "Couple Quiz", "age": "Adults", "place": "Indoor", "duration": "20 min", "materials": "Questions about the couple", "budget": "Low"},
    {"name": "Scavenger Hunt", "age": "Family", "place": "Outdoor", "duration": "30 min", "materials": "List, phone camera", "budget": "Low"},
    {"name": "Charades", "age": "Family", "place": "Indoor", "duration": "20 min", "materials": "Word cards", "budget": "Low"},
    {"name": "Relay Races", "age": "Kids", "place": "Outdoor", "duration": "25 min", "materials": "Cones, batons", "budget": "Low"},
    {"name": "Bingo", "age": "Family", "place": "Indoor", "duration": "20 min", "materials": "Bingo cards, prizes", "budget": "Low"},
    {"name": "Dance Competition", "age": "Teens", "place": "Indoor", "duration": "30 min", "materials": "Music, judges", "budget": "Medium"},
    {"name": "Photo Challenge", "age": "Family", "place": "Indoor", "duration": "20 min", "materials": "Phone camera, prompts", "budget": "Low"},
]

MUSIC_LIBRARY = [
    ("Welcome", "Soft upbeat background"),
    ("Birthday Song", "Birthday"),
    ("Wedding Entrance", "Wedding"),
    ("First Dance", "Wedding"),
    ("Cake Cutting", "Birthday / Wedding"),
    ("Dance Hits", "Dance"),
    ("Kids' Dance", "Kids"),
    ("Dinner Background", "Background"),
    ("Closing", "Background"),
]

KIDS_ACTIVITIES = {
    "Toddler (1-3)": ["Sensory play station", "Soft ball pit", "Bubble play"],
    "Preschool (3-5)": ["Face painting", "Craft station", "Balloon animals"],
    "School-age (6-10)": ["Treasure hunt", "Science demo", "Art competition"],
    "Teen (11-16)": ["Dance competition", "Photo challenge", "Quiz night"],
}

CAKE_FLAVOURS = ["Chocolate", "Vanilla", "Strawberry", "Butterscotch", "Red Velvet", "Mango", "Black Forest"]
INVITATION_TEMPLATES = ["Elegant", "Fun & Colourful", "Traditional", "Minimalist", "Photo Style"]

EVENT_TEMPLATES = [
    {"name": "Kids Birthday — Space", "event_type": "Birthday", "guests": 50, "theme": "Space"},
    {"name": "Wedding — Elegant Gold", "event_type": "Wedding", "guests": 200, "theme": "Elegant Gold"},
    {"name": "Community Festival", "event_type": "Community Event", "guests": 150, "theme": "Rainbow / Fun"},
    {"name": "Anniversary Dinner", "event_type": "Anniversary", "guests": 40, "theme": "Elegant Gold"},
]
