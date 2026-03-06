from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('',views.IndexView.as_view(),name='home'),
    path('requests/',views.RequestsView.as_view(),name='requests'),
    path('konveyer/<uuid:loan_id>/',views.KonveyerView.as_view(),name='konveyer'),
    path('document/<uuid:loan_id>/<str:doct>/',views.document,name="document"),

    # Actions
    path('create_loan/',views.create_request,name='create_loan'),
    path('save_data/',views.save_data,name='save_data'),
    path('add_client/',views.add_client,name='add_client'),
    path('reject/',views.reject,name='reject'),
    path('save_number/',views.save_number,name='save_number'),
    path('delete_number/<int:id>/',views.delete_number,name='delete_number'),
    path('approve/',views.approve,name='approve'),

]
