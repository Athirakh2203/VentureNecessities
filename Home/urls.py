from django.urls import path
from . import views

urlpatterns = [
    path('registration/', views.registration, name='registration'),
    path('equipment/', views.equipment, name='equipment'),
    path('user-register/', views.user_registration, name='user_registration'),
    path('seller-register/', views.seller_registration, name='seller_registration'),
    path('wholesaler-register/', views.wholesaler_registration, name='wholesaler_registration'),
    path('login/',views.logins,name='login'),
    path('',views.index,name='index'),
    path('homeadmin/',views.homeadmin,name='homeadmin'),
    path('userhome/',views.userhome,name='userhome'),
    path('sellerhome/',views.sellerhome,name='sellerhome'),
    path('manufacturehome/',views.manufacturehome,name='manufacturehome'),
    path('viewseller/',views.viewseller,name='viewseller'),
    path('viewmanufacture/',views.viewmanufacture,name='viewmanufacture'),
    path('accept_seller/<id>',views.accept_seller,name='accept_seller'),
    path('reject_seller/<id>',views.reject_seller,name='reject_seller'),
    path('accept_manufacture/<id>',views.accept_manufacture,name='accept_manufacture'),
    path('reject_manufacture/<id>',views.reject_manufacture,name='reject_manufacture'),
    path('category/', views.add_category, name="category"),
    path('categorydetails/', views.categorydetails, name="categorydetails"),
    path('delete_category/<id>',views.delete_category,name="deletecategory"),
    path('feedback/',views.feedback,name="feedback"),
    path('updateseller/',views.updateseller,name="updateseller"),
    path('updatemanufacture/',views.updatemanufacture,name="updatemanufacture"),
    path('updateuser/',views.updateuser,name="updateuser"),
    path('viewcategory/', views.viewcategory, name="viewcategory"),
     path('viewmanucategory/', views.viewmanucategory, name="viewmanucategory"),
    path('viewuser/',views.viewuser,name="viewuser"),
    path('reg/', views.reg, name="reg"),
    path('mequipment/<cat_id>',views.manufacture_equipment,name='mequipment'),
    path('viewequipment/', views.viewequipment, name='viewequipment'),
    path('complaints/',views.complaints,name="complaints"),
    path('view_complaints/',views.view_complaints,name="view_complaints"),
    path('reply_complaints/<id>',views.reply_complaints,name="reply_complaints"),
    path('admin_send_reply/', views.admin_send_reply, name='admin_send_reply'),
    path('feedbacklist/', views.feedback_list, name='admin_feedback'),
    path('delete_equipment/<id>', views.delete_equipment, name='delete_equipment'),
    path('update_equipment/<id>',views.update_equipment,name='update_equipment'),
    path('update_rent_equipment/<id>',views.update_rent_equipment,name='update_rent_equipment'),

    path('payment_page/', views.payment_page, name='payment_page'), 
   
   
    path('payments/', views.payments, name='payments'), 
       path('payment_page_seller/', views.payment_page_seller, name='payment_page_seller'),
    path('paymenthandler_seller/', views.paymenthandler_seller, name='paymenthandler_seller'),
     path('payment_rent/<equipment_id>/<login_id>', views.payment_rent, name='payment_rent'),
   
   
    path('payments_seller/', views.payments_seller, name='payments_seller'), 
    # path('viewequipment/', views.view_equipment, name='view_equipment'),
    path('view-equipment/', views.viewmanuequip, name='viewmanuequip'),
    # path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('buy/<int:equipment_id>/', views.buy_equipment, name='buy_equipment'),
    path('cart_seller/<id>', views.cart_seller, name='cart_seller'),
    path('view_cart_seller/', views.view_cart_seller, name='view_cart_seller'),
    
    path('update_cart_quantity_seller/', views.update_cart_quantity_seller, name='update_cart_quantity_seller'),

    path('del_cart_seller/<int:id>/', views.delete_cart_seller, name='delete_cart_seller'),
    
    path('cart_user/<id>', views.cart_user, name='cart_user'),
    path('view_cart_user/', views.view_cart_user, name='view_cart_user'),
    
    path('update_cart_quantity_user/', views.update_cart_quantity_user, name='update_cart_quantity_user'),

    path('del_cart_user/<int:id>/', views.delete_cart_user, name='delete_cart_user'),
    
    path('viewmanuequip/', views.viewmanuequip, name='viewmanu_equipment'),
    path('viewsellerequip/', views.viewsellerequip, name='viewseller_equipment'),
    path('land/', views.land_equipment_list, name='land'),
    path('water/', views.water_equipment_list, name='water'),
    path('aero/', views.aero_equipment_list, name='aero'),
    path('frozen/', views.frozen_equipment_list, name='frozen'),
    path('order_details/', views.display_order, name='order_details'),
    path('rent_equipment/<cat_id>',views.rent_equipment_,name='rent_equipment'),
    path('orderdetailsuser/', views.display_order_user, name='orderdetailsuser'), 
    path('rent_dates/<equipment_id>/<seller_login_id>', views.rent_dates, name='rent_dates'),
    path('rent_request/', views.rent_requests, name='rent_request'),
    path('viewrent_equipment/', views.viewrentequip, name='viewrent_equipment'),
    path('accept_req/<user_id>/<rent_id>',views.accept_req,name="accept_req"),
    
    path('wishlist/',views.wishlist_view, name='wishlist'),
    path('wishlist_add/<int:equipment_id>/',views.add_to_wishlist, name='wishlist_add'),
    path('wishlist_remove/<int:equipment_id>/', views.remove_from_wishlist, name='wishlist_remove'),
    
    path('viewsr_equipment/', views.viewsellerrent_equipment, name='viewsr_equipment'),
    
    path('search/', views.equipment_search, name='equipment_search'),

 

       
    
    

    
    
    
]
   