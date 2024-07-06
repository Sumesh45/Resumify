
from django.urls import path
from . import views

app_name= "parser"

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name = 'about'),
    path('contact/', views.contact, name = 'contact'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('success/', views.upload_success, name='upload_success'),
    path('view_resume/', views.view_resume, name='view_resume'),
    path('view_all/', views.view_all, name='view_all'),
    path('delete/<int:id>', views.delete , name='delete'),
    path('auth/', views.auth, name='auth'),
    path('logout/', views.logout_view, name='logout')
]