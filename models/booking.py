import uuid

class Booking:
    def __init__(self, guest, room, check_in_date: str, nights: int):
        self._booking_id = str(uuid.uuid4())[:8].upper()
        self._guest = guest
        self._room = room
        self._check_in_date = check_in_date
        self._nights = nights
        self._room.is_occupied = True

    @property
    def booking_id(self):
        return self._booking_id

    @property
    def guest(self):
        return self._guest

    @property
    def room(self):
        return self._room

    @property
    def check_in_date(self):
        return self._check_in_date

    @property
    def nights(self):
        return self._nights

    def calculate_total(self):
        return self._room.calculate_price(self._nights)

    def cancel(self):
        self._room.is_occupied = False

    def __str__(self):
        return (f"Booking {self._booking_id}: {self._guest.name} "
                f"- Room {self._room.room_number} "
                f"({self._nights} nights, check-in {self._check_in_date})")