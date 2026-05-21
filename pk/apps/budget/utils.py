# encoding: utf-8
import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from django.conf import settings
from django.forms.models import model_to_dict
from pk.utils.utils import add_months


def clean_date_filters(search):
    """ Removes any date filters from the search string. """
    clean_search = re.sub(r'date[><]=?"[^"]*"?|date[><]=?\S+', '', search).strip()
    return ' '.join(clean_search.split())


def get_min_and_max_dates(search, interval='year'):
    """ Returns the min and max dates from the search string, if any. """
    mindates = re.findall(r'date>="([^"]*)"', search)
    maxdates = re.findall(r'date<"([^"]*)"', search)
    if len(mindates) == 1 and len(maxdates) == 1:
        try:
            mindate = parse_date(mindates[0])
            maxdate = parse_date(maxdates[0])
            if ((interval == 'year'
              and (mindate.month == 1 and mindate.day == 1)
              and (maxdate.month == 1 and maxdate.day == 1)
              and (maxdate.year - mindate.year) == 1)
            or (interval == 'month'
              and (mindate.day == 1 and maxdate.day == 1)
              and add_months(mindate, 1) == maxdate)):
                selected = mindate
        except Exception:
            return None, None, None
        return mindate, maxdate, selected
    return None, None, None


def get_similar_uncategorized_trxs(user, source_trx):
    """ Returns uncategorized transactions that can be categorized like source_trx. """
    if not source_trx.category_id:
        return []
    from .models import Transaction
    from .trxmanager import TransactionManager
    trxs = Transaction.objects.filter(user=user, account=source_trx.account, category__isnull=True)
    trxs = trxs.exclude(id=source_trx.id)
    updates = TransactionManager.categorize_transactions(
        user,
        source_trx.account,
        trxs,
        source_trxs=[source_trx],
    )
    return [trx for trx in updates if trx.category_id == source_trx.category_id]


def get_suggested_filters(search='', interval='year'):
    """ Returns a list of links to navigate by year or month.
        Interval should be 'year' or 'month'.
    """
    # Create a few helper functions
    to_interval = lambda dt: dt.replace(day=1) if interval == 'month' else dt.replace(month=1, day=1)
    add_interval = lambda dt, n: add_months(dt, n) if interval == 'month' else dt.replace(year=dt.year + n)
    str_interval = lambda dt: dt.strftime('%b') if interval == 'month' else dt.strftime('%Y')
    # Determine mindate, maxdate and selected from date filters
    mindate, maxdate, selected = get_min_and_max_dates(search, interval)
    mindate = to_interval(mindate) if mindate else None
    maxdate = to_interval(maxdate) if maxdate else None
    selected = to_interval(selected or datetime.now())
    # Create list of filters to suggest
    now = to_interval(datetime.now())
    suggested_dates = {add_interval(selected, -1), selected}
    if add_interval(selected, 1) <= now:
        suggested_dates.add(add_interval(selected, 1))
    if now not in suggested_dates:
        suggested_dates.add(now)
    # Generate list of ordered suggestions
    suggestions = []
    clean_search = clean_date_filters(search)
    for suggested_date in sorted(suggested_dates):
        if suggested_date == now:
            name = 'All Transactions' if interval == 'month' else 'This Year'
            is_selected = selected == now
            suggestions.append({'name':name, 'selected':is_selected, 'query':clean_search})
        else:
            is_selected = selected == now
            mindatestr = suggested_date.strftime('%Y-%m-%d')
            maxdatestr = add_interval(suggested_date, 1).strftime('%Y-%m-%d')
            query = f'{clean_search} date>={mindatestr} date<{maxdatestr}'.strip()
            suggestions.append({'name':str_interval(suggested_date), 'selected':is_selected, 'query':query})
    return suggestions


def sort_items(items, sortlist, itemid='id', sortkey='sortid'):
    """ Sort items in the order specified by sortlist.
        itemsdict: Dictionary of items to sort
        sortlist: List of item ids in the desired order
        itemid: Item id field to use for sorting
        sortkey: Item sort field to update
    """
    updates = []
    itemsdict = {getattr(item, itemid):item for item in items}
    for i in range(len(sortlist)):
        item = itemsdict[sortlist[i]]
        sortid = getattr(item, sortkey)
        if sortid != i+1:
            setattr(item, sortkey, i+1)
            updates.append(item)
    return updates


def scrub_payee(payee):
    """ Scrub unique details from payee when trying to match categories. """
    # Scrub payment processor tokens followed by *
    payee = payee.lower()
    # Scrub paymenet processor tokens followed by *
    if payee.split('*', 1)[0].strip() in settings.BUDGET_SCRUB_AGGREGATOR_TOKENS:
        payee = '*' + payee.split('*', 1)[-1].strip()
    # Split the payee into tokens
    tokens = re.sub(r'[^a-z0-9 ]', ' ', payee).split()
    scrubbed, seen, i = [], set(), 0
    while i < len(tokens):
        token = tokens[i]
        # Scrub month tokens followed by year tokens (e.g. "jan 2020", "february 21")
        nexttoken = tokens[i+1] if i+1 < len(tokens) else None
        nextisyear = bool(nexttoken and re.fullmatch(r'(?:\d{2}|20\d{2})', nexttoken))
        if token in settings.BUDGET_SCRUB_MONTH_TOKENS and nextisyear:
            i += 2; continue
        # Scrub junk strings <nums><chars><nums> or similar
        if re.search(r'(?:\d+[a-z]+\d+|[a-z]+\d+[a-z]+)', token):
            i += 1; continue
        # Scrub numbers and asterisks completly
        token = re.sub(r'\d+', '', token)
        # Scrub common noisy tokens
        if token in settings.BUDGET_SCRUB_NOISE_TOKENS:
            i += 1; continue
        # Scrubs tokens <1 char and non-unique within this payee
        if len(token) >= settings.BUDGET_SCRUB_MIN_TOKEN_LEN and token not in seen:
            scrubbed.append(token)
            seen.add(token)
        i += 1
    return ' '.join(scrubbed).strip()


def transaction_to_dict(trx):
    """ Convert transaction model to response dictionary used by API schemas. """
    item = model_to_dict(trx)
    item['url'] = trx.url
    item['account'] = dict(id=trx.account.id, url=trx.account.url, name=trx.account.name)
    item['category'] = dict(id=trx.category.id, url=trx.category.url, name=trx.category.name) if trx.category else None
    if trx.category and trx.category.exclude: item['category']['exclude'] = True
    return item

