# Generated by Django 4.1.5 on 2023-01-31 11:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostSequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='post',
            name='site_id',
        ),
        migrations.AddField(
            model_name='post',
            name='hash_content',
            field=models.CharField(default=1, max_length=64, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='site',
            field=models.CharField(choices=[('IAM', 'Iam'), ('NAVERBLOG', 'Naverblog'), ('BBC', 'Bbc')], max_length=10),
        ),
        migrations.AddField(
            model_name='post',
            name='sequence',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='board.postsequence'),
            preserve_default=False,
        ),
    ]
