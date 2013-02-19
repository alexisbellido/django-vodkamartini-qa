from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from vodkamartiniqa.models import Question
from vodkamartinicategory.models import Category
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

class Command(BaseCommand):
    args = '<question_title question_title ...>'
    option_list = BaseCommand.option_list + (
        make_option('--category_id', dest='category_id', default=None,
            help='Specifies the category id to use for new questions.'),
    )
    help = 'Creates questions.'

    def handle(self, *args, **options):
        try:
            c = Category.objects.get(pk=options['category_id'])
        except Category.DoesNotExist:
            raise CommandError('Category with id "%s" does not exist' % options['category_id'])

        for title in args:
            q = self.create_question(title, c)

    def create_question(self, title, c):
        teaser = 'teaser for %s' % (title,)
        body = 'body for %s' % (title,)
        u = User.objects.get(pk=1)
        slug = slugify(title)
        status = Question.DRAFT_STATUS
        q = Question(title=title, teaser=teaser, body=body, slug=slug, author=u, status=status)
        q.save()
        q.categories.add(c)
        q.save()
        self.stdout.write("Created question %d:'%s' for category '%s'.\n" % (q.id, q.title, c.title))
