# Generated by Django 3.0.4 on 2020-03-21 00:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import pk.apps.budget.models


def get_uncategorized():
    return pk.apps.budget.models.Category.objects.get(name='Uncategorized')


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('fid', models.IntegerField(db_index=True, unique=True)),
                ('type', models.CharField(choices=[('bank', 'Bank'), ('credit', 'Credit')], max_length=255)),
                ('payee', models.CharField(blank=True, default='', max_length=255)),
                ('balance', models.DecimalField(decimal_places=2, default=None, max_digits=9, null=True)),
                ('balancedt', models.DateTimeField(default=None, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
                ('budget', models.DecimalField(decimal_places=2, max_digits=8)),
                ('comment', models.TextField(blank=True, default='')),
                ('sortindex', models.IntegerField(default=None)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KeyValue',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('key', models.SlugField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('value', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('trxid', models.CharField(db_index=True, max_length=255)),
                ('date', models.DateField(db_index=True)),
                ('payee', models.CharField(blank=True, db_index=True, max_length=255)),
                ('amount', models.DecimalField(db_index=True, decimal_places=2, max_digits=8)),
                ('approved', models.BooleanField(db_index=True, default=False)),
                ('memo', models.CharField(blank=True, default='', max_length=255)),
                ('comment', models.TextField(blank=True, db_index=True, default='')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budget.Account')),
                ('category', models.ForeignKey(default=None, on_delete=models.SET(get_uncategorized), to='budget.Category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('account', 'trxid')},
            },
        ),
    ]
