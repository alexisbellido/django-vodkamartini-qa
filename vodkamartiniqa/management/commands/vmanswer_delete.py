from django.core.management.base import BaseCommand, CommandError
from vodkamartiniqa.models import Answer

class Command(BaseCommand):
    args = '<answer_id answer_id ...>'
    help = 'Delete answer. You will be asked for confirmation.'

    def handle(self, *args, **options):
        answers = Answer.objects.filter(id__in=args)
        for answer in answers:
            input_msg = "Are you sure you want to delete answer with %d:'%s' (type 'y' to confirm)" % (answer.id, answer.answer)
            delete = raw_input(input_msg + ': ')
            if delete == 'y':
                self.stdout.write("%d: '%s' deleted.\n" % (answer.id, answer.answer))
                answer.delete()

        if not answers.count():
            self.stdout.write("No answers found, please verify the ids used.\n")
