from vodkamartiniqa.models import Question
from vodkamartiniqa.models import Answer

def get_questions(with_experts_answers=False, type='latest', start=0, end=1):
    """
    Get questions for home and ajax calls. type can be any of 'latest', 'voted', 'answered' and will order by latest,
    most voted or most answered.
    """
    #import pdb; pdb.set_trace()
    if type == 'latest':
        questions_list = Question.live.filter(has_expert_answer=with_experts_answers).extra(select={'num_answers': 'SELECT COUNT(*) FROM vodkamartiniqa_answer WHERE vodkamartiniqa_answer.question_id = vodkamartiniqa_question.id'}).all().order_by('-created')[start:end]
    if type == 'voted':
        questions_list = Question.live.filter(has_expert_answer=with_experts_answers).all().extra(
                                                  select={'votes_difference': 'votes_up - votes_down',
                                                          'num_answers': 'SELECT COUNT(*) FROM vodkamartiniqa_answer WHERE vodkamartiniqa_answer.question_id = vodkamartiniqa_question.id'}
                                                ).order_by('-votes_difference')[start:end]
    if type == 'answered':
        questions_list = Question.live.filter(has_expert_answer=with_experts_answers).select_related().extra(select={'votes_difference': 'votes_up - votes_down', 'num_answers': 'SELECT COUNT(*) FROM vodkamartiniqa_answer WHERE vodkamartiniqa_answer.question_id = vodkamartiniqa_question.id'}).all().order_by('-num_answers', '-votes_difference')[start:end]

    return questions_list

def get_answers(question_id, start=0, end=1):
    question = Question.objects.get(pk=question_id)
    # important for reducing queries
    # see https://docs.djangoproject.com/en/dev/ref/models/querysets/#select-related
    # in other cases could use values()
    # see https://docs.djangoproject.com/en/dev/topics/db/optimization/#don-t-retrieve-things-you-don-t-need
    answers_list = Answer.objects.select_related().filter(question=question).filter(is_public=True).filter(is_removed=False).order_by('submit_date')[start:end]
    return answers_list
