# Generated by Django 4.0.5 on 2022-07-05 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0002_alter_curso_nome'),
    ]

    operations = [
        migrations.AddField(
            model_name='curso',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]