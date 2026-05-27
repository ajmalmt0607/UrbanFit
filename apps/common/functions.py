from django.utils import timezone
from django.db import transaction
from django.utils.text import slugify
import uuid


def get_auto_id(model):

    with transaction.atomic():

        last_object = (
            model.objects
            .select_for_update()
            .order_by("-auto_id")
            .first()
        )

        if last_object and last_object.auto_id:
            return last_object.auto_id + 1

        return 1


def basedata(instance, request):

    user = request.user

    username = None

    # If logged in user exists
    if user and user.is_authenticated:
        username = user.username

    # CREATE
    if instance._state.adding:

        instance.auto_id = get_auto_id(
            instance.__class__
        )

        instance.creator = username

    # UPDATE
    instance.updater = username

    instance.updated_at = timezone.now()


def generate_slug(title):

    slug = slugify(title)

    unique_suffix = uuid.uuid4().hex[:7]

    return f"{slug}-{unique_suffix}"