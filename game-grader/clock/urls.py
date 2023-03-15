from django.urls import path
from django.urls import path, re_path, include

from . import views

urlpatterns = [
    path('<int:id>', views.index, name='clock'),
    # re_path(r'', include('django_private_chat2.urls',
    #         namespace='django_private_chat2_clock')),
]
