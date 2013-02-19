from django import template
from vodkamartiniqa.models import Question
from django.db.models import get_model
from django.db.models import Count

register = template.Library()

@register.tag(name='get_questions')
def do_questions(parser, token):
    """
    Flexible tag to create a new template variable with questions.
    Use like this: {% get_questions type 5 as questions %}
    where type is any of: latest (latest published), voted (most voted),
    visited (most visited), answered (most answered), answered_expert' (most answered by experts).
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, querytype, num, discard_this, varname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly four arguments" % token.contents.split()[0])

    if querytype not in ('latest', 'voted', 'visited', 'answered', 'answered_expert'):
        raise template.TemplateSyntaxError("The first argument to 'get_questions' needs to be any of 'latest', 'voted', 'visited', or 'answered' or 'answered_expert'.")

    return QuestionContentNode(querytype, num, varname)

class QuestionContentNode(template.Node):
    def __init__(self, querytype, num, varname):
        self.querytype = querytype
        self.num = int(num)
        self.varname = varname

    def render(self, context):
        if self.querytype == 'latest':
            context[self.varname] = Question.live.all().order_by('-created')[:self.num]
        if self.querytype == 'voted':
            context[self.varname] = Question.live.all().extra(
                                                        select={'votes_difference': 'votes_up - votes_down'}
                                                        ).order_by('-votes_difference')[:self.num]
        if self.querytype == 'answered':
            """ questions ordered by number of answers, these don't include questions with expert answers. """
            # this one is too slow because of the many fields in GROUP BY, I fixed this by using values and two queries. See below.
            #context[self.varname] = Question.live.filter(has_expert_answer=False).annotate(num_answers=Count('answer')).order_by('-num_answers')[:self.num]

            annotated_questions = Question.live.filter(has_expert_answer=False).values('slug').annotate(num_answers=Count('answer')).order_by('-num_answers')[:self.num]
            slugs = [q['slug'] for q in annotated_questions]
            context[self.varname] = Question.live.filter(slug__in=slugs).values('slug', 'title').annotate(num_answers=Count('answer')).order_by('-num_answers')
        if self.querytype == 'answered_expert':
            """ questions ordered by number of answers, these include questions with expert answers. """
            # this one is too slow because of the many fields in GROUP BY, I fixed this by using values and two queries. See below.
            #context[self.varname] = Question.live.filter(has_expert_answer=True).annotate(num_answers=Count('answer')).order_by('-num_answers')[:self.num]

            annotated_questions = Question.live.filter(has_expert_answer=True).values('slug').annotate(num_answers=Count('answer')).order_by('-num_answers')[:self.num]
            slugs = [q['slug'] for q in annotated_questions]
            context[self.varname] = Question.live.filter(slug__in=slugs).values('slug', 'title').annotate(num_answers=Count('answer')).order_by('-num_answers')
        # TODO, use Google Analytics API and caching?
        #if self.querytype == 'visited':
        #    context[self.varname] = Question.live.all().order_by('-created')[:self.num]
        return ''
