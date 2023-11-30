from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import cache_control,never_cache
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .models import Customer,Product,Category
from django.contrib import messages,auth
from django.db import IntegrityError
from django.db.models import F,Sum
from SHOPPER.models import *
from decimal import Decimal, InvalidOperation

from PIL import Image

import string,random
import json 
import uuid
import psycopg2
import re
import secrets
import smtplib




@never_cache
def loginPage(request):
    context = {
        'messages': messages.get_messages(request)
    }

    # Check if the user is already logged in
    if 'email' in request.session and 'otp' in request.session:
        request.session.flush()
        return redirect('login')
    
    if 'email' in request.session:
        return redirect('welcome')
    
    if 'admin' in request.session:
        return redirect('admin')
    
    # Process login attempt
    if request.method == 'POST' and 'google-oauth2' not in request.POST :
        email = request.POST.get('email')
        password = request.POST.get('pass')

        # Check if both email and password are provided
        if not email or not password:
            messages.error(request, "Please provide both email and password.")
            return render(request, 'login.html', context)

        try:
            user = authenticate(request, email=email, password=password)

            if user is not None:
                request.session['email'] = email
                login(request, user)
                return redirect('welcome')
            else:
                messages.error(request, "Username or password is incorrect.")
                return render(request, 'login.html', context)
            
        except IntegrityError as e:
            if 'google-oauth2' in request.POST:
                messages.error(request, "IntegrityError: This email is already in use.")
                return render(request, 'login.html', context)

    else:
        return render(request, 'login.html', context)
        


@never_cache
def signupPage(request):
    if 'email' in request.session:
        return redirect('welcome')

    if request.method == 'POST':
        email     =    request.POST.get('email')
        number    =    request.POST.get('number')
        username  =    request.POST.get('username')
        pass1     =    request.POST.get('password1')
        pass2     =    request.POST.get('password2')
        refferal  =    request.POST.get('refferal')

    
        if not email or not username or not pass1 or not pass2 or not number:
            messages.error(request, 'Please input all the details.')
            return redirect('signup')

        if pass1 != pass2:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')

        if not validate_email(email):
            messages.error(request, 'Please enter a valid email address.')
            return redirect('signup')

        if Customer.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('signup')
        
        if len(number) < 10:
            messages.error(request, 'Mobile number should have at least 10 digits.')
            return redirect('signup')
        
        if not username.strip():
            messages.error(request, 'Username can not be empty or contain only spaces')
            return redirect('signup')
        
        


        message = generate_otp()
        sender_email = "roffyjose@gmail.com"
        receiver_mail = email
        password = "vapgdhbgkydkecql"


        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_mail, message)

        except smtplib.SMTPAuthenticationError:
            messages.error(request, 'Failed to send OTP email. Please check your email configuration.')
            return redirect('signup')
        
        referral_codes = generate_referral_code()

        try:
            user = Customer.objects.create_user(username=username, password=pass1, email=email,number=number,referral_code=referral_codes)
            user.save()

            request.session['email'] =  email
            request.session['otp']   =  message
            messages.success (request, 'OTP is sent to your email')
            return redirect('verify_signup')
    
        except IntegrityError:
            messages.error(request, 'An account with this email already exists.')
            return redirect('signup')

    return render(request, 'signup.html')

def generate_otp(length = 6):
    return ''.join(secrets.choice("0123456789") for i in range(length)) 

def generate_referral_code():
    letters = string.ascii_letters + string.digits
    referral_code = ''.join(random.choice(letters) for i in range(10))
    return referral_code


def validate_email(email):
    return '@' in email and '.' in email

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def verify_signup(request):
    context = {
        'messages': messages.get_messages(request)
    }
    if request.method == "POST":
        
        user      =  Customer.objects.get(email=request.session['email'])
        x         =  request.session.get('otp')
        OTP       =  request.POST['otp']
      
        if OTP == x:
            user.is_verified = True
            user.save()
            del request.session['email'] 
            del request.session['otp']
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth.login(request,user)
            messages.success(request, "Signup successful!")
            device_id = request.COOKIES.get('device_id')
            if device_id:
                wish_list_items = Wishlist.objects.filter(device=device_id)
                cart_items = Cart.objects.filter(device=device_id)

                for item in wish_list_items:
                    item.user = user
                    item.save()

                for item in cart_items:
                    item.user = user
                    item.save()
            response = redirect('welcome')
            response.delete_cookie('device_id')
            return response
        else:
            user.delete()
            messages.info(request,"invalid otp")
            del request.session['email']
            return redirect('signup')
        return redirect('login')
        
    return render(request,'verify_otp.html',context)

def is_valid_image(file):
    try:
        image = Image.open(file)

        allowed_formats = ['JPEG', 'JPG', 'PNG']
        if image.format.upper() not in allowed_formats:
            raise ValidationError("Invalid image format. Please upload a JPEG, JPG, or PNG file.")
    except IOError:
        raise ValidationError("Not a valid image file. Please upload a valid image.")

    except Exception as e:
        raise ValidationError("Error processing the image file: {}".format(str(e)))


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def welcome(request):
   
    categories =  Category.objects.all()
    for category in categories:
        category.product_count = category.product_set.count()
    context    =  {
            'categories':categories
        }
    return render(request,'home_new/index.html',context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def home(request):
   
    categories =  Category.objects.all()
    for category in categories:
        category.product_count = category.product_set.count()
    context    =  {
            'categories':categories
        }
    return render(request,'home.html',context)
   

@never_cache    
def logoutPage(request):
    if 'email' in request.session:
        request.session.flush()
    logout(request)
    return redirect('welcome')

@never_cache    
def about(request):
    return render(request,'home_new/about.html')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def admin_login(request):
    if 'email' in request.session:
        return redirect('welcome')
    elif 'admin' in request.session:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            username      =  request.POST.get('username')
            pass1         =  request.POST.get('pass')
            user          =  authenticate(request,username=username,password = pass1)

            if user is not None and user.is_superuser:
                login(request,user)
                request.session['admin']=username
                return redirect('dashboard')
            else:
                messages.error(request,"username or password is not same")
                return render(request, 'admin_login.html') 
        else:
             return render (request,'admin_login.html')
        
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def dashboard(request):
    orders = Order.objects.order_by('-id')[:5]
    labels = []
    data = []
    for order in orders:
        labels.append(str(order.id))
        data.append(order.amount)
    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    }

    if 'admin' in request.session:
        return render(request,'dashboard.html',context)
    else:
        return redirect('admin')



@never_cache   
def admin_logout(request):
    if 'admin' in request.session:
        request.session.flush()
    logout(request)
    return redirect('admin')


@never_cache 
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def customers(request):
    if 'admin' in request.session:    
        customer_list =  Customer.objects.filter(is_staff=False).order_by('id')

        paginator = Paginator(customer_list,10)  

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
        }
        return render(request, 'customer.html', context)
    else:
        return redirect('admin')

      

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def product(request):
    if 'admin' in request.session:
        
        products = Product.objects.all().order_by('id')
               
        paginator = Paginator(products, 3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
           
        }
        return render(request, 'products.html', context)
    else:
        return redirect('admin')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def add_product(request):
    if 'admin' in request.session:
        if request.method == 'POST':
            product_name   =  request.POST.get('product_name')
            description    =  request.POST.get('description')
            category_name  =  request.POST.get('category')
            category       =  get_object_or_404(Category, category_name=category_name) 
            stock          =  request.POST.get('stock')
            price          =  request.POST.get('price')
            offer          =  request.POST.get('offer')
            image          =  request.FILES.get('image')  
            images         =  request.FILES.getlist('mulimage')
            
           
            if not (product_name and description and category_name and price and image and stock):
                error_message = "Please fill in all the required fields."


            elif not product_name.strip():
                error_message = "Product name cannot be empty or contain only spaces."

            elif not description.strip():
                error_message = "Description cannot be empty or contain only spaces."

            elif Product.objects.filter(product_name=product_name).exists():
                error_message = "A product with the same name already exists."
                       
            elif not stock.isdigit() or int(stock) < 0:
                error_message = "Stock value must be a non-negative integer."
            
            elif image:
                allowed_formats = ['image/jpeg', 'image/jpg', 'image/png']
                if image.content_type not in allowed_formats:
                    error_message = "Only JPG, JPEG, and PNG format images are allowed."
                    # context = {'category': category, 'error_message': 'Only JPG, JPEG, and PNG format images are allowed.'}
                    # return render(request, 'add_product.html', context)
                    
            elif not offer:
                    offer = '0'       
            try:
                    offer = Decimal(offer)
            except InvalidOperation:
                    error_message = "Offer must be a numeric value. Enter 0 if no offer applicable "
           



            if 'error_message' in locals():
                categories = Category.objects.all()
                context = {
                    'categories': categories,
                    'error_message': error_message,
                    'product_name': product_name,
                    'description': description,
                    'category_name': category_name,
                    'stock': stock,
                    'price': price,
                    'offer': offer,
                    'image': image,
        
                }
                return render(request, 'add_product.html', context)
            

            
            product = Product()
            product.product_name   =  product_name
            product.description    =  description
            product.category       =  category 
            product.stock          =  stock 
            product.price          =  price
            product.product_offer  =  offer
            product.image          =  image
            product.save()

         
            return redirect('products') 

        categories = Category.objects.all()
        context = {'categories': categories}
        return render(request, 'add_product.html', context)
    else:
        return redirect('admin')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache    
def userproductpage(request):
  
    results = Product.objects.filter(deleted=False).order_by('id')
    categories = Category.objects.all()

    total_product_count = Product.objects.count()
    selected_categories = request.GET.getlist('category')

    if selected_categories:
        results_by_category = {}

        for category_name in selected_categories:
            category_results = results.filter(category__category_name=category_name)
            
            sort_option = request.GET.get('sort') 

            if sort_option == 'high':
                category_results = category_results.order_by(F('price').desc())
            elif sort_option == 'all':
                category_results = category_results.order_by('price')

            results_by_category[category_name] = category_results

   
        results = [result for category_results in results_by_category.values() for result in category_results]
    

    paginator = Paginator(results, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for product in page_obj:
        discounted_price = None
        if product.category.category_offer:
            discounted_price = product.price - product.category.category_offer
        product.discounted_price = discounted_price

        offer_price = None
        if product.product_offer:
            offer_price        =  product.price -(product.price * product.product_offer/100)
        product.offer_price    =  offer_price
      
         

    context = {
        'page_obj'             : page_obj,
        'selected_categories'  : selected_categories,
        'total_product_count'  : total_product_count,
        'categories'           : categories,
    }

    device_id = request.COOKIES.get('device_id')
    if not device_id:
        device_id = uuid.uuid4()
        response = render(request, "userproduct.html", context)
        response.set_cookie('device_id', device_id)
        return response
    return render(request, 'userproduct.html', context)


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def category(request):
    if 'admin' in request.session:
        categories = Category.objects.all().order_by('id')
        
        
        paginator = Paginator(categories, per_page=3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'categories': page_obj,
        }
        return render(request, 'category.html', context)
    else:
        return redirect('admin')
    


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache          
def add_category(request):
    if 'admin' in request.session:
        if request.method  == 'POST':
            category_name       =   request.POST['category_name']
            description         =   request.POST['description']
            image               =   request.FILES.get('image')
            offer_description   =   request.POST['offer_details']
            offer_price         =   request.POST.get('offer_price','')

            if not category_name.strip():
                return render(request, 'add_category.html', {'error_message': 'Category name can not be empty or contain only spaces'})
            
            if not description.strip():
                return render(request, 'add_category.html', {'error_message': 'Description can not be empty or contain only spaces'})

            if Category.objects.filter(category_name=category_name).exists():
                return render(request, 'add_category.html', {'error_message': 'Category with this name already exists.'})
            
            if image:
                allowed_formats = ['image/jpeg', 'image/jpg', 'image/png']
                if image.content_type not in allowed_formats:
                    return render(request, 'add_category.html',{'error_message': 'Only JPG, JPEG, and PNG format images are allowed.'})

            if offer_price:
                    offer_price = Decimal(offer_price)
            else:
                    offer_price = '0'        
                    
            try:
                category = Category.objects.create(
                    category_name                =  category_name,
                    description                  =  description,
                    image                        =  image,
                    category_offer_description   =  offer_description,
                    category_offer               =  offer_price
                )
                category.save() 
                return redirect('category')
            except IntegrityError:
                return render(request, 'add_category.html', {'error_message': 'An error occurred while adding the category. Please try again.'})
 
         
        return render(request, 'add_category.html') 
    else:
        return redirect ('admin')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def editproduct(request, product_id):
    if 'admin' in request.session:
        try:
            product = Product.objects.get(id=product_id)           

        except Product.DoesNotExist:
        
            return render(request, 'product_not_found.html')
        
        categories = Category.objects.all()
        selected_category = product.category.category_name if product.category else None

        context = {
            'product'    : product,
            'categories' : categories,
            'selected_category': selected_category,
        }

        return render(request, 'editproduct.html', context)
    else:
        return redirect('admin')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def update(request, id):
    product = Product.objects.get(id=id)
         
    if request.method == 'POST':
        product.product_name    =   request.POST.get('product_name')
        product.description     =   request.POST.get('description')
        category_name           =   request.POST.get('category')
        category                =   Category.objects.get(category_name=category_name)
        product.category        =   category
        product.stock           =   request.POST.get('stock')
        product.price           =   request.POST.get('price')
        product.product_offer   =   request.POST.get('offer')
        image                   =   request.FILES.get('image')
        images                  =   request.FILES.getlist('mulimage')
        

        categories = Category.objects.all()
        selected_category = product.category.category_name if product.category else None

     

        if image:
            allowed_formats = ['image/jpeg', 'image/jpg', 'image/png']
            if image.content_type not in allowed_formats:
                context = {'product': product,'categories' : categories,'selected_category':selected_category, 'error_message': 'Only JPG, JPEG, and PNG format images are allowed.'}

                return render(request, 'editproduct.html', context)

        if Product.objects.exclude(id=product.id).filter(product_name=product.product_name).exists():
            context = {'product': product,'categories' : categories,'selected_category':selected_category, 'error_message': 'Product with this name already exists.'}
        
        if ' ' in product.product_name:
            context = {'product': product,'categories' : categories,'selected_category':selected_category, 'error_message': 'Enter a valid name, avoid keeping only spaces.'}
            return render(request, 'editproduct.html', context)
        
        if ' ' in product.description :
            context = {'product': product,'categories' : categories,'selected_category':selected_category,'error_message': 'Enter a valid description, avoid keeping only spaces.'}
            return render(request, 'editproduct.html', context)
        
        if not product.product_offer :
             context = {'product': product,'categories' : categories,'selected_category':selected_category, 'error_message': 'Offer price cannot be empty. If not applicable, enter 0.'}
             print(selected_category)
             return render(request, 'editproduct.html', context)
           
        
    
        
        product.product_name = request.POST.get('product_name')
        product.description = request.POST.get('description')
        image = request.FILES.get('image')
        product.product_offer = request.POST.get('offer', '')
        category_name         = request.POST.get('category')
        product.category      = category
        
        if image:
            product.image = image

        
        product.save()

        print(selected_category)
        
            
        return redirect('products') 
    else:
        context = {
            'product': product,
            'categories': categories,
            'selected_category': selected_category,

        }
    return render(request, 'products.html', context)
         


@user_passes_test(lambda u: u.is_staff, login_url='admin')
def delete_product(request, product_id):
    try:
        # products = Product.objects.filter(deleted=False)
        product = Product.objects.get(id=product_id)
        product.deleted = True
        product.save()
        
    except Product.DoesNotExist:
        return render(request, 'product_not_found.html')

    
    return redirect('products')


def restore_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.deleted = False  # Set the deleted field back to False
        product.save()
        
    except Product.DoesNotExist:
        return render(request, 'product_not_found.html')

    return redirect('products')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def editcategory(request, category_id):
    if 'admin' in request.session:
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return render(request, 'category_not_found.html')
        
        context = {'category': category}
        return render(request, 'edit_category.html', context)
    else:
        return redirect('admin')


def is_valid_image(file):
    allowed_formats = ['jpeg', 'jpg', 'png']
    return file.name.lower().endswith(tuple(allowed_formats))



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_category(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return render(request, 'category_not_found.html')

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        offer_price = request.FILES.get('offer_price')


        if image:
            allowed_formats = ['image/jpeg', 'image/jpg', 'image/png']
            if image.content_type not in allowed_formats:
                context = {'category': category, 'error_message': 'Only JPG, JPEG, and PNG format images are allowed.'}
                return render(request, 'edit_category.html', context)
        
     
        if Category.objects.exclude(id=category.id).filter(category_name=category_name).exists():
            context = {'category': category, 'error_message': 'Category with this name already exists.'}
            return render(request, 'edit_category.html', context)
        
        if ' ' in category_name:
            context = {'category': category, 'error_message': 'Enter a valid name, avoid keeping only spaces.'}
            return render(request, 'edit_category.html', context)
        
        if ' ' in description:
            context = {'category': category, 'error_message': 'Enter a valid description, avoid keeping only spaces.'}
            return render(request, 'edit_category.html', context)
        
        if not offer_price:
            context = {'category': category, 'error_message': 'Offer price cannot be empty. If not applicable, enter 0.'}
            return render(request, 'edit_category.html', context)
        
        

        
        category.category_name = category_name
        category.description = request.POST.get('description')
        image = request.FILES.get('image')
        category.category_offer_description = request.POST.get('offer_details')
        category.category_offer = request.POST.get('offer_price', '')
        if image:
            category.image = image

        category.save()
        return redirect('category')

    context = {'category': category}
    return render(request, 'edit_category.html', context)



def delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return render(request, 'category_not_found.html')

    category.delete()

    categories = Category.objects.all()
    context = {'categories': categories}

    return redirect('category')


def unblock_customer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except ObjectDoesNotExist:
        return redirect('customer')  
    
    customer.is_active = not customer.is_active
    customer.save()

    return redirect('customer')


def block_customer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return redirect('customer')  
    customer.is_active = False
    customer.save()
    return redirect('customer')


