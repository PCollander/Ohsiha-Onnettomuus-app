# Generated by Django 3.0.5 on 2020-04-04 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanta', '0003_auto_20200404_1732'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='onnettomuus',
            name='id',
        ),
        migrations.AlterField(
            model_name='onnettomuus',
            name='Onnett_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
