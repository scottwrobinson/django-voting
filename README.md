Django-Voting
=============

Django-Voting is a basic app for tracking the number of votes placed for
any object in the database. It provides the ability to upvote and downvote.

This project is based on the [django-hitcount][1] by Damon Timm.

TODO
----

Most of the basic functionality you'd need for a simple voting system has
been implemented. Possible additions are:

- Better JavaScript support for ajax calls
- Better UI/utilities for the admin site
- Rate-limiting to avoid vote-spamming
- Options for allowing users to vote multiple times on an object

Installation:
-------------

Simplest way to formally install is to run:

    ./setup.py install

Or, you could do a PIP installation:

    pip install -e git://github.com/scottwrobinson/django-voting.git#egg=django-voting

Or, you can link the source to your `site-packages` directory.  This is useful
if you plan on pulling future changes and don't want to keep running
`./setup.py install`.

    cd ~/src
    git clone https://github.com/scottwrobinson/django-voting.git
    sudo ln -s `pwd`/django-voting/voting `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`/voting


Then modify your settings.py, adding the package voting in INSTALLED_APPS

    INSTALLED_APPS = (
        '...',
        'voting',
    )


You need to add one line to your urls.py file.
----------------------------------------------
    urlpatterns = patterns('',
        url(r'^site/ajax/vote$', # you can change this url if you would like
            update_vote_count_ajax,
            name='votecount_update_ajax'), # keep this name the same


Ajax Call
---------
The ajax call to the `update_vote_count_ajax` view requires two variables:

- direction
  The vote direction. +1 for upvote and -1 for downvote.
- votecount_pk
  The pk of the object to be voted on. Can be retrieved using the {% get_vote_object_pk for [object] %} tag (see below).
- csrfmiddlewaretoken (optional)
  The CSRF token. Only required if CSRF validation is enabled.
  
The ajax view returns two variables back:

- status
  "success" for successful votes and "failed" for votes that did not get recorded.
- net_change
  The net change of the object's vote total.

Custom Template Tags
--------------------
Don't forget to load the custom tags with: `{% load voting_tags %}`

- Return total votes for an object:
  `{% get_vote_count for [object] %}`
 
- Get total votes for an object as a specified variable:
  `{% get_vote_count for [object] as [var] %}`
 
- Get total votes for an object over a certain time period:
  `{% get_vote_count for [object] within ["days=1,minutes=30"] %}`
 
- Get total votes for an object over a certain time period as a variable:
  `{% get_vote_count for [object] within ["days=1,minutes=30"] as [var] %}`
  
- Get or create the pk for the given object:
  `{% get_vote_object_pk for [object] %}`
  
- Get or create the pk for the given object as a specified variable:
  `{% get_vote_object_pk for [object] as [var] %}`
  
[1]:https://github.com/thornomad/django-hitcount