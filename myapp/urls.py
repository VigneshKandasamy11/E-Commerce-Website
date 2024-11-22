from django.urls import path
from . import views


urlpatterns = [
    path('',views.signup,name = 'signup'),
    path('log/',views.log,name = 'log'),
    path('logout/',views.logoutt, name = 'logoutt'),
    # path('home/',views.home,name = 'home'),
    path('collections/',views.collections, name = 'collections'),
    path('category/<str:name>/',views.category,name = 'category'),
    path('product/<int:id>/',views.product_details,name='product_details'),
    path('cart/', views.cart_views, name='cart_views'),
    path('delivery_page/', views.delivery_page, name='delivery_page'),
    path('order_success/', views.order_success, name='order_success'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('search/', views.search_products, name='search_products'),
    path('order/<int:order_id>/item/<int:item_id>/cancel/', views.cancel_order_item, name='cancel_order_item'),
    # path('order/<int:order_id>/', views.order_detail, name='order_detail')
  
    
]
