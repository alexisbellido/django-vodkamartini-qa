from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from vodkamartiniqa.models import Question, Answer
from django.contrib.auth.models import User

class Command(BaseCommand):
    args = '<answer answer ...>'
    option_list = BaseCommand.option_list + (
        make_option('--question_id', dest='question_id', default=None,
            help='Specifies the question id to use for the answers.'),
    )
    help = 'Creates answers for one question.'

    def handle(self, *args, **options):
        try:
            q = Question.objects.get(pk=options['question_id'])
        except Question.DoesNotExist:
            raise CommandError("Question with id %s does not exist" % (options['question_id']))

        self.stdout.write("Question: '%s'.\n" % (q.title,))
        for answer in args:
            self.create_answer(answer, q)

    def create_answer(self, answer, q):
        u = User.objects.get(pk=1)
        a = Answer(answer=answer, question=q, author=u)
        a.save()
        self.stdout.write("-- Created answer %d:'%s'.\n" % (a.id, a.answer))
