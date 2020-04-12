from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Onnettomuus

# years for the method Choices (vuosi)
VUODET = [tuple([x,x]) for x in range(2005, 2019)]

# months for the method Choices (kuukausi)
KUUKAUDET =  [
    (1, 'Tammikuu'),
    (2, 'Helmikuu'),
    (3, 'Maaliskuu'),
    (4, 'Huhtikuu'),
	(5, 'Toukokuu'),
	(6, 'Kesäkuu'),
	(7, 'Heinäkuu'),
	(8, 'Elokuu'),
	(9, 'Syyskuu'),
	(10, 'Lokakuu'),
	(11, 'Marraskuu'),
	(12, 'Joulukuu'),
    ]

# fetching all the municipalitys in the database and providing them distinctly
# and in aplhabetical order
KUNTASEL = [(i['Kuntasel'], i['Kuntasel']) for i in
					Onnettomuus.objects.values('Kuntasel').distinct().
						order_by('Kuntasel')]


class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']


# search form for making queries from the database
class SearchForm(forms.Form):
	model = Onnettomuus
	vuosi = forms.ChoiceField(required=True, label="Valitse vuosi ",
							choices=VUODET)

	kuukausi = forms.ChoiceField(required=True, label="Valitse kuukausi ",
							   choices=KUUKAUDET)

	kunta = forms.ChoiceField(required=True,label="Valitse kunta ",
							  choices=KUNTASEL)


