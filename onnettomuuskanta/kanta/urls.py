from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.registerPage, name="register"),
	path('', views.home, name="home"),
	path('login/', views.loginPage, name="login"),
	path('logout/', views.logoutUser, name="logout"),
	path('search/plot/', views.createPlot, name="plot"),
	path('search/', views.searchView, name='search'),
	path('kanta/plot/', views.createPlot, name="plot"),
]