from akismet import Akismet, AkismetError
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.utils.encoding import smart_str
from optparse import make_option
from vodkamartiniarticle.helper import check_internal_spam_words
from django.conf import settings

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--filepath', dest='filepath', default=None,
            help='Filepath of file with data to import.'),
        make_option('--ip_address', dest='ip_address', default='127.0.0.1',
            help='Specifies IP address.'),
    )
    help = 'Submit spam text for a file to Akismet.'

    def handle(self, *args, **options):
        filepath = options['filepath']
        ip_address = options['ip_address']

        with open(filepath, 'r') as f:
            content = f.read()

        self.check_spam(content, ip_address)

    def check_spam(self, content, ip_address):
        """
        Test Akismet spam with 'viagra-test-123'
        """
        user_agent = 'VodkaMartiniQA/1.0 Django/1.4'
        akismet_api = Akismet(key=settings.AKISMET_API_KEY, blog_url="http://%s/" % Site.objects.get_current().domain)
        if akismet_api.verify_key():
            akismet_data = {
                    'comment_type' : 'comment', # this needs to be always 'comment'
                    'user_ip': ip_address,
                    'user_agent': user_agent,
                   }
            try:
                if akismet_api.comment_check(smart_str(content), akismet_data, build_data=True):
                    self.stdout.write("-- Spam detected - %s.\n" % ("Akismet",))
                elif check_internal_spam_words(content):
                    self.stdout.write("-- Spam detected - %s.\n" % ("Internal spam words",))
                else:
                    self.stdout.write("-- This is no spam - %s.\n" % ("Akismet",))
            except AkismetError:
                """ This exception can be raised when Akismet is down or some parameter in the call is missing. See akismet.py """
                pass
