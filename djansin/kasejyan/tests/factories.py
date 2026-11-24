import factory
from django.contrib.auth import get_user_model

from djansin.kasejyan.models import Email, Phone


User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "secret123")


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Email

    address = factory.Sequence(lambda n: f"user{n}@example.com")


class PhoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Phone

    number = factory.Sequence(lambda n: f"+98912{n:07d}")
