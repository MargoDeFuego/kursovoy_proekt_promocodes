# Generated manually for business logic, analytics and exam requirements.

import decimal
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('promocode', '0003_historicalpromo'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='category',
            field=models.CharField(blank=True, help_text='Например: электроника, одежда, продукты, маркетплейс.', max_length=100, verbose_name='Категория магазина'),
        ),
        migrations.AddField(
            model_name='promo',
            name='discount_percent',
            field=models.PositiveSmallIntegerField(default=10, help_text='Значение от 1 до 100.', verbose_name='Скидка, %'),
        ),
        migrations.AddField(
            model_name='promo',
            name='min_order_amount',
            field=models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=10, verbose_name='Минимальная сумма заказа'),
        ),
        migrations.AddField(
            model_name='promo',
            name='usage_limit',
            field=models.PositiveIntegerField(blank=True, help_text='Оставьте пустым, если лимита нет.', null=True, verbose_name='Лимит применений'),
        ),
        migrations.AddField(
            model_name='promo',
            name='used_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Использовано'),
        ),
        migrations.AddField(
            model_name='promo',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_promos', to=settings.AUTH_USER_MODEL, verbose_name='Кто создал'),
        ),
        migrations.AddField(
            model_name='historicalpromo',
            name='discount_percent',
            field=models.PositiveSmallIntegerField(default=10, help_text='Значение от 1 до 100.', verbose_name='Скидка, %'),
        ),
        migrations.AddField(
            model_name='historicalpromo',
            name='min_order_amount',
            field=models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=10, verbose_name='Минимальная сумма заказа'),
        ),
        migrations.AddField(
            model_name='historicalpromo',
            name='usage_limit',
            field=models.PositiveIntegerField(blank=True, help_text='Оставьте пустым, если лимита нет.', null=True, verbose_name='Лимит применений'),
        ),
        migrations.AddField(
            model_name='historicalpromo',
            name='used_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Использовано'),
        ),
        migrations.AddField(
            model_name='historicalpromo',
            name='created_by',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Кто создал'),
        ),
        migrations.CreateModel(
            name='PromoClick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP-адрес')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата клика')),
                ('promo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clicks', to='promocode.promo', verbose_name='Промокод')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='promo_clicks', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Клик по промокоду',
                'verbose_name_plural': 'Клики по промокодам',
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddConstraint(
            model_name='promo',
            constraint=models.UniqueConstraint(condition=Q(is_active=True), fields=('shop', 'code'), name='unique_active_promo_code_per_shop'),
        ),
    ]
