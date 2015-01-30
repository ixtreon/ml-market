from django.contrib import admin, messages
from markets.models import Market, Outcome, Order, DataSet, Datum, Document, Event, Result, Position
from django.forms.fields import IntegerField
from django import forms
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError


# the market admin form; 
# right now it does nothing
class MarketAdminForm(forms.ModelForm):   
    class Meta:
        model = Market
        fields = ('description', 'type',) 

    user = None
    
# The market admin. 
# Shows an inline form for outcomes 
# and makes sure they exist and sum to one
class MarketAdmin(admin.ModelAdmin):
    form = MarketAdminForm
    list_display = ('description', 'n_events', 'n_datasets', 'is_active', 'pub_date')


# The form used to create Outcome Sets
# An outcome set can be either added manually
# or (TODO) uploaded from a file. 
class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('market', 'description',)
    
# The admin interface for events. 
# Makes sure inline outcomes are normalized. 
class EventAdmin(admin.ModelAdmin):
    class OutcomeInline(admin.TabularInline):
        model = Outcome
        extra = 2
    form = EventAdminForm
    inlines = [OutcomeInline]

    # save the instance to this admin
    # used later to normalize the prices. 
    def save_model(self, request, obj, form, change):
        #print("Saving the outcomes. ")
        self.instance = obj
        obj.save()
    
    # run whenever some subform is being saved. 
    # in this case we handle the Outcome sub-form
    # and make sure the outcomes starting prices sum to 1. 
    def save_formset(self, request, form, formset, change):
        #print("Saving the market forms. ")
        if formset.model != Outcome:
            return super(MarketAdmin, self).save_formset(request, form, formset, change)
        formset.save()

        # make sure the prices are valid
        self.instance.normalise_outcomes()


# The form used to create and edit DataSets. 
# A dataset can be created either from an uploaded file
# or generated randomly. 
class DataSetAdminForm(forms.ModelForm):
    class Meta:
        model = DataSet
        fields = ('market', 
                'description',
                'reveal_interval',
                'is_training')
    # the amount of random entries to generate. 
    n_random_entries = forms.IntegerField(initial=0, required=False)
    # the uploaded file to use as an input. 
    upload_file = forms.ModelChoiceField(queryset=Document.objects.none(), empty_label='None', required=False)

    # gets the files this user has uploaded
    # also removes the upload buttons if editing a set
    def __init__(self, *args, **kwargs):
        super(DataSetAdminForm, self).__init__(*args, **kwargs)
        if self.instance.id:    # if the set is already created
            # disable uploading new data
            self.fields['n_random_entries'].widget.attrs['readonly'] = True
            self.fields['upload_file'].widget.attrs['readonly'] = True
            # disable market changing
            self.fields['market'].queryset = Market.objects.filter(dataset=self.instance)
            self.is_new = False
        else:
            self.is_new = True
            self.fields['upload_file'].queryset = Document.objects.filter(user=self.user)

    # makes sure the selected market has events
    # only checked for new datasets as existing ones can't have their market changed. 
    def clean_market(self):
        market = self.cleaned_data.get('market', 0)
        if self.is_new:
            # raise error if trying to add a dataset for an empty market
            # (a market with no events)
            event_count = market.events.count()
            if event_count == 0:
                raise forms.ValidationError("The current market has no events!")
        return market

    # check whether only one of random/file data sources is set
    def clean(self):
        if self.is_new:
            cleaned_data = super(DataSetAdminForm, self).clean()
            file = cleaned_data.get('upload_file', None)
            n_random = cleaned_data.get('n_random_entries', 0)

            gen_random = n_random > 0
            has_file = file != None
        
            if (gen_random == has_file):
                raise forms.ValidationError("You must choose exactly one data source for the set. ")
        
            # no uploaded file parsing yet. 
            # TODO: check uploaded file's schema 
            # and raise error if it doesn't match events
            if has_file:
                raise forms.ValidationError("Uploaded file parsing is not yet available!")

    # save the cleaned data to the form
    def save(self, commit=True):
        self.file = self.cleaned_data.get('upload_file', None)
        self.n_random = self.cleaned_data.get('n_random_entries', 0)
        return super().save(commit=commit)

class DataSetAdmin(admin.ModelAdmin):
    form = DataSetAdminForm

    fieldsets = [
        (None,  {'fields': ['market', 
            'description',
            'reveal_interval',
            'is_training', ]}),
        ('Data Source', {'fields': ['n_random_entries', 'upload_file']}),
    ]
    list_display = ('market', 'description', 'is_active', 'active_datum_id', 'next_challenge_in',
                'datum_count')

    actions = ['reset', 'start']

    def start(modeladmin, request, queryset):
        "Starts the selected dataset. "
        if queryset.count() != 1:
            modeladmin.message_user(request, "Please select a single data set!", level=messages.ERROR)
        ds = queryset.first()
        
        ds.start()

    # admin action to reset the dataset
    # todo: what about already collected data?
    def reset(modeladmin, request, queryset):
        for ds in queryset:
            ds.reset()

    # sets the user for the DataSetAdminForm
    def get_form(self, request, *args, **kwargs):
         form = super().get_form(request, **kwargs)
         form.user = request.user
         return form
    
    # generate random data or import it from a file
    # whenever a new model is saved/created
    def save_model(self, request, obj, form, change):
        obj.save()
        # generate random data or (TODO) import from a file
        if form.is_new:
            if form.n_random:
                obj.random(form.n_random)
            else:
                assert(obj.file)


    
# the following classes are temporary admin views used for debugging
# TODO: either remove or make these usable
class OrderAdmin(admin.ModelAdmin):
    list_display = ('datum', 'timestamp', 'is_processed')

class PositionAdmin(admin.ModelAdmin):
    list_display = ('order', 'outcome', 'amount', 'contract_price')
    
class OutcomeAdmin(admin.ModelAdmin):
    list_display = ('name', 'set', 'current_price')

class DatumAdmin(admin.ModelAdmin):
    list_display = ('x', 'set_id', 'data_set')

class ResultAdmin(admin.ModelAdmin):
    list_display = ('datum', 'outcome')

# register the above classes with the admin interface. 
admin.site.register(Market, MarketAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(DataSet, DataSetAdmin)
admin.site.register(Datum, DatumAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Result, ResultAdmin)