from django.urls import path
from . import views

urlpatterns = [

    # ── Home ──────────────────────────────────
    path('', views.home, name='home'),

    # ── Restaurants ───────────────────────────
    path('restaurants/',              views.restaurant_list,   name='restaurants'),
    path('restaurant/<int:pk>/',      views.restaurant_menu,   name='restaurant_menu'),

    # ── Cart (AJAX) ────────────────────────────
    path('cart/',                     views.cart,              name='cart'),
    path('cart/add/',                 views.add_to_cart,       name='add_to_cart'),
    path('cart/update/',              views.update_cart,       name='update_cart'),
    path('cart/clear/',               views.clear_cart,        name='clear_cart'),

    # ── Checkout & Orders ─────────────────────
    path('checkout/',                 views.checkout,          name='checkout'),
    path('checkout/place/',           views.place_order,       name='place_order'),
    path('order/<int:pk>/confirmed/', views.order_confirmation,name='order_confirmation'),
    path('orders/',                   views.orders,            name='orders'),
    path('orders/<int:pk>/',          views.order_detail,      name='order_detail'),
    path('orders/<int:pk>/cancel/',   views.cancel_order,      name='cancel_order'),
    path('orders/<int:pk>/reorder/',  views.reorder,           name='reorder'),

    # ── Auth ──────────────────────────────────
    path('login/',                    views.login_view,        name='login'),
    path('register/',                 views.register_view,     name='register'),
    path('logout/',                   views.logout_view,       name='logout'),

    # ── Profile ───────────────────────────────
    path('profile/',                  views.profile,           name='profile'),
    path('profile/update/',           views.update_profile,    name='update_profile'),
    path('order/<int:pk>/status/', views.get_order_status, name='get_order_status'),

    # ── Admin Dashboard ───────────────────────
    path('dashboard/',                views.admin_dashboard,         name='admin_dashboard'),
    path('dashboard/user/<int:pk>/',        views.admin_view_user,   name='admin_view_user'),
    path('dashboard/user/<int:pk>/delete/', views.admin_delete_user, name='admin_delete_user'),
    path('dashboard/user/<int:pk>/ban/',    views.admin_ban_user,    name='admin_ban_user'),
    path('dashboard/user/<int:pk>/edit/',   views.admin_edit_user,   name='admin_edit_user'),
    path('dashboard/restaurants/',      views.admin_restaurants,       name='admin_restaurants'),
    path('dashboard/orders/',           views.admin_orders,            name='admin_orders'),
    path('dashboard/users/',            views.admin_users,             name='admin_users'),
    path('dashboard/coupons/',          views.admin_coupons,           name='admin_coupons'),
    path('dashboard/select-restaurant/',views.admin_select_restaurant, name='admin_select_restaurant'),
    path('dashboard/order/<int:pk>/status/',
          views.update_order_status,     name='update_order_status'),

    # ── Admin Restaurant CRUD ─────────────────
    path('dashboard/restaurant/add/',
         views.admin_add_restaurant,         name='admin_add_restaurant'),
    path('dashboard/restaurant/<int:pk>/edit/',
         views.admin_edit_restaurant,        name='admin_edit_restaurant'),
    path('dashboard/restaurant/<int:pk>/delete/',
         views.admin_delete_restaurant,      name='admin_delete_restaurant'),

    # ── Admin Menu CRUD ───────────────────────
    path('dashboard/restaurant/<int:restaurant_pk>/menu/',
         views.admin_menu_items,             name='admin_menu_items'),
    path('dashboard/restaurant/<int:restaurant_pk>/menu/add/',
         views.admin_add_menu_item,          name='admin_add_menu_item'),
    path('dashboard/menu-item/<int:pk>/edit/',
         views.admin_edit_menu_item,         name='admin_edit_menu_item'),
    path('dashboard/menu-item/<int:pk>/delete/',
         views.admin_delete_menu_item,       name='admin_delete_menu_item'),

     path('profile/address/add/', views.add_address, name='add_address'),
     path('profile/address/<int:pk>/edit/', views.edit_address, name='edit_address'),
     path('profile/address/<int:pk>/delete/', views.delete_address, name='delete_address'),

     path('profile/payment/add/', views.add_payment, name='add_payment'),
     path('profile/payment/<int:pk>/edit/', views.edit_payment, name='edit_payment'),
     path('profile/payment/<int:pk>/delete/', views.delete_payment, name='delete_payment'),

     path('profile/notifications/save/', views.save_notification_preferences, name='save_notifications'),
]