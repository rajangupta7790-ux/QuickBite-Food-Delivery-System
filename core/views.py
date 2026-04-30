from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Address, PaymentMethod, NotificationPreference

from .models import (
    Restaurant, MenuItem, Category,
    MenuCategory, Order, OrderItem, UserProfile
)


# ─────────────────────────────────────────
#  HOME PAGE
# ─────────────────────────────────────────
def home(request):
    restaurants = Restaurant.objects.filter(is_active=True).select_related()[:12]
    categories  = Category.objects.all()
    top_rated   = Restaurant.objects.filter(is_active=True, rating__gte=4.3)[:4]

    # Filter by category if query param present
    cat_slug = request.GET.get('category')
    if cat_slug:
        restaurants = Restaurant.objects.filter(
            is_active=True, categories__slug=cat_slug
        )

    context = {
        'restaurants': restaurants,
        'categories':  categories,
        'top_rated':   top_rated,
        'active_cat':  cat_slug or 'all',
    }
    return render(request, 'core/home.html', context)


# ─────────────────────────────────────────
#  RESTAURANT LIST
# ─────────────────────────────────────────
def restaurant_list(request):
    qs = Restaurant.objects.filter(is_active=True)

    q      = request.GET.get('q', '')
    sort   = request.GET.get('sort', 'relevance')
    is_veg = request.GET.get('veg')

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(cuisine__icontains=q))
    if is_veg:
        qs = qs.filter(is_pure_veg=True)
    if sort == 'rating':
        qs = qs.order_by('-rating')
    elif sort == 'delivery_time':
        qs = qs.order_by('delivery_time')
    elif sort == 'cost_low':
        qs = qs.order_by('min_order')
    elif sort == 'cost_high':
        qs = qs.order_by('-min_order')

    return render(request, 'core/restaurant_list.html', {
        'restaurants': qs,
        'q': q,
        'sort': sort,
    })


# ─────────────────────────────────────────
#  RESTAURANT MENU
# ─────────────────────────────────────────
def restaurant_menu(request, pk):
    restaurant      = get_object_or_404(Restaurant, pk=pk, is_active=True)
    menu_categories = restaurant.menu_categories.prefetch_related('items').all()
    return render(request, 'core/restaurant_menu.html', {
        'restaurant':      restaurant,
        'menu_categories': menu_categories,
        'demo_sections':   ['Bestsellers', 'Starters', 'Main Course', 'Desserts'],
    })


# ─────────────────────────────────────────
#  CART  (session-based)
# ─────────────────────────────────────────
def cart(request):
    # AJAX request — sidebar ke liye JSON return karo
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_data = request.session.get('cart', {})
        items = []
        subtotal = 0
        for item_id, item in cart_data.items():
            total = item['price'] * item['quantity']
            subtotal += total
            items.append({
                'id':       int(item_id),
                'name':     item['name'],
                'price':    item['price'],
                'quantity': item['quantity'],
                'total':    total,
                'is_veg':   item.get('is_veg', True),
            })
        delivery_fee = 0 if subtotal >= 299 else 40
        total = subtotal + delivery_fee + 5
        return JsonResponse({
            'items':        items,
            'subtotal':     subtotal,
            'delivery_fee': delivery_fee,
            'total':        total,
            'count':        sum(v['quantity'] for v in cart_data.values()),
        })

    cart_data = request.session.get('cart', {})

    cart_items      = []
    subtotal        = 0
    restaurant_id   = request.session.get('cart_restaurant_id')
    restaurant_name = ''

    if restaurant_id:
        try:
            r = Restaurant.objects.get(pk=restaurant_id)
            restaurant_name = r.name
        except Restaurant.DoesNotExist:
            pass

    for item_id, item in cart_data.items():
        total = item['price'] * item['quantity']
        subtotal += total
        cart_items.append({
            'id':       int(item_id),
            'name':     item['name'],
            'price':    item['price'],
            'quantity': item['quantity'],
            'total':    total,
            'is_veg':   item.get('is_veg', True),
        })

    delivery_fee = 0 if subtotal >= 299 else 40
    total = subtotal + delivery_fee + 5  # +5 platform fee

    return render(request, 'core/cart.html', {
        'cart_items':         cart_items,
        'subtotal':           subtotal,
        'delivery_fee':       delivery_fee,
        'total':              total,
        'restaurant_name':    restaurant_name,
        'restaurant_id':      restaurant_id,
        'free_delivery_gap':  max(0, 299 - subtotal),
    })


@require_POST
def add_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required'}, status=401)
    data      = json.loads(request.body)
    item_id   = str(data.get('item_id'))
    cart      = request.session.get('cart', {})

    try:
        item = MenuItem.objects.get(pk=item_id, is_available=True)
    except MenuItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

    # Enforce single restaurant rule
    cart_restaurant = request.session.get('cart_restaurant_id')
    if cart_restaurant and str(cart_restaurant) != str(item.restaurant_id):
        return JsonResponse({'error': 'different_restaurant',
                             'message': 'Clear cart to order from a new restaurant'}, status=400)

    if item_id in cart:
        cart[item_id]['quantity'] += 1
    else:
        cart[item_id] = {
            'name':     item.name,
            'price':    float(item.price),
            'quantity': 1,
            'is_veg':   item.is_veg,
        }
        request.session['cart_restaurant_id'] = item.restaurant_id

    request.session['cart'] = cart
    request.session.modified = True

    count = sum(v['quantity'] for v in cart.values())
    return JsonResponse({'success': True, 'cart_count': count})


@require_POST
def update_cart(request):
    data    = json.loads(request.body)
    item_id = str(data.get('item_id'))
    delta   = int(data.get('delta', 0))
    cart    = request.session.get('cart', {})

    if item_id in cart:
        cart[item_id]['quantity'] += delta
        if cart[item_id]['quantity'] <= 0:
            del cart[item_id]
            if not cart:
                request.session.pop('cart_restaurant_id', None)

    request.session['cart'] = cart
    request.session.modified = True

    count = sum(v['quantity'] for v in cart.values())
    total = sum(v['price'] * v['quantity'] for v in cart.values())
    return JsonResponse({'success': True, 'cart_count': count, 'total': total})


@require_POST
def clear_cart(request):
    request.session['cart'] = {}
    request.session.pop('cart_restaurant_id', None)
    request.session.modified = True
    return JsonResponse({'success': True})


# ─────────────────────────────────────────
#  CHECKOUT
# ─────────────────────────────────────────
@login_required
def checkout(request):
    cart_data = request.session.get('cart', {})
    if not cart_data:
        return redirect('cart')

    cart_items = []
    subtotal   = 0
    for item_id, item in cart_data.items():
        total     = item['price'] * item['quantity']
        subtotal += total
        cart_items.append({**item, 'total': total})

    delivery_fee = 0 if subtotal >= 299 else 40
    total        = subtotal + delivery_fee + 5

    return render(request, 'core/checkout.html', {
        'cart_items':   cart_items,
        'subtotal':     subtotal,
        'delivery_fee': delivery_fee,
        'total':        total,
    })


@login_required
@require_POST
def place_order(request):
    cart_data     = request.session.get('cart', {})
    restaurant_id = request.session.get('cart_restaurant_id')

    if not cart_data or not restaurant_id:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        messages.error(request, 'Restaurant not found.')
        return redirect('cart')

    subtotal     = sum(v['price'] * v['quantity'] for v in cart_data.values())
    delivery_fee = 0 if subtotal >= 299 else 40

    # Coupon validation
    COUPONS = {
        'FIRST50':   {'type': 'percent', 'value': 50},
        'SAVE20':    {'type': 'flat',    'value': 20},
        'FREESHIP':  {'type': 'ship',    'value': 0},
    }
    coupon_code = request.POST.get('coupon_code', '').strip().upper()
    discount = 0
    if coupon_code in COUPONS:
        c = COUPONS[coupon_code]
        if c['type'] == 'percent':
            discount = round(subtotal * c['value'] / 100)
        elif c['type'] == 'flat':
            discount = c['value']
        elif c['type'] == 'ship':
            discount = delivery_fee

    total = subtotal + delivery_fee + 5 - discount

    order = Order.objects.create(
        user           = request.user,
        restaurant     = restaurant,
        status         = 'confirmed',
        payment_method = request.POST.get('payment_method', 'cod'),
        full_name      = request.POST.get('full_name', ''),
        phone          = request.POST.get('phone', ''),
        address        = request.POST.get('address', ''),
        city           = request.POST.get('city', ''),
        pincode        = request.POST.get('pincode', ''),
        instructions   = request.POST.get('instructions', ''),
        subtotal       = subtotal,
        delivery_fee   = delivery_fee,
        discount       = discount,
        total          = total,
    )

    for item_id, item in cart_data.items():
        try:
            menu_item = MenuItem.objects.get(pk=int(item_id))
        except MenuItem.DoesNotExist:
            continue
        OrderItem.objects.create(
            order     = order,
            menu_item = menu_item,
            name      = item['name'],
            price     = item['price'],
            quantity  = item['quantity'],
        )

    # Clear cart
    request.session['cart'] = {}
    request.session.pop('cart_restaurant_id', None)
    request.session.modified = True

    return redirect('order_confirmation', pk=order.pk)


# ─────────────────────────────────────────
#  ORDER CONFIRMATION
# ─────────────────────────────────────────
@login_required
def order_confirmation(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    
    status_steps = ['pending', 'confirmed', 'preparing', 'out_for_delivery', 'delivered']
    current_step = status_steps.index(order.status) + 1 if order.status in status_steps else 1
    
    return render(request, 'core/order_confirmation.html', {
        'order':        order,
        'current_step': current_step,
    })


# ─────────────────────────────────────────
#  ORDERS LIST
# ─────────────────────────────────────────
@login_required
def orders(request):
    user_orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('items').select_related('restaurant')

    active = user_orders.filter(status__in=['pending','confirmed','preparing','out_for_delivery'])
    past   = user_orders.filter(status__in=['delivered','cancelled'])

    return render(request, 'core/orders.html', {
        'orders':  user_orders,
        'active':  active,
        'past':    past,
    })


@login_required
@require_POST
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.status in ('pending', 'confirmed'):
        order.status = 'cancelled'
        order.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Cannot cancel this order'}, status=400)


# ─────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user     = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}! 👋')
            return redirect(request.POST.get('next') or 'home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'core/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name  = request.POST.get('last_name', '')
        username   = request.POST.get('username', '')
        email      = request.POST.get('email', '')
        password1  = request.POST.get('password1', '')
        password2  = request.POST.get('password2', '')
        phone      = request.POST.get('phone', '')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            user = User.objects.create_user(
                username   = username,
                email      = email,
                password   = password1,
                first_name = first_name,
                last_name  = last_name,
            )
            UserProfile.objects.create(user=user, phone=phone)
            login(request, user)
            # Welcome coupon — 24hr expiry
            import time
            request.session['welcome_coupon'] = {
                'code':    'FIRST50',
                'desc':    '50% OFF on your first order',
                'expires': time.time() + 86400  # 24 hours
            }
            messages.success(request, f'Welcome to QuickBite, {first_name}! 🎉')
            return redirect('home')

    return render(request, 'core/register.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


# ─────────────────────────────────────────
#  PROFILE
# ─────────────────────────────────────────
@login_required
def profile(request):
    recent_orders = Order.objects.filter(user=request.user)[:5]
    available_coupons = [
        {'code': 'SAVE20',   'desc': '₹20 Flat OFF',   'min_order': 199},
        {'code': 'FREESHIP', 'desc': 'Free Delivery',   'min_order': 0},
    ]
    return render(request, 'core/profile.html', {
        'recent_orders':     recent_orders,
        'total_orders':      Order.objects.filter(user=request.user).count(),
        'available_coupons': available_coupons,
    })


@login_required
@require_POST
def update_profile(request):
    user = request.user
    user.first_name = request.POST.get('first_name', user.first_name)
    user.last_name  = request.POST.get('last_name',  user.last_name)
    user.email      = request.POST.get('email',      user.email)
    user.save()

    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.phone = request.POST.get('phone', profile.phone)
    profile.save()

    messages.success(request, 'Profile updated successfully!')
    return redirect('profile')


# ─────────────────────────────────────────
#  ADMIN DASHBOARD
# ─────────────────────────────────────────
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')

    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count

    # Last 7 days ka data
    today = timezone.now().date()
    last_7 = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    chart_labels = [d.strftime('%a') for d in last_7]
    chart_data   = [
        Order.objects.filter(created_at__date=d).count()
        for d in last_7
    ]

    # Order status breakdown
    status_counts = {s: 0 for s in ['pending','confirmed','preparing','out_for_delivery','delivered','cancelled']}
    for row in Order.objects.values('status').annotate(c=Count('id')):
        status_counts[row['status']] = row['c']
    status_data = list(status_counts.values())

    # Last 24 hours ke recent orders
    last_24h = timezone.now() - timedelta(hours=24)

    context = {
        'total_orders':      Order.objects.count(),
        'total_revenue':     sum(o.total for o in Order.objects.filter(status='delivered')),
        'total_restaurants': Restaurant.objects.count(),
        'total_users':       User.objects.count(),
        'recent_orders':     Order.objects.select_related('user', 'restaurant').filter(created_at__gte=last_24h)[:10],
        'restaurants':       Restaurant.objects.all()[:20],
        'chart_labels':      chart_labels,
        'chart_data':        chart_data,
        'status_data':       status_data,
    }
    return render(request, 'core/admin_dashboard.html', context)


@login_required
def admin_restaurants(request):
    if not request.user.is_staff:
        return redirect('home')
    restaurants = Restaurant.objects.all()
    context = {
        'restaurants': restaurants,
    }
    return render(request, 'core/admin_restaurants.html', context)


@login_required
def admin_orders(request):
    if not request.user.is_staff:
        return redirect('home')
    orders = Order.objects.select_related('user', 'restaurant').all()
    return render(request, 'core/admin_orders.html', {'orders': orders})


@login_required
def admin_users(request):
    if not request.user.is_staff:
        return redirect('home')
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'core/admin_users.html', {'users': users})


@login_required
def admin_coupons(request):
    if not request.user.is_staff:
        return redirect('home')
    coupons = [
        {'code': 'FIRST50',  'type': '50% OFF',       'min_order': 0,   'active': True},
        {'code': 'SAVE20',   'type': '₹20 Flat OFF',  'min_order': 199, 'active': True},
        {'code': 'FREESHIP', 'type': 'Free Delivery',  'min_order': 0,   'active': True},
    ]
    return render(request, 'core/admin_coupons.html', {'coupons': coupons})


@login_required
def admin_select_restaurant(request):
    if not request.user.is_staff:
        return redirect('home')
    restaurants = Restaurant.objects.all()
    return render(request, 'core/admin_select_restaurant.html', {'restaurants': restaurants})


@login_required
@require_POST
def admin_delete_user(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    try:
        user = User.objects.get(pk=pk)
        if user == request.user:
            return JsonResponse({'error': 'Cannot delete yourself'}, status=400)
        user.delete()
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


@login_required
@require_POST
def admin_ban_user(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    try:
        user = User.objects.get(pk=pk)
        if user == request.user:
            return JsonResponse({'error': 'Cannot ban yourself'}, status=400)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({'success': True, 'is_active': user.is_active})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


@login_required
@require_POST
def admin_edit_user(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    try:
        user = User.objects.get(pk=pk)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name  = request.POST.get('last_name',  user.last_name)
        user.email      = request.POST.get('email',      user.email)
        user.is_staff   = request.POST.get('is_staff') == 'true'
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.save()
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
@login_required
def admin_view_user(request, pk):
    if not request.user.is_staff:
        return redirect('home')
    u = get_object_or_404(User, pk=pk)
    user_orders = Order.objects.filter(user=u).select_related('restaurant').prefetch_related('items')
    return render(request, 'core/admin_view_user.html', {
        'u': u,
        'user_orders': user_orders,
    })


@login_required
@require_POST
def update_order_status(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    order  = get_object_or_404(Order, pk=pk)
    data   = json.loads(request.body)
    status = data.get('status')
    valid  = [s[0] for s in Order.STATUS_CHOICES]
    if status in valid:
        order.status = status
        order.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid status'}, status=400)

# ─────────────────────────────────────────
#  ADMIN — RESTAURANT CRUD
# ─────────────────────────────────────────
@login_required
def admin_add_restaurant(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        from django.utils.text import slugify
        name = request.POST.get('name','')
        restaurant = Restaurant.objects.create(
            name          = name,
            slug          = slugify(name),
            cuisine       = request.POST.get('cuisine',''),
            description   = request.POST.get('description',''),
            emoji         = request.POST.get('emoji','🍽️'),
            rating        = request.POST.get('rating', 4.0),
            delivery_time = request.POST.get('delivery_time', 30),
            min_order     = request.POST.get('min_order', 99),
            avg_cost      = request.POST.get('avg_cost', 200),
            delivery_fee  = request.POST.get('delivery_fee', 40),
            discount      = request.POST.get('discount',''),
            is_pure_veg   = request.POST.get('is_pure_veg') == 'on',
            is_active     = request.POST.get('is_active') == 'on',
        )
        
        # Create default menu categories
        default_categories = [
            'Bestsellers',
            'Appetizers',
            'Main Course',
            'Sides',
            'Desserts',
            'Beverages'
        ]
        for idx, cat_name in enumerate(default_categories, 1):
            MenuCategory.objects.create(
                restaurant=restaurant,
                name=cat_name,
                order=idx
            )
        
        messages.success(request, 'Restaurant added successfully! (Default categories created)')
        return redirect('admin_dashboard')
    return render(request, 'core/admin_restaurant_form.html', {'action': 'Add'})


@login_required
def admin_edit_restaurant(request, pk):
    if not request.user.is_staff:
        return redirect('home')
    restaurant = get_object_or_404(Restaurant, pk=pk)
    if request.method == 'POST':
        from django.utils.text import slugify
        restaurant.name          = request.POST.get('name', restaurant.name)
        restaurant.slug          = slugify(restaurant.name)
        restaurant.cuisine       = request.POST.get('cuisine', restaurant.cuisine)
        restaurant.description   = request.POST.get('description', restaurant.description)
        restaurant.emoji         = request.POST.get('emoji', restaurant.emoji)
        restaurant.rating        = request.POST.get('rating', restaurant.rating)
        restaurant.delivery_time = request.POST.get('delivery_time', restaurant.delivery_time)
        restaurant.min_order     = request.POST.get('min_order', restaurant.min_order)
        restaurant.avg_cost      = request.POST.get('avg_cost', restaurant.avg_cost)
        restaurant.delivery_fee  = request.POST.get('delivery_fee', restaurant.delivery_fee)
        restaurant.discount      = request.POST.get('discount', restaurant.discount)
        restaurant.is_pure_veg   = request.POST.get('is_pure_veg') == 'on'
        restaurant.is_active     = request.POST.get('is_active') == 'on'
        restaurant.save()
        messages.success(request, 'Restaurant updated!')
        return redirect('admin_dashboard')
    return render(request, 'core/admin_restaurant_form.html', {
        'action': 'Edit', 'restaurant': restaurant,
    })


@login_required
def admin_delete_restaurant(request, pk):
    if not request.user.is_staff:
        return redirect('home')
    restaurant = get_object_or_404(Restaurant, pk=pk)
    if request.method == 'POST':
        restaurant.delete()
        messages.success(request, 'Restaurant deleted.')
    return redirect('admin_dashboard')


@login_required
def admin_menu_items(request, restaurant_pk):
    if not request.user.is_staff:
        return redirect('home')
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
    items      = MenuItem.objects.filter(restaurant=restaurant).select_related('menu_category')
    return render(request, 'core/admin_menu_items.html', {
        'restaurant': restaurant, 'items': items,
    })


@login_required
def admin_add_menu_item(request, restaurant_pk):
    if not request.user.is_staff:
        return redirect('home')
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
    categories = MenuCategory.objects.filter(restaurant=restaurant)
    if request.method == 'POST':
        cat_id = request.POST.get('menu_category')
        
        # Validate that menu_category is not empty
        if not cat_id or cat_id.strip() == '':
            messages.error(request, 'Please select a menu category!')
            return render(request, 'core/admin_menu_form.html', {
                'action': 'Add', 'restaurant': restaurant, 'categories': categories,
            })
        
        menu_category = MenuCategory.objects.filter(pk=cat_id).first()
        if not menu_category:
            messages.error(request, 'Invalid menu category selected!')
            return render(request, 'core/admin_menu_form.html', {
                'action': 'Add', 'restaurant': restaurant, 'categories': categories,
            })
        
        MenuItem.objects.create(
            restaurant    = restaurant,
            menu_category = menu_category,
            name          = request.POST.get('name',''),
            description   = request.POST.get('description',''),
            price         = request.POST.get('price', 0),
            original_price= request.POST.get('original_price') or None,
            emoji         = request.POST.get('emoji','🍛'),
            is_veg        = request.POST.get('is_veg') == 'on',
            is_available  = request.POST.get('is_available') == 'on',
            is_bestseller = request.POST.get('is_bestseller') == 'on',
        )
        messages.success(request, 'Menu item added!')
        return redirect('admin_menu_items', restaurant_pk=restaurant_pk)
    return render(request, 'core/admin_menu_form.html', {
        'action': 'Add', 'restaurant': restaurant, 'categories': categories,
    })


@login_required
def admin_edit_menu_item(request, pk):
    if not request.user.is_staff:
        return redirect('home')
    item       = get_object_or_404(MenuItem, pk=pk)
    categories = MenuCategory.objects.filter(restaurant=item.restaurant)
    if request.method == 'POST':
        cat_id = request.POST.get('menu_category')
        item.menu_category  = MenuCategory.objects.filter(pk=cat_id).first()
        item.name           = request.POST.get('name', item.name)
        item.description    = request.POST.get('description', item.description)
        item.price          = request.POST.get('price', item.price)
        item.original_price = request.POST.get('original_price') or None
        item.emoji          = request.POST.get('emoji', item.emoji)
        item.is_veg         = request.POST.get('is_veg') == 'on'
        item.is_available   = request.POST.get('is_available') == 'on'
        item.is_bestseller  = request.POST.get('is_bestseller') == 'on'
        item.save()
        messages.success(request, 'Menu item updated!')
        return redirect('admin_menu_items', restaurant_pk=item.restaurant.pk)
    return render(request, 'core/admin_menu_form.html', {
        'action': 'Edit', 'item': item,
        'restaurant': item.restaurant, 'categories': categories,
    })


@login_required
def admin_delete_menu_item(request, pk):
    if not request.user.is_staff:
        return redirect('home')
    item = get_object_or_404(MenuItem, pk=pk)
    restaurant_pk = item.restaurant.pk
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Menu item deleted.')
    return redirect('admin_menu_items', restaurant_pk=restaurant_pk)

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    status_steps = ['pending','confirmed','preparing','out_for_delivery','delivered']
    current_step = status_steps.index(order.status) + 1 if order.status in status_steps else 1
    return render(request, 'core/order_detail.html', {
        'order':        order,
        'current_step': current_step,
    })

# ─────────────────────────────────────────
#  REORDER
# ─────────────────────────────────────────
@login_required
@require_POST
def reorder(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    cart  = {}
    for item in order.items.all():
        cart[str(item.menu_item_id)] = {
            'name':     item.name,
            'price':    float(item.price),
            'quantity': item.quantity,
            'is_veg':   item.menu_item.is_veg,
        }
    request.session['cart'] = cart
    request.session['cart_restaurant_id'] = order.restaurant_id
    request.session.modified = True
    count = sum(v['quantity'] for v in cart.values())
    return JsonResponse({'success': True, 'cart_count': count})



@login_required
def get_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return JsonResponse({
        'status': order.status,
        'status_display': order.get_status_display(),
        'updated_at': order.updated_at.isoformat()
    })
    
@login_required
def restaurant_list(request):
    restaurants = Restaurant.objects.filter(is_active=True)
    
    # Sort functionality
    sort = request.GET.get('sort', 'relevance')
    
    if sort == 'rating':
        restaurants = restaurants.order_by('-rating')
    elif sort == 'delivery_time':
        restaurants = restaurants.order_by('delivery_time')
    elif sort == 'cost_low':
        restaurants = restaurants.order_by('avg_cost')
    elif sort == 'cost_high':
        restaurants = restaurants.order_by('-avg_cost')
    else:  # relevance (default)
        restaurants = restaurants.order_by('-created_at')
    
    return render(request, 'core/restaurant_list.html', {
        'restaurants': restaurants,
        'current_sort': sort
    })
    
    


# ════ ADDRESS FUNCTIONS ════

@login_required
def add_address(request):
    if request.method == 'POST':
        address = Address.objects.create(
            user=request.user,
            label=request.POST.get('label'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            pincode=request.POST.get('pincode'),
            phone=request.POST.get('phone'),
        )
        return JsonResponse({'success': True, 'message': 'Address added successfully ✅'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def edit_address(request, pk):
    try:
        addr = Address.objects.get(id=pk, user=request.user)
        if request.method == 'POST':
            addr.label = request.POST.get('label', addr.label)
            addr.address = request.POST.get('address', addr.address)
            addr.city = request.POST.get('city', addr.city)
            addr.pincode = request.POST.get('pincode', addr.pincode)
            addr.phone = request.POST.get('phone', addr.phone)
            addr.save()
            return JsonResponse({'success': True, 'message': 'Address updated ✅'})
    except Address.DoesNotExist:
        pass
    return JsonResponse({'success': False, 'error': 'Address not found'})

@login_required
@require_POST
def delete_address(request, pk):
    try:
        addr = Address.objects.get(id=pk, user=request.user)
        addr.delete()
        return JsonResponse({'success': True, 'message': 'Address deleted ✅'})
    except Address.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Address not found'})

# ════ PAYMENT FUNCTIONS ════

@login_required
def add_payment(request):
    if request.method == 'POST':
        payment = PaymentMethod.objects.create(
            user=request.user,
            card_type=request.POST.get('card_type'),
            last_4_digits=request.POST.get('last_4_digits'),
            cardholder_name=request.POST.get('cardholder_name'),
        )
        return JsonResponse({'success': True, 'message': 'Payment method added ✅'})
    return JsonResponse({'success': False})

@login_required
def edit_payment(request, pk):
    try:
        payment = PaymentMethod.objects.get(id=pk, user=request.user)
        if request.method == 'POST':
            payment.cardholder_name = request.POST.get('cardholder_name', payment.cardholder_name)
            payment.save()
            return JsonResponse({'success': True, 'message': 'Payment updated ✅'})
    except PaymentMethod.DoesNotExist:
        pass
    return JsonResponse({'success': False})

@login_required
@require_POST
def delete_payment(request, pk):
    try:
        payment = PaymentMethod.objects.get(id=pk, user=request.user)
        payment.delete()
        return JsonResponse({'success': True, 'message': 'Payment deleted ✅'})
    except PaymentMethod.DoesNotExist:
        return JsonResponse({'success': False})

# ════ NOTIFICATION FUNCTIONS ════

@login_required
@require_POST
def save_notification_preferences(request):
    try:
        prefs, created = NotificationPreference.objects.get_or_create(user=request.user)
        prefs.order_updates = request.POST.get('order_updates') == 'on'
        prefs.promotions = request.POST.get('promotions') == 'on'
        prefs.reviews = request.POST.get('reviews') == 'on'
        prefs.save()
        return JsonResponse({'success': True, 'message': 'Preferences saved ✅'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ════ PROFILE UPDATE ════

@login_required
def profile(request):
    try:
        notif_prefs = request.user.notification_preference
    except NotificationPreference.DoesNotExist:
        notif_prefs = NotificationPreference.objects.create(user=request.user)
    
    context = {
        'addresses': request.user.addresses.all(),
        'payments': request.user.payment_methods.all(),
        'notification_preference': notif_prefs,
    }
    return render(request, 'core/profile.html', context)