from django.urls import path
from hier import views


urlpatterns = [
    path('', views.hier, name='hier'),
    path('lineages/', views.get_lineage, name='lineages'),
    path('lineages/add/', views.add_lineage, name='add_lineage'),
]
