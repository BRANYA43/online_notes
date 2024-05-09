from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, CommandError
from django.utils.translation import gettext as _
from core.settings.components import env
from notes.models import Worktable

User = get_user_model()


class Command(BaseCommand):
    help = _('Create a worktable with an associated superuser.')

    def add_arguments(self, parser):
        parser.add_argument('--email', dest='email', help=_('Specifies the email for the superuser.'))
        parser.add_argument(
            '--no-input',
            action='store_true',
            dest='no_input',
            help=_(
                'Create a worktable with no input. Email will get from DJANGO_SUPERUSER_EMAIL environment variable.'
            ),
        )

    def handle(self, *args, **options):
        if options['no_input']:
            email = env.get('DJANGO_SUPERUSER_EMAIL')
            if not email:
                raise CommandError(_('DJANGO_SUPERUSER_EMAIL environment variable is not set.'))

        else:
            email = options['email']
            if not email:
                raise CommandError(_('You must input an email.'))

        try:
            superuser = User.objects.get(email=email)
        except User.DoesNotExist as e:
            raise CommandError(_(f'Failed to got superuser: {e}'))
        Worktable.objects.create(user=superuser)

        self.stdout.write(self.style.SUCCESS(_('Worktable with an associated superuser was created successfully.')))
