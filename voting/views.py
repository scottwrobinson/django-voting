import json

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from voting.utils import get_ip
from voting.models import Vote, VoteCount, UPVOTE, DOWNVOTE

def _update_vote_count(request, votecount, direction):
    '''
    Evaluates a request's Vote and corresponding VoteCount object and,
    after a bit of clever logic, either ignores the request or registers
    a new Vote.

    This is NOT a view!  But should be used within a view ...

    Returns True if the request was considered a Vote; returns False if not.
    '''
    user = request.user
    ip_address = get_ip(request)
    
    net_change = 0

    # TODO: Rate-limit users based on IP to avoid spamming
    #votes_per_ip_limit = getattr(settings, 'VOTECOUNT_VOTES_PER_IP_LIMIT', 0)
    # check limit on votes from a unique ip address (VOTECOUNT_VOTES_PER_IP_LIMIT)
    #if votes_per_ip_limit:
    #    if qs.filter(ip_address__exact=ip_address).count() > votes_per_ip_limit:
    #        return net_change, False

    # Check if the user already voted
    try:
        prev_vote = Vote.objects.get(user=user, votecount=votecount)
        
        # SLOW: Instead of deleting the old and creating a new vote, we really
        # should just alter the old vote's direction and then change the 
        # VoteCounts total accordingly. The VoteCount change should be done
        # in the overridden save() method
        
        # Since the user already voted, remove it. Then check if the new vote
        # is in a different direction, and if so, create that one
        prev_direction = prev_vote.direction
        prev_vote.delete()
        net_change -= prev_direction
        
        if prev_direction != direction:
            # TODO: Is there a better way to refresh this? Like in save()/delete() methods?
            # Reload VoteCount from DB since the previous delete() just changed its up/downvote totals
            votecount = VoteCount.objects.get(id=votecount.id)
            
            vote = Vote(votecount=votecount, direction=direction, ip_address=get_ip(request))
            vote.user = user
            vote.save()
            net_change += direction
    except Vote.DoesNotExist:
        vote = Vote(votecount=votecount, direction=direction, ip_address=get_ip(request))
        vote.user = user
        vote.save()
        net_change += direction

    return net_change, True

def json_error_response(error_message):
    return HttpResponse(json.dumps(dict(success=False, error_message=error_message)))

# TODO better status responses - consider model after django-voting,
# right now the django handling isn't great.  should return the current
# vote count so we could update it via javascript (since each view will
# be one behind).
def update_vote_count_ajax(request):
    '''
    Ajax call that can be used to update a vote count.

    See template tags for how to implement.
    '''

    # make sure this is an ajax request
    if not request.is_ajax():
        raise Http404()

    if request.method == "GET":
        return json_error_response("Votes counted via POST only.")
        
    if not request.user.is_authenticated():
        return json_error_response('You must be authenticated to vote.')

    # TODO: Should probably use a form for validating this
    # Parse inputs
    try:
        votecount_pk = request.POST.get('votecount_pk')
        direction = int(request.POST.get('direction'))
    except ValueError:
        return HttpResponseBadRequest("Invalid vote direction")
    
    # Verify direction is valid
    if direction != UPVOTE and direction != DOWNVOTE:
        return HttpResponseBadRequest("Invalid vote direction")

    # Verify VoteCount pk is valid
    try:
        votecount = VoteCount.objects.get(pk=votecount_pk)
    except:
        return HttpResponseBadRequest("VoteCount object_pk not working")

    net_change, result = _update_vote_count(request, votecount, direction)

    if result:
        status = "success"
    else:
        status = "failed"

    json_response = json.dumps({'status': status, 'net_change':net_change})
    return HttpResponse(json_response, content_type="application/json")
