#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import datetime, re, shlex
from functools import reduce
from types import SimpleNamespace

NONE = ('none', 'null')
OPERATIONS = {'=':'', '>':'__gt', '>=':'__gte', '<=':'__lte', '<':'__lt', ':': '__icontains'}
STOPWORDS = ('and', '&&', '&', 'or', '||', '|')

FIELDTYPES = SimpleNamespace()
FIELDTYPES.NUM = 'numeric'
FIELDTYPES.STR = 'string'


class SearchError(Exception):
    pass


class SearchField:

    def __init__(self, fieldtype, field, modifier=None):
        self.fieldtype = fieldtype      # field type (NUM, STR, ...)
        self.field = field              # model field lookup (ex: account__first_name)
        self.modifier = modifier        # callback to modify search_value comparing
        
    def __str__(self):
        return '<%s:%s:%s>' % (self.__class__.__name__, self.fieldtype, self.field)
        
        
class Search:
    
    def __init__(self, basequeryset, fields, searchstr):
        self.errors = []                            # list of errors to display
        self.warnings = []                          # list of warnings to display
        self.datefilters = []                       # list of date translations to display
        self.basequeryset = basequeryset            # base queryset to filter in Search
        self.fields = fields                        # field objects to filter on
        self.searchstr = searchstr                  # orignal Search String
        self._queryset = None                       # final queryset
        self.chunks = self._build_chunks()          # search chunks
    
    def _build_chunks(self):
        try:
            chunkstrs = shlex.split(self.searchstr)
            for chunk in [c for c in chunkstrs if c in STOPWORDS]:
                self.warnings.append('Part of the search is being ignored: %s' % chunk)
            return [SearchChunk(self, c) for c in chunkstrs if c not in STOPWORDS]
        except Exception as err:
            print('Error: %s' % err)
            self.errors.append(Exception('Invalid query: %s' % err))

    def _list_datefilters(self):
        datefilters = []
        datestrings = [c.datefilter for c in self.chunks if c.datefilter]
        for datestring in datestrings:
            opused = None
            for operation, qoperation in OPERATIONS.items():
                if qoperation:
                    opused = operation
                    datestring = datestring.replace(qoperation, ' %s' % operation)
            if not opused:
                datestring = datestring.replace(' ', ' = ' % operation)
            datestring = datestring.replace('__', '.')
            datefilters.append(datestring)
        return datefilters
            
    def queryset(self):
        if self._queryset is None:
            if self.errors:
                print('%s errors found in search!' % len(self.errors))
                self._queryset = self.basequeryset.filter(pk=-1)
            else:
                queryset = self.basequeryset
                for chunk in self.chunks:
                    queryset = queryset & chunk.queryset()
                self.errors = [c.error for c in self.chunks if c.error]
                self.datefilters = self._list_datefilters()
                self._queryset = queryset
        return self._queryset
        
    
class SearchChunk:
    
    def __init__(self, search, chunkstr):
        self.search = search            # reference to parent search object
        self.chunkstr = chunkstr        # single part of search.searchstr
        self.exclude = False            # set True if this is an exclude
        self.field = None               # search field from chunkstr
        self.operation = None           # search operation from chunkstr
        self.value = None               # search value from chunkstr
        self.qfield = None              # django query field
        self.qoperation = None          # django query operation
        self.qvalue = None              # django query value
        self.error = None               # error message (if applicable)
        self.datefilter = None          # date filter representation
        self._parse_chunkstr()
        
    def __str__(self):
        rtnstr = '\n--- %s ---\n' % self.__class__.__name__
        for attr in ('chunkstr','exclude','field','value','qfield','qoperation','qvalue','error'):
            value = getattr(self, attr)
            if value is not None:
                rtnstr += '%-12s %s\n' % (attr + ':', value)
        return rtnstr
        
    @property
    def searchtype(self):
        if self.operation == ':':
            return FIELDTYPES.STR
        return self.search.fields.get(self.field).fieldtype
        
    @property
    def is_value_list(self):
        if len(self.value) == 0:
            return False
        return self.value[0] == '[' and self.value[-1] == ']'
        
    def _parse_chunkstr(self):
        try:
            chunkstr = self.chunkstr
            # check exclude pattern
            if '-' == chunkstr[0]:
                self.exclude = True
                chunkstr = chunkstr[1:]
            # save default value and operation
            self.value = chunkstr
            self.qvalue = chunkstr
            self.operation = ':'
            # check advanced search operations
            for operation in sorted(OPERATIONS.keys(), key=len, reverse=True):
                parts = chunkstr.split(operation, 1)
                if len(parts) == 2:
                    # extract field, operation, and value
                    self.field = parts[0]
                    self.operation = operation
                    self.value = parts[1]
                    # fetch the qfield, qoperation, and qvalue
                    self.qfield = self._get_qfield()
                    self.qoperation = self._get_qoperation()
                    self.qvalue = self._get_qvalue()
                    break  # only use one operation
        except SearchError as err:
            self.error = err
            
    def _get_qfield(self):
        field = self.search.fields.get(self.field)
        if not field:
            raise SearchError('Unknown field: %s' % self.field)
        elif self.searchtype != field.fieldtype:
            raise SearchError('Unknown %s field: %s' % (self.searchtype, self.field))
        return field
    
    def _get_qoperation(self):
        # check were searching none
        if self.value.lower() in NONE:
            return '__in'
        # regex will catch invalid operations, no need to check
        operation = OPERATIONS[self.operation]
        if self.is_value_list and self.operation == '=':
            operation = '__in'
        return operation
        
    def _get_qvalue(self):
        # check were searching none
        if self.value.lower() in NONE:
            return [None, '']
        # get correct modifier
        modifier = lambda value: value
        if self.qfield.modifier:
            modifier = self.qfield.modifier
        elif self.searchtype == FIELDTYPES.NUM:
            modifier = modifier_numeric
        # process the modifier
        if self.is_value_list:
            return self._parse_value_list(modifier)
        return modifier(self.value)
        
    def _parse_value_list(self, modifier):
        if self.operation != '=':
            raise SearchError('Invalid operation is using list search: %s' % self.operation)
        qvalues = set()
        values = self.value.lstrip('[').rstrip(']')
        for value in values.split(','):
            qvalues.add(modifier(value))
        return qvalues
        
    def queryset(self):
        queryset = self.search.basequeryset.all()
        if self.error:
            return queryset
        elif not self.field:
            return queryset & self._queryset_generic()
        elif type(self.value) == datetime:
            return queryset & self._queryset_datetime()
        return queryset & self._queryset_advanced()
        
    def _queryset_generic(self):
        # create a list of subqueries
        subqueries = []
        stringfields = (f for f in self.search.fields.values() if f.fieldtype == FIELDTYPES.STR)
        for field in stringfields:
            kwarg = '%s%s' % (field.field, OPERATIONS[':'])
            if self.exclude:
                subquery = self.search.basequeryset.exclude(**{kwarg: self.qvalue})
                subqueries.append(subquery)
                continue
            subquery = self.search.basequeryset.filter(**{kwarg: self.qvalue})
            subqueries.append(subquery)
        # join and return the subqueries
        if self.exclude:
            return reduce(lambda x,y: x & y, subqueries)
        return reduce(lambda x,y: x | y, subqueries)
        
    def _queryset_advanced(self):
        kwarg = '%s%s' % (self.qfield.field, self.qoperation)
        if self.exclude:
            return self.search.basequeryset.exclude(**{kwarg: self.qvalue})
        return self.search.basequeryset.filter(**{kwarg: self.qvalue})

    def _queryset_date(self):
        return self.search.basequeryset


def modifier_numeric(value):
    if re.match('^\d+$', value):
        return int(value)
    elif re.match('^\d+.\d+$'):
        return float(value)
    raise SearchError('Invalid int value: %s' % value)
