# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0009_auto_20141125_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProofOfManufacturing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('laboratory_name', models.CharField(max_length=128)),
                ('laboratory_address', models.CharField(max_length=128)),
                ('laboratory_city', models.CharField(max_length=128)),
                ('laboratory_postal_code', models.CharField(max_length=6)),
                ('laboratory_country', models.CharField(max_length=128)),
                ('laboratory_phone', models.CharField(max_length=14)),
                ('laboratory_fax', models.CharField(max_length=14)),
                ('invoice_date', models.DateTimeField()),
                ('invoice_number', models.IntegerField()),
                ('bill_name', models.CharField(max_length=128)),
                ('bill_address', models.CharField(max_length=128)),
                ('bill_city', models.CharField(max_length=128)),
                ('bill_postal_code', models.CharField(max_length=6)),
                ('bill_country', models.CharField(max_length=128)),
                ('ship_name', models.CharField(max_length=128)),
                ('ship_address', models.CharField(max_length=128)),
                ('ship_city', models.CharField(max_length=128)),
                ('ship_postal_code', models.CharField(max_length=6)),
                ('ship_country', models.CharField(max_length=128)),
                ('patient', models.CharField(max_length=128)),
                ('product', models.CharField(max_length=256)),
                ('quantity', models.IntegerField()),
                ('laboratory_information', models.CharField(max_length=128)),
                ('laboratory_supervisor', models.CharField(max_length=128)),
                ('raw_materials', models.TextField()),
                ('manufacturing', models.TextField()),
                ('casting_technique', models.TextField()),
                ('claim', models.ForeignKey(to='clients.Claim')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='abnormal_gait_pressures',
            field=models.BooleanField(verbose_name='Abnormal Gait Pressures', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='abnormal_gait_tracking',
            field=models.BooleanField(verbose_name='Abnormal Gait Timing', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='abnormal_patellar_tracking',
            field=models.BooleanField(verbose_name='Abnormal Patellar Tracking', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='achilles_tendinitis',
            field=models.BooleanField(verbose_name='Achilles Tendinitis', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='ankle_abnormal_rom',
            field=models.BooleanField(verbose_name='Ankle: Abnormal ROM', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='ankle_arthritis',
            field=models.BooleanField(verbose_name='Ankle Arthritis', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='bunions_hallux_valgus',
            field=models.BooleanField(verbose_name='Bunions / Hallux Valgus', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='diabetes',
            field=models.BooleanField(verbose_name='Diabetes', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='drop_foot',
            field=models.BooleanField(verbose_name='Drop Foot', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='first_mtp_arthritis',
            field=models.BooleanField(verbose_name='1st MTP Arthritis', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='foot_abnormal_ROM',
            field=models.BooleanField(verbose_name='Foot: Abnormal ROM', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='foot_arthritis',
            field=models.BooleanField(verbose_name='Foot Arthritis', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='forefoot_valgus',
            field=models.BooleanField(verbose_name='Forefoot Valgus', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='forefoot_varus',
            field=models.BooleanField(verbose_name='Forefoot Varus', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='genu_valgum',
            field=models.BooleanField(verbose_name='Genu Valgum', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='genu_varum',
            field=models.BooleanField(verbose_name='Genu Varum', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='gout',
            field=models.BooleanField(verbose_name='Gout', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='hammer_toes',
            field=models.BooleanField(verbose_name='Hammer Toes', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='heel_spur',
            field=models.BooleanField(verbose_name='Heel Spur', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='hip_arthritis',
            field=models.BooleanField(verbose_name='Hip Arthritis', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='interdigital_neuroma',
            field=models.BooleanField(verbose_name='Interdigital Neuroma', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='knee_arthritis',
            field=models.BooleanField(verbose_name='Knee Arthritis', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='leg_length_discrepency',
            field=models.BooleanField(verbose_name='Leg Length Discrepancy', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='ligament_tear',
            field=models.BooleanField(verbose_name='Ligament Tear / Sprain', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='lumbar_arthritis',
            field=models.BooleanField(verbose_name='Lumbar Arthritis', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='lumbar_spine_dysfunction',
            field=models.BooleanField(verbose_name='Lumbar Spine Dysfunction', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='metatarsalgia',
            field=models.BooleanField(verbose_name='Metatarsalgia', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='mtp_drop',
            field=models.BooleanField(verbose_name='MTP Drop', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='neuropathy',
            field=models.BooleanField(verbose_name='Neuropathy', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='over_pronation',
            field=models.BooleanField(verbose_name='Over Pronation', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='over_supination',
            field=models.BooleanField(verbose_name='Over Supination', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='peroneal_dysfunction',
            field=models.BooleanField(verbose_name='Peroneal Dysfunction', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='pes_cavus',
            field=models.BooleanField(verbose_name='Pes Cavus', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='pes_planus',
            field=models.BooleanField(verbose_name='Pes Planus', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='plantar_fasciitis',
            field=models.BooleanField(verbose_name='Plantar Fasciitis', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='rheumatoid_arthritis',
            field=models.BooleanField(verbose_name='Rheumatoid Arthritis', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='scoliosis_with_pelvic_tilt',
            field=models.BooleanField(verbose_name='Scoliosis With Pelvic Tilt', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='shin_splints',
            field=models.BooleanField(verbose_name='Shin Splints', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='si_arthritis',
            field=models.BooleanField(verbose_name='SI Arthritis', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='si_joint_dysfunction',
            field=models.BooleanField(verbose_name='SI Joint Dysfunction', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='insuranceletter',
            name='ulcers',
            field=models.BooleanField(verbose_name='Ulcers', default=False),
            preserve_default=True,
        ),
    ]