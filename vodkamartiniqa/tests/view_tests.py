import json
from django.contrib.auth.models import User, Group, Permission
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from vodkamartiniqa.models import Question, Answer, expert_groups


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

#class JSONViews(TestCase):
#    def setUp(self):
#        """
#        Create a normal user and an expert user, then 
#        create a few questions and answers, some of the answers published by experts.
#        django.test.client.Client gets confused with templates when using the cache, that's why we need to clear it.
#        """
#        cache.clear()
#
#        self.regular_user = User.objects.create_user(username='bill_normal', password='secret')
#        self.group_expert = Group.objects.create(name=expert_groups[0])
#        self.expert_user = User.objects.create_user(username='joe_expert', password='secret')
#        self.expert_user.groups.add(self.group_expert)
#        self.questions = []
#
#        number_questions = 24
#        for i in range(0, number_questions):
#            title='Question #%d' % (i, )
#            body='This is question #%d.' % (i, )
#            author=self.regular_user 
#            question = Question(
#                                title=title,
#                                body=body,
#                                author=author, 
#                                status=Question.LIVE_STATUS,
#                               )
#            question.save()
#            self.questions.append(question)
#
#        answers_map = [ 
#                        {'question_id': 0, 'regular_answers': 0, 'expert_answers': 0, 'votes_up': 1, 'votes_down': 3},
#                        {'question_id': 3, 'regular_answers': 2, 'expert_answers': 0, 'votes_up': 8, 'votes_down': 1},
#                        {'question_id': 4, 'regular_answers': 1, 'expert_answers': 2, 'votes_up': 3, 'votes_down': 3},
#                        {'question_id': 6, 'regular_answers': 0, 'expert_answers': 5, 'votes_up': 1, 'votes_down': 1},
#                        {'question_id': 7, 'regular_answers': 3, 'expert_answers': 3, 'votes_up': 8, 'votes_down': 3},
#                        {'question_id': 9, 'regular_answers': 0, 'expert_answers': 8, 'votes_up': 3, 'votes_down': 1},
#                        {'question_id': 11, 'regular_answers': 2, 'expert_answers': 1, 'votes_up': 2, 'votes_down': 1},
#                        {'question_id': 2, 'regular_answers': 3, 'expert_answers': 2, 'votes_up': 7, 'votes_down': 1},
#                        {'question_id': 13, 'regular_answers': 5, 'expert_answers': 2, 'votes_up': 3, 'votes_down': 3},
#                        {'question_id': 15, 'regular_answers': 1, 'expert_answers': 1, 'votes_up': 10, 'votes_down': 1},
#                        {'question_id': 19, 'regular_answers': 0, 'expert_answers': 3, 'votes_up': 5, 'votes_down': 3},
#                        {'question_id': 21, 'regular_answers': 2, 'expert_answers': 1, 'votes_up': 4, 'votes_down': 2},
#                      ]
#
#        for item in answers_map:
#            self.questions[item['question_id']].votes_up = item['votes_up']
#            self.questions[item['question_id']].votes_down = item['votes_down']
#            self.questions[item['question_id']].save()
#            for i in range(0, item['regular_answers']):
#                answer = Answer(
#                                answer='Regular answer %d for question %d' % (i, item['question_id']),
#                                user=self.regular_user,
#                                question=self.questions[item['question_id']],
#                               )
#                answer.save()
#            for i in range(0, item['expert_answers']):
#                answer = Answer(
#                                answer='Expert answer %d for question %d' % (i, item['question_id']),
#                                user=self.expert_user,
#                                question=self.questions[item['question_id']],
#                               )
#                answer.save()
#
#    def testHomeLatestExpertsQuestionsAjax(self):
#        """
#        Get latest questions with at least one answer by an expert.
#        """
#        data = {
#                'with_experts_answers': 'experts',
#                'type': 'latest',
#                'start': 0,
#                'end': 9,
#               }
#        response = self.client.get(reverse('vodkamartiniqa_questions_get_ajax', kwargs=data))
#        self.assertEqual(response.status_code, 200)
#
#        # TODO test that json results are in correct order
#        parsed_data = json.loads(response.content)
#        self.assertEqual(len(parsed_data), data['end'] - data['start'])
#        for element in parsed_data:
#            self.assertEqual(element['title'], self.questions[element['id']-1].title)
#
#    def testHomeMostAnsweredExpertsQuestionsAjax(self):
#        """
#        Get most answered questions with at least one answer by an expert.
#        http://armitage.yourtango.com:8006/questions/get-questions/experts/answered/0/9/
#        """
#        data = {
#                'with_experts_answers': 'experts',
#                'type': 'answered',
#                'start': 0,
#                'end': 9,
#               }
#        response = self.client.get(reverse('vodkamartiniqa_questions_get_ajax', kwargs=data))
#        self.assertEqual(response.status_code, 200)
#
#        # TODO test that json results are in correct order
#        parsed_data = json.loads(response.content)
#        self.assertEqual(len(parsed_data), data['end'] - data['start'])
#        for element in parsed_data:
#            self.assertEqual(element['title'], self.questions[element['id']-1].title)
#
#    def testHomeMostVotedExpertsQuestionsAjax(self):
#        """
#        Get most voted questions with at least one answer by an expert.
#        http://armitage.yourtango.com:8006/questions/get-questions/experts/voted/0/9/
#        """
#        data = {
#                'with_experts_answers': 'experts',
#                'type': 'voted',
#                'start': 0,
#                'end': 9,
#               }
#        response = self.client.get(reverse('vodkamartiniqa_questions_get_ajax', kwargs=data))
#        self.assertEqual(response.status_code, 200)
#
#        # TODO test that json results are in correct order
#        parsed_data = json.loads(response.content)
#        self.assertEqual(len(parsed_data), data['end'] - data['start'])
#        for element in parsed_data:
#            self.assertEqual(element['title'], self.questions[element['id']-1].title)
#
#    def testHomeLatestQuestionsAjax(self):
#        """
#        Get latest questions with answers by only regular users.
#        """
#        pass
#
#    def testHomeMostAnsweredQuestionsAjax(self):
#        """
#        Get latest questions with answers by only regular users.
#        """
#        pass
#
#    def testHomeMostVotedQuestionsAjax(self):
#        """
#        Get latest questions with answers by only regular users.
#        """
#        pass
#
#    def testLatestQuestions(self):
#        """
#        Get latest questions.
#        """
#        pass
