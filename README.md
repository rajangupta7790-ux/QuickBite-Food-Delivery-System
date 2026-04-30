# 🍔 QuickBite - Food Delivery System

--- Home Page ---

<img width="1883" height="907" alt="Screenshot 2026-04-30 110054" src="https://github.com/user-attachments/assets/ad4afce3-694e-444b-91f4-780267573516" />




A modern **Django-based food delivery web application** similar to Zomato/Swiggy. Order food from your favorite restaurants with real-time tracking and multiple payment options.

---

## 🌟 Features

### 👥 User Features
- **User Registration & Authentication** - Secure sign-up and login
- **Restaurant Discovery** - Search, filter, and browse restaurants
- **Menu Browsing** - View restaurant menus with categories
- **Shopping Cart** - Add/remove items with real-time updates
- **Order Placement** - Checkout with delivery details
- **Order Tracking** - Track your order status in real-time
- **Coupon Codes** - Apply discount coupons (FIRST50, SAVE20, FREESHIP)
- **User Profile** - Manage personal info, saved addresses, and payment methods
- **Order History** - View past orders and reorder quickly

### 🏪 Restaurant Management
- **Restaurant Dashboard** - Manage restaurant details and menu items
- **Menu Management** - Add/edit/delete food items with categories
- **Order Management** - Track incoming orders and update status

### 🛠️ Admin Features
- **Admin Dashboard** - View sales analytics and order stats
- **User Management** - View, edit, delete, or ban users
- **Restaurant Management** - Manage all restaurants
- **Coupon Management** - Create and manage discount coupons
- **7-Day Analytics** - Visual charts of order trends

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Django 6.0.3 |
| **Language** | Python 3.8+ |
| **Database** | SQLite3 |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Authentication** | Django Built-in Auth |
| **Image Handling** | Pillow |

---

## 📋 Requirements

- **Python 3.8** or higher
- **pip** (Python package manager)
- **Git** (for version control)

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/QuickBite.git
cd QuickBite
```

### 2️⃣ Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Setup Database
```bash
# Create database tables
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Follow prompts to create your admin account
```

### 5️⃣ Load Sample Data (Optional)
```bash
python manage.py seed_data
```

### 6️⃣ Run Development Server
```bash
python manage.py runserver
```

**Your app is now running on:** `http://localhost:8000`

---

## 📍 Important URLs

| Page | URL |
|------|-----|
| Home | http://localhost:8000/ |
| Restaurants | http://localhost:8000/restaurants/ |
| Cart | http://localhost:8000/cart/ |
| Orders | http://localhost:8000/orders/ |
| Profile | http://localhost:8000/profile/ |
| Admin Panel | http://localhost:8000/admin/ |

---

## 💳 Available Coupons

Test these coupon codes during checkout:

| Code | Discount | Validity |
|------|----------|----------|
| **FIRST50** | 50% OFF | First order only (24 hours) |
| **SAVE20** | ₹20 Flat OFF | Minimum ₹199 order |
| **FREESHIP** | Free Delivery | No minimum order |

---

## 📊 Database Models

```
User (Django Built-in)
├── UserProfile (Phone, Address, Avatar)
├── Orders (Order details & tracking)
│   └── OrderItems (Items in each order)
├── Addresses (Saved delivery addresses)
├── PaymentMethods (Saved cards)
└── NotificationPreferences

Restaurant
├── MenuCategories
│   └── MenuItems
├── Orders (Related orders)
└── Categories (Food types)
```

---

## 🔐 Security Notes

⚠️ **For Development Only:**
- `DEBUG = True` is enabled (disable in production)
- `SECRET_KEY` is exposed (change in production)
- Use environment variables for sensitive data
- Enable HTTPS in production
- Set `ALLOWED_HOSTS` properly

### Production Checklist:
- [ ] Set `DEBUG = False`
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Setup proper authentication & permissions
- [ ] Integrate real payment gateway
- [ ] Add email verification
- [ ] Implement rate limiting

---

## 🚀 Future Enhancements

- [ ] Real payment gateway integration (Razorpay, Stripe)
- [ ] Email & SMS notifications
- [ ] Real-time order tracking (WebSockets)
- [ ] Restaurant reviews & ratings
- [ ] Wallet & loyalty points system
- [ ] Mobile app (React Native/Flutter)
- [ ] Delivery partner tracking
- [ ] Multiple language support

---

## 👨‍💻 Project Structure

```
QuickBite/
├── manage.py                 # Django management
├── requirements.txt          # Python dependencies
├── db.sqlite3                # Database
│
├── fooddelivery/             # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── core/                     # Main app
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── urls.py              # URL routing
│   ├── admin.py             # Admin interface
│   │
│   ├── templates/core/      # HTML templates
│   │   ├── home.html
│   │   ├── restaurant_menu.html
│   │   ├── cart.html
│   │   ├── checkout.html
│   │   └── ... (18+ templates)
│   │
│   ├── management/
│   │   └── commands/
│   │       ├── seed_data.py      # Load sample data
│   │       └── add_categories.py
│   │
│   └── migrations/          # Database migrations
│
└── static/                  # CSS, JS, Images
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

---

## 🐛 Troubleshooting

### Issue: "Port 8000 already in use"
```bash
python manage.py runserver 8080
```

### Issue: "No module named 'django'"
```bash
pip install -r requirements.txt
```

### Issue: "Migration errors"
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: "Static files not showing"
```bash
python manage.py collectstatic --noinput
```

---

## 📧 Contact & Support

- **Author:** Your Name
- **Email:** your.email@example.com
- **GitHub:** [@yourusername](https://github.com/yourusername)

---

## 🎓 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Python Official Docs](https://www.python.org/doc/)
- [HTML/CSS/JavaScript MDN](https://developer.mozilla.org/)

---

**Made with Mr.Rajan❤️ | Happy Coding! 🚀**

--- Admin Page --- 
<img width="1887" height="913" alt="Screenshot 2026-04-30 110118" src="https://github.com/user-attachments/assets/171c4692-425a-4f68-8b26-cb330b1b86c8" />

---- Menu Items ----

<img width="1610" height="838" alt="Screenshot 2026-04-30 110140" src="https://github.com/user-attachments/assets/4932a8db-f03c-4632-88aa-a7f4e0140844" />




