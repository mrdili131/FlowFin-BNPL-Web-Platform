from django.shortcuts import render, redirect
from .models import *
from django.views import View
from django.http.response import JsonResponse
import json
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .utils import role_required
from django.utils.decorators import method_decorator
from django.db.models import Q

@method_decorator(role_required('creditor'),name="dispatch")
class IndexView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,'creditor/index.html')

@method_decorator(role_required('creditor'),name="dispatch")
class KonveyerView(LoginRequiredMixin,View):
    def get(self,request,id):
        loan = Loan.objects.get(id=id)
        products = Product.objects.filter(filial=request.user.filial,is_available=True)
        if loan.product_price and loan.rate and loan.product.price:
            loan.amount = (loan.product_price/100*loan.rate)+loan.product_price
            loan.save()
        return render(request,'creditor/konveyer.html',{"loan":loan,"products":products})
    
@method_decorator(role_required('creditor'),name="dispatch")
class RequestsView(LoginRequiredMixin,View):
    def get(self,request):
        query = request.GET.get("q","").strip()
        if query:
            loans = Loan.objects.filter(filial=request.user.filial).filter(
            Q(client__full_name__icontains=query) |
            Q(client__passport_pinfl__icontains=query) |
            Q(contract_id__icontains=query)
        ).order_by("-created_at")
            return render(request,'creditor/history.html',{"loans":loans,"q":query})
        else:
            loans = Loan.objects.filter(filial=request.user.filial).order_by("-created_at")
        return render(request,'creditor/history.html',{"loans":loans,"q":query})
                

@role_required('creditor')
def document(request,id,doct):
    loan = Loan.objects.get(id=id)
    if (doct and doct == "graphic"):
        return render(request,"creditor/graphic.html",{"loan":loan})
    elif (doct and doct == "agreement"):
        return render(request,"creditor/agreement.html",{"loan":loan})
    elif (doct and doct == "request"):
        return render(request,"creditor/ariza.html",{"loan":loan})
    elif (doct and doct == "information"):
        return render(request,"creditor/information.html",{"loan":loan})
    elif (doct and doct == "contract"):
        return render(request,"creditor/contract.html",{"loan":loan})
    elif (doct and doct == "order"):
        return render(request,"creditor/order.html",{"loan":loan})
    else:
        return redirect('home')




# Shortcuts
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
            if loan.status not in ["done","rejected","approved","paid"]:
                product = Product.objects.get(id=int(data["product"]))
                loan.total_amount = float(data["total_amount"] or 0)
                loan.product = product
                loan.product_price = product.price
                loan.rate = int(data["loan_rate"])
                loan.monthly_income = int(data["monthly_income"])
                loan.monthly_spending = int(data["monthly_spending"])
                loan.scoring = int(data["scoring"])
                loan.work_type = data["work_type"]
                loan.loans = int(data["loans"])
                loan.monthly_loan_payment = int(data["monthly_loan_payment"])
                loan.end_date = datetime.strptime(data["loan_end_date"], "%Y-%m-%d").date()
                loan.payday = int(data["payday"])
                loan.fine = int(data["loan_fine"])

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
            else:
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
    
@login_required
def delete_number(request,id):
    PhoneNumber.objects.get(id=id).delete()
    return JsonResponse({"status":True})
    
@login_required
def approve(request):
    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')

        if(loan_id):
            loan = Loan.objects.get(id=loan_id)
            if (loan.status == "rejected"):
                return JsonResponse({"status":False,"msg":"Ushbu hujjat rad etilgan!"})
            elif(loan.status == "done"):
                return JsonResponse({"status":False,"msg":"Ushbu hujjat avvalroq tasdiqlangan!"})
            elif(loan.status == "paid"):
                return JsonResponse({"status":False,"msg":"Ushbu shartnoma yakunlangan!"})
            elif(loan.status == "approved"):
                return JsonResponse({"status":False,"msg":"Ushbu shartnoma yakunlangan!"})
            else:
                loan.status = "approved"
                loan.save()
                return JsonResponse({"status":True,"msg":"Mijozni buxgalteriyaga jo'nating!"})
            
             
@login_required
def reject(request):
    if request.method == "POST":
        id = request.POST.get("id")
        loan = Loan.objects.get(id=id)
        if loan.status == "rejected":
            return JsonResponse({"status":False,"msg":"Bu shartnoma rad etilgan"})
        elif loan.status == "done":
            return JsonResponse({"status":False,"msg":"Bu shartnoma bajarilgan"})
        elif loan.status == "paid":
            return JsonResponse({"status":False,"msg":"Bu shartnoma tugatilgan"})
        else:
            loan.status = "rejected"
            loan.save()
            return JsonResponse({"status":True,"msg":"Rad etildi"})