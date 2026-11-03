"""Rename mixed Cyrillic/Latin blog slugs to pure Latin (301s live in BlogDetailView)."""
from django.db import migrations

RENAMES = {
    'mobilna-versiya-ch\u043e\u043c\u0443-67-kliyentiv-vidvalyvalys': 'mobilna-versiya-chomu-67-kliyentiv-vidvalyvalys',
    'telegram-boty-dlya-biznesu-chomu-vlasnyk-kavi\u044f\u0440\u043d\u0456-zvilnyv': 'telegram-boty-dlya-biznesu-chomu-vlasnyk-kaviarni-zvilnyv',
}


def forwards(apps, schema_editor):
    BlogPost = apps.get_model('blog', 'BlogPost')
    for old, new in RENAMES.items():
        if BlogPost.objects.filter(slug=new).exists():
            continue  # idempotent: already renamed (or seeded with the new slug)
        # .update() keeps updated_at (auto_now) untouched: the article did not change.
        BlogPost.objects.filter(slug=old).update(slug=new)


def backwards(apps, schema_editor):
    BlogPost = apps.get_model('blog', 'BlogPost')
    for old, new in RENAMES.items():
        if not BlogPost.objects.filter(slug=old).exists():
            BlogPost.objects.filter(slug=new).update(slug=old)


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_add_ru_content_fields'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
