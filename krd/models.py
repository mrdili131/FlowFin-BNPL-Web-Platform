from django.db import models
from users.models import User, Filial
from django.core.validators import MinValueValidator, MaxValueValidator

gender = [
    ('male','Erkak'),
    ('female','Ayol')
]

status = [
    ('done','berildi'),
    ('rejected',"rad etildi"),
    ('pending','jarayonda'),
    ('paid','yopilgan')
]

class Client(models.Model):
    # Client's data
    first_name = models.CharField(max_length=100,null=True,blank=True)
    last_name = models.CharField(max_length=100,null=True,blank=True)
    middle_name = models.CharField(max_length=100,null=True,blank=True)
    full_name = models.CharField(max_length=250,null=True,blank=True)
    birth_date = models.DateField(null=True,blank=True)
    gender = models.CharField(choices=gender,default='male')

    # Passport data
    passport_serial = models.CharField(max_length=9,null=True,blank=True)
    passport_pinfl = models.CharField(max_length=14,unique=True,null=True,blank=True)
    passport_got_date = models.DateField(null=True,blank=True)
    passport_expiry_date = models.DateField(null=True,blank=True)
    passport_got_region = models.CharField(max_length=100,null=True,blank=True)

    # Address
    current_address = models.CharField(max_length=100,null=True,blank=True)
    gov_address = models.CharField(max_length=100,null=True,blank=True)
    location =  models.CharField(max_length=250,null=True,blank=True)

    # Other data
    description = models.TextField(null=True,blank=True)
    filial = models.ForeignKey(Filial,on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    def save(self,*args,**kwargs):
        parts = filter(None,[self.last_name,self.first_name,self.middle_name])
        self.full_name = " ".join(parts)
        super().save(*args,**kwargs)

    def __str__(self):
        if self.first_name:
            return self.first_name
        else:
            return "No name"
        
class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    filial = models.ForeignKey(Filial,on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    is_available = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} {self.price}"
    
class Loan(models.Model):
    # Linkings
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client,on_delete=models.SET_NULL,null=True,blank=True)
    contract_id = models.CharField(max_length=50,null=True,blank=True)

    # Credit essentials
    amount = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True,blank=True)
    product_price = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    rate = models.IntegerField(default=0,null=True,blank=True)

    # Client data
    monthly_income = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    monthly_spending = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    work_type = models.CharField(max_length=50,null=True,blank=True)

    # Loans
    loans = models.IntegerField(default=0)
    monthly_loan_payment = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    scoring = models.IntegerField(default=0)

    # Dates
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(auto_now_add=True)

    # Other data
    description =  models.TextField(null=True,blank=True)
    status = models.CharField(choices=status,default="pending",max_length=50)
    filial = models.ForeignKey(Filial,on_delete=models.SET_NULL,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str__(self):
        return f"{self.id} | {self.amount} | {self.created_at.ctime()}"


        

class PhoneNumber(models.Model):
    number = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    client = models.ForeignKey(Client,on_delete=models.SET_NULL,null=True,blank=True,related_name="numbers")

    def __str__(self):
        return f'{self.name} {self.number}'