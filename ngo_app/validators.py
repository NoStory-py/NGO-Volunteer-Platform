from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class CustomPasswordValidator:
    def validate(self, password, user=None):
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("This password must contain at least one uppercase letter."),
                code='no_uppercase',
            )

        # Check for at least one symbol
        if not re.search(r'[@$!%*?&]', password):
            raise ValidationError(
                _("This password must contain at least one special character (e.g., @$!%*?&)."),
                code='no_symbol',
            )

        # Check for at least one digit
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("This password must contain at least one digit."),
                code='no_digit',
            )

    def get_help_text(self):
        return _("Your password must contain at least one uppercase letter, one special character (e.g., @$!%*?&), and one digit.")