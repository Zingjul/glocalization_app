from django.core.management.base import BaseCommand
from board.models import Board

class Command(BaseCommand):
    help = "Create the central Board instances for notifications (PostBoard and SeekersBoard)."

    def handle(self, *args, **options):
        boards = [
            {"name": "PostBoard", "description": "Board for all new approved posts."},
            {"name": "SeekersBoard", "description": "Board for all new approved seeker requests."}
        ]
        for board_info in boards:
            board, created = Board.objects.get_or_create(
                name=board_info["name"],
                defaults={"description": board_info["description"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Board '{board.name}' created."))
            else:
                self.stdout.write(self.style.WARNING(f"Board '{board.name}' already exists."))