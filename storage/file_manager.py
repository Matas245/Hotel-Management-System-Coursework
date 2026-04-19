import csv
import os
from models.room_factory import RoomFactory
from models.guest import Guest
from models.booking import Booking


class FileManager:
    ROOMS_FILE = "data/rooms.csv"
    GUESTS_FILE = "data/guests.csv"
    BOOKINGS_FILE = "data/bookings.csv"

    @staticmethod
    def save(hotel):
        os.makedirs("data", exist_ok=True)
        FileManager._save_rooms(hotel.rooms)
        FileManager._save_guests(hotel.guests)
        FileManager._save_bookings(hotel.bookings)

    @staticmethod
    def load(hotel):
        for guest in FileManager._load_guests():
            hotel.add_guest(guest)
        for room in FileManager._load_rooms():
            hotel.add_room(room)
        FileManager._load_bookings(hotel)

    @staticmethod
    def _save_rooms(rooms):
        with open(FileManager.ROOMS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["room_number", "room_type"])
            for room in rooms:
                writer.writerow([room.room_number, room.get_room_type()])

    @staticmethod
    def _save_guests(guests):
        with open(FileManager.GUESTS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "guest_id", "email"])
            for guest in guests:
                writer.writerow([guest.name, guest.guest_id, guest.email])

    @staticmethod
    def _save_bookings(bookings):
        with open(FileManager.BOOKINGS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["booking_id", "guest_id", "room_number", "check_in_date", "nights"])
            for b in bookings:
                writer.writerow([b.booking_id, b.guest.guest_id, b.room.room_number, b.check_in_date, b.nights])

    @staticmethod
    def _load_rooms():
        if not os.path.exists(FileManager.ROOMS_FILE):
            return []
        with open(FileManager.ROOMS_FILE, "r") as f:
            return [RoomFactory.create_room(row["room_type"], row["room_number"]) for row in csv.DictReader(f)]

    @staticmethod
    def _load_guests():
        if not os.path.exists(FileManager.GUESTS_FILE):
            return []
        with open(FileManager.GUESTS_FILE, "r") as f:
            return [Guest(row["name"], row["guest_id"], row["email"]) for row in csv.DictReader(f)]

    @staticmethod
    def _load_bookings(hotel):
        if not os.path.exists(FileManager.BOOKINGS_FILE):
            return
        with open(FileManager.BOOKINGS_FILE, "r") as f:
            for row in csv.DictReader(f):
                guest = next((g for g in hotel.guests if g.guest_id == row["guest_id"]), None)
                room = next((r for r in hotel.rooms if r.room_number == row["room_number"]), None)
                if guest and room:
                    b = Booking(guest, room, row["check_in_date"], int(row["nights"]))
                    b._booking_id = row["booking_id"]
                    hotel.add_booking(b)