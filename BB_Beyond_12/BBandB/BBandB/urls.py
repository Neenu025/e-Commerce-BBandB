from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from APP1 import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include

urlpatterns = [

    path('admin/', admin.site.urls),


#admin login,logout..user signup,login,otp,logout
    
    path('adminn/', views.admin_login,name='admin'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    path('signup/', views.signupPage, name='signup'),
    path('otp/', views.verify_signup, name='otp'),
    path('category/',views.category, name = 'category'),
    path('addc/',views.add_category,name= 'add_category'),
    path('edit/<int:product_id>/',views.editproduct,name='edit_product'),
    path('product/<int:id>/update/', views.update, name='update'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('customer/<int:customer_id>/block/', views.block_customer, name='block_customer'),
    path('customer/<int:customer_id>/unblock/', views.unblock_customer, name='unblock_customer'),
    path('category/<int:id>/update_category/', views.update_category, name='update_category'),
    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('category/<int:category_id>/edit/', views.editcategory, name='edit_category'),
 

    
#dashboard,customer,order,product
    path('dashboard/', views.dashboard,name='dashboard'),
    path('Customer/',views.customers,name='customer'),
    path('products/',views.product,name='products'),
    path('add/', views.add_product, name='add_product'),

     


#user side
    path('',views.home,name='home'),
    path('login', views.loginPage, name='login'),
    path('logout/',views.logoutPage,name='logout'),
    path('userproduct/',views.userproductpage,name='userproduct'),
    path('verify_otp/',views.verify_signup,name='verify_signup'),
    path('social-auth/', include('social_django.urls', namespace = 'social')),


# app2
    path('', include('SHOPPER.urls')),



]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
