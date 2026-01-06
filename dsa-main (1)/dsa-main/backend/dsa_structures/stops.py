"""Bus Stop Management using Array/List and Graph nodes."""

import json
import os
import uuid
from datetime import datetime


class BusStopManager:
    """Manage city bus stops with list-based storage."""

    def __init__(self, stops_file: str):
        self.stops_file = stops_file
        self.stops = []
        self.load_stops()

    def load_stops(self):
        """Load stops from JSON file."""
        if not os.path.exists(self.stops_file):
            self.save_stops()
            return
        try:
            with open(self.stops_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.stops = data.get("stops", []) if isinstance(data, dict) else []
        except (OSError, json.JSONDecodeError):
            self.stops = []

    def save_stops(self):
        """Persist stops to JSON file."""
        os.makedirs(os.path.dirname(self.stops_file), exist_ok=True)
        data = {
            "stops": self.stops,
            "total_stops": len(self.stops),
            "last_updated": datetime.now().isoformat(),
        }
        with open(self.stops_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _normalize_name(self, name: str) -> str:
        return (name or "").strip()

    def _find_duplicate_name(self, name: str):
        name_lower = name.lower()
        for stop in self.stops:
            if stop.get("stop_name", "").strip().lower() == name_lower:
                return stop
        return None

    def add_stop(self, stop_data: dict):
        """Add a new stop after validating duplicates."""
        stop_name = self._normalize_name(stop_data.get("stop_name"))
        if not stop_name:
            raise ValueError("stop_name is required")

        if self._find_duplicate_name(stop_name):
            raise ValueError(f"Stop '{stop_name}' already exists")

        stop = {
            "stop_id": stop_data.get("stop_id") or str(uuid.uuid4()),
            "stop_name": stop_name,
            "location": stop_data.get("location", ""),
            "latitude": stop_data.get("latitude"),
            "longitude": stop_data.get("longitude"),
            "created_at": datetime.now().isoformat(),
        }
        self.stops.append(stop)
        self.save_stops()
        return stop

    def remove_stop(self, stop_id: str):
        """Remove a stop by ID."""
        for idx, stop in enumerate(self.stops):
            if stop.get("stop_id") == stop_id:
                removed = self.stops.pop(idx)
                self.save_stops()
                return removed
        raise ValueError("Stop not found")

    def restore_stop(self, stop_data: dict):
        """Restore a previously removed stop."""
        stop_name = self._normalize_name(stop_data.get("stop_name"))
        if self._find_duplicate_name(stop_name):
            raise ValueError(f"Stop '{stop_name}' already exists")
        self.stops.append(stop_data)
        self.save_stops()
        return stop_data

    def get_all_stops(self):
        """Return all stops."""
        return list(self.stops)

    def get_stop_by_id(self, stop_id: str):
        for stop in self.stops:
            if stop.get("stop_id") == stop_id:
                return stop
        return None

    def assign_stop_to_route(self, route_manager, route_id: str, stop_id: str, position=None):
        """Assign an existing stop to a route with validation."""
        route = route_manager.routes.get(route_id)
        if not route:
            raise ValueError("Route not found")

        stop = self.get_stop_by_id(stop_id)
        if not stop:
            raise ValueError("Stop not found")

        stop_name = stop.get("stop_name", "").strip()
        if route_manager.has_stop_name(route_id, stop_name):
            raise ValueError(f"Route already contains stop '{stop_name}'")

        if position is not None and position > len(route) + 1:
            raise ValueError("Position out of bounds for route assignment")

        return route_manager.add_stop(route_id, stop.copy(), position)
