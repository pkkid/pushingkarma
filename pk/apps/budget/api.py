# encoding: utf-8
from decimal import Decimal
from django_searchquery import searchfields as sf
from pk import utils
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import Account, Category, Transaction


IGNORED = 'Ignored'
RESET_DECIMAL = Decimal('-99999.99')
RESET = ['_RESET', RESET_DECIMAL]
REVERSE = True   # Set 'True' or 'False' for reversed month order.
ACCOUNTSEARCHFIELDS = [
    sf.StrField('name', 'name', desc='Account name', generic=True),
    sf.StrField('fid', 'fid', desc='Financial institution id', generic=True),
    sf.StrField('type', 'type', desc='Account type (bank, credit)'),
    sf.NumField('balance', 'balance', desc='Account balance'),
    sf.DateField('updated', 'balancedt', desc='Last update'),
]
CATEGORYSEARCHFIELDS = [
    sf.StrField('name', 'name', desc='Category name', generic=True),
    sf.StrField('comment', 'comment', desc='Comment'),
]
TRANSACTIONSEARCHFIELDS = {
    sf.StrField('bank', 'account__name', desc='Bank name', generic=True),
    sf.DateField('date', 'date', desc='Transaction date'),
    sf.StrField('payee', 'payee', desc='Transacation payee', generic=True),
    sf.StrField('category', 'category__name', desc='Transaction category', generic=True),
    sf.NumField('amount', 'amount', desc='Transaction amount'),
    sf.BoolField('approved', 'approved', desc='User approved'),
    sf.StrField('comment', 'comment', desc='Comment', generic=True),
}


class AccountSerializer(utils.DynamicFieldsSerializer):
    class Meta:
        model = Account
        fields = ('id', 'url', 'name', 'fid', 'type', 'payee', 'balance', 'balancedt')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        account = Account(**validated_data)
        account.save()
        return account


class AccountsViewSet(viewsets.ModelViewSet, utils.ViewSetMixin):
    """ Rest endpoint to list or modifiy user's financial accounts. """
    serializer_class = AccountSerializer
    queryset = Account.objects.order_by('name')
    permission_classes = [IsAuthenticated]
    list_fields = AccountSerializer.Meta.fields

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).order_by('name')

    def list(self, request, *args, **kwargs):
        return self.list_response(request, paginated=True, searchfields=ACCOUNTSEARCHFIELDS)


class CategorySerializer(utils.DynamicFieldsSerializer):
    class Meta:
        model = Category
        fields = ('id', 'url', 'name', 'sortindex', 'budget', 'comment', 'exclude_budget')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        account = Category(**validated_data)
        account.save()
        return account


class CategoriesViewSet(viewsets.ModelViewSet, utils.ViewSetMixin):
    """ Rest endpoint to list or modifiy user's budget categories. """
    queryset = Category.objects.order_by('-sortindex')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    list_fields = CategorySerializer.Meta.fields
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by('-sortindex')

    def to_internal_value(self, data):
        if data.get('budget'): data['budget'] = utils.clean_amount(data['budget'])
        return super(CategorySerializer, self).to_internal_value(data)

    def list(self, request, *args, **kwargs):
        return self.list_response(request, paginated=True, searchfields=CATEGORYSEARCHFIELDS)


class TransactionSerializer(utils.DynamicFieldsSerializer):
    account = utils.PartialFieldsSerializer(AccountSerializer, ('url', 'name'))
    category = utils.PartialFieldsSerializer(CategorySerializer, ('url', 'name', 'budget'))

    class Meta:
        model = Transaction
        fields = ('id', 'url', 'trxid', 'date', 'payee', 'amount', 'approved',
            'comment', 'account', 'category')

    def to_internal_value(self, data):
        if data.get('amount') in RESET: data['amount'] = RESET_DECIMAL
        elif data.get('amount'): data['amount'] = utils.clean_amount(data['amount'])
        return super(TransactionSerializer, self).to_internal_value(data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        user = self.context['request'].user
        # Update category_name
        category_name = self.context['request'].data.get('category_name')
        if category_name is not None:
            instance.category = None
            if category_name != '':
                instance.category = utils.get_object_or_none(Category, user=user, name__iexact=category_name)
                if not instance.category:
                    raise ValidationError("Unknown category '%s'." % category_name)
        # Some values can be reset
        if self.context['request'].data.get('date') in RESET: instance.date = instance.original_date
        if self.context['request'].data.get('payee') in RESET: instance.payee = instance.original_payee
        if self.context['request'].data.get('amount') in RESET: instance.amount = instance.original_amount
        instance.save()
        return instance


class TransactionsViewSet(viewsets.ModelViewSet, utils.ViewSetMixin):
    """ Rest endpoint to list or modifiy user's transactions. """
    queryset = Transaction.objects.order_by('-date')
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    list_fields = TransactionSerializer.Meta.fields

    def list(self, request, *args, **kwargs):
        return self.list_response(request, paginated=True, searchfields=TRANSACTIONSEARCHFIELDS)
