from django.contrib import admin
from polls.models import Market, Outcome, Order, DataSet, Datum
from django.forms.fields import IntegerField
from django import forms
# Register your models here.


class OutcomeInline(admin.StackedInline):
    model = Outcome
    extra = 2

# contains any extras that can be performed from the market admin page. 
# currently includes functionality for dummy (randomised) dataset creation. 
# TODO: allow xml/json serialization. 
class MarketAdminForm(forms.ModelForm):

    extra_field = forms.IntegerField(initial=0)
    


    def save(self, commit=True):
        extra_field = self.cleaned_data.get('extra_field', None)
        # ...do something with extra_field here...

        
        print("creating dataset wohoo!")
        market = super(MarketAdminForm, self).save(commit=commit)
        ds = DataSet.newTrain(market, 10)
        print('done!')

        return market

    class Meta:
        model = Market
        fields = ('description', 'exp_date', 'reveal_interval', 'last_revealed_id')

class DataSetAdminForm(forms.ModelForm):
    class Meta:
        model = DataSet
        fields = ('market', 'is_training',)

    upload_file = forms.FileInput()

    gen_random_entries = forms.IntegerField(initial=0)
    
    def clean(self):
        cleaned_data = super(ContactForm, self).clean()
        cc_myself = cleaned_data.get("cc_myself")
        subject = cleaned_data.get("subject")

    def save(self, commit=True):
        extra_field = self.cleaned_data.get('extra_field', None)
        # ...do something with the extra fields here...
        
        return super(DataSetAdminForm, self).save(commit=commit)


class DataSetAdmin(admin.ModelAdmin):
    form = DataSetAdminForm
    list_display = ('market', 'is_training', 'datum_count')
    fieldsets = ((None, {
            'fields': ('market', 'is_training', 'upload_file', 'gen_random_entries'),
        }),)

class DataSetInline(admin.StackedInline):
    model = DataSet
    fields = ('is_training',)
    extra = 1

class MarketAdmin(admin.ModelAdmin):
    form = MarketAdminForm
    inlines = [OutcomeInline, DataSetInline]
    
    # gets the market we're saving from the inline stuff. 
    def save_model(self, request, obj, form, change):
        self.market = obj
        obj.save()

    def save_formset(self, request, form, formset, change):
        if formset.model != Outcome:
            return super(MarketAdmin, self).save_formset(request, form, formset, change)
        formset.save()
        Market.fix_outcomes(Market, instance=self.market)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('datum', 'claim', 'price', 'amount', 'timestamp')

class OutcomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'market', 'name', 'current_price')

class DatumAdmin(admin.ModelAdmin):
    list_display = ('x', 'y', 'setId', 'data_set')

admin.site.register(Market, MarketAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Outcome, OutcomeAdmin)
admin.site.register(DataSet, DataSetAdmin)
admin.site.register(Datum, DatumAdmin)