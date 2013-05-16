from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from .models import Question

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authorization= Authorization()

class QuestionResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author')
    class Meta:
        queryset = Question.live.all()
        resource_name = 'question'
        # TODO disable this when testing done, VERY INSECURE
        authorization= Authorization()

    #def determine_format(self, request):
    #    """
    #    Set json response as default.
    #    See: http://stackoverflow.com/questions/8649387/django-tastypie-output-in-json-to-the-browser-by-default
    #    """
    #    return 'application/json'
