from django.http import HttpResponse
from vodkamartiniqa.views.helpers import get_answers
from vodkamartiniqa.views.helpers import get_questions
import json
#from django.core.serializers.json import DjangoJSONEncoder

# TODO get answers via ajax with start and end
def get_answers_ajax(request, question_id, start=0, end=8):
    objects = get_answers(question_id, start, end)
    answers = []
    for object in objects:
        submit_date = object.submit_date.strftime("%B %e, %Y")
        answers.append({
                            'id': object.id,
                            'answer': object.answer,
                            'user': object.user.username,
                            'user_picture': object.user.drupaluser.picture,
                            'votes_up': object.votes_up,
                            'votes_down': object.votes_down,
                            'posted_by_expert': object.posted_by_expert,
                            'submit_date': submit_date,
                        })

    return HttpResponse(json.dumps(answers), mimetype='application/json')
    # use DjangoJSONEncoder to pass datetime objects to json
    #return HttpResponse(json.dumps(answers, cls=DjangoJSONEncoder), mimetype='application/json')
