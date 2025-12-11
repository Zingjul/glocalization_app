# board/mixins.py
from board.models import Board

class BoardItemsMixin:
    """Mixin to add board items to context for widgets"""
    
    def get_board_items(self, limit=7):
        """Get latest board items for widget display"""
        board_items = []
        
        # Handle PostBoard items
        try:
            post_board = Board.objects.get(name="PostBoard")
            qs = post_board.posts.all().order_by("-created_at")
            
            if hasattr(post_board.posts.model, "status"):
                qs = qs.filter(status="approved")
            
            for obj in qs[:5]:  # Get 5 latest from each board
                board_items.append({
                    "board": post_board,
                    "obj": obj,
                    "type": "post",
                    "created_at": obj.created_at
                })
        except Board.DoesNotExist:
            pass
        
        # Handle SeekersBoard items
        try:
            seeker_board = Board.objects.get(name="SeekersBoard")
            qs = seeker_board.seeker_posts.all().order_by("-created_at")
            
            if hasattr(seeker_board.seeker_posts.model, "status"):
                qs = qs.filter(status="approved")
            
            for obj in qs[:5]:  # Get 5 latest from each board
                board_items.append({
                    "board": seeker_board,
                    "obj": obj,
                    "type": "seekerpost", 
                    "created_at": obj.created_at
                })
        except Board.DoesNotExist:
            pass
        
        # Sort and limit
        board_items.sort(key=lambda x: x["created_at"] if x.get("created_at") else 0, reverse=True)
        return board_items[:limit]

