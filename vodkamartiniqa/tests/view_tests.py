import json
from django.contrib.auth.models import User, Group, Permission
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from vodkamartiniqa.models import Question, expert_groups


class MainViews(TestCase):
    def setUp(self):
        """
        Create one question marked as normal and one question marked as answered by expert.
        Notice the normal question has "Keyword" in the title, which is used for testing the basic search view.
        django.test.client.Client gets confused with templates when using the cache, that's why we need to clear it.
        """
        cache.clear()
        author = User.objects.create_user(username='joe', password='qwerty')
        self.normal_title='Normal Question With Keyword In Title'
        self.normal_hidden_title='Normal Hidden Question'
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

        self.hidden_question = Question(
                                 title=self.normal_hidden_title,
                                 body='This is a normal hidden question', 
                                 author=author, 
                                 status=Question.HIDDEN_STATUS,
                               )
        self.hidden_question.save()

    def testQuestionHome(self):
        """
        Test the correct template is used for the questions home and that one normal question and one question marked as having an
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
        """
        Question details page.
        """
        slug = 'normal-question-with-keyword-in-title'
        response = self.client.get(reverse('vodkamartiniqa_question_detail', kwargs={'slug': slug}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vodkamartiniqa/question_detail.html')
        self.assertEqual(response.context['object'].title, self.normal_title)
        self.assertEqual(response.context['object'].slug, slug)

    def testQuestionHidden(self):
        """
        Question hidden.
        """
        slug = 'normal-hidden-question'
        response = self.client.get(reverse('vodkamartiniqa_question_detail', kwargs={'slug': slug}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vodkamartiniqa/question_list.html')

    def testQuestionNumericSlug(self):
        """
        Question with numeric slug should redirect to home.
        """
        slug = '12345'
        response = self.client.get(reverse('vodkamartiniqa_question_detail', kwargs={'slug': slug}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vodkamartiniqa/question_list.html')

    def testQuestionCategory(self):
        """
        Category page listing all questions in that category.
        """
        pass

class JSONViews(TestCase):
    def setUp(self):
        """
        Create a normal user and an expert user, then 
        create a few questions and answers, some of the answers published by experts.
        django.test.client.Client gets confused with templates when using the cache, that's why we need to clear it.
        """
        cache.clear()

        self.regular_user = User.objects.create_user(username='bill_normal', password='secret')
        self.group_expert = Group.objects.create(name=expert_groups[0])
        self.expert_user = User.objects.create_user(username='joe_expert', password='secret')
        self.expert_user.groups.add(self.group_expert)
        self.questions = []

        number_questions = 24
        for i in range(0, number_questions):
            title='Question #%d' % (i+1, )
            body='This is question #%d.' % (i+1, )
            author=self.regular_user 
            question = Question(
                                title=title,
                                body=body,
                                author=author, 
                                status=Question.LIVE_STATUS,
                               )
            question.save()
            self.questions.append(question)

        print "==="
        print " start answering "
        print "==="
        # choose a few questions and publish answers here and there, some with answers from experts, others from regular and others mixed
        # follow the answers_map below
        answers_map = [ 
                        {'question_id': 0, 'regular_answers': 0, 'expert_answers': 0},
                        {'question_id': 3, 'regular_answers': 2, 'expert_answers': 0},
                        {'question_id': 4, 'regular_answers': 1, 'expert_answers': 2},
                        {'question_id': 6, 'regular_answers': 0, 'expert_answers': 5},
                        {'question_id': 7, 'regular_answers': 3, 'expert_answers': 3},
                        {'question_id': 9, 'regular_answers': 0, 'expert_answers': 8},
                        {'question_id': 13, 'regular_answers': 5, 'expert_answers': 2},
                        {'question_id': 15, 'regular_answers': 1, 'expert_answers': 1},
                        {'question_id': 19, 'regular_answers': 0, 'expert_answers': 3},
                        {'question_id': 21, 'regular_answers': 2, 'expert_answers': 1},
                      ]

        #print self.questions[0], self.questions[0].id

    def testHomeLatestExpertsQuestionsAjax(self):
        """
        http://armitage.yourtango.com:8006/questions/get-questions/experts/latest/0/9/
        """
        #url(r'^get-questions/(?P<with_experts_answers>(experts|regular))/(?P<type>(latest|voted|answered))/(?P<start>\d+)/(?P<end>\d+)/$', 'get_questions_ajax', name='vodkamartiniqa_questions_get_ajax'),
        #def get_questions_ajax(request, with_experts_answers='regular', type='latest', start=0, end=8):
        slug = 'normal-question-with-keyword-in-title'
        data = {
                'with_experts_answers': 'experts',
                'type': 'latest',
                'start': 0,
                'end': 9,
               }
        response = self.client.get(reverse('vodkamartiniqa_questions_get_ajax', kwargs=data))
        self.assertEqual(response.status_code, 200)
        print response.content
        #self.assertTemplateUsed(response, 'vodkamartiniqa/question_detail.html')
        #self.assertEqual(response.context['object'].title, self.normal_title)
        #self.assertEqual(response.context['object'].slug, slug)

    def testHomeMostAnsweredExpertsQuestionsAjax(self):
        """
        http://armitage.yourtango.com:8006/questions/get-questions/experts/answered/0/9/
        """
        #def get_questions_ajax(request, with_experts_answers='regular', type='latest', start=0, end=8):
        pass

    def testHomeMostVotedQuestionsAjax(self):
        """
        http://armitage.yourtango.com:8006/questions/get-questions/experts/voted/0/9/
        """
        #def get_questions_ajax(request, with_experts_answers='regular', type='latest', start=0, end=8):
        pass

    def testLatestQuestions(self):
        """
        """
        #def question_latest_questions(request, num=4):
        pass
