import datetime

from django.db import models
from django.conf import settings
from django.db.models import F
from django.utils import timezone

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.encoding import force_text

from django.dispatch import Signal

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

VOTE_DIRECTIONS = (('up', 1), ('down', -1))
UPVOTE = 1
DOWNVOTE = -1

# EXCEPTIONS #

class DuplicateContentObject(Exception):
    'If content_object already exists for this model'
    pass

class VoteCountManager(models.Manager):
    def for_object(self, obj):
        """
        QuerySet for all votes for a particular model (either an instance or
        a class).
        """
        ct = ContentType.objects.get_for_model(obj)
        qs = self.get_queryset().filter(content_type=ct)
        if isinstance(obj, models.Model):
            qs = qs.filter(object_pk=force_text(obj._get_pk_val()))
        return qs
        
    def get_for_object(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        pk = force_text(obj._get_pk_val())
        return self.get_queryset().get(content_type=ct, object_pk=pk)

# MODELS #

class VoteCount(models.Model):
    '''
    Model that stores the vote totals for any content object.

    '''
    
    objects = VoteCountManager()
    
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    modified = models.DateTimeField(default=timezone.now)
    content_type = models.ForeignKey(ContentType,
                        verbose_name="content type",
                        related_name="content_type_set_for_%(class)s",)
    object_pk = models.TextField('object ID')
    content_object = generic.GenericForeignKey('content_type', 'object_pk')
    
    @property
    def vote_sum(self):
        return self.upvotes - self.downvotes

    class Meta:
        #ordering = ( '-vote_sum', )    # TODO: Ordering is not free, so should we really include this?
        #unique_together = (("content_type", "object_pk"),)
        get_latest_by = 'modified'
        #db_table = 'votecount_vote_count'
        verbose_name = 'Vote Count'
        verbose_name_plural = 'Vote Counts'

    def __unicode__(self):
        return u'%s' % self.content_object

    def save(self, *args, **kwargs):
        self.modified = timezone.now()

        if not self.pk and self.object_pk and self.content_type:
            # Because we are using a models.TextField() for `object_pk` to
            # allow *any* primary key type (integer or text), we
            # can't use `unique_together` or `unique=True` to gaurantee
            # that only one VoteCount object exists for a given object.
            #
            # This is just a simple hack - if there is no `self.pk`
            # set, it checks the database once to see if the `content_type`
            # and `object_pk` exist together (uniqueness).  Obviously, this
            # is not fool proof - if someone sets their own `id` or `pk` 
            # when initializing the VoteCount object, we could get a duplicate.
            if VoteCount.objects.filter(
                    object_pk=self.object_pk).filter(content_type=self.content_type):
                raise DuplicateContentObject, "A VoteCount object already " + \
                        "exists for this content_object."

        super(VoteCount, self).save(*args, **kwargs)

    # TODO: Add kwarg for specifying if we want count for upvotes, downvotes, or all votes
    def votes_in_last(self, **kwargs):
        '''
        Returns number of votes for an object during a given time period. THIS
        IS NOT THE VOTE SUM, just the number of votes cast (upvote OR downvote).

        This will only work for as long as votes are saved in the Vote database.
        If you are purging your database after 45 days, for example, that means
        that asking for votes in the last 60 days will return an incorrect
        number as that the longest period it can search will be 45 days.
        
        For example: votes_in_last(days=7).

        Accepts days, seconds, microseconds, milliseconds, minutes, 
        hours, and weeks.  It's creating a datetime.timedelta object.
        '''
        assert kwargs, "Must provide at least one timedelta arg (eg, days=1)"
        period = timezone.now() - datetime.timedelta(**kwargs)
        return self.vote_set.filter(date_created__gte=period).count()

    def get_content_object_url(self):
        '''
        Django has this in its contrib.comments.model file -- seems worth
        implementing though it may take a couple steps.
        '''
        pass
        
class VoteManager(models.Manager):
    def for_votecount(self, votecount):
        """
        QuerySet for all votes for a particular votecount.
        """
        qs = self.get_queryset()
        if isinstance(votecount, VoteCount):
            qs = qs.filter(votecount=votecount)
        return qs

class Vote(models.Model):
    '''
    Model captures a single Vote by a user.

    None of the fields are editable because they are all dynamically created.
    '''
    
    objects = VoteManager()
    
    user = models.ForeignKey(AUTH_USER_MODEL, editable=False)
    votecount = models.ForeignKey(VoteCount, editable=False)
    direction = models.IntegerField(choices=VOTE_DIRECTIONS)
    ip_address = models.GenericIPAddressField(editable=False)
    date_created = models.DateTimeField(editable=False)

    class Meta:
        ordering = ( '-date_created', )    
        get_latest_by = 'date_created'
        
    def __unicode__(self):
        vote_type = 'Upvote' if self.type == UPVOTE else 'Downvote'
        return vote_type + ' by ' + str(self.user)

    def save(self, *args, **kwargs):
        '''
        The first time the object is created and saved, we set
        the date_created field.
        '''
        if not self.date_created:
            if self.direction == UPVOTE:
                self.votecount.upvotes += 1
            else:
                self.votecount.downvotes += 1
            self.votecount.save()
            self.date_created = timezone.now()

        super(Vote, self).save(*args, **kwargs)


    def delete(self, save_votecount=False):
        '''
        If a Vote is deleted and save_votecount=True, it will preserve the 
        VoteCount object's total.  However, under normal circumstances, a 
        delete() will trigger a subtraction from the VoteCount object's total.

        NOTE: This doesn't work at all during a queryset.delete().
        '''
        if not save_votecount:
            if self.direction == UPVOTE:
                self.votecount.upvotes -= 1
            else:
                self.votecount.downvotes -= 1
            self.votecount.save()
        super(Vote, self).delete()
