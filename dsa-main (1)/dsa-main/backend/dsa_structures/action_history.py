"""Action history and undo support using a stack."""

from datetime import datetime
from .utils import Stack


class ActionHistory:
    """Maintain action history and undo operations."""

    def __init__(self):
        self.stack = Stack()

    def record(self, action_type: str, payload: dict):
        self.stack.push(
            {
                "type": action_type,
                "payload": payload,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def undo_last(self, route_manager, stop_manager=None):
        action = self.stack.pop()
        if not action:
            return {"success": False, "message": "No actions to undo"}

        action_type = action["type"]
        payload = action["payload"]

        if action_type == "route_created":
            route_manager.delete_route(payload["route_id"])
        elif action_type == "route_deleted":
            route_manager.restore_route(payload["route_data"])
        elif action_type == "stop_added":
            position = route_manager.get_stop_position(payload["route_id"], payload["stop_id"])
            if position == -1:
                raise ValueError("Stop not found for undo")
            route_manager.remove_stop(payload["route_id"], position)
        elif action_type == "stop_removed":
            route_manager.add_stop(payload["route_id"], payload["stop_data"], payload["position"])
        elif action_type == "stop_updated":
            route_manager.update_stop(payload["route_id"], payload["position"], payload["previous_stop"])
        elif action_type == "stops_reordered":
            route_manager.replace_stops(payload["route_id"], payload["previous_stops"])
        elif action_type == "stop_created":
            if not stop_manager:
                raise ValueError("Stop manager not available for undo")
            stop_manager.remove_stop(payload["stop_id"])
        elif action_type == "stop_deleted":
            if not stop_manager:
                raise ValueError("Stop manager not available for undo")
            stop_manager.restore_stop(payload["stop_data"])
        elif action_type == "stop_assigned":
            position = route_manager.get_stop_position(payload["route_id"], payload["stop_id"])
            if position != -1:
                route_manager.remove_stop(payload["route_id"], position)
        else:
            raise ValueError(f"Unsupported action type: {action_type}")

        return {"success": True, "action": action}
