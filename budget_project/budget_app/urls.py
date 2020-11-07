from django.urls import path,include
from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', auth_views.LoginView.as_view(),name='login'),
    path('app',views.index,name='index'),
    path('add_item',views.add_item,name='add item'),
    path('delete_item<part_id>$', views.delete_item, name='delete_item'),
    path('accounts/',include('django.contrib.auth.urls')),
    path('logout',views.logout_view,name='logout'),
    path('sign_up',views.sign_up,name="sign up")
]