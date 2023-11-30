from django.urls import path
from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # banner
    path('banner/',views.banner,name='banner'),
    path('add_banner/',views.add_banner,name='add_banner'),
    path('edit_banner/<int:banner_id>/',views.edit_banner,name='edit_banner'),
    path('update_banner/<int:banner_id>/',views.update_banner,name='update_banner'),
    path('delete_banner/<int:banner_id>/',views.delete_banner,name='delete_banner'),
     
#     #invoice
#     path('invoice/<int:id>',views.invoice,name='invoice'),

#     #salesreprt
#     path('report-pdf-order/', views.report_pdf_order, name='report_pdf_order'),
#     path('chart-demo/', views.chart_demo, name='chart_demo'),

#     #admin order search
#     path('searchorder/',views.searchorder,name='searchorder'),
      
#    #search
#     path('search/',views.search,name='search'),
#     path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    
 
    
    

   

]