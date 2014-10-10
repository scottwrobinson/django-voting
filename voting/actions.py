from django.core.exceptions import PermissionDenied

def delete_queryset(modeladmin, request, queryset):
    # TODO 
    #
    # Right now, when you delete a vote there is no warning or "turing back".
    # Consider adding a "are you sure you want to do this?" as is 
    # implemented in django's contrib.admin.actions file.

    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied
    else:
        if queryset.count() == 1:
            msg = "1 vote was"
        else:
            msg = "%s votes were" % queryset.count()

        for obj in queryset.iterator():
            obj.delete() # calling it this way to get custom delete() method

        modeladmin.message_user(request, "%s successfully deleted." % msg)
delete_queryset.short_description = "DELETE selected votes"
