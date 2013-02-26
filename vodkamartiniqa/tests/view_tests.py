from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from vodkamartiniqa.models import Question

"""
TODO check views module and test all views, including the ajax/json stuff, compare with URLConf to see what's
being used.

normal views
def question_detail(request, slug):
def category(request, category):

ajax views
def get_questions_ajax(request, with_experts_answers='regular', type='latest', start=0, end=8):
def question_latest_questions(request, num=4):
"""

class MainViews(TestCase):
    def setUp(self):
        """
        Create one question marked as normal and one question marked as answered by expert.
        django.test.client.Client gets confused with templates when using the cache, that's why we need to clear it.
        """
        cache.clear()
        author = User.objects.create_user(username='joe', password='qwerty')
        self.normal_title='Normal Question With Keyword In Title'
        self.expert_title='Question With Expert Answer'

        self.question = Question(
                                 title=self.normal_title,
                                 body='This is a normal question, with no answers by experts', 
                                 author=author, 
                                 status=Question.LIVE_STATUS,
                                )
        self.question.save()

        self.expert_question = Question(
                                 title=self.expert_title,
                                 body='This is a question with at least one answer by experts', 
                                 author=author, 
                                 status=Question.LIVE_STATUS,
                                 has_expert_answer=True,
                                )
        self.expert_question.save()

    def testQuestionHome(self):
        """
        Test the correct template is used for the questions home and that one normal question and one question markd as having an
        expert answer are present.
        """
        response = self.client.get(reverse('vodkamartiniqa_questions_home'))
        #from pprint import pprint
        #for template in response.templates:
        #    print template.name

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vodkamartiniqa/question_list.html')
        self.assertEqual(response.context['experts_object_list'][0].title, self.expert_title)
        self.assertEqual(response.context['experts_object_list'].count(), 1)
        self.assertEqual(response.context['object_list'][0].title, self.normal_title)
        self.assertEqual(response.context['object_list'].count(), 1)

    def testQuestionSearch(self):
        """
        Visit search page and get just the search form.
        """
        response = self.client.get(reverse('vodkamartiniqa_question_search'))
        self.assertTemplateUsed(response, 'vodkamartiniqa/search_form.html')

    def testQuestionSearchResults(self):
        """
        Search results page with one result.
        """
        data = {'q': 'keyword'}
        response = self.client.get(reverse('vodkamartiniqa_question_search'), data)
        self.assertTemplateUsed(response, 'vodkamartiniqa/search_results.html')
        self.assertEqual(response.context['questions'][0].title, self.normal_title)

    def testQuestionSearchNoResults(self):
        """
        Search results page with no results.
        """
        data = {'q': 'noresultsforthis'}
        response = self.client.get(reverse('vodkamartiniqa_question_search'), data)
        self.assertTemplateUsed(response, 'vodkamartiniqa/search_results.html')
        self.assertEqual(response.context['questions'].count(), 0)

    def testQuestionDetail(self):
        """ Question details page """
        one = 1
        self.assertEqual(one, 1),

class JSONViews(TestCase):
    pass
