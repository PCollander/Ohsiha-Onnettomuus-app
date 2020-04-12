from django.shortcuts import render, redirect
from .forms import CreateUserForm, SearchForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Onnettomuus
import plotly.express as px

from django.contrib.auth.decorators import login_required

# a month dict for better visualization than just numbers
KUUKAUDET = {1 : 'Tammikuu',
             2 : 'Helmikuu',
             3 : 'Maaliskuu',
             4 : 'Huhtikuu',
             5 : 'Toukokuu',
             6 : 'Kesäkuu',
             7 : 'Heinäkuu',
             8 : 'Elokuu',
             9 : 'Syyskuu',
             10 : 'Lokakuu',
             11 : 'Marraskuu',
             12 : 'Joulukuu'}

# providing verbal information of the accident class (onnettomuusluokka)
onnettomuusluokka = {1 : "Yksittäisonnettomuus",
                     2 : "Kääntymisonnettomuus",
                     3 : "Ohitusonnettomuus",
                     4 : "Risteämisonnettomuus",
                     5 : "Kohtaamisonnettomuus",
                     6 : "Peräänajo-onnettomuus",
                     7 : "Mopedionnettomuus",
                     8 : "Polkupyöräonnettomuus",
                     9 : "Jalankulkijaonnettomuus",
                     10 : "Hirvionnettomuus",
                     11 : "Peura- tai kaurisonnettomuus",
                     12 : "Muu eläinonnettomuus",
                     13 : "Muu onnettomuus"}

# verbal information of the surface of the road during the accident
pinta = {1 : "Paljas, kuiva",
         2 : "Paljas, märkä",
         3 : "Urissa, märkä",
         4 : "Luminen",
         5 : "Sohjoinen",
         6 : "Jäinen",
         7 : "Ajourat paljaana",
        -1 : "Ei tietoa tien pinnasta"}

# verbal information of the lighting during the accident
valoisuus = {1 : "Päivänvalo",
             2 : "Hämärä",
             3 : "Pimeä (valaisematon)",
             4 : "Tie valaistu (muutoin pimeä)",
            -1 : "Ei tietoa valaistuksesta"}

# verbal information of the weather conditions during the accident
saa = {1 : "Kirkas",
       2 : "Pilvipouta",
       3 : "Sumu",
       4 : "Vesisade",
       5 : "Lumisade",
       6 : "Räntäsade",
      -1 : "Ei säätietoja"}


# receive registration data or redirect properly
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)

                return redirect('login')

        context = {'form': form}
        return render(request, 'register.html', context)


# login page to the service
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'login.html', context)


# logout function
def logoutUser(request):
    logout(request)
    return redirect('login')


# simple home page call
@login_required(login_url='login')
def home(request):
    return render(request, 'base.html')

# provides the information for the search forms query from the database
@login_required(login_url='login')
def searchView(request):
    location_list = SearchForm()
    context = {
        'location_list': location_list,
    }
    return render(request,'search.html', context)

# receives user input from the dropdown selections, validates it and calls a
# function to create the scatter plot visualization
@login_required(login_url='login')
def createPlot(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form = form.cleaned_data
            kuvaaja = create_plot_html(form)
            return render(request, 'plot.html', kuvaaja)
    return render(request, 'plot.html')


# check if there are any casualties or injured people in the accident, defines
# the color of the accident in the visualization
def tarkista_onko_kuoll_loukkaant(onnettomuus):
    kuolleet = list(onnettomuus.values('Kuolleet'))
    loukkaantuneet = list(onnettomuus.values('Loukkaant'))
    vakavuuslista = []

    # returns an empty list if there are no accidents found for the given
    # criteria
    if len(kuolleet) == 0:
        return vakavuuslista
    else:
        for i in range(len(kuolleet)):
            if kuolleet[i]['Kuolleet'] > 0:
                vakavuuslista.append('Onnettomuudessa kuolleita')
            elif loukkaantuneet[i]['Loukkaant'] > 0:
                vakavuuslista.append('Onnettomuudessa loukkaantuneita')
            else:
                vakavuuslista.append('Ei vahingoittuneita')
        return vakavuuslista

# checks the amount of casualties or injured people in the accident, defines
# the size of the accident in the visualization
def tarkista_kuoll_loukkaant_maara(onnettomuus):
    kuolleet = list(onnettomuus.values('Kuolleet'))
    loukkaantuneet = list(onnettomuus.values('Loukkaant'))
    maara = []

    # returns an empty list if there are no accidents found for the given
    # criteria
    if len(kuolleet) == 0:
        return maara
    else:
        for i in range(len(kuolleet)):
            if kuolleet[i]['Kuolleet'] > 0:
                maara.append(float(kuolleet[i]['Kuolleet']))
            elif loukkaantuneet[i]['Loukkaant'] > 0:
                maara.append(float(loukkaantuneet[i]['Loukkaant']))
            else:
                maara.append(1.0)
        return maara

# collects the additional information about the accident for the hover-tool
# from the attributes that don't show from the y or the x axis
def tietojenhaku(onnettomuus):
    tapaturmat = list(onnettomuus)
    tietolista = []

    # returns an empty list if there are no found accidents for the given
    # criteria
    if len(tapaturmat) == 0:
        return tietolista
    else:
        for i in range(len(tapaturmat)):

            # accident class
            if tapaturmat[i]['Onluokka'] in onnettomuusluokka.keys():
                onluokka = "Onnettomuusluokka: " + onnettomuusluokka[tapaturmat[i]['Onluokka']]

            # road surface
            if tapaturmat[i]['Pinta'] in pinta.keys():
                tien_pinta = ", Tien pinta: " + pinta[tapaturmat[i]['Pinta']]

            # lightness
            if tapaturmat[i]['Valoisuus'] in valoisuus.keys():
                valo = ", Valoisuus: " + valoisuus[tapaturmat[i]['Valoisuus']]

            # weather conditions
            if tapaturmat[i]['Saa'] in saa.keys():
                saatieto = ", Säätila: " + saa[tapaturmat[i]['Saa']]

            # speed limit
            nopraj =", Nopeusrajoitus {:d} km/h".\
                format(tapaturmat[i]['Nopraj'])

            # temperature
            if tapaturmat[i]['Lampotila'] is None:
                lampotila = ", Lämpötilatietoja ei saatavilla"
            else:
                # makes sure the format of the temperature is integer
                l_tila = int(tapaturmat[i]['Lampotila'])
                lampotila = ", Lämpötila celsiuksina: {:d}".\
                    format(l_tila)

            tietolista.append(onluokka + tien_pinta + valo + saatieto + nopraj + lampotila)

        return tietolista

# fetches the correct amount of days to the x axis based on the chosen month
def hae_paivat(onnettomuus):
    kuukausi = list(onnettomuus.values('Kk'))
    vuosi = list(onnettomuus.values('Vuosi'))

    # returns two empty values if there are no accidents found for the given
    # criteria
    if len(kuukausi) == 0:
        pvm1 = ""
        pvm2 = ""
        return pvm1, pvm2
    else:
        i = kuukausi[0]['Kk']
        j = vuosi[0]['Vuosi']
        if i == 1 or i == 3 or i == 5 or i == 7 or i == 8 or i == 10 or i == 12:
            if i == 10 or i == 12:
                pvm1 = "{:d}-{:d}-01".format(j, i)
                pvm2 = "{:d}-{:d}-31".format(j, i)
            else:
                pvm1 = "{:d}-0{:d}-01".format(j, i)
                pvm2 = "{:d}-0{:d}-31".format(j, i)

        elif i == 4 or i == 6 or i == 9 or i == 11:
            if i == 11:
                pvm1 = "{:d}-{:d}-01".format(j, i)
                pvm2 = "{:d}-{:d}-30".format(j, i)
            else:
                pvm1 = "{:d}-0{:d}-01".format(j, i)
                pvm2 = "{:d}-0{:d}-30".format(j, i)

        else:
            # checks for leap years from the possible values
            if j == 2020 or j == 2016 or j == 2012 or j == 2008:
                pvm1 = "{:d}-0{:d}-01".format(j, i)
                pvm2 = "{:d}-0{:d}-29".format(j, i)
            else:
                pvm1 = "{:d}-0{:d}-01".format(j, i)
                pvm2 = "{:d}-0{:d}-28".format(j, i)
        return pvm1, pvm2

# fetches the hours when the accidents have taken place to position the
# accidents regarding the y axis
def hae_tunnit(onnettomuus):
    tunnit = list(onnettomuus.values('Tunti'))
    tuntilista = []

    # returns an empty list if there are no found accidents for the given
    # criteria
    if len(tunnit) == 0:
        return tuntilista
    else:
        for i in range(len(tunnit)):
            if tunnit[i]['Tunti'] == -1:
                tuntilista.append('0')
            else:
                tuntilista.append(str(tunnit[i]['Tunti']))
        return tuntilista

# fetches the dates when the accidents have taken place to position the
# accidents regrading the x axis
def hae_pvm(onnettomuus):
    pvmrt = []
    paivat = list(onnettomuus.values('Pvm'))

    for i in range(len(paivat)):
        pvmrt.append(paivat[i]['Pvm'])
    return pvmrt

# provides prettier and more informative labels for the information provided in
# the hover tool
def hae_label():
    labelit = {}
    labelit['color'] = "Väriselite"
    labelit['y'] = 'Vuorokaudetn tunti'
    labelit['x'] = 'Onnettomuuden päivämäärä'
    labelit['size'] = "Osallisten määrä"
    labelit['hover_data_0'] = "Onnettomuuden tiedot"
    return labelit

# provides the title for the graph with information of the chosen criteria or
# the information that there were no found accidents for the given criteria
def hae_title(onnettomuus):
    kuntal = list(onnettomuus.values('Kuntasel'))
    kuukausil = list(onnettomuus.values('Kk'))
    vuosil = list(onnettomuus.values('Vuosi'))

    if len(kuukausil) == 0:
        title = "Hakuehdoilla ei löytynyt tuloksia"
    else:
        kunta = kuntal[0]['Kuntasel']
        kuukausi = kuukausil[0]['Kk']
        vuosi = vuosil[0]['Vuosi']

        title = "{}, {} {:d}".format(kunta, KUUKAUDET[kuukausi], vuosi)
    return title

# gets called by the createPlot-fuction and actually creates the plot with the
# help of helper functions and returns it to the caller function
def create_plot_html(form):

    # filter the accidents based on user input
    onnettomuudet = Onnettomuus.objects.filter(Vuosi = form['vuosi'], Kk = form['kuukausi'], Kuntasel = form['kunta'])
    df = onnettomuudet

    # define plot
    fig = px.scatter(df, x= hae_pvm(onnettomuudet.values()),
                     y= hae_tunnit(onnettomuudet.values()),
                     range_x= hae_paivat(onnettomuudet.values()),
                     range_y=('0', '24'),
                     color=tarkista_onko_kuoll_loukkaant(onnettomuudet.values()),
                     size=tarkista_kuoll_loukkaant_maara(onnettomuudet.values()),
                     hover_data=[tietojenhaku(onnettomuudet.values())],
                     title=hae_title(onnettomuudet), labels=hae_label())

    # turn to html
    graph = fig.to_html(full_html=False, default_height=700, default_width=1500)
    context = {'graph': graph}

    return context
