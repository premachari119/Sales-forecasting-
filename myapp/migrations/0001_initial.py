
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        # Add your dependencies here
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=100)),
                ('sales', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
                ('profit', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]
