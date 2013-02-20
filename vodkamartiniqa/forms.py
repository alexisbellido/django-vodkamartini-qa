from django import forms
from django.conf import settings
import time
from django.utils.crypto import salted_hmac, constant_time_compare
from django.forms.util import ErrorDict
from vodkamartiniqa.models import Answer, Question
from vodkamartinicategory.models import Category
from django.utils import timezone
from django.utils.translation import ungettext
from django.utils.text import get_text_list
from vodkamartiniqa import signals

ANSWER_MAX_LENGTH = getattr(settings,'ANSWER_MAX_LENGTH',3000)

class AnswerSecurityForm(forms.Form):
    """
    Handles the security aspects (anti-spoofing) for answer forms.
    """
    object_pk     = forms.CharField(widget=forms.HiddenInput)
    timestamp     = forms.IntegerField(widget=forms.HiddenInput)
    security_hash = forms.CharField(min_length=40, max_length=40, widget=forms.HiddenInput)

    def __init__(self, target_object, data=None, initial=None):
        self.target_object = target_object
        if initial is None:
            initial = {}
        initial.update(self.generate_security_data())
        super(AnswerSecurityForm, self).__init__(data=data, initial=initial)

    def security_errors(self):
        """Return just those errors associated with security"""
        errors = ErrorDict()
        for f in ["honeypot", "timestamp", "security_hash"]:
            if f in self.errors:
                errors[f] = self.errors[f]
        return errors

    def clean_security_hash(self):
        """Check the security hash."""
        security_hash_dict = {
            'object_pk' : self.data.get("object_pk", ""),
            'timestamp' : self.data.get("timestamp", ""),
        }
        expected_hash = self.generate_security_hash(**security_hash_dict)
        actual_hash = self.cleaned_data["security_hash"]
        if not constant_time_compare(expected_hash, actual_hash):
            raise forms.ValidationError("Security hash check failed.")
        return actual_hash

    def clean_timestamp(self):
        """Make sure the timestamp isn't too far (> 2 hours) in the past."""
        ts = self.cleaned_data["timestamp"]
        if time.time() - ts > (2 * 60 * 60):
            raise forms.ValidationError("Timestamp check failed")
        return ts

    def generate_security_data(self):
        """Generate a dict of security data for "initial" data."""
        timestamp = int(time.time())
        security_dict =   {
            'object_pk'     : str(self.target_object._get_pk_val()),
            'timestamp'     : str(timestamp),
            'security_hash' : self.initial_security_hash(timestamp),
        }
        return security_dict

    def initial_security_hash(self, timestamp):
        """
        Generate the initial security hash from self.content_object
        and a (unix) timestamp.
        """

        initial_security_dict = {
            'object_pk' : str(self.target_object._get_pk_val()),
            'timestamp' : str(timestamp),
          }
        return self.generate_security_hash(**initial_security_dict)

    def generate_security_hash(self, object_pk, timestamp):
        """
        Generate a HMAC security hash from the provided info.
        """
        info = (object_pk, timestamp)
        key_salt = "vodkamartiniqa.forms.AnswerSecurityForm"
        value = "-".join(info)
        return salted_hmac(key_salt, value).hexdigest()

class AnswerForm(AnswerSecurityForm):
    answer        = forms.CharField(label='Answer', widget=forms.Textarea,
                                    max_length=ANSWER_MAX_LENGTH)
    honeypot      = forms.CharField(required=False,
                                    label='If you enter anything in this field '\
                                            'your answer will be treated as spam')

    def get_answer_object(self):
        """
        Return a new (unsaved) answer object based on the information in this
        form. Assumes that the form is already validated and will throw a
        ValueError if not.

        Does not set any of the fields that would come from a Request object
        (i.e. ``user`` or ``ip_address``).
        """
        if not self.is_valid():
            raise ValueError("get_answer_object may only be called on valid forms")

        new = Answer(**self.get_answer_create_data())
        # TODO should we check for duplicate answer? See django.contrib.comments.forms
        #new = self.check_for_duplicate_comment(new)

        return new

    def get_answer_create_data(self):
        """
        Returns the dict of data to be used to create an answer.
        """
        return dict(
            answer       = self.cleaned_data["answer"],
            submit_date  = timezone.now(),
            is_public    = True,
            is_removed   = False,
        )

    def clean_answer(self):
        """
        If ANSWERS_ALLOW_PROFANITIES is False, check that the answer doesn't
        contain anything in PROFANITIES_LIST.
        """
        answer = self.cleaned_data["answer"]
        if settings.ANSWERS_ALLOW_PROFANITIES == False:
            bad_words = [w for w in settings.PROFANITIES_LIST if w in answer.lower()]
            if bad_words:
                raise forms.ValidationError(ungettext(
                    "Watch your mouth! The word %s is not allowed here.",
                    "Watch your mouth! The words %s are not allowed here.",
                    len(bad_words)) % get_text_list(
                        ['"%s%s%s"' % (i[0], '-'*(len(i)-2), i[-1])
                         for i in bad_words], 'and'))
        return answer

    def clean_honeypot(self):
        """Check that nothing's been entered into the honeypot."""
        value = self.cleaned_data["honeypot"]
        if value:
            raise forms.ValidationError(self.fields["honeypot"].label)
        return value

class QuestionForm(forms.Form):
    def __init__(self, author, question_id=0, request=None, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.author = author
        self.question_id = question_id
        self.request = request

    title = forms.CharField()
    body = forms.CharField(widget=forms.Textarea, label='Enter your question')
    # select box for one category
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label='Choose a category')
    # checkboxes for multiple categories
    #categories = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Category.objects.all(), required=False)

    def save(self):
        # Signal that the question is about to be saved
        #signals.question_will_be_posted.send(
        #    sender  = answer.__class__,
        #    answer = answer,
        #    request = request
        #)

        # TODO what to do about status?
        if self.question_id:
            """ existing question, no need to change author or status """
            question = Question.objects.get(pk=self.question_id)
            question.title = self.cleaned_data['title']
            question.body = self.cleaned_data['body']
            question.save()
            if self.cleaned_data['category']:
                question.categories.clear()
                question.categories.add(self.cleaned_data['category'])
        else:
            question = Question(title=self.cleaned_data['title'], body=self.cleaned_data['body'], author=self.author, status=Question.LIVE_STATUS)
            question.save()
            if self.cleaned_data['category']:
                question.categories.add(self.cleaned_data['category'])
            # use this for multiple categories, probably with checkboxes
            #categories = self.cleaned_data['categories']
            #for category in categories:
            #    question.categories.add(category)
        return question
