from django.db import models
from users.models import User, Filial
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
import uuid

gender = [
    ('male','Erkak'),
    ('female','Ayol')
]

status = [
    ('done','berildi'),
    ('approved', 'tasdiqlandi'),
    ('rejected',"rad etildi"),
    ('pending','jarayonda'),
    ('paid','yopilgan')
]

class Client(models.Model):
    # Client's data
    first_name = models.CharField(max_length=100,default="")
    last_name = models.CharField(max_length=100,default="")
    middle_name = models.CharField(max_length=100,default="")
    full_name = models.CharField(max_length=250,default="")
    birth_date = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=30,choices=gender,default='male')

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
        if self.full_name:
            return self.full_name
        else:
            return "NULL"     
        

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    filial = models.ForeignKey(Filial,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    is_available = models.BooleanField(default=False)

    def save(self,*args,**kwargs):
        if self.quantity <= 0:
            self.is_available = False
        super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.name} | {self.price} so'm"
        
    
class Loan(models.Model):
    # Linkings
    loan_id = models.UUIDField(default=uuid.uuid4,primary_key=True,unique=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client,on_delete=models.SET_NULL,null=True,blank=True)
    contract_id = models.CharField(max_length=50,default="",unique=True)

    # Credit essentials
    payment = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    total_amount = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    term = models.IntegerField(default=0)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True,blank=True)
    product_price = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    rate = models.PositiveIntegerField(default=0)
    fine = models.PositiveIntegerField(default=1)

    # Client data
    monthly_income = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    monthly_spending = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    work_type = models.CharField(max_length=50,null=True,blank=True)

    # Loans
    loans = models.IntegerField(default=0)
    monthly_loan_payment = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    scoring = models.IntegerField(default=0)

    # Dates
    payday = models.PositiveIntegerField(default=now().day)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(auto_now_add=True)

    # Other data
    description =  models.TextField(null=True,blank=True)
    status = models.CharField(choices=status,default="pending",max_length=50)
    filial = models.ForeignKey(Filial,on_delete=models.SET_NULL,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self,*args,**kwargs):
        if (self.loan_id):
            self.contract_id = f"99{str(self.loan_id)[:6]}"
        if (self.product_price == 0 and self.product):
            self.product_price == self.product.price
        if (
            self.product and
            self.product.price and
            self.start_date and
            self.rate and
            self.end_date and
            self.status not in ["done","rejected","approved","paid"]
        ):
            months = (self.end_date.year - self.start_date.year) * 12 + (self.end_date.month - self.start_date.month)
            if months <= 0:
                months = 1
            amount = self.product_price + (self.product_price * self.rate /100)
            self.total_amount = amount
            self.payment = round(amount / months)
            self.term = months
        super().save(*args,**kwargs)

    def pay(self,payment_amount):
        if payment_amount > self.total_amount:
            payment_amount = self.total_amount
            self.status = 'paid'
            self.save()
            Payment(loan=self,amount=payment_amount).save()
            return payment_amount
        left = payment_amount
        months = self.payment_months.order_by("month")
        for i in months:
            if left <= 0:
                break
            due = (i.payment + i.penalty) - i.paid_amount

            if due <= 0:
                continue

            pay = min(due,left)
            i.paid_amount += pay
            left -= pay

            if i.paid_amount >= i.payment + i.penalty:
                i.is_paid = True
                i.paid_date = now().date()
            i.save()
        Payment(loan=self,amount=payment_amount).save()
        return payment_amount - left

    def __str__(self):
        return f"ID: {self.loan_id} | At: {self.created_at.ctime()}"
        
    

class PaymentMonth(models.Model):
    loan = models.ForeignKey(Loan,on_delete=models.CASCADE,related_name='payment_months')
    month = models.PositiveIntegerField(default=0)
    total = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    payment = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    penalty = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    paid_amount = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    is_paid = models.BooleanField(default=False,null=True,blank=True)
    payment_date = models.DateField(null=True,blank=True)
    paid_date = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    @property
    def left_amount(self):
        return (self.payment + self.penalty) - self.paid_amount
            

    def save(self,*args,**kwargs):
        if (self.payment_date and self.is_paid != True):
            if now().date() > self.payment_date:
                days = (now().date() - self.payment_date).days
                self.penalty = (self.loan.payment/100*self.loan.fine)*days
        super().save(*args,**kwargs)


    def __str__(self):
        return f'{self.loan.contract_id}\'s {self.month}th payment = {self.payment}'
    
class Payment(models.Model):
    loan = models.ForeignKey(Loan,on_delete=models.SET_NULL,null=True,blank=True,related_name="payments")
    amount = models.DecimalField(max_digits=10,decimal_places=0,default=0)
    paid_date = models.DateField(auto_now_add=True,null=True,blank=True)



class PhoneNumber(models.Model):
    number = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    client = models.ForeignKey(Client,on_delete=models.SET_NULL,null=True,blank=True,related_name="numbers")

    def __str__(self):
        return f'{self.name} | {self.number}'