from django.db import migrations


def remove_bad_tickers(apps, schema_editor):
    symbols = ['FMEIX', 'AACIX', 'FSAIX', '.SPX', '.NDAQ']
    Ticker = apps.get_model('stocks', 'Ticker')
    Ticker.objects.filter(ticker__in=symbols).delete()


class Migration(migrations.Migration):
    dependencies = [('stocks', '0005_alter_ticker_info_alter_ticker_ticker'),]
    operations = [migrations.RunPython(remove_bad_tickers),]
