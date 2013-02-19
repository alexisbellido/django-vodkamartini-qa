from django.core.management.base import BaseCommand, CommandError
from vodkamartiniqa.models import Question

class Command(BaseCommand):
    args = '<question_id question_id ...>'
    help = 'Delete question. You will be asked for confirmation on each object.'

    def handle(self, *args, **options):
        questions = Question.objects.filter(id__in=args)
        for question in questions:
            input_msg = "Are you sure you want to delete question with id %d and title '%s'? (type 'y' to confirm)" % (question.id, question.title)
            # TODO list answers and mention they will be deleted as well,
            # maybe use option to just show partial list when it is too long
            delete = raw_input(input_msg + ': ')
            if delete == 'y':
                id = question.id
                title = question.title
                question.delete()
                self.stdout.write("%d: '%s' deleted.\n" % (id, title))

        if not questions.count():
            self.stdout.write("No questions found, please verify the ids used.\n")
