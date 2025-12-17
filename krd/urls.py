from django.urls import path
from . import views

urlpatterns = [
    path('',views.IndexView.as_view(),name='home'),
    path('requests/',views.RequestsView.as_view(),name='requests'),
    path('konveyer/<int:id>/',views.KonveyerView.as_view(),name='konveyer'),
    path('create_loan/',views.create_request,name='create_loan'),
    path('save_data/',views.save_data,name='save_data'),
    path('add_client/',views.add_client,name='add_client'),
    path('reject/',views.reject,name='reject'),
    path('save_number/',views.save_number,name='save_number'),
    path('approve/',views.approve,name='approve')
]
