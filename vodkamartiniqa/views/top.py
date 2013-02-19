from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from vodkamartiniqa.models import Question
from django.db.models import Count
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#from django.core.urlresolvers import reverse


def questioners(request):
    """ list users with more live questions """

    users = User.objects.filter(question__status=Question.LIVE_STATUS).annotate(num_questions=Count('question')).order_by('-num_questions')

    return render_to_response('vodkamartiniqa/top_questioners.html',
                              {'users': users,
                              },
                              RequestContext(request))
