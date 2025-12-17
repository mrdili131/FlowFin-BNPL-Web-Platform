from django.shortcuts import render, redirect
from .models import *
from django.views import View
from django.http.response import JsonResponse
import json
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

class IndexView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,'index.html')
    
class KonveyerView(LoginRequiredMixin,View):
    def get(self,request,id):
        loan = Loan.objects.get(id=id)
        products = Product.objects.filter(filial=request.user.filial,is_available=True)
        if loan.product_price and loan.rate and loan.product.price:
            loan.amount = (loan.product_price/100*loan.rate)+loan.product_price
            loan.save()
        return render(request,'konveyer.html',{"loan":loan,"products":products})
    
@login_required
def create_request(request):
    newloan = Loan(
        user = request.user,
        filial = request.user.filial
    )
    newloan.save()
    return redirect('konveyer',id=newloan.id)

def timify(data):
    from datetime import date
    if str(data)!= '' and len(str(data)) == 10:
        time = date(int(str(data).split('-')[0]),int(str(data).split('-')[1]),int(str(data).split('-')[2]))
        return time
    else:
        return date(2025,1,1)

@login_required
def save_data(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        id = request.POST.get("id")
        if data and id:
            loan = Loan.objects.get(id=id)
            product = Product.objects.get(id=int(data["product"]))
            loan.amount = float(data["amount"])
            loan.product = product
            loan.product_price = product.price
            loan.rate = int(data["loan_rate"])
            loan.monthly_income = int(data["monthly_income"])
            loan.monthly_spending = int(data["monthly_spending"])
            loan.scoring = int(data["scoring"])
            loan.work_type = data["work_type"]
            loan.end_date = datetime.strptime(data["loan_end_date"], "%Y-%m-%d").date()

            client, newclient = Client.objects.update_or_create(
                passport_pinfl = data["client_pinfl"],
                defaults={
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "middle_name": data["middle_name"],
                "gender": data["gender"],
                "passport_serial": data["passport_serial"],
                "passport_got_date": timify(data["passport_got_date"]),
                "passport_expiry_date": timify(data["passport_expiry_date"]),
                "passport_got_region": data["passport_got_region"],
                "current_address": data["current_address"],
                "birth_date": timify(data["birth_date"]),
                "gov_address": data["gov_address"],
                "location": data["location"],
                "description": data["description"],
                "filial": request.user.filial
                }
            )
            if loan.client is None:
                newclient = Client.objects.get(passport_pinfl=data["client_pinfl"])
                loan.client = newclient
                loan.save()
                return JsonResponse({"status":True})
            loan.client = client
            loan.save()
            return JsonResponse({"status":True})
    
@login_required
def add_client(request):
    if request.method == "POST":
        passport_pinfl = request.POST.get("pinfl")
        id = request.POST.get("id")
        loan = Loan.objects.get(id=id)
        try:
            client = Client.objects.get(passport_pinfl=passport_pinfl)
            loan.client = client
            loan.save()
            return JsonResponse({"status":True,"msg":"Mijoz topildi !"})
        except Client.DoesNotExist:
            loan.client = None
            return JsonResponse({"status":False, "msg":"Mijoz topilmadi"})
        
@login_required
def reject(request):
    if request.method == "POST":
        id = request.POST.get("id")
        loan = Loan.objects.get(id=id)
        if loan.status == "rejected":
            return JsonResponse({"status":False,"msg":"Bu shartnoma rad etilgan"})
        else:
            loan.status = "rejected"
            loan.save()
            return JsonResponse({"status":True,"msg":"Rad etildi"})


@login_required
def save_number(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        loan_id = request.POST.get('loan')
        name = request.POST.get('desc')
        loan = Loan.objects.get(id=loan_id)
        client_obj = Client.objects.get(id=loan.client.id)
        if (number and loan_id):
            num = PhoneNumber(
                number = number,
                name = name,
                client = client_obj
            )
            num.save()
            numbers = PhoneNumber.objects.filter(client_id=client_obj.id).order_by("id")
            nums = {}
            for i in numbers:
                nums[i.name] = i.number
            return JsonResponse({"status":True,"numbers":nums})
        return JsonResponse({"status":False})