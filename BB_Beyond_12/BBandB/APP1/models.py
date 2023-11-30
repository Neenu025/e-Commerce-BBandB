from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from .manager import UserManager


# Create your models here.


class Customer(AbstractUser):
    username           =   models.CharField(unique=True,null=True,blank=True)
    email              =   models.EmailField(unique=True)
    number             =   models.CharField(max_length=10)
    is_verified        =   models.BooleanField(default=False)
    email_token        =   models.CharField(max_length=100, null=True, blank=True)
    forgot_password    =   models.CharField(max_length=100,null=True, blank=True)
    last_login_time    =   models.DateTimeField(null = True, blank = True)
    last_logout_time   =   models.DateTimeField(null=True,blank=True)
    profile_photo      =   models.ImageField(upload_to='products', null=True, blank=True)
    referral_code      =   models.CharField(max_length=100,null=True, unique=True)
    referral_amount    =   models.IntegerField(default=0)
    wallet_bal         =   models.DecimalField(max_digits=10, decimal_places=2, default=0.00)



    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=[]

    def __str__(self):
        return self.email
    




class Category(models.Model):
    category_name               =     models.CharField(max_length=100, unique=True, blank=False)
    description                 =     models.CharField(max_length=1000,default='')
    image                       =     models.ImageField(upload_to='products', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    category_offer_description  =     models.CharField(max_length=100, blank=True)
    category_offer              =     models.PositiveBigIntegerField(default=0, null=True, blank=True)
    
    


class Product(models.Model):
    # VARIANTS = (
    #     ('None' , 'None'),
    #     ('Type' , 'Type'),
    #     ('Gms' , 'Gms'),
        
    # )
   
    product_name                =     models.CharField(max_length=100, unique=True)
    description                 =     models.CharField(max_length=1000,default='')
    category                    =     models.ForeignKey(Category, on_delete=models.CASCADE)
    stock                       =     models.IntegerField(default=0)
    price                       =     models.IntegerField(default=0)
    image                       =     models.ImageField(upload_to='products', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    product_offer               =     models.PositiveBigIntegerField(default=0,null=True, blank=True)
    deleted                     =     models.BooleanField(default=False)
    # variant                   =     models.CharField(max_length=20,choices=VARIANTS, default=None)

 

# class Slider(models.Model):
#     DISCOUNT_DEAL = (
#         ('HOT DEALS', 'HOT DEALS'),
#         ('New Arrivals', 'New Arrivals'),
#     )

#     Image = models.ImageField(upload_to='media/slider_imgs')
#     Discount_Deal = models.CharField(choices=DISCOUNT_DEAL,max_length=100)
#     SALE = models.IntegerField()
    
#     Discount = models.IntegerField()
   

class Type(models.Model):
    name = models.CharField(max_length=25)




    
