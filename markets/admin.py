from django.contrib import admin
from markets.models import Market, Outcome, Order, DataSet, Datum, Document
from django.forms.fields import IntegerField
from django import forms
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
# Register your models here.


class OutcomeInline(admin.StackedInline):
    model = Outcome
    extra = 2

# contains any extras that can be performed from the market admin page. 
# currently includes functionality for dummy (randomised) dataset creation. 
# TODO: allow xml/json serialization. 
class MarketAdminForm(forms.ModelForm):

    extra_field = forms.IntegerField(initial=0)
    
    
    def __init__(self, *args, **kwargs):
        super(MarketAdminForm, self).__init__(*args, **kwargs)

    def clean_last_revealed_id(self):
        data = self.cleaned_data['last_revealed_id']

        try:
            last_id = int(data)
        except:
            raise forms.ValidationError("This value must be an integer. ")

        # check if there is such challenge for any of this market's datasets. 
        if last_id != -1:
            try:
                sets = Datum.objects.get(data_set__market=self.instance, setId=last_id)
            except ObjectDoesNotExist:
                raise forms.ValidationError("There is no challenge with such id!")
            except MultipleObjectsReturned:
                raise Exception("Too many challenges with this id! Corrupted db?.. ")
        return data



    def save(self, commit=True):
        extra_field = self.cleaned_data.get('extra_field', None)
        # ...do something with extra_field here...

        
        print("market admin save.. ")
        # set the pub_date field to today, now. 
        market = super(MarketAdminForm, self).save(commit=False)
        market.pub_date = timezone.now()
        market.save(commit=commit)
        #ds = DataSet.newTrain(market, 10)
        print('done!')

        return market

    class Meta:
        model = Market
        fields = ('description', 'exp_date', 'reveal_interval', 'last_revealed_id')

# The form used to create DataSets. 
# A dataset can be created either from an uploaded file
# or generated randomly. 
class DataSetAdminForm(forms.ModelForm):
    class Meta:
        model = DataSet
        fields = ('market', 'is_training',)

    upload_file = forms.ModelChoiceField(queryset=Document.objects, empty_label='None')

    n_random_entries = forms.IntegerField(initial=0)
    
    def get_form(self, request, **kwargs):
         form = super(DataSetAdminForm, self).get_form(request, **kwargs)
         form.user = request.user
         self.fields['upload_file'].queryset = Document.objects.filter(user=self.user)
         print('get form')
         return form
   
    def __init__(self, *args, **kwargs):
        super(DataSetAdminForm, self).__init__(*args, **kwargs)
        # set the uploaded file dropdown


    def clean(self):
        cleaned_data = super(ContactForm, self).clean()

    # todo: generate random data
    def save(self, commit=True):
        file = self.cleaned_data.get('upload_file', None)
        n_random = self.cleaned_data.get('n_random_entries', None)
        # ...do something with the extra fields here...
        
        return super(DataSetAdminForm, self).save(commit=commit)


class DataSetAdmin(admin.ModelAdmin):
    form = DataSetAdminForm
    list_display = ('market', 'is_training', 'datum_count')

class DataSetInline(admin.StackedInline):
    model = DataSet
    fields = ('is_training',)
    extra = 1

class MarketAdmin(admin.ModelAdmin):
    form = MarketAdminForm
    inlines = [OutcomeInline, DataSetInline]
    list_display = ('description', 'pub_date', 'last_revealed_id')
    
    # gets the market we're saving from the inline stuff. 
    def save_model(self, request, obj, form, change):
        print("saving the market...")
        self.market = obj
        obj.save()
    
    # run whenever some subform is being saved. 
    # in this case we want to handle the Outcome sub-form
    # and make sure the outcomes starting prices sum to 1. 
    def save_formset(self, request, form, formset, change):
        print("saving the market forms..")
        if formset.model != Outcome:
            return super(MarketAdmin, self).save_formset(request, form, formset, change)
        formset.save()

        print("fixing outcomes..")
        Market.fix_outcomes(Market, instance=self.market)

# the following 3 are temporary admin views used for debugging
# todo: remove or make these usable
class OrderAdmin(admin.ModelAdmin):
    list_display = ('datum', 'claim', 'price', 'amount', 'timestamp')

class OutcomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'market', 'name', 'current_price')

class DatumAdmin(admin.ModelAdmin):
    list_display = ('x', 'y', 'setId', 'data_set')

# register the above classes with the admin interface. 

admin.site.register(Market, MarketAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Outcome, OutcomeAdmin)
admin.site.register(DataSet, DataSetAdmin)
admin.site.register(Datum, DatumAdmin)