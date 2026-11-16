from core.utils.user_identifier import is_valid_email, is_valid_phone
from djansin.kasejyan.models import Email, Phone, User


class UserResolverMixin:
    def _resolve_user(self, identifier: str) -> User | None:
        if is_valid_email(identifier=identifier):
            contact = (
                Email.objects.filter(address=identifier).select_related("user").first()
            )
            return contact.user if contact else None
        if is_valid_phone(identifier=identifier):
            contact = (
                Phone.objects.filter(number=identifier).select_related("user").first()
            )
            return contact.user if contact else None
        return User.objects.filter(username=identifier).first()
