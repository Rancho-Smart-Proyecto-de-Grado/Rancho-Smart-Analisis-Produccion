from django.urls import path

from analisis_produccion.produccion import views


urlpatterns = [
    path('info_lote/<str:tiempo>/', views.info_lote, name='info_lote'),
    path('produccion_por_lote/<int:lote_id>/<str:tiempo>/', views.produccion_por_lote, name='produccion_por_lote'),
    path('info_vaca/<int:vaca_id>/<str:tiempo>/', views.info_vaca, name='info_vaca'),
    path('comparar_lotes/<int:lote_id1>/<int:lote_id2>/<str:tiempo>/', views.comparar_lotes, name='comparar_lotes'),
]
