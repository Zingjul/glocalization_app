from django.apps import apps
from django.db import transaction
from django.utils import timezone

def _app_and_model(obj):
    return obj._meta.app_label, obj.class.name.lower()

def _get_board(name: str):
    Board = apps.get_model('notifications', 'Board')
    return Board.objects.get(name=name)

def push_to_board(board_name: str, instance, title=None, url=None, extra=None, approved_at=None):
    BoardItem = apps.get_model('notifications', 'BoardItem')
    board = _get_board(board_name)
    app_label, model = _app_and_model(instance)

    get_url = getattr(instance, 'get_absolute_url', None)
    resolved_url = url or (get_url() if callable(get_url) else '')

    payload = {
        'title': title or getattr(instance, 'title', None) or str(instance),
        'url': resolved_url,
        'extra': extra or {},
        'approved_at': approved_at or timezone.now(),
    }

    def _do():
        BoardItem.objects.update_or_create(
            board=board,
            target_app_label=app_label,
            target_model=model,
            target_object_id=instance.pk,
            defaults=payload
        )
    transaction.on_commit(_do)

def remove_from_board(board_name: str, instance):
    BoardItem = apps.get_model('notifications', 'BoardItem')
    board = _get_board(board_name)
    app_label, model = _app_and_model(instance)
    def _do():
        BoardItem.objects.filter(
            board=board,
            target_app_label=app_label,
            target_model=model,
            target_object_id=instance.pk
        ).delete()
    transaction.on_commit(_do)