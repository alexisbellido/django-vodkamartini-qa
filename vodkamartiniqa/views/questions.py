from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponsePermanentRedirect
from django.db.models import F
from django.conf import settings
from django.template.loader import render_to_string
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from vodkamartiniqa.models import Question
from vodkamartiniqa import signals
from vodkamartiniqa.forms import QuestionForm, AnswerForm
from vodkamartiniqa.views.helpers import get_questions
from vodkamartiniarticle.helper import get_client_ip
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from vodkamartiniauth.forms import LoginForm
import urlparse
from django.contrib.auth import login as auth_login
from django.contrib.sites.models import get_current_site
import datetime
from django.core.urlresolvers import reverse
import logging
from django.utils.html import escape
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_cookie
from django.utils.cache import patch_vary_headers
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.utils.text import Truncator
import json
from django.utils.html import strip_tags

def questions_index(request, page=1):
    """ list on questions home"""

    # only needed if no other object that bypasses the lazy loading is being called on the view or template
    bypass_lazyload = request.user.is_authenticated()

    # use this for debug toolbar settings.INTERNAL_IPS
    #print request.META['REMOTE_ADDR']

    #questions_list = Question.live.all()
    # important for reducing queries if displaying the username on template
    # see https://docs.djangoproject.com/en/dev/ref/models/querysets/#select-related
    # in other cases could use values()
    # see https://docs.djangoproject.com/en/dev/topics/db/optimization/#don-t-retrieve-things-you-don-t-need

    # TODO create different queries to return questions with expert answers or not according to design

    # ordering by has_expert_answer and then by answers count
    #questions_list = Question.live.select_related().annotate(num_answers=Count('answer')).order_by('-has_expert_answer', '-num_answers')

    # all questions
    # questions_list = Question.live.select_related().annotate(num_answers=Count('answer')).order_by('-created')

    offset = 9
    questions_list = get_questions(with_experts_answers = False, type='latest', start=0, end=offset)
    experts_questions_list = get_questions(with_experts_answers = True, type='latest', start=0, end=offset)

    redirect_to = request.REQUEST.get('next', '')
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = QuestionForm(author=request.user, data=request.POST, request=request)
            if form.is_valid():
                question = form.save()
                #import pdb; pdb.set_trace()
                messages.add_message(request, messages.INFO, 'Your question has been published.')
                return HttpResponseRedirect(question.get_absolute_url())
        else:
            form = QuestionForm(author=request.user, request=request)
    else:
        if request.method == "POST":
            form = LoginForm(data=request.POST)
            if form.is_valid():
                netloc = urlparse.urlparse(redirect_to)[1]

                # Use default setting if redirect_to is empty
                if not redirect_to:
                    redirect_to = settings.LOGIN_REDIRECT_URL

                # Heavier security check -- don't allow redirection to a different
                # host.
                elif netloc and netloc != request.get_host():
                    redirect_to = settings.LOGIN_REDIRECT_URL

                # Okay, security checks complete. Log the user in.
                auth_login(request, form.get_user())

                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()
                return HttpResponseRedirect(redirect_to)
        else:
            form = LoginForm(request)

        request.session.set_test_cookie()
        current_site = get_current_site(request)

    return render_to_response('vodkamartiniqa/question_list.html',
                              {
                                'object_list': questions_list,
                                'experts_object_list': experts_questions_list,
                                'form': form,
                                'next': redirect_to,
                              },
                              RequestContext(request))

    #paginate_by = 9 
    #paginator = Paginator(questions_list, paginate_by)

    #try:        
    #    # TODO get it from request.GET, for example ?page=1 and then we can use canonical to avoid URLs with ?page
    #    page = int(page)
    #except ValueError:
    #    page = 1

    #try:
    #    questions = paginator.page(page)
    #except PageNotAnInteger:
    #    # If page is not an integer, deliver first page.
    #    questions = paginator.page(1)
    #except EmptyPage:
    #    # If page is out of range, deliver last page.
    #    questions = paginator.page(paginator.num_pages)

    #return render_to_response('vodkamartiniqa/question_list.html',
    #                          {'object_list': questions.object_list,
    #                           'questions': questions,
    #                          },
    #                          RequestContext(request))

def get_questions_ajax(request, with_experts_answers='regular', type='latest', start=0, end=8):
    objects = get_questions(True if with_experts_answers == 'experts' else False, type, start, end)

    questions = []
    truncate_at = 32
    for object in objects:
        created_date = object.created.strftime("%B %e, %Y")
        if object.teaser_html:
            teaser = object.teaser_html
        else:
            teaser = Truncator(object.body_html).words(truncate_at, html=True, truncate=' ...')
        questions.append({
                            'id': object.id,
                            'title': object.title,
                            'user': object.author.username,
                            'created_date': created_date,
                            'url': object.get_absolute_url(),
                            'teaser_html': teaser,
                            'votes_up': object.votes_up,
                            'votes_down': object.votes_down,
                            'num_answers': object.num_answers,
                        })

    return HttpResponse(json.dumps(questions), mimetype='application/json')

# TODO maybe check permission inside view?
@permission_required('vodkamartiniqa.add_question')
def question_add(request):
    """
    @permission_required will check for permission and ask for login, there's no need for extra @login_required.
    """
    #logging.debug(request.user)
    if request.method == 'POST':
        form = QuestionForm(author=request.user, data=request.POST, request=request)
        if form.is_valid():
            question = form.save()
            #import pdb; pdb.set_trace()
            messages.add_message(request, messages.INFO, 'Your question has been published.')
            return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = QuestionForm(author=request.user, request=request)
    return render_to_response('vodkamartiniqa/question_form.html',
                              {
                               'form': form,
                              },
                              RequestContext(request))

def question_edit(request, pk):
    #import pdb; pdb.set_trace()
    object = get_object_or_404(Question, pk=pk)

    if not request.user.has_perm('vodkamartiniqa.change_own_question', obj=object):
        # no need for the extra reverse when I can use use get_absolute_url for the object
        #return HttpResponseRedirect(reverse('vodkamartiniqa_question_detail', kwargs={'slug': object.slug}))
        return HttpResponseRedirect(object.get_absolute_url())

    if request.method == 'POST':
        form = QuestionForm(author=request.user, question_id=object.id, data=request.POST, request=request)
        if form.is_valid():
            object = form.save()
            messages.info(request, 'Your question has been updated.')
            return HttpResponseRedirect(object.get_absolute_url())
    else:
        data = {'title': object.title, 'body': object.body}
        categories = object.categories.all()
        if categories:
            data['category'] = categories.all()[0]
        form = QuestionForm(author=request.user, question_id=object.id, data=data, request=request)

    return render_to_response('vodkamartiniqa/question_form.html',
                              {
                               'object': object,
                               'form': form,
                              },
                              RequestContext(request))

def question_thanks(request, pk):
    question = get_object_or_404(Question, pk=pk)
    return render_to_response('vodkamartiniqa/question_thanks.html',
                              {
                               'question': question,
                              },
                              RequestContext(request)
                              )

def question_search(request):
    error = False
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            questions = Question.objects.filter(title__icontains=q)
            return render_to_response('vodkamartiniqa/search_results.html',
                                  {'questions': questions, 'q': q},
                                  RequestContext(request))
    return render_to_response('vodkamartiniqa/search_form.html',
                                  {'error': error},
                                  RequestContext(request))

#def user_answers(request, username):
#    return render_to_response('vodkamartiniqa/user_answers.html',
#                              {'username': username},
#                              RequestContext(request))
#
#def user_questions(request, username):
#    return render_to_response('vodkamartiniqa/user_questions.html',
#                              {'username': username},
#                              RequestContext(request))
#
#def user_profile(request, username):
#    return render_to_response('vodkamartiniqa/user_profile.html',
#                              {'username': username},
#                              RequestContext(request))

#def question_detail(request, year, month, day, slug):
def question_detail(request, slug):
    """
    Question detail view

    Templates: ``<app_label>/<model_name>_detail.html``
    Context:
        object:
            the object to be detailed
        can_edit:
            boolean to decide if the edit link is displayed
    """
    #print request.META['REMOTE_ADDR']
    try:
        object = Question.objects.get(slug=slug, status = Question.LIVE_STATUS)
        # use this for urls like /2012/09/12/question-title-here, change function signature above and URLconf too.
        #created = datetime.datetime.strptime(year+month+day, "%Y%m%d")
        #object = get_object_or_404(Question, slug=slug, created__year=created.year, created__month=created.month, created__day=created.day)
    except Question.DoesNotExist:
        return HttpResponsePermanentRedirect(reverse('vodkamartiniqa_questions_home'))

    can_edit = False
    if request.user.has_perm('vodkamartiniqa.change_own_question', obj=object):
        can_edit = True

    if request.user.is_authenticated():
        voted_up_by_current_user = request.user in object.voted_up_by.all()
        voted_down_by_current_user = request.user in object.voted_down_by.all()
        #logged_in = True
    else:
        voted_up_by_current_user = False
        voted_down_by_current_user = False
        #logged_in = False

    if object.status == Question.LIVE_STATUS:
        object_is_live = True
    else:
        object_is_live = False

    voted_up_by_current_user = request.user in object.voted_up_by.all()
    return render_to_response('vodkamartiniqa/question_detail.html',
                              {'object': object,
                               'can_edit': can_edit,
                               'object_is_live': object_is_live,
                               'voted_up_by_current_user': voted_up_by_current_user,
                               'voted_down_by_current_user': voted_down_by_current_user,
                              },
                              RequestContext(request))

#def question_edit(request, year, month, day, slug):
#    # TODO just show live object
#    created = datetime.datetime.strptime(year+month+day, "%Y%m%d")
#    object = get_object_or_404(Question, slug=slug, created__year=created.year, created__month=created.month, created__day=created.day)
#    return HttpResponse('edit question %d:%s' % (object.id, object.title))
#
#def question_answer(request, year, month, day, slug):
#    # TODO just show live object
#    created = datetime.datetime.strptime(year+month+day, "%Y%m%d")
#    object = get_object_or_404(Question, slug=slug, created__year=created.year, created__month=created.month, created__day=created.day)
#    return HttpResponse('answer question %d:%s' % (object.id, object.title))
#
#def question_delete(request, year, month, day, slug):
#    # TODO just show live object
#    created = datetime.datetime.strptime(year+month+day, "%Y%m%d")
#    object = get_object_or_404(Question, slug=slug, created__year=created.year, created__month=created.month, created__day=created.day)
#    return HttpResponse('delete question %d:%s' % (object.id, object.title))

def category(request, category):
    return render_to_response('vodkamartiniqa/category.html',
                              {'category': category},
                              RequestContext(request))

class AnswerPostBadRequest(HttpResponseBadRequest):
    """
    Response returned when an answer post is invalid. If ``DEBUG`` is on a
    nice-ish error message will be displayed (for debugging purposes), but in
    production mode a simple opaque 400 page will be displayed.
    """
    def __init__(self, why):
        super(AnswerPostBadRequest, self).__init__()
        if settings.DEBUG:
            self.content = render_to_string("vodkamartiniqa/400-debug.html", {"why": why})

@csrf_protect
@require_POST
def post_answer(request, next=None, using=None):
    """
    Post an answer

    HTTP POST is required. If ``POST['submit'] == "preview"`` or if there are
    errors a preview template, ``vodkamartiniqa/answer_preview.html``, will be rendered.
    """
    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()
    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name() or request.user.username
        if not data.get('email', ''):
            data["email"] = request.user.email

    # Check to see if the POST data overrides the view's next argument.
    next = data.get("next", next)

    # Look up the object (the question) we're trying to answer
    object_pk = data.get("object_pk")

    if object_pk is None:
        return AnswerPostBadRequest("Missing content_type or object_pk field.")
    try:
        question = Question._default_manager.using(using).get(pk=object_pk)
    except Question.DoesNotExist:
        return AnswerPostBadRequest("No object matching object PK %r exists." % (escape(object_pk),))

    # Do we want to preview the answer?
    preview = "preview" in data

    # Construct the answer form
    form = AnswerForm(question, data=data)

    # Check security information
    if form.security_errors():
        return AnswerPostBadRequest("The answer form failed security verification: %s" % escape(str(form.security_errors())))

    # If there are errors or if we requested a preview show the answer
    if form.errors or preview:
        template = "vodkamartiniqa/answer_preview.html"
        return render_to_response(
            template, {
                "answer" : form.data.get("answer", ""),
                "form" : form,
                "next": next,
            },
            RequestContext(request, {})
        )

    # Otherwise create the answer
    answer = form.get_answer_object()
    answer.ip_address = request.META.get("REMOTE_ADDR", None)
    answer.question = question
    if request.user.is_authenticated():
        answer.user = request.user

    # Signal that the answer is about to be saved
    responses = signals.answer_will_be_posted.send(
        sender  = answer.__class__,
        answer = answer,
        request = request
    )

    for (receiver, response) in responses:
        if response == False:
            return AnswerPostBadRequest(
                "answer_will_be_posted receiver %r killed the comment" % receiver.__name__)

    # Save the answer and signal that it was saved
    answer.save()
    signals.answer_was_posted.send(
        sender  = answer.__class__,
        answer = answer,
        request = request
    )

    # see how this is used in django.contrib.comments.views.comments, needed to add anchor
    #return next_redirect(data, next, comment_done, c=comment._get_pk_val())

    return HttpResponseRedirect(reverse('vodkamartiniqa_question_detail', kwargs={'slug': question.slug}))


def question_latest_questions(request, num=4):
    questions = Question.live.all().order_by('-created')[:num]
    to_json = []
    for question in questions:
        to_json.append({'title': strip_tags(question.title), 'url': question.get_absolute_url()})
    return HttpResponse(json.dumps(to_json), mimetype='application/json')

def question_vote(request, pk, vote):
    """
    A user can't vote a question up and down at the same time.
    """
    question = Question.objects.get(pk=pk)
    update_question = False

    if request.user.is_authenticated() and request.user not in question.voted_up_by.all() and request.user not in question.voted_down_by.all():
        can_vote = True
    else:
        can_vote = False

    if vote == 'up':
        if can_vote:
            question.votes_up = F('votes_up') + 1
            question.voted_up_by.add(request.user)
            update_question = True
    if vote == 'down':
        if can_vote:
            question.votes_down = F('votes_down') + 1
            question.voted_down_by.add(request.user)
            update_question = True
    if update_question:
        question.save()
        question = Question.objects.get(pk=pk)

    to_json = {"votes_up": question.votes_up, "votes_down": question.votes_down}
    return HttpResponse(json.dumps(to_json), mimetype='application/json')
