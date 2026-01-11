from django.urls import path
from . import views

app_name = "accounting"

urlpatterns = [
    path('',views.IndexView.as_view(),name='home'),
    path('history/',views.HistoryView.as_view(),name='history'),
    path('payment/',views.PaymentView.as_view(),name='payment'),
    path('report/',views.ReportView.as_view(),name='report'),
    path('pay/<int:id>/<int:amount>/',views.pay,name='pay'),
    path('done/',views.done,name='done'),
    path('document/<int:id>/<str:doct>/',views.document,name='document'),
    
]