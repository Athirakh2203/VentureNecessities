from django.db import models


# Create your models here.
class login(models.Model):
    login_id=models.AutoField(primary_key=True)
    username=models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    
    usertype=models.CharField(max_length=200)
    
    
class user(models.Model):
    user_id=models.AutoField(primary_key=True)
    login=models.ForeignKey(login,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    place=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    phone=models.CharField(max_length=200)
    landmark=models.CharField(max_length=200)
    
class seller(models.Model):
    seller_id=models.AutoField(primary_key=True)
    login=models.ForeignKey(login,on_delete=models.CASCADE)
    seller_name=models.CharField(max_length=200)
    company_name=models.CharField(max_length=200)
    licence_no=models.CharField(max_length=200)
    place=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    phone=models.CharField(max_length=200)
    landmark=models.CharField(max_length=200)
    
class manufacture(models.Model):
    manufacture_id=models.AutoField(primary_key=True)
    login=models.ForeignKey(login,on_delete=models.CASCADE)
    manufacturename=models.CharField(max_length=200)
    licence_no=models.CharField(max_length=200)
    place=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    phone=models.CharField(max_length=200)
    landmark=models.CharField(max_length=200)
    
class category(models.Model):
    category_id=models.AutoField(primary_key=True)
    category_name=models.CharField(max_length=200)
    
class equipment(models.Model):
    equipment_id=models.AutoField(primary_key=True)
    login=models.ForeignKey(login,on_delete=models.CASCADE)
    category=models.ForeignKey(category,on_delete=models.CASCADE)
    equipment_name=models.CharField(max_length=200)
    description=models.CharField(max_length=200)
    amount=models.CharField(max_length=200)
    stock=models.CharField(max_length=200)
    Zone=models.CharField(max_length=200)
    image = models.ImageField(upload_to='equipment_images/', default='default.jpg')
    low_stock_alert_sent = models.BooleanField(default=False)

    
class sell_equipment(models.Model):
    sell_id=models.AutoField(primary_key=True)
    user=models.ForeignKey(login,on_delete=models.CASCADE)
    equipment=models.ForeignKey(category,on_delete=models.CASCADE)
    amount=models.CharField(max_length=200)
    stock=models.CharField(max_length=200)
    total_amount=models.CharField(max_length=200)
    date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=200)
    
class rent_equipment(models.Model):
    equipment_id=models.AutoField(primary_key=True)
    login=models.ForeignKey(login,on_delete=models.CASCADE)
    category=models.ForeignKey(category,on_delete=models.CASCADE)
    equipment_name=models.CharField(max_length=200)
    description=models.CharField(max_length=200)
    amount=models.CharField(max_length=200)
    stock=models.CharField(max_length=200)
    Zone=models.CharField(max_length=200)
    image = models.ImageField(upload_to='equipment_images/', default='default.jpg')
    
    
class seller_orders(models.Model):
    seller_order_id=models.AutoField(primary_key=True)
    seller=models.ForeignKey(seller,on_delete=models.CASCADE)
    equipment=models.CharField(max_length=200)
    buy_amount=models.CharField(max_length=200)
    stock=models.CharField(max_length=200)
    status=models.CharField(max_length=200)
    sell_amount=models.CharField(max_length=200)
    rent_amount=models.CharField(max_length=200)
    
class rent(models.Model):
    rent_id=models.AutoField(primary_key=True)
    seller=models.ForeignKey(seller,on_delete=models.CASCADE)
    user=models.ForeignKey(user,on_delete=models.CASCADE)
    equipment=models.ForeignKey(equipment,on_delete=models.CASCADE)
    from_date=models.DateTimeField(auto_now_add=True)
    to_date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=200)
    
class order_master_seller(models.Model):
    order_master_seller_id=models.AutoField(primary_key=True)
    seller=models.ForeignKey(seller,on_delete=models.CASCADE)
    total_amount=models.CharField(max_length=200)
    login=models.ForeignKey(login,on_delete=models.CASCADE)
    status=models.CharField(max_length=200)
    
class order_details_seller(models.Model):
    order_details_seller_id=models.AutoField(primary_key=True)
    order_master_seller=models.ForeignKey(order_master_seller,on_delete=models.CASCADE)
    product=models.ForeignKey(equipment,on_delete=models.CASCADE)
    quantity=models.CharField(max_length=200)
    amount=models.CharField(max_length=200)
    date=models.DateTimeField(auto_now_add=True)
    
class order_master_user(models.Model):
    order_master_user_id=models.AutoField(primary_key=True)
    user=models.ForeignKey(user,on_delete=models.CASCADE)
    total_amount=models.CharField(max_length=200)
    seller=models.ForeignKey(seller,on_delete=models.CASCADE)
    status=models.CharField(max_length=200)
    
class order_details_user(models.Model):
    order_details_user_id=models.AutoField(primary_key=True)
    order_master_user=models.ForeignKey(order_master_user,on_delete=models.CASCADE)
    product=models.ForeignKey(equipment,on_delete=models.CASCADE)
    quantity=models.CharField(max_length=200)
    amount=models.CharField(max_length=200)
    date=models.DateTimeField(auto_now_add=True)
    

    
class payment_user(models.Model):
    payment_id=models.AutoField(primary_key=True)
    order_master_user=models.ForeignKey(order_master_user,on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=200)
    
class payment_seller(models.Model):
    payment_id=models.AutoField(primary_key=True)
    order_master_seller=models.ForeignKey(order_master_seller,on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=200)
    

class complaint(models.Model):
    complaint_id=models.AutoField(primary_key=True)
    sender=models.ForeignKey(login,on_delete=models.CASCADE,null=True)
    description=models.CharField(max_length=200)
    reply = models.CharField(max_length=200)  
    date=models.DateTimeField(auto_now_add=True)
    
class Feedback(models.Model):
    name = models.CharField(max_length=100)
    feedback_id=models.AutoField(primary_key=True)
    sender_id=models.ForeignKey(login,on_delete=models.CASCADE,null=True)
    feedback_desc=models.CharField(max_length=255)
    date=models.DateTimeField(auto_now_add=True)
    
class rating(models.Model):
    rating_id=models.AutoField(primary_key=True)
    user=models.ForeignKey(user,on_delete=models.CASCADE)
    equipment=models.ForeignKey(equipment,on_delete=models.CASCADE)
    rating=models.CharField( max_length=200)
    review=models.CharField(max_length=200)
    date=models.DateTimeField(auto_now_add=True)
    

    
class Wishlist(models.Model):
    user = models.ForeignKey(login, on_delete=models.CASCADE)  # <-- your custom login model
    equipment = models.ForeignKey(equipment, on_delete=models.CASCADE)

    
    

