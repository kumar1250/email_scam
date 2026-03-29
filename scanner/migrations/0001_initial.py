from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScamKeyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=200, unique=True)),
                ('weight', models.FloatField(default=1.0)),
                ('category', models.CharField(default='general', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-weight']},
        ),
        migrations.CreateModel(
            name='EmailScan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=500, null=True)),
                ('sender', models.CharField(blank=True, max_length=300, null=True)),
                ('email_content', models.TextField()),
                ('result', models.CharField(choices=[('SCAM', 'Scam'), ('SAFE', 'Safe'), ('SUSPICIOUS', 'Suspicious')], max_length=20)),
                ('confidence_score', models.FloatField(default=0.0)),
                ('reasons', models.TextField(default='[]')),
                ('suspicious_links', models.TextField(default='[]')),
                ('detected_keywords', models.TextField(default='[]')),
                ('scanned_at', models.DateTimeField(auto_now_add=True)),
                ('file_name', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scans', to='auth.user')),
            ],
            options={'ordering': ['-scanned_at']},
        ),
    ]
