from django import template
from django.template import TemplateSyntaxError
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.exceptions import MultipleObjectsReturned

from voting.models import VoteCount

register = template.Library()


def get_target_ctype_pk(context, object_expr):
    # I don't really understand how this is working, but I took it from the
    # comment app in django.contrib and the removed it from the Node.
    try:
        obj = object_expr.resolve(context)
    except template.VariableDoesNotExist:
        return None, None

    return ContentType.objects.get_for_model(obj), obj.pk


def return_period_from_string(arg):
    '''
    Takes a string such as "days=1,seconds=30" and strips the quotes
    and returns a dictionary with the key/value pairs
    '''
    period = {}

    if arg[0] == '"' and arg[-1] == '"':
        opt = arg[1:-1] #remove quotes
    else:
        opt = arg

    for o in opt.split(","):
        key, value = o.split("=")
        period[str(key)] = int(value)

    return period
    

class GetVoteCount(template.Node):

    def handle_token(cls, parser, token):
        args = token.contents.split()

        # {% get_vote_count for [obj] %}
        if len(args) == 3 and args[1] == 'for':
            return cls(object_expr = parser.compile_filter(args[2]))
        
        # {% get_vote_count for [obj] as [var] %}
        elif len(args) == 5 and args[1] == 'for' and args[3] == 'as':
            return cls(object_expr = parser.compile_filter(args[2]),
                        as_varname  = args[4],)

        # {% get_vote_count for [obj] within ["days=1,minutes=30"] %}
        elif len(args) == 5 and args[1] == 'for' and args[3] == 'within':
            return cls(object_expr = parser.compile_filter(args[2]),
                        period = return_period_from_string(args[4]))

        # {% get_vote_count for [obj] within ["days=1,minutes=30"] as [var] %}
        elif len(args) == 7 and args [1] == 'for' and \
                args[3] == 'within' and args[5] == 'as':
            return cls(object_expr = parser.compile_filter(args[2]),
                        as_varname  = args[6],
                        period      = return_period_from_string(args[4]))

        else: # TODO - should there be more troubleshooting prior to bailing?
            raise TemplateSyntaxError, \
                    "'get_vote_count' requires " + \
                    "'for [object] in [timeframe] as [variable]' " + \
                    "(got %r)" % args
        
    handle_token = classmethod(handle_token)


    def __init__(self, object_expr, as_varname=None, period=None):
        self.object_expr = object_expr
        self.as_varname = as_varname
        self.period = period


    def render(self, context):
        ctype, object_pk = get_target_ctype_pk(context, self.object_expr)
        
        try:
            obj, created = VoteCount.objects.get_or_create(content_type=ctype, 
                        object_pk=object_pk)
        except MultipleObjectsReturned:
            # from voting.models
            # Because we are using a models.TextField() for `object_pk` to
            # allow *any* primary key type (integer or text), we
            # can't use `unique_together` or `unique=True` to gaurantee
            # that only one VoteCount object exists for a given object.

            # remove duplicate
            items = VoteCount.objects.all().filter(content_type=ctype, object_pk=object_pk)
            obj = items[0]
            for extra_items in items[1:]:
                extra_items.delete()
                
        if self.period: # if user sets a time period, use it
            try:
                votes = obj.votes_in_last(**self.period)
            except:
                votes = '[votecount error w/ time period]'
        else:
            votes = obj.vote_sum
        
        if self.as_varname: # if user gives us a variable to return
            context[self.as_varname] = str(votes)
            return ''
        else:
            return str(votes)


def get_vote_count(parser, token):
    '''
    Returns vote counts for an object.

    - Return total votes for an object: 
      {% get_vote_count for [object] %}
    
    - Get total votes for an object as a specified variable:
      {% get_vote_count for [object] as [var] %}
    
    - Get total votes for an object over a certain time period:
      {% get_vote_count for [object] within ["days=1,minutes=30"] %}

    - Get total votes for an object over a certain time period as a variable:
      {% get_vote_count for [object] within ["days=1,minutes=30"] as [var] %}

    The time arguments need to follow datetime.timedelta's limitations:         
    Accepts days, seconds, microseconds, milliseconds, minutes, 
    hours, and weeks. 
    '''
    return GetVoteCount.handle_token(parser, token)

register.tag('get_vote_count', get_vote_count)

class GetVoteObjectPk(template.Node):

    def handle_token(cls, parser, token):
        args = token.contents.split()
        
        # {% get_vote_object_pk for [obj] %}
        if len(args) == 3 and args[1] == 'for':
            return cls(object_expr = parser.compile_filter(args[2]))
            
        # {% get_vote_object_pk for [obj] as [var] %}
        elif len(args) == 5 and args[1] == 'for' and args[3] == 'as':
            return cls(object_expr = parser.compile_filter(args[2]),
                        as_varname  = args[4],)
        else:
            raise TemplateSyntaxError, \
                    "'get_vote_object_pk' requires " + \
                    "'for [object] as [var]'" + \
                    "(got %r)" % args

    handle_token = classmethod(handle_token)

    def __init__(self, object_expr, as_varname=None):
        self.object_expr = object_expr
        self.as_varname = as_varname

    def render(self, context):
        ctype, object_pk = get_target_ctype_pk(context, self.object_expr)
        obj, created = VoteCount.objects.get_or_create(content_type=ctype, 
                        object_pk=object_pk)
        
        if self.as_varname: # if user gives us a variable to return
            context[self.as_varname] = str(obj.pk) 
            return ''
        else:
            return str(obj.pk)

def get_vote_object_pk(parser, token):
    '''
    Gets or creates the pk for the given object.
    '''
    return GetVoteObjectPk.handle_token(parser, token)

register.tag('get_vote_object_pk', get_vote_object_pk)