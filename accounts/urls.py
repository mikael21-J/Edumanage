from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/check-identity/', views.check_identity, name='check_identity'),
    path('register/create-password/', views.create_password, name='create_password'),
    path('register/select-ues/', views.select_ues, name='select_ues'),
    path('register/select-teacher-ues/', views.select_teacher_ues, name='select_teacher_ues'),
    path('dashboard/etudiant/', views.dashboard_etudiant, name='dashboard_etudiant'),
    path('dashboard/etudiant/ue/<str:code_ue>/', views.student_ue_detail, name='student_ue_detail'),
    path('dashboard/enseignant/', views.dashboard_enseignant, name='dashboard_enseignant'),
    path('dashboard/enseignant/ue/<str:code_ue>/', views.teacher_evaluations, name='teacher_evaluations'),
    path('dashboard/enseignant/ue/<str:code_ue>/<str:evaluation_type>/', views.teacher_gradebook, name='teacher_gradebook'),
]