# Generated by Django 4.1.2 on 2022-10-17 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enderecos', '0003_alter_endereco_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endereco',
            name='complemento',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
