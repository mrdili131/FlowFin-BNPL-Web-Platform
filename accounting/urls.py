from django.urls import path
from . import views

app_name = "accounting"

urlpatterns = [
    path('',views.IndexView.as_view(),name='home'),
    path('history/',views.HistoryView.as_view(),name='history'),
    path('payment/',views.PaymentView.as_view(),name='payment'),
    path('report/',views.ReportView.as_view(),name='report'),
    path('payment_history/<str:contract_id>/',views.payment_history,name='payment_history'),
    path('payment_cheque/<int:id>/',views.payment_cheque,name='payment_cheque'),
    path('pay/<uuid:loan_id>/<int:amount>/',views.pay,name='pay'),
    path('done/',views.done,name='done'),
    path('document/<uuid:loan_id>/<str:doct>/',views.document,name='document'),
    
]