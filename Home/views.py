import os
from django.shortcuts import render,redirect,HttpResponse

from VentureNecessities import settings
from .models import login, user  
from django.contrib import messages
import re
from datetime import datetime
from django.utils.timezone import now  # ✅ Correct way
from django.shortcuts import render, get_object_or_404,redirect



from Home.models import *
from django.contrib.auth.hashers import make_password


from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse,Http404





# Create your views here.

def index(request):
    return render(request,'index.html')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import *
import json

@csrf_exempt
def update_cart_quantity_seller(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_details_seller_id = data.get('order_details_seller_id')
            new_quantity = int(data.get('new_quantity'))  # Ensure it's an integer

            # Debugging - print received data
            print(f"Updating item {order_details_seller_id} to quantity {new_quantity}")

            try:
                item = order_details_seller.objects.get(order_details_seller_id=order_details_seller_id)
            except order_details_seller.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f"Item not found"
                }, status=404)

            # Calculate new amount
            price = float(item.product.amount)
            item.quantity = new_quantity
            item.amount = str(price * new_quantity)
            item.save()
            
            # Update order total
            order = item.order_master_seller
            order.total_amount = str(sum(float(d.amount) for d in order.order_details_seller_set.all()))
            order.save()
            
            return JsonResponse({
                'success': True,
                'new_amount': item.amount,
                'new_quantity': item.quantity
            })
        except Exception as e:
            print(f"Error updating quantity: {str(e)}")  # Debugging
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def delete_cart_seller(request, id):
    if request.method == "GET":
        try:
            with transaction.atomic():
                # Get the order detail to delete
                order_detail_seller = order_details_seller.objects.get(order_details_seller_id=id)
                order_master_seller = order_detail_seller.order_master_seller
                
                # Delete the order detail
                order_detail_seller.delete()
                
                # Update or delete order_master_seller
                remaining_details = order_details_seller.objects.filter(order_master_seller=order_master_seller)
                if remaining_details.exists():
                    # Update total_amount if there are remaining items
                    total_amount = sum(float(detail.amount) for detail in remaining_details)
                    order_master_seller.total_amount = str(total_amount)
                    order_master_seller.save()
                else:
                    # Delete order_master if no items remain
                    order_master_seller.delete()
                
                return HttpResponse("<script>alert('Item removed from cart');window.location='/view_cart_seller';</script>")
                
        except order_details_seller.DoesNotExist:
            return HttpResponse("<script>alert('Item not found');window.location='/view_cart_seller';</script>")
        except Exception as e:
            return HttpResponse(f"<script>alert('Error: {str(e)}');window.location='/view_cart_seller';</script>")
    return HttpResponse("<script>alert('Invalid request');window.location='/view_cart_seller';</script>")



def cart_seller(request, id):
    try:
        # Fetch the equipment
        equip = equipment.objects.get(equipment_id=id)
        seller_id = equip.login_id
        
        seller_id_from_session = request.session.get('sid', None)
        print("////////////////")
        
        print("YYYYYYYYYYYYYYYYYYYYYYYYY")
        
        # Check for pending orders from other sellers
        if order_master_seller.objects.exclude(login=equip.login).filter(status='pending', seller_id=seller_id_from_session).exists():
            # Return a JavaScript alert and redirect back to the cart page
            return HttpResponse("<script>alert('Complete the pending order from one manufacturer first.'); window.location='/view_cart_seller'</script>")
        
        # Get or create a pending order for this seller
        order_master, created = order_master_seller.objects.get_or_create(
            seller_id=seller_id_from_session,
            status='pending',
            login=equip.login,  # This is where the login field is being set
            defaults={
                'total_amount': '0.00',
            }
        )

        # Check if product already exists in the cart
        existing_item = order_details_seller.objects.filter(
            order_master_seller=order_master,
            product=equip
        ).first()

        if existing_item:
            return HttpResponse("<script>alert('Item already in cart.'); window.location='/view_cart_seller'</script>")

        # Use a transaction to ensure atomic updates
        with transaction.atomic():
            # Update the total amount in the order
            current_total = float(order_master.total_amount)
            equip_amount = float(equip.amount)
            order_master.total_amount = str(current_total + equip_amount)
            order_master.save()

            # Add the new item to the cart
            order_detail_seller = order_details_seller(
                quantity=1,  # Assuming quantity is always 1 initially
                amount=str(equip.amount),
                order_master_seller=order_master,
                product=equip
            )
            order_detail_seller.save()

        return HttpResponse("<script>alert('Item added to cart successfully.'); window.location='/view_cart_seller'</script>")

    except equipment.DoesNotExist:
        messages.error(request, "Equipment not found.")
        return redirect('view_cart_seller')
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        print(f"{str(e)}")
        return redirect('view_cart_seller')



# from datetime import datetime
# from django.http import HttpResponse
# from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse  # Import your models properly

# def cart(request, id):
#     try:
#         # Get the equipment
#         q = equipment.objects.get(pk=id)
#         sid = q.login  # This is a ForeignKey object
#         am = q.amount

#         # Check if there are any pending orders for OTHER login_ids
#         rr = order_master_seller.objects.exclude(login=sid).filter(status='pending')
        
#         if rr.exists():
#             return HttpResponse("<script>alert('Complete pending orders');window.location='/view_cart';</script>")
        
#         # Get or create order_master for this login
#         try:
#             cc = order_master_seller.objects.get(login=sid, status='pending')
            
#             # Check if the product is already in order_details
#             existing_item = order_details_seller.objects.filter(order_master=cc, product=q).first()
#             if existing_item:
#                 return HttpResponse("<script>alert('Already in cart');window.location='/view_cart';</script>")
            
#             # If product is not in the cart, add it
#             cc.total_amount = str(float(cc.total_amount) + float(am))
#             cc.save()
            
#             xy = order_details_seller(
#                 quantity='1',
#                 amount=str(am),
#                 order_master=cc,
#                 product=q
#             )
#             xy.save()
            
#         except order_master_seller.DoesNotExist:
#             xx = order_master_seller(
#                 total_amount=str(am),
#                 status='pending',
#                 login=sid,
#                 user_id=request.session.get('uid')  # Assuming uid is stored in session
#             )
#             xx.save()
            
#             xy = order_details_seller(
#                 quantity='1',
#                 amount=str(am),
#                 order_master=xx,
#                 product=q
#             )
#             xy.save()

#         return HttpResponse("<script>alert('Added to cart');window.location='/view_cart';</script>")

#     except equipment.DoesNotExist:
#         return HttpResponse("<script>alert('Equipment not found');window.location='/view_cart';</script>")
#     except Exception as e:
#         return HttpResponse(f"<script>alert('Unexpected error: {str(e)}');window.location='/view_cart';</script>")

def view_cart_seller(request):
    if 'sid' not in request.session:
        return render(request, 'cart_seller.html', {'q': [], 'error': "User not logged in"})
    
    sid = request.session['sid']
    
    try:
        # Try to get the pending order for the seller
        pending_order = order_master_seller.objects.get(seller_id=sid, status='pending')
        
        # If we found an order, get its items
        cart_items = order_details_seller.objects.filter(order_master_seller=pending_order)
        
        if not cart_items.exists():
            # Order exists but has no items
            return render(request, 'cart_seller.html', {'q': [], 'message': "No items in cart"})
        
        tt = pending_order.total_amount
        print(f"{tt} /////////")
        
        return render(request, 'cart_seller.html', {
            'q': cart_items, 
            'order_master_seller_id': pending_order.pk,
            'total_amount': tt
        })
        
    except order_master_seller.DoesNotExist:
        # No pending order exists for this seller
        return render(request, 'cart_seller.html', {'q': [], 'message': "No items in cart"})
    
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Error in view_cart_seller: {str(e)}")
        return render(request, 'cart_seller.html', {'q': [], 'error': f"An error occurred: {str(e)}"})



@csrf_exempt
def update_cart_quantity_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_details_user_id = data.get('order_details_user_id')
            new_quantity = int(data.get('new_quantity'))  # Ensure it's an integer

            # Debugging - print received data
            print(f"Updating item {order_details_user_id} to quantity {new_quantity}")

            try:
                item = order_details_user.objects.get(order_details_user_id=order_details_user_id)
            except order_details_user.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f"Item not found"
                }, status=404)

            # Calculate new amount
            price = float(item.product.amount)
            item.quantity = new_quantity
            item.amount = str(price * new_quantity)
            item.save()
            
            # Update order total
            order = item.order_master_user
            order.total_amount = str(sum(float(d.amount) for d in order.order_details_user_set.all()))
            order.save()
            
            return JsonResponse({
                'success': True,
                'new_amount': item.amount,
                'new_quantity': item.quantity
            })
        except Exception as e:
            print(f"Error updating quantity: {str(e)}")  # Debugging
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def delete_cart_user(request, id):
    if request.method == "GET":
        try:
            with transaction.atomic():
                # Get the order detail to delete
                order_detail_user = order_details_user.objects.get(order_details_user_id=id)
                order_master_user = order_detail_user.order_master_user
                
                # Delete the order detail
                order_detail_user.delete()
                
                # Update or delete order_master_seller
                remaining_details = order_details_user.objects.filter(order_master_user=order_master_user)
                if remaining_details.exists():
                    # Update total_amount if there are remaining items
                    total_amount = sum(float(detail.amount) for detail in remaining_details)
                    order_master_user.total_amount = str(total_amount)
                    order_master_user.save()
                else:
                    # Delete order_master if no items remain
                    order_master_user.delete()
                
                return HttpResponse("<script>alert('Item removed from cart');window.location='/view_cart_user';</script>")
                
        except order_details_user.DoesNotExist:
            return HttpResponse("<script>alert('Item not found');window.location='/view_cart_user';</script>")
        except Exception as e:
            return HttpResponse(f"<script>alert('Error: {str(e)}');window.location='/view_cart_user';</script>")
    return HttpResponse("<script>alert('Invalid request');window.location='/view_cart_user';</script>")



# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import equipment, order_master_user, order_details_user
# from django.db import transaction
# from django.contrib import messages

# def cart_user(request, id):
#     try:
#         # Fetch the equipment
#         equip = equipment.objects.get(pk=id)
#         user_id = equip.login_id
        
#         print(user_id,"{{{{{{{{{{{{{{{{}}}}}}}}}}}}}}}}")

#         # Check for pending orders from other sellers
#         if order_master_user.objects.exclude(seller_id=user_id).filter(status='pending').exists():
#             messages.error(request, "Complete pending orders from other sellers first.")
#             return redirect('view_cart_user')

#         # Get or create pending order for this seller
#         order_master_user, created = order_master_user.objects.get_or_create(
#             seller_id=user_id,
#             status='pending',
#             defaults={
#                 'total_amount': '0.00',
#                 'user_id': request.session.get('uid', '')  # Handle missing session key gracefully
#             }
#         )

#         # Check if product already exists in cart
#         existing_item = order_details_user.objects.filter(
#             order_master_user=order_master_user,
#             product=equip
#         ).first()

#         if existing_item:
#             messages.warning(request, "Item already in cart.")
#             return redirect('view_cart_user')

#         # Use a transaction to ensure atomic updates
#         with transaction.atomic():
#             # Update total amount
#             current_total = float(order_master_user.total_amount)
#             equip_amount = float(equip.amount)
#             order_master_user.total_amount = str(current_total + equip_amount)
#             order_master_user.save()

#             # Add new item to cart
#             order_detail_user = order_details_user(
#                 quantity=1,  # Assuming quantity is always 1 initially
#                 amount=equip.amount,
#                 order_master_user=order_master_user,
#                 product=equip
#             )
#             order_detail_user.save()

#         messages.success(request, "Item added to cart successfully.")
#         return redirect('view_cart_user')

#     except equipment.DoesNotExist:
#         messages.error(request, "Equipment not found.")
#         return redirect('view_cart_user')
#     except Exception as e:
#         messages.error(request, f"An unexpected error occurred: {str(e)}")
#         return redirect('view_cart_user')


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import equipment, order_master_user, order_details_user
from django.db import transaction
from django.contrib import messages
from decimal import Decimal

def cart_user(request, id):
    try:
        # Fetch the equipment
        equip = equipment.objects.get(equipment_id=id)
        print(equip,"[[[[[[[[]]]]]]]]")
        user_id = equip.login_id
        
        # Ensure the session has the user ID
        user_id_from_session = request.session.get('uid', None)
        print("////////////////")
        # if not user_id_from_session:
        #     print("RRRRRRRRRRRRRRRRRRRRRRRR")
        #     messages.error(request, "User session expired. Please log in again.")
        #     return redirect('login_page')  # Redirect to login if the session doesn't exist
        
        
        print("YYYYYYYYYYYYYYYYYYYYYYYYY")
        
        # Check for pending orders from other sellers
        if order_master_user.objects.exclude(seller_id=equip.login_id).filter(status='pending', user_id=user_id_from_session).exists():
            # messages.error(request, "Complete pending orders from other sellers first.")
            print("KKKKKKKKKKKKKKKKKKKKKKK")
            return HttpResponse("<script>alert('Complete pending orders from other sellers first.');window.location='/view_cart_user'</script>")
            return redirect('view_cart_user')

        # Get or create a pending order for this seller
        order_master, created = order_master_user.objects.get_or_create(
            user_id=user_id_from_session,
            status='pending',
            seller_id=equip.login_id,
            defaults={
                'total_amount': '0.00',
            }
        )

        # Check if product already exists in the cart for this order
        existing_item = order_details_user.objects.filter(
            order_master_user=order_master,
            product=equip
        ).first()

        if existing_item:
             return HttpResponse("<script>alert('Item already in cart.'); window.location='/view_cart_user'</script>")

           

        # Use transaction to ensure atomic updates
        with transaction.atomic():
            # Update total amount using Decimal for accuracy in calculations
            current_total = Decimal(order_master.total_amount)
            equip_amount = Decimal(equip.amount)
            order_master.total_amount = str(current_total + equip_amount)
            order_master.save()

            # Add new item to the cart
            order_detail_user = order_details_user(
                quantity=1,  # Assuming quantity is 1 initially
                amount=str(equip.amount),
                order_master_user=order_master,
                product=equip
            )
            order_detail_user.save()

        messages.success(request, "Item added to cart successfully.")
        return redirect('view_cart_user')

    except equipment.DoesNotExist:
        messages.error(request, "Equipment not found.")
        print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
        return redirect('view_cart_user')
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        print(f"{str(e)}")
        return redirect('view_cart_user')

    
def view_cart_user(request):
    if 'uid' not in request.session:
        return render(request, 'cart_user.html', {'q': [], 'error': "User not logged in"})
    
    uid = request.session['uid']
    pending_orders = order_master_user.objects.filter(user_id=uid, status='pending')
    
    if not pending_orders.exists():
        return render(request, 'cart_user.html', {'q': [], 'message': "No items in cart"})
    
    pending_order = pending_orders.first()  # Get the first pending order
    cart_items = order_details_user.objects.filter(order_master_user=pending_order)
    
    return render(request, 'cart_user.html', {'q': cart_items, 'order_master_user_id': pending_order.pk,'tt':pending_order.total_amount})








'''@csrf_exempt
def update_cart_quantity(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_details_id = data.get('order_details_id')
            new_quantity = data.get('new_quantity')

            with transaction.atomic():
                # Get the order detail
                order_detail = order_details_user.objects.get(order_details_user_id=order_details_id)
                
                # Get product price (assuming equipment has an amount field)
                product_price = float(order_detail.product.amount)  # Convert to float
                
                # Convert new_quantity to string for CharField
                order_detail.quantity = str(new_quantity)
                # Calculate and store amount as string
                order_detail.amount = str(product_price * new_quantity)
                order_detail.save()

                # Update total_amount in order_master_seller
                order_master = order_master_user.objects.get(order_master_user_id=order_detail.order_master_user.order_master_user_id)
                # Get all order details and calculate total
                all_details = order_details_user.objects.filter(order_master_user=order_master)
                total_amount = sum(float(detail.amount) for detail in all_details)
                order_master.total_amount = str(total_amount)  # Convert back to string for CharField
                order_master.save()

            return JsonResponse({
                'success': True,
                'new_amount': order_detail.amount,
                'new_total': order_master.total_amount
            })

        except order_details_seller.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order detail not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def delete_cart(request, id):
    if request.method == "GET":
        try:
            with transaction.atomic():
                # Get the order detail to delete
                order_detail = order_details_user.objects.get(order_details_user_id=id)
                order_master = order_detail.order_master_user
                
                # Delete the order detail
                order_detail.delete()
                
                # Update or delete order_master_seller
                remaining_details = order_details_user.objects.filter(order_master_user=order_master)
                if remaining_details.exists():
                    # Update total_amount if there are remaining items
                    total_amount = sum(float(detail.amount) for detail in remaining_details)
                    order_master.total_amount = str(total_amount)
                    order_master.save()
                else:
                    # Delete order_master if no items remain
                    order_master.delete()
                
                return HttpResponse("<script>alert('Item removed from cart');window.location='/view_cart';</script>")
                
        except order_details_seller.DoesNotExist:
            return HttpResponse("<script>alert('Item not found');window.location='/view_cart';</script>")
        except Exception as e:
            return HttpResponse(f"<script>alert('Error: {str(e)}');window.location='/view_cart';</script>")
    return HttpResponse("<script>alert('Invalid request');window.location='/view_cart';</script>")

#from django.http import HttpResponse
from .models import equipment, order_master_user, order_details_user

def cart(request, id):
    try:
        # Get the equipment
        q = equipment.objects.get(pk=id)
        sid = q.login_id
        am = q.amount

        # Check if there are any pending orders for OTHER login_ids
        rr = order_master_user.objects.exclude(login_id=sid).filter(status='pending')
        
        if rr.exists():  # Use .exists() since exclude() returns a QuerySet
            return HttpResponse("<script>alert('Complete pending orders');window.location='/view_cart';</script>")
        
        # If no pending orders for other login_ids, proceed with this user's cart
        try:
            # Check if there's an existing pending order for this login
            cc = order_master_user.objects.get(login_id=sid, status='pending')
            
            # Update existing order_master_seller
            try:
                cc.total_amount = str(float(cc.total_amount) + float(am))  # Add to existing total
                cc.save()
                
                # Create new order detail
                xy = order_details_user(
                    quantity='1',
                    amount=str(am),
                    order_master_user=cc,
                    product_id=id
                )
                xy.save()
                
                return HttpResponse("<script>alert('Added to cart');window.location='/view_cart';</script>")
            
            except Exception as e:
                return HttpResponse(f"<script>alert('Error updating cart: {str(e)}');window.location='/view_cart';</script>")

        except order_master_user.DoesNotExist:
            # Create new order_master_seller if none exists for this login_id
            try:
                xx = order_master_user(
                    total_amount=str(am),
                    status='pending',
                    login_id=sid,
                    seller_id=request.session['sid']
                )
                xx.save()

                # Create new order detail
                xy = order_details_user(
                    quantity='1',
                    amount=str(am),
                    order_master_user=xx,
                    product_id=id
                )
                xy.save()

                return HttpResponse("<script>alert('Added to cart');window.location='/view_cart';</script>")
            
            except Exception as e:
                return HttpResponse(f"<script>alert('Error creating new cart: {str(e)}');window.location='/view_cart';</script>")

    except equipment.DoesNotExist:
        return HttpResponse("<script>alert('Equipment not found');window.location='/view_cart';</script>")
    except Exception as e:
        return HttpResponse(f"<script>alert('Unexpected error: {str(e)}');window.location='/view_cart';</script>")

def view_cart(request):
    user_id = request.session.get('uid')  # Get logged-in seller ID

    # Get all order details for this seller where status is pending
    q = order_details_user.objects.filter(
        order_master_user__seller_id=user_id,
        order_master_user__status='pending'
    )

    # Get total amount from order_master_seller for this seller
    total_amount = order_master_user.objects.filter(
        user_id=user_id,
        status='pending'
    ).values_list('total_amount', flat=True).first()

    return render(request, 'user_cart.html', {'q': q, 'total_amount': total_amount})

# def cart(request,id):
#    q=equipment.objects.get(pk=id)
#    sid=q.login_id
#    am=q.amount


#    xx=order_master_seller(total_amount=am,status='pending',login_id=sid,seller_id=request.session['sid'])
#    xx.save()

#    xy=order_details_seller(quantity=1,amount=am,date=datetime.now().today(),order_master_seller_id=xx.pk,product_id=id)
#    xy.save()

#    return HttpResponse("<script>alert('Added to cart');window.location='/view_cart';</script>")




# def view_cart(request):
#    q=order_details_seller.objects.filter(order_master_seller_id=request.session['sid'],order_master_seller__status='pending')
#    print(q,"////////////")
#    return render(request,'cart.html',{'q':q})'''






def registration(request):
    return render(request, 'registration.html')

# def equipment(request):
#     return render(request, 'equipment.html')


from .models import login, user  # Adjust imports based on your app's structure

def user_registration(request):
    if request.method == 'POST':
        f = request.POST['name']
        e = request.POST['email']
        m = request.POST['phone']
        pl = request.POST['place']
        p = request.POST['password']
        u = request.POST['username']
        l = request.POST['landmark']
        
        
        print(f, u, e, m, p, l, pl, "Received Data")
        
        
        log = login(username=u, password=p, usertype='user')
        log.save()
        
       
        users = user(login_id=log.pk, name=f, place=pl, email=e, phone=m, landmark=l)
        users.save()
        
       
        return redirect('login') 
    
    
    return render(request,"user_register.html")
    

      
      
      
      

def seller_registration(request):
     if request.method=='POST':
        f=request.POST['name']
        l=request.POST['companyname']
        e=request.POST['email']
        m=request.POST['phone']
        pl=request.POST['place']
        p=request.POST['password']
        u=request.POST['username']
        i=request.POST['licence_no']
        a=request.POST['landmark']
        print(f,l,e,m,p,i,u,l,a,"y")
        log=login(username=u,password=p,usertype='pending')
        log.save()
      
        sellers=seller(login_id=log.pk,seller_name=f,company_name=l,place=pl,email=e,licence_no=i,phone=m,landmark=a)
        sellers.save()
     return render(request,"seller_register.html")



def wholesaler_registration(request):
     if request.method=='POST':
        f=request.POST['manufacturename']
        e=request.POST['email']
        m=request.POST['phone']
        pl=request.POST['place']
        p=request.POST['password']
        u=request.POST['username']
        i=request.POST['licence_no']
        a=request.POST['landmark']
        print(f,e,m,p,i,u,a,"y")
        log=login(username=u,password=p,usertype='pending')
        log.save()
      
        manufactures=manufacture(login_id=log.pk,manufacturename=f,licence_no=i,place=pl,email=e,phone=m,landmark=a)
        manufactures.save()
     return render(request,"wholesaler_register.html")
        
        
        
        
    




def logins(request):
   if request.method=='POST':
      u=request.POST['username']
      p=request.POST['password']

      print(u,p,"=============")
   
      try:

         log=login.objects.get(username=u,password=p)
         request.session['lid']=log.pk

         if log.usertype=='user':
            x=user.objects.get(login_id=request.session['lid'])
            request.session['uid']=x.pk
            return redirect('/userhome')
             
            
        
         if log.usertype=='seller':
            x=seller.objects.get(login_id=request.session['lid'])
            request.session['sid']=x.pk
            return redirect('/sellerhome')
            
         if log.usertype=='manufacture':
            x=manufacture.objects.get(login_id=request.session['lid'])
            request.session['mid']=x.pk
            return redirect('/manufacturehome')
        
         elif log.usertype=='admin':
            return redirect('/homeadmin')
         else :
            return HttpResponse("<script>alert('Waiting for approval by admin');window.location='/login';</script>")
      
      except:
          return HttpResponse("<script>alert('Login Failed');window.location='/login';</script>")
         
   return render(request,'login.html')



def index(request):
    return render(request,'index.html')

def homeadmin(request):
    return render(request,'homeadmin.html')




def sellerhome(request):
    return render(request,'sellerhome.html')

def reg(request):
    return render(request,'reg.html')


def manufacturehome(request):
    return render(request,'manufacturehome.html')

def viewseller(request):
    sellers=seller.objects.all()
    return render(request,'viewseller.html',{'sellers':sellers})

def viewmanufacture(request):
    manufactures=manufacture.objects.all()
    return render(request,'viewmanufacture.html',{'manufacture':manufactures})

def viewuser(request):
    users=user.objects.all()
    return render(request,'viewuser.html',{'users':users})

def categorydetails(request):
    categorys=category.objects.all()
    return render(request,'categorydetails.html',{'category':categorys})




# def accept_seller(request,id):
#     z=login.objects.get(pk=id)
#     z.usertype='seller'
#     z.save()
#     return HttpResponse("<script>alert('Accepted');window.location='/viewseller';</script>")

import logging
from django.core.mail import send_mail
from django.http import HttpResponse
from .models import login, seller
from django.conf import settings

# Set up logging
logger = logging.getLogger(__name__)

def accept_seller(request, id):
    try:
        logger.info(f"Starting accept_seller for ID: {id}")
        
        # Fetch the seller's login entry
        logger.debug("Fetching login object...")
        z = login.objects.get(pk=id)
        z.usertype = 'seller'
        z.save()
        logger.info(f"Updated login {id} to seller type")

        # Fetch seller details
        logger.debug("Fetching seller object...")
        seller_obj = seller.objects.get(login_id=id)
        receiver_email = seller_obj.email
        sender_email = settings.EMAIL_HOST_USER
        
        logger.info(f"Preparing email to: {receiver_email}")
        logger.debug(f"Using sender email: {sender_email}")

        # Email details
        subject = "Your Seller Account Has Been Accepted"
        message = f"""
        Hello {seller_obj.seller_name},

        Your request to become a seller has been approved.
        You can now log in and start selling!

        Thank you.
        """

        # Log email content (redact sensitive info in production)
        logger.debug(f"Email subject: {subject}")
        logger.debug(f"Email message body: {message[:100]}...")  # Log first 100 chars

        # Verify email settings
        logger.debug("Current email settings:")
        logger.debug(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Not set')}")
        logger.debug(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
        logger.debug(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
        logger.debug(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
        logger.debug(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
        logger.debug(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")

        # Send email
        logger.info("Attempting to send email...")
        send_mail(
            subject,
            message,
            sender_email,
            [receiver_email],
            fail_silently=False
        )
        logger.info("Email sent successfully")

        return HttpResponse("<script>alert('Seller Accepted and Email Sent!');window.location='/viewseller';</script>")
    
    except login.DoesNotExist:
        logger.error(f"Login not found for ID: {id}")
        return HttpResponse("<script>alert('Error: Seller not found!');window.location='/viewseller';</script>")
    
    except seller.DoesNotExist:
        logger.error(f"Seller details not found for login ID: {id}")
        return HttpResponse("<script>alert('Error: Seller details not found!');window.location='/viewseller';</script>")
    
    except Exception as e:
        logger.exception(f"Unexpected error in accept_seller: {str(e)}")
        return HttpResponse(f"<script>alert('Error: {str(e)}');window.location='/viewseller';</script>")

# def reject_seller(request,id):
#    z=login.objects.get(pk=id)
#    z.usertype='rejected'
#    z.save()
#    return HttpResponse("<script>alert('Rejected');window.location='/viewseller';</script>")

def reject_seller(request, id):
    try:
        logger.info(f"Starting reject_seller for ID: {id}")

        # Fetch the seller's login entry
        logger.debug("Fetching login object...")
        z = login.objects.get(pk=id)

        # Fetch seller details
        logger.debug("Fetching seller object...")
        seller_obj = seller.objects.get(login_id=id)
        receiver_email = seller_obj.email
        sender_email = settings.EMAIL_HOST_USER

        logger.info(f"Preparing email to: {receiver_email}")

        # Email details
        subject = "Your Seller Account Request Has Been Rejected"
        message = f"""
        Hello {seller_obj.seller_name},

        We regret to inform you that your request to become a seller has been rejected.
        If you believe this is a mistake, please contact our support team.

        Thank you.
        """

        # Send email
        logger.info("Attempting to send rejection email...")
        send_mail(
            subject,
            message,
            sender_email,
            [receiver_email],
            fail_silently=False
        )
        logger.info("Rejection email sent successfully")

        # Ensure seller exists before deletion
        if seller.objects.filter(login_id=id).exists():
            logger.debug("Deleting seller details...")
            seller_obj.delete()
            logger.info("Seller details deleted successfully")
        else:
            logger.warning("Seller details not found for deletion!")

        # Ensure login exists before deletion
        if login.objects.filter(pk=id).exists():
            logger.debug("Deleting login entry...")
            z.delete()
            logger.info("Login entry deleted successfully")
        else:
            logger.warning("Login entry not found for deletion!")

        return HttpResponse("<script>alert('Seller Rejected, and Email Sent!');window.location='/viewseller';</script>")

    except login.DoesNotExist:
        logger.error(f"Login not found for ID: {id}")
        return HttpResponse("<script>alert('Error: Seller not found!');window.location='/viewseller';</script>")

    except seller.DoesNotExist:
        logger.error(f"Seller details not found for login ID: {id}")
        return HttpResponse("<script>alert('Error: Seller details not found!');window.location='/viewseller';</script>")

    except Exception as e:
        logger.exception(f"Unexpected error in reject_seller: {str(e)}")
        return HttpResponse(f"<script>alert('Error: {str(e)}');window.location='/viewseller';</script>")


def accept_manufacture(request,id):
    z=login.objects.get(pk=id)
    z.usertype='manufacture'
    z.save()
    return HttpResponse("<script>alert('Accepted');window.location='/viewmanufacture';</script>")

def reject_manufacture(request,id):
   z=login.objects.get(pk=id)
   z.usertype='rejected'
   z.save()
   return HttpResponse("<script>alert('Rejected');window.location='/viewmanufacture';</script>")

from .models import category  # Ensure you have a Category model

def add_category(request):
    if request.method == 'POST':
        n = request.POST['category_name']
        cat = category(category_name=n)  # Ensure the correct model name
        cat.save()
        return redirect('categorydetails')  # Ensure 'categorydetails' is defined in urls.py
    
    return render(request, 'managecategory.html') 
 
def delete_category(request,id):
    cate = category.objects.get(category_id=id)
    cate.delete()
    return redirect('categorydetails')



def feedback(request):
    feedback_data=Feedback.objects.filter(sender_id=request.session['lid'])
    if request.method=='POST':
        name=request.POST['name']
        feedback_desc=request.POST['feedback_desc']
        
        res = Feedback(sender_id_id=request.session['lid'],feedback_desc=feedback_desc,name=name,date=datetime.now())
        res.save()
        return HttpResponse("<script>alert('subitted');window.location='/feedback';</script>")
    return render(request,'feedback.html',{'feedbacks':feedback_data})
    
    


def updateseller(request):
    a = seller.objects.get(login_id=request.session['lid'])
    if request.method=='POST':
        f=request.POST['name']
        l=request.POST['companyname']
        e=request.POST['email']
        m=request.POST['phone']
        pl=request.POST['place']
        i=request.POST['licence_no']
        p=request.POST['landmark']
        
        a.company_name=l
        a.seller_name=f
        a.phone=m
        a.email=e
        a.place=pl
        a.landmark=p
        a.licence_no=i
        a.save()
    return render(request, 'updateseller.html', {'a': a})

def updatemanufacture(request):
    a = manufacture.objects.get(login_id=request.session['lid'])
    if request.method=='POST':
        f=request.POST['manufacturename']
        e=request.POST['email']
        m=request.POST['phone']
        pl=request.POST['place']
        i=request.POST['licence_no']
        p=request.POST['landmark']
        
        
        a.manufacturename=f
        a.phone=m
        a.email=e
        a.place=pl
        a.landmark=p
        a.licence_no=i
        a.save()
    return render(request, 'updatemanufacture.html', {'a': a})

def updateuser(request): 
    a = user.objects.get(login_id=request.session['lid'])
    print(a,"--------"*100)
    if request.method=='POST':
       f=request.POST['name']
       e=request.POST['email']
       m=request.POST['phone']
       pl=request.POST['place']
       l=request.POST['landmark']

       a.name=f
       a.email=e
       a.phone=m
       a.place=pl
       a.landmark=l    
       a.save()
       return redirect('userhome')
    return render(request, 'updateuser.html',{'a' : a})

        
def viewcategory(request):
    categorys=category.objects.all()
    return render(request,'viewcategory.html',{'category':categorys})

def viewmanucategory(request):
    categorys=category.objects.all()
    return render(request,'viewmanucategory.html',{'category':categorys})




# from .models import equipment
# from .forms import EquipmentForm  # Import the form
# from django.contrib import messages  # For user feedback

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .models import equipment  # Ensure correct model import
# # from .forms import EquipmentForm

# def manufacture_equipment(request):
#     if request.method == "POST":
#         form = EquipmentForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Equipment added successfully!")
#             return redirect('viewequipment')  # Ensure this matches your URL name
#         else:
#             messages.error(request, "Error adding equipment. Please check your inputs.")
#     else:
#         form = EquipmentForm()

#     return render(request, 'manufacture_equipment.html', {'form': form})

from django.core.files.storage import FileSystemStorage

from .models import equipment

def manufacture_equipment(request, cat_id):
    if request.method == 'POST':
        d = request.POST['description']
        image = request.FILES['image']
        e = request.POST['equipment_name']
        a = request.POST['amount']
        s = request.POST['stock']
        z= request.POST['zone']
        
        fs = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'static/img/'))
        filename = fs.save(image.name, image)  # Saves the file and returns the filename
        image_path = f'static/img/{filename}'
        
        category_id = category.objects.get(pk=cat_id)
        manuf = login.objects.get(pk=request.session['lid'])

        res = equipment(description=d, category=category_id, login=manuf, image=image_path, equipment_name=e, amount=a,Zone=z, stock=s)
        res.save()
        
    return render(request, 'manufacture_equipment.html')




from django.shortcuts import render, get_object_or_404, redirect
from .models import equipment

from collections import defaultdict
from django.shortcuts import render
from .models import equipment  # Ensure 'equipment' model is imported properly

def viewequipment(request):
    lid = request.session.get('lid')  # Get the login_id safely
    if not lid:
        return render(request, 'view_equipment.html', {'equipment_by_zone': {}})

    equip = equipment.objects.filter(login_id=lid)
    if not equip.exists():
        return render(request, 'view_equipment.html', {'equipment_by_zone': {}})

    equipment_by_zone = defaultdict(list)
    for item in equip:
        equipment_by_zone[item.Zone].append(item)

    return render(request, 'view_equipment.html', {'equipment_by_zone': dict(equipment_by_zone)})

def viewmanuequip(request):
    equip = equipment.objects.exclude(login__usertype='seller')
    if not equip.exists():
        return render(request, 'viewmanu_equipment.html', {'equipment_by_zone': {}})
    equipment_by_zone = defaultdict(list)
    for item in equip:
        equipment_by_zone[item.Zone].append(item)

    return render(request, 'viewmanu_equipment.html', {'equipment_by_zone': dict(equipment_by_zone)})

# def viewsellerequip(request):
#     equip = equipment.objects.exclude(login__usertype='manufacture')
#     if not equip.exists():
#         return render(request, 'viewseller_equipment.html', {'equipment_by_zone': {}})
#     equipment_by_zone = defaultdict(list)
#     for item in equip:
#         equipment_by_zone[item.Zone].append(item)
    
#         for equip in equipment_by_zone:
#             if int(equip.stock) <= 1:
#                 print(equip.login.username)
#                 subject = "Low Stock Alert"
#                 message = f"""
#                 Hello {equip.login.username},

#                 This is a notification that your equipment '{equip.equipment_name}' has low stock (Current stock: {equip.stock}).
#                 Please update your inventory if needed.

#                 Regards,
#                 MedEquip Team
#                 """
#                 try:
#                     receiver_data = seller.objects.get(login=equip.login)
#                     receiver_email = receiver_data.email
#                     print(receiver_email)
#                 except seller.DoesNotExist:
#                     receiver_email = None

#                 if receiver_email:
#                     try:
#                         send_mail(subject, message, settings.EMAIL_HOST_USER, [receiver_email], fail_silently=True)
#                     except Exception as e:
#                         print("Mail send failed:", e)

#     return render(request, 'viewequip.html', {'category_equipment': zone_equipment})

#     return render(request, 'viewseller_equipment.html', {'equipment_by_zone': dict(equipment_by_zone)})



# from collections import defaultdict

# def viewsellerequip(request):
#     equip = equipment.objects.exclude(login__usertype='manufacture')
#     if not equip.exists():
#         return render(request, 'viewseller_equipment.html', {'equipment_by_zone': {}})
    
#     equipment_by_zone = defaultdict(list)
#     for item in equip:
#         equipment_by_zone[item.Zone].append(item)

#     for zone, items in equipment_by_zone.items():
#         for equip in items:
#             if int(equip.stock) <= 1:
#                 print(equip.login.username)
#                 subject = "Low Stock Alert"
#                 message = f"""
#                 Hello {equip.login.username},

#                 This is a notification that your equipment '{equip.equipment_name}' has low stock (Current stock: {equip.stock}).
#                 Please update your inventory if needed.

#                 Regards,
#                 MedEquip Team
#                 """
#                 try:
#                     receiver_data = seller.objects.get(login=equip.login)
#                     receiver_email = receiver_data.email
#                     print(receiver_email)
#                 except seller.DoesNotExist:
#                     receiver_email = None

#                 if receiver_email:
#                     try:
#                         send_mail(subject, message, settings.EMAIL_HOST_USER, [receiver_email], fail_silently=True)
#                     except Exception as e:
#                         print("Mail send failed:", e)
                        
#         print(equipment_by_zone,"((((((((((((()))))))))))))")

#     return render(request, 'viewseller_equipment.html', {'equipment_by_zone': equipment_by_zone})



from collections import defaultdict
from django.core.mail import send_mail
from django.conf import settings
from .models import equipment, seller

def viewsellerequip(request):
    equip = equipment.objects.exclude(login__usertype='manufacture')
    
    if not equip.exists():
        return render(request, 'viewseller_equipment.html', {'equipment_by_zone': {}})
    
    equipment_by_zone = defaultdict(list)

    for item in equip:
        equipment_by_zone[item.Zone].append(item)

    # Stock alert emails (Only if not already sent)
    for zone_items in equipment_by_zone.values():
        for equip_item in zone_items:
            if int(equip_item.stock) <= 1 and not equip_item.low_stock_alert_sent:
                print("Sending alert to:", equip_item.login.username)
                subject = "Low Stock Alert"
                message = f"""
Hello {equip_item.login.username},

This is a notification that your equipment '{equip_item.equipment_name}' has low stock (Current stock: {equip_item.stock}).
Please update your inventory if needed.

Regards,
MedEquip Team
"""
                try:
                    receiver_data = seller.objects.get(login=equip_item.login)
                    receiver_email = receiver_data.email
                except seller.DoesNotExist:
                    receiver_email = None

                if receiver_email:
                    try:
                        send_mail(subject, message, settings.EMAIL_HOST_USER, [receiver_email], fail_silently=True)
                        equip_item.low_stock_alert_sent = True  # Mark as alerted
                        equip_item.save()
                    except Exception as e:
                        print("Mail send failed:", e)

    return render(request, 'viewseller_equipment.html', {'equipment_by_zone': dict(equipment_by_zone)})



def userhome(request):
    equip = equipment.objects.exclude(login__usertype='manufacture')
    if not equip.exists():
        return render(request, 'userhome.html', {'equipment_by_zone': {}})
    equipment_by_zone = defaultdict(list)
    for item in equip:
        equipment_by_zone[item.Zone].append(item)

    return render(request, 'userhome.html', {'equipment_by_zone': dict(equipment_by_zone)})

   




def buy_equipment(request, equipment_id):
    """ Handles the purchase of equipment """
    equipment = get_object_or_404(equipment, equipment_id=equipment_id)  # Use 'equipment_id' instead of 'id'

    if int(equipment.stock) > 0:
        equipment.stock = str(int(equipment.stock) - 1)  # Convert stock to integer before decreasing
        equipment.save()
        message = f"You have successfully purchased {equipment.equipment_name}!"
    else:
        message = f"Sorry, {equipment.equipment_name} is out of stock!"

    return render(request, 'buy_equipment.html', {'equipment': equipment, 'message': message})






#from django.shortcuts import render, redirect
#from .models import complaint, login
#from django.utils.timezone import now
#from django.contrib.auth.models import User

#def complaint_page(request):
    if request.method == "POST":
        description = request.POST.get("description")
        sender = None  # Default to None for anonymous users

        if request.user.is_authenticated:
            try:
                sender = login.objects.get(user=request.manufacture)  # Fetch the logged-in user from 'login' model
            except login.DoesNotExist:
                sender = None  # If no associated login model, treat as anonymous

        new_complaint = complaint.objects.create(
            sender=sender,  # Can be None if anonymous
            description=description,
            date=now().strftime("%Y-%m-%d"),  # Store current date
        )
        new_complaint.save()
        return redirect("complaint_page")  # Reload the page after submitting

    # Fetch complaints and order by newest first
    complaints = complaint.objects.all().order_by("-complaint_id")

    return render(request, "complaint_page.html", {"complaints": complaints})


#from django.shortcuts import render, redirect
#from .models import complaint

#def view_complaints(request):
    complaints = complaint.objects.all().order_by("-date")  # Get all complaints

    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id", "").strip()  # Ensure it's not empty
        reply_text = request.POST.get("reply", "").strip()  # Remove extra spaces

        if complaint_id.isdigit():  # ✅ Check if complaint_id is a valid number
            try:
                comp = complaint.objects.get(complaint_id=int(complaint_id))  # Convert to int
                comp.reply = reply_text
                comp.save()
            except complaint.DoesNotExist:
                pass  # Handle if complaint doesn't exist

        return redirect("view_complaints")  # Redirect after reply submission

    return render(request, "admin_complaint.html", {"complaints": complaints})



def comp_adm(request):
    return render(request,'comp_adm.html')

def submit_complaint(request):
   complaint_data=complaint.objects.filter(sender=request.session['lid'])
   if request.method=='POST':
      desc=request.POST['description']
      res = complaint(sender_id=request.session['lid'],description=desc,reply='pending',date=datetime.now())
      res.save()
      return HttpResponse("<script>alert('subitted');window.location='/submit_complaint';</script>")

   return render(request,'submit_complaint.html',{'send_comp':complaint_data})

def view_complaints(request):
   complaints = complaint.objects.all()
   return render(request,'admin_complaint.html',{'complaints': complaints})

from django.http import JsonResponse

def submit_reply(request):
    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")
        reply_text = request.POST.get("reply_text")

        print("Complaint ID:", complaint_id)
        print("Reply Text:", reply_text)

        if not complaint_id or not reply_text:
            return JsonResponse({"success": False, "error": "Missing data"})

        try:
            complaint = complaint.objects.get(complaint_id=complaint_id)  # ✅ Fixed model reference
            complaint.reply = reply_text  # ✅ Ensure `reply` field exists
            complaint.save()
            print("Reply saved successfully!")
            return JsonResponse({"success": True})
        except complaint.DoesNotExist:
            print("Complaint not found!")
            return JsonResponse({"success": False, "error": "Complaint not found"})

    return JsonResponse({"success": False, "error": "Invalid request"})


# # from django.shortcuts import render
# from collections import defaultdict
# # from .models import equipment
# from collections import defaultdict

# def viewmanuequip(request):
#     lid = request.session.get('lid')  # Get the login_id safely
#     if not lid:
#         return render(request, 'viewmanu_equipment.html', {'equipment_by_zone': {}})

#     equip = equipment.objects.filter(login_id=lid)

#     # Ensure queryset is not empty
#     if not equip.exists():
#         return render(request, 'viewmanu_equipment.html', {'equipment_by_zone': {}})

#     # Grouping by Zone
#     equipment_by_zone = defaultdict(list)
#     for item in equip:
#         equipment_by_zone[item.Zone].append(item)

#     return render(request, 'viewmanu_equipment.html', {'equipment_by_zone': dict(equipment_by_zone)})










def feedback_view(request):
    if request.method == 'POST':
        sender_id = request.POST.get('sender_id')
        name=request.POST.get('name')
        feedback_desc = request.POST.get('feedback_desc')

        
        feedback=Feedback.objects.create(sender_id=sender_id, feedback_desc=feedback_desc,name=name, date=now())
        feedback.save()

        return redirect('feedback_page')  # Replace with the correct URL name for feedback page

    feedbacks = Feedback.objects.all().order_by('-date')  # Display latest feedback first
    return render(request, 'feedback.html', {'feedbacks': feedbacks})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# from .models import complaint  # Import the complaint model

@csrf_exempt
def admin_send_reply(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            complaint_id = data.get('complaint_id')
            reply_text = data.get('reply_text')

            if not complaint_id or not reply_text:
                return JsonResponse({'error': 'Missing data'}, status=400)

            # Fetch the complaint and update the reply field
            complaint_obj = complaint.objects.get(complaint_id=complaint_id)
            complaint_obj.reply = reply_text
            complaint_obj.save()

            # return JsonResponse("<script>alert('replied successfully');window.location='/view_complaints'</script>")
            return JsonResponse({'success': True, 'message': 'Reply submitted successfully'})

        except complaint.DoesNotExist:
            return JsonResponse({'error': 'Complaint not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def reply_complaints(request,id):
   a=complaint.objects.get(pk=id)
   if request.method=='POST':
      rep=request.POST['reply_text']
      a.reply=rep
      a.save()
      return HttpResponse("<script>alert('Submitted');window.location='/view_complaints';</script>")
  
def complaints(request):
   complaint_data=complaint.objects.filter(sender=request.session['lid'])
   if request.method=='POST':
      desc=request.POST['description']
      res = complaint(sender_id=request.session['lid'],description=desc,reply='pending',date=datetime.now())
      res.save()
      return HttpResponse("<script>alert('subitted');window.location='/complaints';</script>")

   return render(request,'complaints.html',{'send_comp':complaint_data})


def view_complaints(request):
   complaints = complaint.objects.all()
   return render(request,'view_complaints.html',{'complaints': complaints})

def land_equipment_list(request):
    land_equipments = equipment.objects.filter(Zone="Land Adventure Gear")  # Filter only "Land" zone
    return render(request, 'land.html', {'equipments': land_equipments})

def water_equipment_list(request):
    water_equipments = equipment.objects.filter(Zone="Ocean Adventure Gear")  # Filter only "Land" zone
    return render(request, 'water.html', {'equipments': water_equipments})

def aero_equipment_list(request):
    aero_equipments = equipment.objects.filter(Zone="Aero Adventure Gear")  # Filter only "Land" zone
    return render(request, 'aero.html', {'equipments': aero_equipments})

def frozen_equipment_list(request):
    frozen_equipments = equipment.objects.filter(Zone="Frozen Adventure Gear")  # Filter only "Land" zone
    return render(request, 'frozen.html', {'equipments': frozen_equipments})

def feedback_list(request):
    feedbacks = Feedback.objects.all().order_by('-date')  # Fetch feedback in descending order
    return render(request, 'admin_feedback.html', {'feedbacks': feedbacks})
    
def equipment_list(request):
    zones = ["Land Adventure Gear", "Ocean Adventure Gear", "Frozen Adventure Gear", "Aero Adventure Gear"]
    equipment_data = {zone: equipment.objects.filter(Zone=zone) for zone in zones}
    return render(request, 'section.html', {'equipment_data': equipment_data, 'zones': zones})

def delete_equipment(request, id):
    equip_del = equipment.objects.get(equipment_id=id)
    equip_del.delete()
    return redirect('viewequipment')


def update_equipment(request,id): 
    a = equipment.objects.get(equipment_id=id)
    if request.method=='POST':
       f=request.POST['equipment_name']
       l=request.POST['description']
       e=request.POST['amount']
       m=request.POST['stock']
       

       a.equipment_name=f
       a.description=l
       a.amount=e
       a.stock=m
      
       a.save()
       return redirect('viewequipment')
    return render(request,'update_equipment.html', {'a': a})

def update_rent_equipment(request,id): 
    a = rent_equipment.objects.get(equipment_id=id)
    if request.method=='POST':
       f=request.POST['equipment_name']
       l=request.POST['description']
       e=request.POST['amount']
       m=request.POST['stock']
       

       a.equipment_name=f
       a.description=l
       a.amount=e
       a.stock=m
      
       a.save()
       return redirect('viewequipment')
    return render(request,'update_rent_equipment.html', {'a': a})


# from django.shortcuts import render, redirect
# from .models import payment_user, order_master_user, order_details_user

# def payment_page(request):
#     # Retrieve total_amount and order_master_user_id from GET or session
#     total_amount = request.GET.get('total_amount', request.session.get('total_amount', '0.00'))
#     order_master_user_id = request.GET.get('ordermaster_id', request.session.get('ordermaster_id', None))

#     print(total_amount, "/////////////")
#     print(order_master_user_id, "////////")

#     # Validate order_master_user_id
#     if order_master_user_id:
#         try:
#             order = order_master_user.objects.get(order_master_user_id=order_master_user_id)
#         except order_master_user.DoesNotExist:
#             return render(request, 'payment_page.html', {
#                 'error': 'Order not found',
#                 'total_amount': total_amount,
#                 'order_master_user_id': order_master_user_id
#             })
#         except Exception as e:
#             return render(request, 'payment_page.html', {
#                 'error': str(e),
#                 'total_amount': total_amount,
#                 'order_master_user_id': order_master_user_id
#             })

#     return render(request, 'payment_page.html', {
#         'total_amount': total_amount,
#         'order_master_user_id': order_master_user_id
#     })

# def payments(request):
#     if request.method == 'POST':
#         # Retrieve total_amount and order_master_user_id from POST data
#         total_amount = request.POST.get('total_amount', '0.00')
#         order_master_user_id = request.POST.get('order_master_user_id', None)

#         print(total_amount, "///////////// payments")
#         print(order_master_user_id, "//////// payments")

#         try:
#             order = order_master_user.objects.get(order_master_user_id=order_master_user_id)
#             order.status = 'paid'
#             order.save()

#             order_items = order_details_user.objects.filter(order_master_user=order)
#             for item in order_items:
#                 product = item.product
#                 product.stock = max(0, int(product.stock) - int(item.quantity))
#                 product.save()

#             # Save payment_user entry
#             print("Saving payment_user now...")
#             payment_user.objects.create(
#                 order_master_user=order,
#                 status='paid'
#             )
#             print("Payment saved successfully")

#             # Redirect to success page
#             return render(request, 'payment_success.html', {'message': 'Payment completed successfully!'})

#         except order_master_user.DoesNotExist:
#             return render(request, 'payment_page.html', {
#                 'error': 'Order not found',
#                 'total_amount': total_amount,
#                 'order_master_user_id': order_master_user_id
#             })
#         except Exception as e:
#             return render(request, 'payment_page.html', {
#                 'error': str(e),
#                 'total_amount': total_amount,
#                 'order_master_user_id': order_master_user_id
#             })

#     # If not POST, redirect to payment_page
#     return redirect('payment_page')

from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import razorpay
from .models import payment_user, order_master_user, order_details_user

# Initialize Razorpay client with API keys
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def payment_page(request):
    # Retrieve total_amount and ordermaster_id from GET or session
    total_amount = request.GET.get('total_amount', request.session.get('total_amount', '0.00'))
    order_master_user_id = request.GET.get('ordermaster_id', request.session.get('ordermaster_id', None))

    print(total_amount, "///////////// payment_page")
    print(order_master_user_id, "//////// payment_page")

    # Validate order_master_user_id
    if order_master_user_id:
        try:
            order = order_master_user.objects.get(order_master_user_id=order_master_user_id)
            # Create Razorpay order
            amount_in_paise = int(float(total_amount) * 100)  # Convert to paise
            print(f"Creating Razorpay order with amount: {amount_in_paise}, currency: INR")
            razorpay_order = razorpay_client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': '1',  # Auto-capture payment
                'notes': {
                    'total_amount': str(total_amount),
                    'ordermaster_id': str(order_master_user_id)
                }
            })
            print(f"Razorpay order created: {razorpay_order}")
            # Store Razorpay order ID, total_amount, and ordermaster_id in session
            request.session['razorpay_order_id'] = razorpay_order['id']
            request.session['total_amount'] = str(total_amount)  # Ensure string for consistency
            request.session['ordermaster_id'] = str(order_master_user_id)  # Ensure string
            request.session.modified = True  # Force session save
            print(f"Session data set: {request.session.items()}")
        except order_master_user.DoesNotExist:
            return render(request, 'payment_page.html', {
                'error': 'Order not found',
                'total_amount': total_amount,
                'order_master_user_id': order_master_user_id
            })
        except razorpay.errors.BadRequestError as e:
            print(f"Razorpay error: {str(e)}")
            return render(request, 'payment_page.html', {
                'error': f'Failed to create Razorpay order: {str(e)}',
                'total_amount': total_amount,
                'order_master_user_id': order_master_user_id
            })
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return render(request, 'payment_page.html', {
                'error': str(e),
                'total_amount': total_amount,
                'order_master_user_id': order_master_user_id
            })

        return render(request, 'payment_page.html', {
            'total_amount': total_amount,
            'order_master_user_id': order_master_user_id,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_amount': amount_in_paise,
            'currency': 'INR',
            'callback_url': request.build_absolute_uri('/payments/')
        })

    return render(request, 'payment_page.html', {
        'total_amount': total_amount,
        'order_master_user_id': order_master_user_id,
        'error': 'Invalid order ID'
    })

@csrf_exempt
def payments(request):
    if request.method == 'POST':
        # Retrieve data from session
        total_amount = request.session.get('total_amount', '0.00')
        order_master_user_id = request.session.get('ordermaster_id', None)
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')

        # Fallback to Razorpay order notes if session data is missing
        if not order_master_user_id or total_amount == '0.00':
            try:
                order_data = razorpay_client.order.fetch(razorpay_order_id)
                total_amount = order_data.get('notes', {}).get('total_amount', total_amount)
                order_master_user_id = order_data.get('notes', {}).get('ordermaster_id', order_master_user_id)
                print(f"Fallback to notes: total_amount={total_amount}, ordermaster_id={order_master_user_id}")
            except Exception as e:
                print(f"Failed to fetch order notes: {str(e)}")

        print(total_amount, "///////////// payments")
        print(order_master_user_id, "//////// payments")
        print(razorpay_payment_id, razorpay_order_id, razorpay_signature, "//////// Razorpay data")

        if not order_master_user_id:
            return render(request, 'payment_page.html', {
                'error': 'Order ID not found in session or order notes',
                'total_amount': total_amount,
                'order_master_user_id': order_master_user_id
            })

        try:
            # Verify payment signature
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            # Update order and stock
            order = order_master_user.objects.get(order_master_user_id=order_master_user_id)
            order.status = 'paid'
            order.save()

            order_items = order_details_user.objects.filter(order_master_user=order)
            for item in order_items:
                product = item.product
                product.stock = max(0, int(product.stock) - int(item.quantity))
                product.save()

            # Save payment_user entry
            print("Saving payment_user now...")
            payment_user.objects.create(
                order_master_user=order,
                status='paid'
            )
            print("Payment saved successfully")

            # Clear session data after successful payment
            request.session.pop('razorpay_order_id', None)
            request.session.pop('total_amount', None)
            request.session.pop('ordermaster_id', None)
            request.session.modified = True

            # Redirect to /userhome after successful payment
            return redirect('userhome')

        except order_master_user.DoesNotExist:
            return render(request, 'payment_page.html', {
                'error': 'Order not found',
                'total_amount': total_amount,
                'order_master_user_id': order_master_user_id
            })
        except razorpay.errors.SignatureVerificationError:
            return render(request, 'payment_page.html', {
                'error': 'Payment verification failed',
                'total_amount': total_amount,
                'order_master_user_id': order_master_user_id
            })
        except Exception as e:
            print(f"Unexpected error in payments: {str(e)}")
            return render(request, 'payment_page.html', {
                'error': str(e),
                'total_amount': total_amount,
                'order_master_user_id': order_master_user_id
            })

    # Handle non-POST requests
    return HttpResponseBadRequest("Invalid request method")





def userhome(request):
    return render(request, 'userhome.html', {'message': 'Welcome to your home page!'})

def display_order(request):
    users=order_details_seller.objects.all()
    return render(request,'orderdetails.html',{'users':users})

def display_order_user(request):
    ord=order_master_user.objects.filter(user_id=request.session['uid'])
    return render(request,'orderdetailsuser.html',{'orders':ord})

def rent_equipment_(request, cat_id):
    if request.method == 'POST':
        image = request.FILES['image']
        e = request.POST['equipment_name']
        a = request.POST['amount']
        s = request.POST['stock']
        z= request.POST['zone']
        d = request.POST['description']
        
        fs = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'static/img/'))
        filename = fs.save(image.name, image)  # Saves the file and returns the filename
        image_path = f'static/img/{filename}'
        
        category_id = category.objects.get(pk=cat_id)
        seller = login.objects.get(pk=request.session['lid'])

        res = rent_equipment(description=d,category=category_id,login=seller,image=image_path,equipment_name=e,amount=a,Zone=z,stock=s)
        res.save()
        
    return render(request, 'rent_equipment.html')

# def viewrentequip(request):
#     equip = rent_equipment.objects.exclude(login__usertype='manufacture')
#     if not equip.exists():
#         return render(request, 'viewrent_equipment.html', {'equipment_by_zone': {}})
    
#     equipment_by_zone = defaultdict(list)
    
#     for item in equip:
#         equipment_by_zone[item.Zone].append(item)
#     return render(request, 'viewrent_equipment.html', {'equipment_by_zone': dict(equipment_by_zone)})
from django.shortcuts import render
from django.db.models import Subquery, OuterRef
from collections import defaultdict
from .models import rent_equipment, rent
def viewrentequip(request):
    user_login_id = request.session.get('lid')

    equipments = rent_equipment.objects.exclude(login__usertype='manufacture')

    if user_login_id:
        rent_status_subquery = rent.objects.filter(
            user__login_id=user_login_id,
            equipment_id=OuterRef('equipment_id')
        ).order_by('-from_date').values('status')[:1]

        equipments = equipments.annotate(rent_status=Subquery(rent_status_subquery))
    else:
        equipments = equipments.annotate(rent_status=None)

    equipment_by_zone = defaultdict(list)
    for item in equipments:
        equipment_by_zone[item.Zone].append(item)

    return render(request, 'viewrent_equipment.html', {
        'equipment_by_zone': dict(equipment_by_zone),
    })

def rent_dates(request,equipment_id,seller_login_id):
    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']        
        # Optional: Validate dates
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                if start > end:
                    return HttpResponse("<script>alert('Start date cannot be after end date.');window.location='/viewrentequip';</script>")
                    
                else:
                    seller_id = seller.objects.get(login_id=seller_login_id)
                    dt = rent(from_date=start_date,to_date=end_date,
                    seller=seller_id,user_id=request.session['uid'],status='pending',equipment_id=equipment_id)
                    dt.save()
                    # Send email to seller
                    seller_obj = seller.objects.get(login_id=seller_login_id)  # Ensure 'login_id' is a valid ForeignKey
                    receiver_email = seller_id.email  # Seller's email
                    sender_email = settings.EMAIL_HOST_USER  # Use sender email from settings
                    
                    subject = "New Rent Request"
                    message = f"""
                    Hello {seller_obj.seller_name},

                    You have received a new rent request from {start_date} to {end_date}. Please log in to view details.

                    Thank you.
                    """

                 # Send email using the custom backend
                send_mail(
                   subject,
                   message,
                   sender_email,
                  [receiver_email],
                   fail_silently=False  # Change to True if you want to suppress errors
                   )
                return HttpResponse(f"<script>alert('Request submitted and email sent to seller!');window.location='/viewrent_equipment';</script>")

            except ValueError:
                return HttpResponse("<script>alert('Invalid date format.');window.location='/viewrent_equipment';</script>")
        else:
            return HttpResponse("Both dates are required.")    
    return render(request, 'rent_dates.html')

def rent_requests(request):
    rent_req= rent.objects.filter(seller_id=request.session['sid'])
    return render(request,'rent_request.html',{'rent_request': rent_req})

def accept_req(request, user_id,rent_id):
    try:
        z = rent.objects.get(pk=rent_id)
        z.status = 'accepted'
        z.save()
        # Fetch seller details
        user_obj = user.objects.get(user_id=user_id)  # Ensure 'login_id' is a valid ForeignKey
        receiver_email = user_obj.email  # Seller's email
        sender_email = settings.EMAIL_HOST_USER  # Use sender email from settings

        # Email details
        subject = "Your Rent Has Been Approved"
        message = f"""
        Hello {user_obj.name},

        Your Request for equipment has been accepted
        You can now log in and proceed to payment!

        Thank you.
        """
        # Send email using the custom backend
        send_mail(
            subject,
            message,
            sender_email,
            [receiver_email],
            fail_silently=False  # Change to True if you want to suppress errors
        )
        return HttpResponse("<script>alert('Request Accepted and Email Sent!');window.location='/rent_request';</script>")   
    except login.DoesNotExist:
        return HttpResponse("<script>alert('Error: User not found!');window.location='/rent_request';</script>")    
    except seller.DoesNotExist:
        return HttpResponse("<script>alert('Error: User details not found!');window.location='/rent_request';</script>")   
    except Exception as e:
        return HttpResponse(f"<script>alert('Error: {str(e)}');window.location='/rent_request';</script>")
    
    
from django.shortcuts import render, redirect, get_object_or_404
from .models import equipment, Wishlist
from .models import login  # replace 'your_app' with actual app name

def add_to_wishlist(request, equipment_id):
    if 'lid' not in request.session:
        return redirect('/login/?next=' + request.path)

    user_login = get_object_or_404(login, pk=request.session['lid'])
    item = get_object_or_404(equipment, equipment_id=equipment_id)

    Wishlist.objects.get_or_create(user=user_login, equipment=item)
    return redirect('wishlist')


def remove_from_wishlist(request, equipment_id):
    if 'lid' not in request.session:
        return redirect('/login/?next=' + request.path)

    user_login = get_object_or_404(login, pk=request.session['lid'])
    Wishlist.objects.filter(user=user_login, equipment_id=equipment_id).delete()
    return redirect('wishlist')


def wishlist_view(request):
    if 'lid' not in request.session:
        return redirect('/login/?next=' + request.path)

    user_login = get_object_or_404(login, pk=request.session['lid'])
    wishlist_items = Wishlist.objects.filter(user=user_login)
    return render(request, 'wishlist.html', {'wishlist': wishlist_items})


def viewsellerrent_equipment(request):
    lid = request.session.get('lid')  # Get the login_id safely
    if not lid:
        return render(request, 'viewsellerrent_equip.html', {'equipment_by_zone': {}})

    equip = rent_equipment.objects.filter(login_id=lid)
    if not equip.exists():
        return render(request, 'viewsellerrent_equip.html', {'equipment_by_zone': {}})

    equipment_by_zone = defaultdict(list)
    for item in equip:
        equipment_by_zone[item.Zone].append(item)

    return render(request, 'viewsellerrent_equip.html', {'equipment_by_zone': dict(equipment_by_zone)})

# views.py
from django.shortcuts import render
from django.db.models import Q
from .models import rent_equipment

def equipment_search(request):
    query = request.GET.get('query')  # Get the search input
    print(query, "//////////")

    # Start with excluding manufacturers
    equipments = equipment.objects.exclude(login__usertype='manufacture')

    if query:
        # Apply search filter only if there's a query
        equipments = equipments.filter(
            Q(category__category_name__icontains=query) |
            Q(equipment_name__icontains=query) |
            Q(description__icontains=query)
        )

    # Debugging output
    print(f"Search Query: {query}")
    print(f"Equipment Count: {equipments.count()}")
    print(f"Equipment IDs: {[eq.equipment_id for eq in equipments]}")

    return render(request, 'search.html', {'equipments': equipments, 'query': query})



import razorpay
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from .models import order_master_seller, order_details_seller

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def payment_page_seller(request):
    order_master_seller_id = request.GET.get('ordermaster_id')
    total_amount = request.GET.get('total_amount')
    
    if order_master_seller_id and total_amount:
        try:
            # Check if a valid Razorpay order ID exists in session
            razorpay_order_id = request.session.get('razorpay_order_id')
            if razorpay_order_id:
                try:
                    # Verify if the existing order is still valid
                    order_status = razorpay_client.order.fetch(razorpay_order_id)
                    if order_status['status'] == 'created':
                        context = {
                            'razorpay_key': settings.RAZORPAY_KEY_ID,
                            'razorpay_order_id': razorpay_order_id,
                            'total_amount': total_amount,
                            'amount_in_paise': int(float(total_amount) * 100),
                            'order_master_seller_id': order_master_seller_id,
                            'callback_url': request.build_absolute_uri(reverse('paymenthandler_seller')),
                            'error': request.session.pop('error', None)
                        }
                        print(f"Reusing session: razorpay_order_id={razorpay_order_id}, order_master_seller_id={order_master_seller_id}, total_amount={total_amount}")
                        return render(request, 'payment_page_seller.html', context)
                except razorpay.errors.BadRequestError:
                    # Order ID invalid or expired, create a new one
                    pass

            # Create new Razorpay order
            razorpay_order = razorpay_client.order.create({
                'amount': int(float(total_amount) * 100),  # Convert to paise
                'currency': 'INR',
                'payment_capture': '1'  # Auto-capture payment
            })
            
            # Store in session
            request.session['razorpay_order_id'] = razorpay_order['id']
            request.session['order_master_seller_id'] = order_master_seller_id
            request.session['total_amount'] = total_amount
            
            print(f"Session set: razorpay_order_id={razorpay_order['id']}, order_master_seller_id={order_master_seller_id}, total_amount={total_amount}")
            
            context = {
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
                'total_amount': total_amount,
                'amount_in_paise': int(float(total_amount) * 100),
                'order_master_seller_id': order_master_seller_id,
                'callback_url': request.build_absolute_uri(reverse('paymenthandler_seller')),
                'error': request.session.pop('error', None)
            }
            return render(request, 'payment_page_seller.html', context)
            
        except order_master_seller.DoesNotExist:
            return render(request, 'payment_page_seller.html', {'error': 'Order not found'})
        except Exception as e:
            return render(request, 'payment_page_seller.html', {'error': str(e)})
    
    return render(request, 'payment_page_seller.html', {'error': 'Invalid order details'})

@csrf_exempt
def paymenthandler_seller(request):
    if request.method == "POST":
        try:
            # Get payment details from Razorpay
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            
            # Log for debugging
            session_order_id = request.session.get('razorpay_order_id')
            print(f"POST data: razorpay_order_id={razorpay_order_id}, payment_id={payment_id}, signature={signature}")
            print(f"Session data: razorpay_order_id={session_order_id}, order_master_seller_id={request.session.get('order_master_seller_id')}")
            
            # Check if the Razorpay order ID matches the session
            if not razorpay_order_id or razorpay_order_id != session_order_id:
                request.session['error'] = f'Invalid order ID: received {razorpay_order_id}, expected {session_order_id}'
                return HttpResponseRedirect(
                    f"{reverse('payment_page_seller')}?ordermaster_id={request.session.get('order_master_seller_id')}&total_amount={request.session.get('total_amount')}"
                )
            
            # Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
                
                # Update order status and stock
                order_master_seller_id = request.session.get('order_master_seller_id')
                order = order_master_seller.objects.get(order_master_seller_id=int(order_master_seller_id))
                order.status = 'paid'
                order.save()
                
                # Deduct stock from equipment table
                order_items = order_details_seller.objects.filter(order_master_seller=order)
                for item in order_items:
                    product = item.product
                    product.stock = max(0, int(product.stock) - int(item.quantity))
                    product.save()
                
                # Clear session data
                for key in ['razorpay_order_id', 'order_master_seller_id', 'total_amount']:
                    if key in request.session:
                        del request.session[key]
                
                # Store success message
                request.session['success_message'] = 'Payment completed successfully.'
                return HttpResponseRedirect(reverse('sellerhome'))
                
            except razorpay.errors.SignatureVerificationError:
                request.session['error'] = 'Payment verification failed. Please try again.'
                return HttpResponseRedirect(
                    f"{reverse('payment_page_seller')}?ordermaster_id={request.session.get('order_master_seller_id')}&total_amount={request.session.get('total_amount')}"
                )
                
        except order_master_seller.DoesNotExist:
            request.session['error'] = 'Order not found'
            return HttpResponseRedirect(
                f"{reverse('payment_page_seller')}?ordermaster_id={request.session.get('order_master_seller_id')}&total_amount={request.session.get('total_amount')}"
            )
        except Exception as e:
            request.session['error'] = str(e)
            return HttpResponseRedirect(
                f"{reverse('payment_page_seller')}?ordermaster_id={request.session.get('order_master_seller_id')}&total_amount={request.session.get('total_amount')}"
            )
    
    return HttpResponseBadRequest('Invalid request method')

# from django.shortcuts import render
# from .models import order_master_seller, order_details_seller, equipment

# def payment_page_seller(request):
#     order_master_seller_id = request.GET.get('ordermaster_id')
#     total_amount = request.GET.get('total_amount')
    
#     print(order_master_seller_id,total_amount)
    
    
    
#     if order_master_seller_id:
#         try:
#             # Update order status to 'paid'
#             order = order_master_seller.objects.get(order_master_seller_id=order_master_seller_id)
#             order.status = 'paid'
#             order.save()
            
#             # Fetch order details
#             order_items = order_details_seller.objects.filter(order_master_seller=order)
            
#             # Deduct stock from equipment table
#             for item in order_items:
#                 product = item.product
#                 product.stock = max(0, int(product.stock) - int(item.quantity))  # Ensure stock doesn't go negative
#                 product.save()
            
#         except order_master_seller.DoesNotExist:
#             return render(request, 'payment_page.html', {'error': 'Order not found'})
#         except Exception as e:
#             return render(request, 'payments_seller.html', {'error': str(e)})
    
#     return render(request, 'payment_page_seller.html',{'total_amount':total_amount})

def payments_seller(request):
    if 'lid' not in request.session:
        return redirect('login')  # Ensure user is logged in

    seller_id = request.session['lid']
    
    # Fetch all ongoing orders for the logged-in user
    ongoing_orders = order_master_seller.objects.filter(seller_id=seller_id, status='pending')

    return render(request, 'payments_seller.html', {'orders': ongoing_orders})

def payment_rent(request, equipment_id, login_id):
    try:
        equipment = rent_equipment.objects.get(equipment_id=equipment_id, login_id=login_id)
        if request.method == 'POST':
            rent_request = rent.objects.get(equipment_id=equipment_id, user_id=request.session['uid'], status='accepted')
            rent_request.status = 'paid'
            rent_request.total_rent_amount = int(float(equipment.amount))
            rent_request.save()
            current_stock = int(equipment.stock) if equipment.stock else 0
            new_stock = max(0, current_stock - 1)
            equipment.stock = str(new_stock)
            equipment.save()
            return HttpResponse("<script>alert('Payment successful! Equipment rented.');window.location='/userhome';</script>")
        return render(request, 'payment_rent.html', {'equipment': equipment})
    except rent_equipment.DoesNotExist:
        return render(request, 'payment_rent.html', {'error': 'Equipment not found'})
    except rent.DoesNotExist:
        return render(request, 'payment_rent.html', {'error': 'Rent request not found or not accepted'})
    except Exception as e:
        return render(request, 'payment_rent.html', {'error': str(e)})
    from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch, Subquery, OuterRef, Min
from .models import order_master_user, order_details_user, equipment
from django.conf import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)

def display_order(request):
    if 'uid' not in request.session:
        logger.warning("User not logged in, redirecting to login page")
        return render(request, 'order_details.html', {'orders': [], 'error': "User not logged in"})

    uid = request.session['uid']
    try:
        # Subquery to get the earliest date from order_details_user for each order_master_user
        earliest_date = order_details_user.objects.filter(
            order_master_user=OuterRef('pk')
        ).values('date')[:1]

        # Fetch orders with related order_details and equipment, annotated with earliest date
        orders = order_master_user.objects.filter(user_id=uid).annotate(
            order_date=Subquery(earliest_date)
        ).prefetch_related(
            Prefetch('order_details_user_set', queryset=order_details_user.objects.select_related('product'))
        ).order_by('-order_date')

        if not orders.exists():
            logger.info(f"No orders found for user_id: {uid}")
            return render(request, 'order_details.html', {'orders': [], 'message': "No orders found"})

        logger.info(f"Retrieved {orders.count()} orders for user_id: {uid}")
        return render(request, 'order_details.html', {'orders': orders})

    except Exception as e:
        logger.error(f"Error retrieving orders for user_id {uid}: {str(e)}")
        return render(request, 'order_details.html', {'orders': [], 'error': f"An error occurred: {str(e)}"})