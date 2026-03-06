from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from krd.models import Loan, Product, PaymentMonth, Payment
from django.http.response import JsonResponse
from .models import AccountedLoan
from django.utils.decorators import method_decorator
from krd.utils import role_required
from datetime import date
import calendar
from django.db.models import Sum
from django.utils import timezone
from django.db.models import Q
from datetime import datetime


@method_decorator(role_required('accountant'),name="dispatch")
class IndexView(LoginRequiredMixin,View):
    def get(self,request):
        loans = Loan.objects.filter(filial=request.user.filial,status="approved")
        return render(request,'accounting/index.html',{"loans":loans})
    
@method_decorator(role_required('accountant'),name="dispatch")
class HistoryView(LoginRequiredMixin,View):
    def get(self,request):
        loans = AccountedLoan.objects.filter(filial=request.user.filial).order_by("-id")
        return render(request,'accounting/history.html',{"loans":loans})
    
@method_decorator(role_required('accountant'),name="dispatch")
class PaymentView(LoginRequiredMixin,View):
    def get(self,request):
        query = request.GET.get("q")
        try:
            element = AccountedLoan.objects.get(loan__contract_id=query)
            loan = Loan.objects.get(loan_id=element.loan.loan_id)
            return render(request,'accounting/payment.html',{"loan":loan,"q":query})
        except AccountedLoan.DoesNotExist:
            return render(request,'accounting/payment.html',{"q":query})

@method_decorator(role_required('accountant'),name="dispatch")
class ReportView(LoginRequiredMixin,View):
    def get(self,request):
        start_date = request.GET.get("start_date", str(timezone.now().date()))
        end_date = request.GET.get("end_date", str(timezone.now().date()))
        contract_id = request.GET.get("contract_id", "").strip()

        try:
            start_date_valid = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_valid = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            start_date_valid = timezone.now().date()
            end_date_valid = timezone.now().date()
        print(start_date_valid)
        print(end_date_valid)

        payments = PaymentMonth.objects.filter(loan__filial = request.user.filial).filter(
            Q(loan__contract_id__icontains=contract_id)
        )

        if (start_date_valid and end_date_valid):
            payments = payments.filter(
                payment_date__gte=start_date_valid,
                payment_date__lte=end_date_valid
            )
        payments = payments.order_by("-payment_date")
        return render(request,'accounting/report.html',{"payments":payments,"start_date":start_date,"end_date":end_date,"contract_id":contract_id})  
    
@role_required('accountant')
def document(request,loan_id,doct):
    loan = Loan.objects.get(loan_id=loan_id)
    if (doct and doct == "accounting_cheque"):
        return render(request,'accounting/accounting_cheque.html',{"loan":loan})
    
@role_required('accountant')
def payment_history(request,contract_id):
    loan = Loan.objects.get(contract_id=contract_id)
    payments = Payment.objects.filter(loan__contract_id=contract_id).order_by("-id")
    return render(request,'accounting/payment_history.html',{"loan":loan,"payments":payments})

@role_required('accountant')
def payment_cheque(request,id):
    payment = Payment.objects.get(id=id)
    return render(request,'accounting/payment_cheque.html',{"payment":payment})
    

@login_required
def done(request):
    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')

        if(loan_id):
            loan = Loan.objects.get(loan_id=loan_id)
            product = Product.objects.get(id=loan.product.id)
            product.quantity-=1
            product.save()
            loan.status = "done"
            loan.save()
            AccountedLoan( # Accountant is approving
                user=request.user,
                loan = loan,
                filial = request.user.filial
            ).save()
            for exists in PaymentMonth.objects.filter(loan=loan):
                exists.delete()
            for i in range(1,loan.term+1): # Creates monthly payment objects
                month = loan.start_date.month + i
                year = loan.start_date.year + (month-1)//12
                month = (month-1)%12+1
                last_day = calendar.monthrange(year,month)[1]
                day = min(loan.payday,last_day)
                payment_date = date(year,month,day)
                PaymentMonth(
                    loan=loan,
                    month=i,
                    payment=loan.payment,
                    payment_date = payment_date
                ).save()
            return JsonResponse({"status":True,"msg":"Kredit rasmiylashtirildi!"})
        
@role_required('accountant')
def pay(request,loan_id,amount):
    loan = Loan.objects.get(loan_id=loan_id)
    loan.pay(amount)
    return JsonResponse({"status":True})