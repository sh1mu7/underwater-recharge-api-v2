# Generated by Django 5.0 on 2024-05-28 07:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CropCoefficient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('kc_a1', models.FloatField()),
                ('kc_a2', models.FloatField()),
                ('kc_a3', models.FloatField()),
                ('kc_a4', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CurveNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('cn1', models.FloatField()),
                ('cn2', models.FloatField()),
                ('cn3', models.FloatField()),
                ('cn4', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='EtoData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('value', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EtoRsData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('RH_t', models.FloatField()),
                ('WS_t', models.FloatField()),
                ('SR_t', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EtoShData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('RH_t', models.FloatField()),
                ('WS_t', models.FloatField()),
                ('SH_t', models.FloatField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LandUseArea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('a1', models.FloatField()),
                ('a2', models.FloatField()),
                ('a3', models.FloatField()),
                ('a4', models.FloatField()),
                ('a5', models.FloatField()),
                ('a6', models.FloatField()),
                ('a7', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='RechargeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('re_previous', models.FloatField()),
                ('re_water_body', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RHValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='SolarRadiation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Temperature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('t_max', models.FloatField()),
                ('t_min', models.FloatField()),
                ('t_mean', models.FloatField(blank=True, editable=False, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TMeanValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='WBMethodData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('catchment_area', models.FloatField(blank=True, null=True)),
                ('rlc', models.CharField(blank=True, choices=[(1, 'Arid (P ≤ 500 mm)'), (2, 'Semi-arid (500 < P < 1000)'), (3, 'Semi-humid (1000 < P < 1500)'), (4, 'Humid (P > 1500)')], max_length=100, null=True)),
                ('rp', models.FloatField(blank=True, null=True)),
                ('classification', models.CharField(blank=True, choices=[(1, 'Arid (P ≤ 500 mm)'), (2, 'Semi-arid (500 < P < 1000)'), (3, 'Semi-humid (1000 < P < 1500)'), (4, 'Humid (P > 1500)')], max_length=100, null=True)),
                ('eto_method', models.CharField(choices=[(1, 'Fao combined pm method'), (2, 'PM SH method)'), (3, 'PM no sh and rs method'), (4, 'FAO Blaney-Criddle method'), (5, 'Makkink method'), (6, 'Hargreaves method'), (7, 'Hansen method'), (8, 'Turc method'), (9, 'Priestly taylor method'), (10, 'Jensen haise method'), (11, 'Abtew method'), (12, 'De bruin method')], max_length=100)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('elevation', models.FloatField(blank=True, null=True)),
                ('yearly_rainfall', models.FloatField(blank=True, null=True)),
                ('yearly_recharge', models.FloatField(blank=True, null=True)),
                ('yearly_runoff', models.FloatField(blank=True, null=True)),
                ('yearly_recharge_percentage_precipitation', models.FloatField(blank=True, null=True)),
                ('yearly_runoff_percentage_rainfall', models.FloatField(blank=True, null=True)),
                ('aridity_index', models.FloatField(blank=True, null=True)),
                ('yeto', models.FloatField(blank=True, null=True)),
                ('c_value', models.ManyToManyField(blank=True, related_name='wb_c_value', to='estimation.cvalue')),
                ('cn_value', models.ManyToManyField(blank=True, related_name='wb_cn_value', to='estimation.curvenumber')),
                ('eto_list', models.ManyToManyField(blank=True, related_name='wb_eto_list', to='estimation.etodata')),
                ('eto_rs_data', models.ManyToManyField(blank=True, related_name='wb_eto_rs_data', to='estimation.etorsdata')),
                ('eto_sh_data', models.ManyToManyField(blank=True, related_name='wb_eto_sh_data', to='estimation.etoshdata')),
                ('kc_value', models.ManyToManyField(blank=True, related_name='wb_kc_value', to='estimation.cropcoefficient')),
                ('land_use_area', models.ManyToManyField(blank=True, related_name='wb_land_use_area', to='estimation.landusearea')),
                ('p_value', models.ManyToManyField(blank=True, related_name='wb_p_value', to='estimation.pvalue')),
                ('recharge_rate', models.ManyToManyField(blank=True, related_name='wb_recharge_rate', to='estimation.rechargerate')),
                ('rh_value', models.ManyToManyField(blank=True, related_name='wb_rh_value', to='estimation.rhvalue')),
                ('solar_radiation', models.ManyToManyField(blank=True, related_name='wb_solar_radiation', to='estimation.solarradiation')),
                ('t_mean_value', models.ManyToManyField(blank=True, related_name='wb_t_mean_value', to='estimation.tmeanvalue')),
                ('temperature', models.ManyToManyField(blank=True, related_name='wb_temperature', to='estimation.temperature')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WTFMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('catchment_area', models.FloatField()),
                ('wt_max', models.FloatField()),
                ('wt_min', models.FloatField()),
                ('num_layers', models.IntegerField()),
                ('is_precipitation_given', models.BooleanField(default=True)),
                ('precipitation', models.FloatField()),
                ('ratio', models.FloatField(blank=True, null=True)),
                ('yearly_recharge', models.FloatField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SPYieldData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('layer_height', models.FloatField()),
                ('sp_yield_percentage', models.FloatField()),
                ('wtf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sp_yield_data', to='estimation.wtfmethod')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('QP_n', models.FloatField()),
                ('QB_n', models.FloatField()),
                ('Qin_n', models.FloatField()),
                ('Qout_n', models.FloatField()),
                ('Qr_n', models.FloatField()),
                ('wtf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wtf_q_data', to='estimation.wtfmethod')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
