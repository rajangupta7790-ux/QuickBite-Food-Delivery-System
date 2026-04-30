"""
Management command to seed demo data.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from core.models import Category, Restaurant, MenuCategory, MenuItem, UserProfile


CATEGORIES = [
    ("Pizza",     "🍕"),
    ("Burgers",   "🍔"),
    ("Biryani",   "🍛"),
    ("Chinese",   "🍜"),
    ("Sushi",     "🍣"),
    ("Salads",    "🥗"),
    ("Desserts",  "🍦"),
    ("Beverages", "☕"),
    ("Wraps",     "🥙"),
    ("Thali",     "🍱"),
]

RESTAURANTS = [
    {
        "name": "Spice Garden",
        "cuisine": "North Indian, Mughlai",
        "emoji": "🍛",
        "rating": 4.5,
        "delivery_time": 30,
        "min_order": 149,
        "avg_cost": 350,
        "discount": "40% OFF upto ₹80",
        "is_pure_veg": False,
        "menu": {
            "Bestsellers": [
                ("Butter Chicken",  "Rich creamy tomato gravy",  280, 349, False),
                ("Dal Makhani",     "Slow cooked black lentils",  180, 220, True),
                ("Paneer Tikka",    "Char-grilled cottage cheese",240, 299, True),
            ],
            "Breads": [
                ("Butter Naan",     "Soft leavened bread",        40,  None, True),
                ("Garlic Naan",     "With garlic & butter",       50,  None, True),
                ("Laccha Paratha",  "Layered whole wheat",        45,  None, True),
            ],
            "Rice": [
                ("Jeera Rice",      "Cumin flavoured basmati",    120, None, True),
                ("Veg Biryani",     "Fragrant basmati with veggies",220,280, True),
            ],
            "Desserts": [
                ("Gulab Jamun",     "Soft milk dumplings",        80,  None, True),
                ("Kheer",           "Rice pudding",               90,  None, True),
            ],
        },
    },
    {
        "name": "Burger Barn",
        "cuisine": "American, Fast Food",
        "emoji": "🍔",
        "rating": 4.3,
        "delivery_time": 25,
        "min_order": 99,
        "avg_cost": 200,
        "discount": "Buy 1 Get 1",
        "is_pure_veg": False,
        "menu": {
            "Burgers": [
                ("Classic Beef Burger",  "Juicy beef patty",       199, 249, False),
                ("Chicken Zinger",       "Crispy fried chicken",   179, 219, False),
                ("Veggie Delight",       "Aloo tikki patty",       149, 189, True),
                ("Double Smash Burger",  "Double patty smash",     279, 329, False),
            ],
            "Sides": [
                ("Loaded Fries",   "With cheese & jalapeños",   99,  None, True),
                ("Onion Rings",    "Crispy battered rings",     79,  None, True),
                ("Coleslaw",       "Creamy house slaw",         49,  None, True),
            ],
            "Beverages": [
                ("Thick Shake",    "Chocolate/Vanilla/Strawberry",129, None, True),
                ("Fresh Lime Soda","Chilled & refreshing",       59,  None, True),
            ],
        },
    },
    {
        "name": "Wok & Roll",
        "cuisine": "Chinese, Thai, Pan-Asian",
        "emoji": "🍜",
        "rating": 4.2,
        "delivery_time": 35,
        "min_order": 149,
        "avg_cost": 300,
        "discount": "20% OFF",
        "is_pure_veg": False,
        "menu": {
            "Noodles & Rice": [
                ("Chicken Hakka Noodles", "Wok tossed noodles",  180, 220, False),
                ("Veg Fried Rice",        "Classic fried rice",  160, 190, True),
                ("Pad Thai",              "Thai style noodles",  220, 270, False),
            ],
            "Starters": [
                ("Veg Spring Rolls",  "Crispy with veggies",  120, None, True),
                ("Chicken Dimsums",   "Steamed dumplings",    160, None, False),
                ("Chilli Paneer",     "Dry / Gravy",          200, 240, True),
            ],
            "Main Course": [
                ("Kung Pao Chicken",  "Spicy Sichuan style",  240, None, False),
                ("Tofu in Black Bean","Silken tofu",          200, None, True),
            ],
        },
    },
    {
        "name": "Green Bowl",
        "cuisine": "Healthy, Salads, Wraps",
        "emoji": "🥗",
        "rating": 4.4,
        "delivery_time": 20,
        "min_order": 129,
        "avg_cost": 250,
        "discount": "",
        "is_pure_veg": True,
        "menu": {
            "Salads": [
                ("Caesar Salad",   "Romaine, croutons, parmesan", 180, None, True),
                ("Greek Salad",    "Olives, feta, cucumber",      190, None, True),
                ("Quinoa Bowl",    "Protein-packed superfood",    220, None, True),
            ],
            "Wraps": [
                ("Hummus Wrap",    "Roasted veggies & hummus",    160, None, True),
                ("Falafel Wrap",   "Crispy falafel, tzatziki",    170, None, True),
            ],
            "Juices": [
                ("Green Detox",    "Spinach, apple, ginger",       99, None, True),
                ("Berry Blast",    "Mixed berries & yoghurt",     110, None, True),
            ],
        },
    },
    {
        "name": "Pizza Peak",
        "cuisine": "Pizza, Italian",
        "emoji": "🍕",
        "rating": 4.1,
        "delivery_time": 40,
        "min_order": 199,
        "avg_cost": 400,
        "discount": "Flat ₹100 OFF",
        "is_pure_veg": False,
        "menu": {
            "Pizzas": [
                ("Margherita",         "Tomato, mozzarella, basil",  249, 299, True),
                ("Pepperoni",          "Classic American pepperoni", 329, 379, False),
                ("BBQ Chicken",        "Smoky BBQ sauce, chicken",   349, 399, False),
                ("Paneer Makhani",     "Indian twist pizza",         299, 349, True),
                ("Veggie Supreme",     "Garden fresh vegetables",    279, 329, True),
            ],
            "Sides": [
                ("Garlic Bread",   "With cheese dip",               99, None, True),
                ("Pasta Arrabiata","Spicy tomato pasta",            179, None, True),
            ],
        },
    },
]


class Command(BaseCommand):
    help = 'Seed database with demo restaurants, menus, and users'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding demo data...')

        # Categories
        for i, (name, emoji) in enumerate(CATEGORIES):
            Category.objects.get_or_create(
                slug=slugify(name),
                defaults={'name': name, 'emoji': emoji, 'order': i}
            )
        self.stdout.write('  ✅ Categories created')

        # Restaurants & menus
        for r_data in RESTAURANTS:
            menu_data = r_data.pop('menu')
            restaurant, created = Restaurant.objects.get_or_create(
                slug=slugify(r_data['name']),
                defaults=r_data
            )
            if created:
                for cat_order, (cat_name, items) in enumerate(menu_data.items()):
                    menu_cat = MenuCategory.objects.create(
                        restaurant=restaurant,
                        name=cat_name,
                        order=cat_order
                    )
                    for item_order, (iname, idesc, iprice, iorig, iveg) in enumerate(items):
                        MenuItem.objects.create(
                            restaurant    = restaurant,
                            menu_category = menu_cat,
                            name          = iname,
                            description   = idesc,
                            price         = iprice,
                            original_price= iorig,
                            is_veg        = iveg,
                            order         = item_order,
                            is_bestseller = item_order == 0,
                        )
                r_data['menu'] = menu_data  # restore for next iteration
        self.stdout.write('  ✅ Restaurants & menus created')

        # Demo user
        if not User.objects.filter(username='demo').exists():
            u = User.objects.create_user(
                username='demo', email='demo@quickbite.com',
                password='demo123', first_name='Demo', last_name='User'
            )
            UserProfile.objects.create(user=u, phone='9876543210')
            self.stdout.write('  ✅ Demo user: demo / demo123')

        # Admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin', email='admin@quickbite.com', password='admin123'
            )
            self.stdout.write('  ✅ Admin user: admin / admin123')

        self.stdout.write(self.style.SUCCESS('\n🎉 Seeding complete!'))