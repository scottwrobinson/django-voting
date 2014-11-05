from django.contrib import admin

from voting.models import Vote, VoteCount, UPVOTE, DOWNVOTE
from voting import actions

def created_format(obj):
    '''
    Format the created time for the admin. PS: I am not happy with this.
    '''
    return "%s" % obj.date_created.strftime("%m/%d/%y<br />%H:%M:%S")
created_format.short_description = "Date (UTC)"
created_format.allow_tags = True
created_format.admin_order_field = 'date_created'

def direction_format(obj):
    '''
    Format the vote direction.
    '''
    return 'Upvote' if obj.direction == UPVOTE else 'Downvote'
direction_format.short_description = 'Direction'
direction_format.allow_tags = True
direction_format.admin_order_field = 'direction'


class VoteAdmin(admin.ModelAdmin):
    list_display = (created_format, 'user', direction_format, 'ip_address','votecount')
    search_fields = ('ip_address',)
    date_hierarchy = 'date_created'
    actions = [ actions.delete_queryset, ]

    def __init__(self, *args, **kwargs):
        super(VoteAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None,)

    def get_actions(self, request):
        # Override the default `get_actions` to ensure that our model's
        # `delete()` method is called.
        actions = super(VoteAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

# TODO: Add inlines to the VoteCount object so we can see a list of the recent
# votes for the object.  For this inline to work, we need to:
#   a) be able to see the vote data but *not* edit it
#   b) have the `delete` command actually alter the VoteCount
#   c) remove the ability to 'add new vote'
#
#class VoteInline(admin.TabularInline):
#    model = Vote
#    fk_name = 'votecount'
#    extra = 0

class VoteCountAdmin(admin.ModelAdmin):
    list_display = ('content_object','vote_sum','modified')
    fields = ('upvotes', 'downvotes')
    
    # TODO: Another option
    #The fields option, unlike list_display, may only contain names of fields on the model or the form specified by form. It may contain callables only if they are listed in readonly_fields.

    # TODO - when above is ready
    #inlines = [ VoteInline, ]
 
admin.site.register(Vote, VoteAdmin)
admin.site.register(VoteCount, VoteCountAdmin) 
