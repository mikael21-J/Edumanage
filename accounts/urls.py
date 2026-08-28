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
    path('dashboard/etudiant/requetes/', views.student_requetes, name='student_requetes'),
    path('dashboard/etudiant/ue/<str:code_ue>/requete/', views.student_submit_requete, name='student_submit_requete'),
    path('dashboard/enseignant/', views.dashboard_enseignant, name='dashboard_enseignant'),
    path('dashboard/enseignant/requetes/', views.teacher_requetes, name='teacher_requetes'),
    path('dashboard/enseignant/requetes/<int:requete_id>/', views.teacher_requete_detail, name='teacher_requete_detail'),
    path('dashboard/enseignant/ue/<str:code_ue>/', views.teacher_evaluations, name='teacher_evaluations'),
    path('dashboard/enseignant/ue/<str:code_ue>/pv/', views.teacher_pv, name='teacher_pv'),
    path('dashboard/enseignant/ue/<str:code_ue>/<str:evaluation_type>/', views.teacher_gradebook, name='teacher_gradebook'),
    path('dashboard/admin-cellule/', views.dashboard_admin_cellule, name='dashboard_admin_cellule'),
    path('dashboard/admin-cellule/pv/<int:pv_id>/', views.admin_pv_detail, name='admin_pv_detail'),
    path('dashboard/admin-cellule/gestion/<str:resource>/', views.admin_resource, name='admin_resource'),
    path('dashboard/admin-cellule/gestion/<str:resource>/<str:object_id>/', views.admin_resource, name='admin_resource_edit'),
]