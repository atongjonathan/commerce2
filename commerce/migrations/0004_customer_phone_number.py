# Generated by Django 4.2.5 on 2023-09-25 09:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("commerce", "0003_alter_customer_email_alter_product_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="phone_number",
            field=models.CharField(
                blank=True,
                max_length=17,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
                        regex="^\\+?1?\\d{9,15}$",
                    )
                ],
            ),
        ),
    ]