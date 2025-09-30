# encoding: utf-8
import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from pk.utils.utils import add_months


def get_filters_by_month(search):
    """ Returns a list of links to navigate the months. """
    from calendar import month_name
    this_month = datetime.now().replace(day=1)
    # Remove existing date filters and get clean search
    clean_search = re.sub(r'date[><]=?"[^"]*"?|date[><]=?\S+', '', search).strip()
    clean_search = ' '.join(clean_search.split())
    # Determine selected month from date filters
    selected_month = this_month
    mindates = re.findall(r'date>="([^"]*)"', search)
    maxdates = re.findall(r'date<"([^"]*)"', search)
    if len(mindates) == 1 and len(maxdates) == 1:
        try:
            mindate = parse_date(mindates[0]).replace(day=1)
            maxdate = parse_date(maxdates[0]).replace(day=1)
            # Check if this looks like a month selection (1st of month to 1st of next month)
            next_month = add_months(mindate, 1)
            if mindate.day == 1 and maxdate == next_month:
                selected_month = mindate
        except Exception:
            pass
    # Build set of months to include
    months = {add_months(selected_month, -1), selected_month}
    next_month = add_months(selected_month, 1)
    if next_month <= this_month: months.add(next_month)
    if this_month not in months: months.add(this_month)
    # Generate ordered month links
    month_links = []
    for month in sorted(months):
        if month == this_month:
            selected = selected_month == this_month
            month_links.append({'name':'this month', 'selected':selected, 'query':clean_search})
        else:
            selected = selected_month == month
            month_name_str = f"{month_name[month.month]} {month.year}"
            next_month_date = add_months(month, 1)
            query = f'{clean_search} date>="{month.strftime("%Y-%m-%d")}" date<"{next_month_date.strftime("%Y-%m-%d")}"'.strip()
            month_links.append({'name':month_name_str, 'selected':selected, 'query':query})
    return month_links


def get_filters_by_year(search):
    """ Returns a list of links to navigate the years. """
    this_year = datetime.now().year
    # Remove existing date filters and get clean search
    clean_search = re.sub(r'date[><]=?"[^"]*"?|date[><]=?\S+', '', search).strip()
    clean_search = ' '.join(clean_search.split())
    # Determine selected year from date filters
    selected_year = this_year
    mindates = re.findall(r'date>="([^"]*)"', search)
    maxdates = re.findall(r'date<"([^"]*)"', search)
    if len(mindates) == 1 and len(maxdates) == 1:
        try:
            mindate = parse_date(mindates[0])
            maxdate = parse_date(maxdates[0])
            if (mindate.month == 1 and mindate.day == 1 and maxdate.month == 1
              and maxdate.day == 1 and maxdate.year == mindate.year + 1):
                selected_year = mindate.year
        except Exception:
            pass
    # Build set of years to include
    years = {selected_year - 1, selected_year}
    if selected_year + 1 <= this_year: years.add(selected_year + 1)
    if this_year not in years: years.add(this_year)
    # Generate ordered year links
    year_links = []
    for year in sorted(years):
        if year == this_year:
            selected = selected_year == this_year
            year_links.append({'name':'this year', 'selected':selected, 'query':clean_search})
        else:
            selected = selected_year == year
            query = f'{clean_search} date>="{year}-01-01" date<"{year + 1}-01-01"'.strip()
            year_links.append({'name':str(year), 'selected':selected, 'query':query})
    return year_links


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
