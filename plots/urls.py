from django.urls import path
from .views import homepage, graph_plot
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', homepage, name="homepage"),
    path('plot', graph_plot, name='graph_plot')

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
