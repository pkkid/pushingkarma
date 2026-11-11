from django.db import migrations

# GitHub repos that were renamed. The row is renamed in place so the hand-picked icon
# and color carry over, rather than the next sync creating a new row without them.
RENAMES = {
    'pkkid/python-algorithmx': 'pkkid/puzzle-a-day',
}


def rename_repos(apps, schema_editor):
    """ Rename synced repo rows to their new GitHub names. """
    GithubRepo = apps.get_model('projects', 'GithubRepo')
    for old, new in RENAMES.items():
        if not GithubRepo.objects.filter(name=new).exists():
            GithubRepo.objects.filter(name=old).update(name=new)


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_contributors'),
    ]

    operations = [
        migrations.RunPython(rename_repos, migrations.RunPython.noop),
    ]
