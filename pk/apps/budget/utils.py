# encoding: utf-8
import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from pk.utils.utils import add_months


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
            if (interval == 'year'
              and (mindate.month == 1 and mindate.day == 1)
              and (maxdate.month == 1 and maxdate.day == 1)
              and (maxdate.year - mindate.year) == 1):
                selected = mindate
            elif (interval == 'month'
              and (mindate.day == 1 and maxdate.day == 1)
              and add_months(mindate, 1) == maxdate):
                selected = mindate
        except Exception:
            return None, None, None
        return mindate, maxdate, selected
    return None, None, None
