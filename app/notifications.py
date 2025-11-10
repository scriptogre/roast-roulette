# """
# Notification service for handling player join/leave/reconnect notifications.
# """
#
# from datetime import datetime
# from main.models import PlayerConnection, Game
#
#
# def is_recently_joined(connection: PlayerConnection, game: Game) -> bool:
#     """Check if connection is a new joiner (not host, created recently)."""
#     if not connection.created_at or connection.player == game.host:
#         return False
#     return (datetime.now() - connection.created_at).total_seconds() < 5
#
#
# def is_recently_reconnected(connection: PlayerConnection) -> bool:
#     """Check if connection recently reconnected (was existing connection that reconnected)."""
#     if not connection.is_active:
#         return False
#
#     # Only show reconnection if they became active recently but weren't just created
#     recently_became_active = (
#         datetime.now() - connection.activity_changed_at
#     ).total_seconds() < 5
#     not_new_connection = (datetime.now() - connection.created_at).total_seconds() > 30
#
#     return recently_became_active and not_new_connection
#
#
# def is_recently_left(connection: PlayerConnection) -> bool:
#     """Check if connection was recently disconnected."""
#     if connection.is_active:
#         return False
#     return (datetime.now() - connection.activity_changed_at).total_seconds() < 5
#
#
# def get_latest_notifications(game: Game) -> list[dict]:
#     """Generate latest notifications based on current connection states."""
#     notifications = []
#
#     for connection in game.connections:
#         if is_recently_joined(connection, game):
#             notifications.append(
#                 {
#                     "type": "player_joined",
#                     "player": connection.player,
#                     "message": f"{connection.player.name} joined the game",
#                 }
#             )
#         elif is_recently_reconnected(connection):
#             notifications.append(
#                 {
#                     "type": "player_reconnected",
#                     "player": connection.player,
#                     "message": f"{connection.player.name} reconnected",
#                 }
#             )
#         elif is_recently_left(connection):
#             notifications.append(
#                 {
#                     "type": "player_left",
#                     "player": connection.player,
#                     "message": f"{connection.player.name} left the game",
#                 }
#             )
#
#     return notifications
