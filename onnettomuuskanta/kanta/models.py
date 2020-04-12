from django.db import models


# create the table with the desired attributes
class Onnettomuus(models.Model):
    Onnett_id = models.IntegerField(primary_key=True)
    Vuosi = models.IntegerField()
    Kk = models.IntegerField()
    Pvm = models.DateField(null=True)
    Kuolleet = models.IntegerField()
    Loukkaant = models.IntegerField()
    Tunti = models.IntegerField()
    Onluokka = models.IntegerField()
    Nopraj = models.IntegerField()
    Pinta = models.IntegerField()
    Valoisuus = models.IntegerField()
    Saa = models.IntegerField()
    Kunta = models.IntegerField(null=True)
    Kuntasel = models.CharField(max_length=100)
    Nopsuunoik = models.IntegerField()
    Lampotila = models.IntegerField(null=True)


    def __str__(self):
        return self.Onnett_id