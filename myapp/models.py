from django.db import models
import os
from datetime import datetime
from django.contrib.auth.models import User

def get_file_name(request,filename):
    current_time = datetime.now().strftime('%Y%m%d%H:%M:%S')
    new_filename = f"{current_time}_{filename}"
    return os.path.join('uploads/',new_filename)

class Category(models.Model):
    name = models.CharField(max_length = 100, blank= False, null=False)
    image = models.ImageField(upload_to=get_file_name, null=True, blank=True)
    descriptions = models.TextField(null=False,blank=False)
    status = models.BooleanField(default= 0, help_text= '0 - show, 1- hidden')
    trending = models.BooleanField(default = 0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        
        return self.name
    
    
    
class Product(models.Model):
    Category = models.ForeignKey(Category,on_delete=models.CASCADE)
    name = models.CharField(max_length = 100, blank= False, null=False)
    image = models.ImageField(upload_to=get_file_name, null=True, blank=True)
    vendor = models.CharField(max_length= 100, default='unknown')
    quantity = models.IntegerField(blank=False, null=False)
    selling_price = models.FloatField(blank=False,null=False)
    original_price = models.FloatField(blank=False, null=False)
    descriptions = models.TextField(null=False,blank=False)
    status = models.BooleanField(default= 0, help_text= '0 - show, 1- hidden')
    trending = models.BooleanField(default = 0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    def get_discount(self):
        
        if self.original_price > 0:
            return ((self.original_price - self.selling_price) / self.original_price) * 100
        return 0
    
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    bio = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=250,null= False, blank=True)
    gender = models.CharField(max_length=20, choices= (('male','Male'),('female','Female'),('other','Other')), blank =True)
    mobile = models.CharField(max_length=10, blank=False, null=False)
    
    
    def __str__(self):
        return self.user.username
class Order(models.Model):
    STATUS_CHOICES = [
        ('placed', 'Placed'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')  # New field for status

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
        
    def total_price(self):
        return sum(item.total_price() for item in self.items.filter(status='active'))

    



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='active')  # New field to track item status

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    def total_price(self):
        return self.quantity * self.price

  