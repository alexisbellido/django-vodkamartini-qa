from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from .models import Question

class QuestionResource(ModelResource):
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
