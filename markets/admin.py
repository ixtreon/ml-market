from django.contrib import admin
from markets.models import Market, Outcome, Order, DataSet, Datum, Document
from django.forms.fields import IntegerField
from django import forms
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
# Register your models here.



# the market admin form; 
# right now it makes sure pub_date is set to today when we save a
class MarketAdminForm(forms.ModelForm):   
    class Meta:
        model = Market
        fields = ('description',) 

    user = None

    #def clean_last_revealed_id(self):
    #    # get the user-specified last-revealed id
    #    data = self.cleaned_data['last_revealed_id']
    #    try:    # as int
    #        last_id = int(data)
    #    except:
    #        raise forms.ValidationError("This value must be an integer. ")

    #    # check if there is such a challenge for any (!!) of this market's datasets. 
    #    if last_id != -1:
    #        try:
    #            sets = Datum.objects.get(data_set__market=self.instance, setId=last_id)
    #        except ObjectDoesNotExist:
    #            raise forms.ValidationError("There is no such challenge for this market!")
    #        except MultipleObjectsReturned:
    #            raise Exception("Too many challenges with this id! Corrupted db?.. ")
    #    return data

    # if published_date is None 
    # (the default when creating a new market)
    # set it to today. 
    def save(self, commit=True):
        market = super(MarketAdminForm, self).save(commit=False)
        if market.pub_date == None:
            market.pub_date = timezone.now()
        market.save(commit=commit)
        return market


# The form used to create DataSets. 
# A dataset can be created either from an uploaded file
# or generated randomly. 
class DataSetAdminForm(forms.ModelForm):
    class Meta:
        model = DataSet
        fields = (
            'market', 
            'description',
            'reveal_interval',
            'is_training', 
            )
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
            self.fields['n_random_entries'].widget.attrs['readonly'] = True
            self.fields['upload_file'].widget.attrs['readonly'] = True
            self.is_new = False
            print(self.fields)
        else:
            self.is_new = True
            self.fields['upload_file'].queryset = Document.objects.filter(user=self.user)

    # check whether only one of random/file data sources is set
    def clean(self):
        if self.is_new:
            cleaned_data = super(DataSetAdminForm, self).clean()
            file = cleaned_data.get('upload_file', None)
            n_random = cleaned_data.get('n_random_entries', 0)

            gen_random = n_random > 0
            has_file = file != None
        
            if (gen_random == has_file):
                raise forms.ValidationError("You must choose exactly one source for the data set. ")
        
            # no uploaded file parsing yet. 
            if has_file:
                raise forms.ValidationError("Uploaded file parsing not yet available!")

    # Checks whether we are to parse an uploaded file
    # or to generate random entries. Then does it. 
    def save(self, commit=True):
        file = self.cleaned_data.get('upload_file', None)
        n_random = self.cleaned_data.get('n_random_entries', 0)
        # if we are here then exactly one of n_random, file would be non-default
        
        if n_random > 0:
            DataSet.new_random(self.instance.market, n_random)
        else:
            pass    # nyi - see if clean throws a validation error


        return super(DataSetAdminForm, self).save(commit=commit)
    

class DataSetAdmin(admin.ModelAdmin):
    form = DataSetAdminForm
    list_display = ('market', 'description', 'is_active', 'datum_count')
    actions = ['reset', 'start']
    def start(modeladmin, request, queryset):
        if queryset.count() == 1:
            queryset.first().start()
        else:
            print("tried to activate 0 or 2+ datasets")
            
    def reset(modeladmin, request, queryset):
        for ds in queryset:
            ds.reset()

    # sets the user for the DataSetAdminForm
    def get_form(self, request, *args, **kwargs):
         form = super(DataSetAdmin, self).get_form(request, **kwargs)
         form.user = request.user
         return form
     
class OutcomeInline(admin.StackedInline):
    model = Outcome
    extra = 2

class MarketAdmin(admin.ModelAdmin):
    form = MarketAdminForm
    inlines = [OutcomeInline]
    list_display = ('description', 'pub_date')
    
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

# the following 3 classes are temporary admin views used for debugging
# TODO: remove or make these usable
class OrderAdmin(admin.ModelAdmin):
    list_display = ('datum', 'timestamp', 'is_processed')

class OutcomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'market', 'name', 'current_price')

class DatumAdmin(admin.ModelAdmin):
    list_display = ('x', 'y', 'set_id', 'data_set')

# register the above classes with the admin interface. 
admin.site.register(Market, MarketAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Outcome, OutcomeAdmin)
admin.site.register(DataSet, DataSetAdmin)
admin.site.register(Datum, DatumAdmin)