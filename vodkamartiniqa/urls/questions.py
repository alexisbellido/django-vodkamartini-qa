from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('vodkamartiniqa.views.top',
    url(r'^top-questioners/$', 'questioners', name='vodkamartiniqa_top_questioners'),
)

urlpatterns += patterns('vodkamartiniqa.views.questions',
    url(r'^$', 'questions_index', {'page': 1}, name='vodkamartiniqa_questions_home'),

    # used for ajax question vote
    url(r'^vote/(?P<pk>\d+)/(?P<vote>(up|down))/$', 'question_vote', name='vodkamartiniqa_question_vote'),

    # used for getting ajax questions
    url(r'^get-questions/(?P<with_experts_answers>(experts|regular))/(?P<type>(latest|voted|answered))/(?P<start>\d+)/(?P<end>\d+)/$', 'get_questions_ajax', name='vodkamartiniqa_questions_get_ajax'),

    url(r'^latest/$', 'question_latest_questions', name='vodkamartiniqa_question_latest_questions'),
    url(r'^latest/(?P<username>[-\w\ ]+)/(?P<start>\d+)/(?P<end>\d+)/$', 'question_latest_questions', name='vodkamartiniqa_question_latest_questions'),
    url(r'^page-(?P<page>\d+)/$', 'questions_index', name='vodkamartiniqa_questions_index'),
    url(r'^ask/$', 'question_add', name='vodkamartiniqa_question_add'),
    url(r'^edit/question/(?P<pk>\d+)/$', 'question_edit', name='vodkamartiniqa_question_edit'),
    #url(r'^thanks/(?P<pk>\d+)/$', 'question_thanks', name='vodkamartiniqa_question_thanks'),
    url(r'^search/$', 'question_search', name='vodkamartiniqa_question_search'),
    url(r'^(?P<slug>[-\w]+)/$', 'question_detail', name='vodkamartiniqa_question_detail'),
    url(r'^(?P<slug>[\d]+)/.*$', 'question_detail', name='vodkamartiniqa_question_detail'),
    #url(r'^(?P<username>[-\w]+)/questions/$', 'user_questions', name='vodkamartiniqa_user_questions'),
    #url(r'^(?P<username>[-\w]+)/answers/$', 'user_answers', name='vodkamartiniqa_user_answers'),
    #url(r'^(?P<username>[-\w]+)/$', 'user_profile', name='vodkamartiniqa_user_profile'),

    # use these for urls like /2012/09/12/question-title-here, change views, models and URLconf too.
    #url(r'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})/(?P<slug>[-\w]+)/edit/$', 'question_edit', name='vodkamartiniqa_question_edit'),
    #url(r'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})/(?P<slug>[-\w]+)/answer/$', 'question_answer', name='vodkamartiniqa_question_answer'),
    #url(r'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})/(?P<slug>[-\w]+)/delete/$', 'question_delete', name='vodkamartiniqa_question_delete'),
    #url(r'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})/(?P<slug>[-\w]+)/$', 'question_detail', name='vodkamartiniqa_question_detail'),

    url(r'^category/(?P<category>[-\w]+)/$', 'category', name='vodkamartiniqa_category'),
    url(r'^answer/post/$', 'post_answer', name='vodkamartiniqa_post_answer'),
)
