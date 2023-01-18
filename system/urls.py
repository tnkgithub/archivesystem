from django.urls import path
from .views import electionView, imgSOMView, SOM, menu, titleSOMView


urlpatterns = [
    path('', electionView, name="rep-image"),
    path('main', imgSOMView),
    path('som', SOM, name="img-som-frame"),
    path('menu', menu, name="menu"),
    path('title', titleSOMView, name="title-som-frame")
]
