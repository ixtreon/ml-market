from django.contrib import admin, messages
from markets.models import Market, Outcome, Order, DataSet, Datum, Document, Event, Result, Position
from django.forms.fields import IntegerField
from django import forms
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError


# the market admin form; 
# right now it makes sure pub_date is set to today when we save a market
class MarketAdminForm(forms.ModelForm):   
    class Meta:
        model = Market
        fields = ('description',) 

    user = None
    
    def clean(self):
        cleaned_data = self.cleaned_data

        #n_outcomes = self.instance.outcome_set.count()
        #if n_outcomes == 0:
        #    raise ValidationError("KUR")

    # if published_date is None set it to today. 
    # (the default when creating a new market)
    def save(self, commit=True):
        market = super(MarketAdminForm, self).save(commit=False)
        if market.pub_date == None:
            market.pub_date = timezone.now()
        market.save(commit=commit)
        return market

# The market admin. 
# Shows an inline form for outcomes 
# and makes sure they exist and sum to one
class MarketAdmin(admin.ModelAdmin):
    form = MarketAdminForm
    list_display = ('description', 'n_events', 'n_datasets', 'is_active')


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
        print("saving the outcomes...")
        self.instance = obj
        obj.save()
    

    # run whenever some subform is being saved. 
    # in this case we handle the Outcome sub-form
    # and make sure the outcomes starting prices sum to 1. 
    def save_formset(self, request, form, formset, change):
        print("saving the market forms..")
        if formset.model != Outcome:
            return super(MarketAdmin, self).save_formset(request, form, formset, change)
        formset.save()

        print("fixing outcomes..")
        self.instance.fix_outcomes()
        print("done!")
        # Market.fix_outcomes(Market, instance=self.market)


# The form used to create and edit DataSets. 
# A dataset can be created either from an uploaded file
# or generated randomly. 
class DataSetAdminForm(forms.ModelForm):
    class Meta:
        model = DataSet
        fields = ('market', 
                'description',
                'reveal_interval',
                'is_training',)
    # the amount of random entries to generate. 
    # if <= 0, then no random entries are generated. 
    n_random_entries = forms.IntegerField(initial=0, required=False)
    # the uploaded file to use as an input. 
    upload_file = forms.ModelChoiceField(queryset=Document.objects.none(), empty_label='None', required=False)

    # gets the files this user has uploaded
    # also removes the upload buttons if editing a set
    def __init__(self, *args, **kwargs):
        super(DataSetAdminForm, self).__init__(*args, **kwargs)
        if self.instance.id:    
            # disable uploading new data if the set is already created. 
            self.fields['n_random_entries'].widget.attrs['readonly'] = True
            self.fields['upload_file'].widget.attrs['readonly'] = True
            # disable market changing. 
            self.fields['market'].queryset = Market.objects.filter(dataset=self.instance)
            self.is_new = False
        else:
            self.is_new = True
            self.fields['upload_file'].queryset = Document.objects.filter(user=self.user)
            #self.fields['market'].queryset = Market.objects.filter(event_set__count>0)

    def clean_market(self):
        if self.is_new:
            market = self.cleaned_data.get('market', 0)
            # raise error if trying to add a dataset for an empty market
            # (a market with no events)
            event_count = market.event_set.count()
            if event_count == 0:
                raise forms.ValidationError("The current market has no events!")


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


    def save(self, commit=True):
        self.file = self.cleaned_data.get('upload_file', None)
        self.n_random = self.cleaned_data.get('n_random_entries', 0)
        return super(DataSetAdminForm, self).save(commit=commit)
    
class DataSetAdmin(admin.ModelAdmin):
    form = DataSetAdminForm

    fieldsets = [
        (None,               {'fields': ['market', 
            'description',
            'reveal_interval',
            'is_training', ]}),
        ('Data Source', {'fields': ['n_random_entries', 'upload_file']}),
    ]
    list_display = ('market', 'description', 'is_active', 'datum_count')
    actions = ['reset', 'start']

    def start(modeladmin, request, queryset):
        "Starts the selected dataset. "
        if queryset.count() != 1:
            modeladmin.message_user(request, "Please select a single data set!", level=messages.ERROR)
        queryset.first().start()
        # todo: set start, next dates?

            
    def reset(modeladmin, request, queryset):
        for ds in queryset:
            ds.reset()

    # sets the user for the DataSetAdminForm
    def get_form(self, request, *args, **kwargs):
         form = super(DataSetAdmin, self).get_form(request, **kwargs)
         form.user = request.user
         return form

    def save_model(self, request, obj, form, change):
        obj.save()
        if form.is_new:
            if form.n_random:
                obj.new_random(form.n_random)
            else:
                assert(obj.file)
                pass    # TODO: handle parsing of uploaded files somehow. 

    def save(self, *args, **kwargs):
        super(Model, self).save(*args, **kwargs)
     

    
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