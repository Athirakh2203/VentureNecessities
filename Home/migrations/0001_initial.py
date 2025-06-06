# Generated by Django 4.1 on 2025-03-19 05:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='category',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('category_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='equipment',
            fields=[
                ('equipment_id', models.AutoField(primary_key=True, serialize=False)),
                ('equipment_name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('amount', models.CharField(max_length=200)),
                ('stock', models.CharField(max_length=200)),
                ('Zone', models.CharField(max_length=200)),
                ('image', models.ImageField(default='default.jpg', upload_to='equipment_images/')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.category')),
            ],
        ),
        migrations.CreateModel(
            name='login',
            fields=[
                ('login_id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=200)),
                ('password', models.CharField(max_length=200)),
                ('usertype', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='payment',
            fields=[
                ('payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_master', models.CharField(max_length=200)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='seller',
            fields=[
                ('seller_id', models.AutoField(primary_key=True, serialize=False)),
                ('seller_name', models.CharField(max_length=200)),
                ('company_name', models.CharField(max_length=200)),
                ('licence_no', models.CharField(max_length=200)),
                ('place', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=200)),
                ('landmark', models.CharField(max_length=200)),
                ('login', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.login')),
            ],
        ),
        migrations.CreateModel(
            name='user',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('place', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=200)),
                ('landmark', models.CharField(max_length=200)),
                ('login', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.login')),
            ],
        ),
        migrations.CreateModel(
            name='seller_orders',
            fields=[
                ('seller_order_id', models.AutoField(primary_key=True, serialize=False)),
                ('equipment', models.CharField(max_length=200)),
                ('buy_amount', models.CharField(max_length=200)),
                ('stock', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=200)),
                ('sell_amount', models.CharField(max_length=200)),
                ('rent_amount', models.CharField(max_length=200)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.seller')),
            ],
        ),
        migrations.CreateModel(
            name='sell_equipment',
            fields=[
                ('sell_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.CharField(max_length=200)),
                ('stock', models.CharField(max_length=200)),
                ('total_amount', models.CharField(max_length=200)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=200)),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.login')),
            ],
        ),
        migrations.CreateModel(
            name='rent_equipment',
            fields=[
                ('equipment_id', models.AutoField(primary_key=True, serialize=False)),
                ('equipment_name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('amount', models.CharField(max_length=200)),
                ('stock', models.CharField(max_length=200)),
                ('Zone', models.CharField(max_length=200)),
                ('image', models.ImageField(default='default.jpg', upload_to='equipment_images/')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.category')),
                ('login', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.login')),
            ],
        ),
        migrations.CreateModel(
            name='rent',
            fields=[
                ('rent_id', models.AutoField(primary_key=True, serialize=False)),
                ('from_date', models.DateTimeField(auto_now_add=True)),
                ('to_date', models.DateTimeField(auto_now_add=True)),
                ('total_rent_amount', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=200)),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.equipment')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.seller')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.user')),
            ],
        ),
        migrations.CreateModel(
            name='rating',
            fields=[
                ('rating_id', models.AutoField(primary_key=True, serialize=False)),
                ('rating', models.CharField(max_length=200)),
                ('review', models.CharField(max_length=200)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.equipment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.user')),
            ],
        ),
        migrations.CreateModel(
            name='order_master_user',
            fields=[
                ('order_master_user_id', models.AutoField(primary_key=True, serialize=False)),
                ('total_amount', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=200)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.seller')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.user')),
            ],
        ),
        migrations.CreateModel(
            name='order_master_seller',
            fields=[
                ('order_master_seller_id', models.AutoField(primary_key=True, serialize=False)),
                ('total_amount', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=200)),
                ('login', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.login')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.seller')),
            ],
        ),
        migrations.CreateModel(
            name='order_details_user',
            fields=[
                ('order_details_user_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.CharField(max_length=200)),
                ('amount', models.CharField(max_length=200)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('order_master_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.order_master_user')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.equipment')),
            ],
        ),
        migrations.CreateModel(
            name='order_details_seller',
            fields=[
                ('order_details_seller_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.CharField(max_length=200)),
                ('amount', models.CharField(max_length=200)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('order_master_seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.order_master_seller')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.equipment')),
            ],
        ),
        migrations.CreateModel(
            name='manufacture',
            fields=[
                ('manufacture_id', models.AutoField(primary_key=True, serialize=False)),
                ('manufacturename', models.CharField(max_length=200)),
                ('licence_no', models.CharField(max_length=200)),
                ('place', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=200)),
                ('landmark', models.CharField(max_length=200)),
                ('login', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.login')),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('name', models.CharField(max_length=100)),
                ('feedback_id', models.AutoField(primary_key=True, serialize=False)),
                ('feedback_desc', models.CharField(max_length=255)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('sender_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Home.login')),
            ],
        ),
        migrations.AddField(
            model_name='equipment',
            name='login',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Home.login'),
        ),
        migrations.CreateModel(
            name='complaint',
            fields=[
                ('complaint_id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('reply', models.CharField(max_length=200)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Home.login')),
            ],
        ),
    ]
