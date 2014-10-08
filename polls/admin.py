from django.contrib import admin
from polls.models import Claim, Outcome
# Register your models here.


class OutcomeInline(admin.StackedInline):
    model = Outcome
    extra = 2

class ClaimAdmin(admin.ModelAdmin):
    
    list_display = ('description', 'pub_date', 'real_outcome')
    inlines = [OutcomeInline]

admin.site.register(Claim, ClaimAdmin)
#admin.site.register(Outcome)