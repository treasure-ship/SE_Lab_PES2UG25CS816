"""Hostel room allocation system.

Reads a YAML room configuration, allocates beds by block and gender,
vacates rooms, calculates fees, orders students by seniority, runs a room
lottery, counts vacant beds and exposes a small Flask page for looking up
a student's room.
"""
import logging.config
import math
import os
import random

import yaml
from flask import Flask, request
from markupsafe import escape

# Global hostel state
rooms = {}
allocations = {}
waitlist = []
app = Flask(__name__)

DAYS_PER_MONTH = 30

CONFIG = """
blocks:
  A: {gender: M, rooms: 3, capacity: 2, fee: 4000}
  B: {gender: F, rooms: 2, capacity: 3, fee: 3500}
"""


def load_config(text=CONFIG):
    """Parse the YAML configuration and build the room table."""
    config = yaml.safe_load(text)
    for block, info in config["blocks"].items():
        for number in range(1, info["rooms"] + 1):
            rooms[block + str(number)] = {
                "gender": info["gender"],
                "capacity": info["capacity"],
                "fee": info["fee"],
                "occupants": [],
            }
    return config


def allocate_room(student_id, name, gender, year, preferred=None):
    """Allocate a bed to a student and return the room number.

    Returns None if the year is invalid or the student is waitlisted.
    A student who already has a room keeps it.
    """
    if not isinstance(year, int) or isinstance(year, bool):
        return None
    if student_id in allocations:
        return allocations[student_id]["room"]
    candidates = [r for r in (preferred or []) if r in rooms] + list(rooms)
    for room_no in candidates:
        room = rooms[room_no]
        if room["gender"] != gender:
            continue
        if len(room["occupants"]) >= room["capacity"]:
            continue
        room["occupants"].append(student_id)
        allocations[student_id] = {"name": name, "room": room_no,
                                   "year": year}
        return room_no
    if student_id not in waitlist:
        waitlist.append(student_id)
    return None


def vacate_room(student_id):
    """Free the student's bed. Return True if they had a room."""
    allocation = allocations.pop(student_id, None)
    if allocation is None:
        return False
    rooms[allocation["room"]]["occupants"].remove(student_id)
    return True


def monthly_fee(student_id, days_stayed):
    """Return the fee for the stay; a part month is billed as a full month."""
    if student_id not in allocations:
        raise ValueError(f"{student_id} has no room allocated")
    room = rooms[allocations[student_id]["room"]]
    months = math.ceil(days_stayed / DAYS_PER_MONTH)
    return months * room["fee"]


def priority_order(students):
    """Order students by seniority, most senior (highest year) first."""
    return sorted(students, key=lambda s: s["year"], reverse=True)


def room_lottery(student_ids):
    """Return the students in a random order."""
    return random.SystemRandom().sample(student_ids, len(student_ids))


def vacant_beds():
    """Count every free bed, including those in partly filled rooms."""
    return sum(info["capacity"] - len(info["occupants"])
               for info in rooms.values())


def connect_warden_db():
    """Connect using credentials taken from environment variables."""
    return sqlite_connect(
        host=os.environ.get("WARDEN_DB_HOST", "localhost"),
        user=os.environ.get("WARDEN_DB_USER", "warden"),
        password=os.environ.get("WARDEN_DB_PASSWORD", ""),
    )


def sqlite_connect(host, user, password):
    """Stand-in for a real database connection."""
    return {"host": host, "user": user, "connected": len(password) > 0}


def start_remote_log_config():
    """Configure logging locally (no network listener)."""
    logging.config.dictConfig({"version": 1, "root": {"level": "INFO"}})


@app.route("/room")
def room_lookup():
    """Show the room of the student given in the ?id= query parameter."""
    sid = request.args.get("id")
    if sid is None:
        return "<h1>Missing id parameter</h1>", 400
    return f"<h1>Room for {escape(sid)}: {escape(allocations.get(sid))}</h1>"


def run_portal():
    """Start the lookup portal without the debugger."""
    app.run(debug=False)


def main():
    """Run a demonstration of the allocation system."""
    load_config()
    print("Rooms:", list(rooms.keys()))
    print("S1 ->", allocate_room("S1", "Arjun", "M", 1))
    print("S2 ->", allocate_room("S2", "Kabir", "M", 2))
    print("S3 ->", allocate_room("S3", "Rohan", "M", 3))
    print("S4 (female) ->", allocate_room("S4", "Diya", "F", 1))
    print("S1 again ->", allocate_room("S1", "Arjun", "M", 1))
    print("S5 year '2' ->", allocate_room("S5", "Vikram", "M", "2"))
    print("Occupants of A1:", rooms["A1"]["occupants"])
    vacate_room("S2")
    print("Occupants of A1 after S2 left:", rooms["A1"]["occupants"])
    print("Fee for S1, 45 days:", monthly_fee("S1", 45))
    ordered = priority_order([{"year": 1}, {"year": 4}, {"year": 2}])
    print("Priority (seniors first):", [s["year"] for s in ordered])
    print("Lottery:", room_lottery(["S6", "S7", "S8"]))
    print("Vacant beds:", vacant_beds())
    print("Warden DB:", connect_warden_db())
    print("Waitlist:", waitlist)


if __name__ == "__main__":
    main()
