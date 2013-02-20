from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from vodkamartiniarticle.models import BaseArticle
from vodkamartiniarticle.helper import check_internal_spam_words
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from vodkamartiniqa.signals import answer_will_be_posted, question_will_be_posted
from django.db.models.signals import pre_delete
from django.contrib.sites.models import Site
from akismet import Akismet
from akismet import AkismetError
from django.utils.encoding import smart_str
from django.contrib import messages
from vodkamartiniarticle.helper import get_client_ip

ANSWER_MAX_LENGTH = getattr(settings,'ANSWER_MAX_LENGTH',3000)

expert_groups = ['yte directory', 'yte basic', 'yte advanced', 'yte organization']

class Question(BaseArticle):
    asked_to = models.ForeignKey(User, related_name='questions_asked', blank=True, null=True)
    votes_up = models.IntegerField(default=0)
    voted_up_by = models.ManyToManyField(User, blank=True, related_name='questions_voted_up') # Users who voted up this question
    votes_down = models.IntegerField(default=0)
    voted_down_by = models.ManyToManyField(User, blank=True, related_name='questions_voted_down') # Users who voted down this question
    has_expert_answer = models.BooleanField(default=False,
                                      help_text='Check this box if this question has at least an answer by an expert.')
    # TODO a many to many model for linking question to whom question is directed?

    @models.permalink
    def get_absolute_url(self):
        return ('vodkamartiniqa_question_detail', (), {'slug': self.slug})

    # use this for urls like /2012/09/12/question-title-here, change view and URLconf too.
    #@models.permalink
    #def get_absolute_url(self):
    #    return ('vodkamartiniqa_question_detail', (), {
    #            'year': self.created.strftime("%Y"), 
    #            'month': self.created.strftime("%m"), 
    #            'day': self.created.strftime("%d"),
    #            'slug': self.slug})

    class Meta(BaseArticle.Meta):
        permissions = (
                ('can_moderate_question', 'Can moderate questions'),
                ('change_own_question', 'Can change own question'),
                ('view_question', 'View question'),
                ('vote_question', 'Can vote for question'),
        )

class Answer(models.Model):
    """
    An answer linked to one Question object.
    """

    answer = models.TextField(max_length=ANSWER_MAX_LENGTH)
    user = models.ForeignKey(User) # user who published this answer
    question = models.ForeignKey(Question)
    votes_up = models.IntegerField(default=0)
    voted_up_by = models.ManyToManyField(User, blank=True, related_name='answers_voted_up') # Users who voted up this answer
    votes_down = models.IntegerField(default=0)
    voted_down_by = models.ManyToManyField(User, blank=True, related_name='answers_voted_down') # Users who voted down this answer

    # Metadata about the answer
    submit_date = models.DateTimeField('date/time submitted', default=None)
    ip_address  = models.IPAddressField('IP address', blank=True, null=True)
    is_public   = models.BooleanField(default=True,
                                      help_text='Uncheck this box to make the answer effectively disappear from the site.')
    is_removed  = models.BooleanField(default=False,
                                      help_text='Check this box if the answer is inappropriate. ' \
                                      'A "This answer has been removed" message will be displayed instead.')
    posted_by_expert   = models.BooleanField(default=False,
                                      help_text='Check this box if this an answer by an expert.')

    class Meta:
        ordering = ('-submit_date',)
        permissions = (
                ('can_moderate_answer', 'Can moderate answers'),
                ('change_own_answer', 'Can change own answer'),
                ('view_answer', 'View answer'),
                ('vote_answer', 'Can vote for answer'),
        )

    def __unicode__(self):
        return "%s..." % (self.answer[:50],)

    def save(self, *args, **kwargs):
        # TODO markdown? See vodkamartiniarticle.models
        user_is_expert = self.user.groups.filter(name__in=expert_groups).count()
        if not self.pk and user_is_expert:
            self.posted_by_expert = True
            if not self.question.has_expert_answer:
                """ set has_expert_answer on Question object to True if not already set """
                self.question.has_expert_answer = True
                self.question.save()
        if self.submit_date is None:
            self.submit_date = timezone.now()
        super(Answer, self).save(*args, **kwargs)

    # too expensive, we are better having posted_by_expert as a field in the Answer model
    #def posted_by_expert(self):
    #    #import pdb; pdb.set_trace()
    #    return expert_group in self.user.groups.all()

def moderate_answer(sender, answer, request, **kwargs):
    """
    Test Akismet spam with 'viagra-test-123'
    """
    if not answer.id:
        akismet_api = Akismet(key=settings.AKISMET_API_KEY, blog_url="http://%s/" % Site.objects.get_current().domain)
        if akismet_api.verify_key():
            akismet_data = {
                    'comment_type' : 'comment', # this needs to be always 'comment'
                    'referrer': request.META['HTTP_REFERER'],
                    'user_ip': answer.ip_address,
                    'user_agent': request.META['HTTP_USER_AGENT'],
                   }
            try:
                if akismet_api.comment_check(smart_str(answer.answer), akismet_data, build_data=True) or check_internal_spam_words(answer.answer):
                    answer.is_public = False
                    messages.info(request, 'Your answer was marked as spam.')
                else:
                    messages.info(request, 'Your answer has been published.')
            except AkismetError:
                """ This exception can be raised when Akismet is down or some parameter in the call is missing. See akismet.py """
                pass


def delete_answer(sender, instance, **kwargs):
    """
    Update has_expert_answer field on related Question if there are no more expert answers.
    """
    question = instance.question
    if question.has_expert_answer:
        """
        Set question.has_expert_answer to False only if this
        was the last answer by an expert in this question
        """
        if question.answer_set.filter(posted_by_expert=True).count() == 1:
            question.has_expert_answer = False
            question.save()

def moderate_question(sender, question, request, **kwargs):
    """
    Test Akismet spam with 'viagra-test-123'
    """
    if not question.id:
        pass

answer_will_be_posted.connect(moderate_answer, sender=Answer)
pre_delete.connect(delete_answer, sender=Answer)
question_will_be_posted.connect(moderate_question, sender=Question)
