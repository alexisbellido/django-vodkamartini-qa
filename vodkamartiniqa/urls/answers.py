from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('vodkamartiniqa.views.answers',
    # used for getting ajax answers
    url(r'^get-answers/(?P<question_id>\d+)/(?P<start>\d+)/(?P<end>\d+)/$', 'get_answers_ajax', name='vodkamartiniqa_answers_get_ajax'),
)
