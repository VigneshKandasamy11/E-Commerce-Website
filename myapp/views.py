from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.db import transaction
from django.contrib.auth.models import User
from .models import * 
from django.db.models import Q
def search_products(request):
    query = request.GET.get('q','').strip()
    price_filter = request.GET.get('price','')
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(
            Q(name__icontains = query) |
            Q(vendor__icontains = query) |
            Q(descriptions__icontains = query) |
            Q(Category__name__icontains = query)
        ).distinct()
        
    if price_filter:
        if '-' in price_filter:
            min_price, max_price = map(int,price_filter.split('-'))
            products = products.filter(
                selling_price__gte=min_price,selling_price__lte= max_price
            )
        elif '5000+' in price_filter:
            products = products.filter(selling_price__gte= 5000)
            
    return render(request,'myapp/search.html',
                  {
                      'products':products,
                      'query':query
                  }
                  )
    
    
            
        
def signup(request):
    if request.method == 'POST':
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        username = request.POST['username']
        password = request.POST['password']
        dob = request.POST['dob']
        email = request.POST['email']
        bio = request.POST['bio']
        mobile = request.POST['mobile']
        address =request.POST['address']
        gender = request.POST['gender']
        
        if User.objects.filter(username = username).exists():
            return render(request,'myapp/signup.html',{'error':'username already exists'})
        
        user = User.objects.create_user(username=username, password=password, email=email,first_name = firstname, last_name = lastname)
        user.save()
        
        profile = UserProfile(mobile = mobile,bio = bio, date_of_birth = dob,address = address, gender = gender,user =User)
        profile.save()
        
        return redirect('log')
        
        
        
        
    return render(request, 'myapp/signup.html')
# Login View
def log(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            
            
            return redirect('collections')
        else:
            return render(request, 'myapp/log.html', {'error': 'Invalid username or password'})
    
    return render(request, 'myapp/log.html')

# Logout View
def logoutt(request):
    logout(request)
    return redirect('log')


# Collections View
def collections(request):
    collection = Category.objects.all()
    return render(request, 'myapp/collection_of_item.html', {'collection': collection})

# Category View
# Category View
# Category View
# Category View
def category(request, name):
    price_filter = request.GET.get('price', '')

    # Correct field name here to match the model exactly
    products = Product.objects.filter(Category__name=name)  # Ensure 'Category' matches the field in the model

    # Apply price filter
    if price_filter:
        if '-' in price_filter:
            min_price, max_price = map(int, price_filter.split('-'))
            products = products.filter(selling_price__gte=min_price, selling_price__lte=max_price)
        elif '5000+' in price_filter:
            products = products.filter(selling_price__gte=5000)

    return render(request, 'myapp/category.html', {
        'products': products,
        'collection': name,
    })


def product_details(request,id):
    product_info = get_object_or_404(Product,id = id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity',''))
        action = request.POST.get('act')
        
        cart = request.session.get('cart',{})
        if isinstance(cart,str):
            cart = {}
        
        if action == 'add_to_cart':
            if str(id) in cart:
                cart[str(id)]['quantity'] += quantity
            else:
                cart[str(id)] = {
                    'name': product_info.name,
                    'quantity': quantity,
                    'price':product_info.selling_price,
                    'image': product_info.image.url
                }
            request.session['cart'] = cart
            return redirect('cart_views')
            
    
    return render (request,'myapp/product_details.html',{
        'product': product_info
    })

# Cart View
def cart_views(request):
    cart = request.session.get('cart',{})
    
    if isinstance (cart,str):
        cart = {}
        
    out_of_stock_items = []
        
    if 'remove_item' in request.POST:
        item_id = request.POST.get('remove_item')
        if item_id in cart:
            del cart[item_id]
            request.session['cart'] = cart

    # Handle quantity increase
    if 'increase_quantity' in request.POST:
        item_id = request.POST.get('increase_quantity')
        if item_id in cart:
            product = get_object_or_404(Product, id=item_id)
            if cart[item_id]['quantity'] < product.quantity:
                cart[item_id]['quantity'] += 1
                request.session['cart'] = cart
            else:
                out_of_stock_items.append(cart[item_id]['name'])

    # Handle quantity decrease (ensure it doesn’t go below 1)
    if 'decrease_quantity' in request.POST:
        item_id = request.POST.get('decrease_quantity')
        if item_id in cart and cart[item_id]['quantity'] > 1:
            cart[item_id]['quantity'] -= 1
            request.session['cart'] = cart
    
    total_price = 0
    out_of_stock = False
    
    for item_id, item in cart.items():
        product = get_object_or_404(Product,id = item_id)
        if item['quantity'] > product.quantity:
            item['is_in_stock'] = False
            out_of_stock_items.append(item['name'])
            out_of_stock = True
            
        else:
            item['is_in_stock'] = True
            
        item['total'] = item['quantity'] * item['price']
        total_price += item['total']
    request.session['cart'] = cart
    
    return render(request, 'myapp/cart.html',{
        'cart':cart,
        'total_price':total_price,
        'out_of_stock_items': out_of_stock_items,
        'out_of_stock':out_of_stock
    })

    # Calculate total price and check stock
   


@transaction.non_atomic_requests
def delivery_page(request):
    cart = request.session.get('cart', {})
    
    if isinstance(cart, str):
        cart = {}

    total_price = sum(item['quantity'] * item['price'] for item in cart.values())
    
    if request.method == 'POST':
        address = request.POST.get('address')
        if not address:
            return render(request, 'myapp/delivery.html', {
                'cart': cart,
                'total_price': total_price,
                'error': "Invalid address. Please enter a valid address."
            })

        with transaction.atomic():
            ordered_items = []  # List to store ordered items for displaying later

            # Create an Order instance without total_price
            order = Order.objects.create(
                user=request.user,  # Assuming the user is logged in
                address=address
            )

            for item_id, item in cart.items():
                product = get_object_or_404(Product, id=item_id)
                if product.quantity >= item['quantity']:
                    product.quantity -= item['quantity']
                    product.save()

                    # Create an OrderItem instance
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item['quantity'],
                        price=item['price']
                    )

                    ordered_items.append({
                        'name': product.name,
                        'quantity': item['quantity'],
                        'price': item['price'],
                        'total': item['quantity'] * item['price']
                    })
                else:
                    return render(request, 'myapp/delivery.html', {
                        'cart': cart,
                        'total_price': total_price,
                        'error': f'Sorry, not enough stock for {product.name}.'
                    })

            # Clear cart and store ordered items in session for the order success page
            request.session['cart'] = {}
            request.session['ordered_items'] = ordered_items
            request.session['delivery_address'] = address  # Store the address
            return redirect('order_success')

    return render(request, 'myapp/delivery.html', {'cart': cart, 'total_price': total_price})

    

def order_success(request):
    # Fetch all orders for the logged-in user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')  # Order by latest first
    return render(request, 'myapp/order_success.html', {
        'orders': orders
    })
from django.shortcuts import redirect, get_object_or_404
from .models import Order

def cancel_order(request, order_id):
    # Fetch the order to cancel
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Set the order status to 'canceled' instead of deleting it
    order.status = 'canceled'
    order.save()

    # Redirect to the order cancellation confirmation page
    return render(request, 'myapp/order_cancelled.html', {
        'message': "Your order has been cancelled successfully."
    })


def cancel_order_item(request, order_id, item_id):
    # Fetch the order item to cancel
    order_item = get_object_or_404(OrderItem, id=item_id, order_id=order_id, order__user=request.user)
    order_item.status = 'canceled'  # Update the status to "canceled"
    order_item.save()

    
    return redirect('order_success')  # views.py
# def order_detail(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user)
#     return render(request, 'myapp/order_detail.html', {'order': order})
