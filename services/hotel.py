class Hotel:
    def __init__(self, name="My Hotel"):
        self._name = name
        self._rooms = []
        self._guests = []
        self._bookings = []

    @property
    def name(self):
        return self._name

    @property
    def rooms(self):
        return self._rooms

    @property
    def guests(self):
        return self._guests

    @property
    def bookings(self):
        return self._bookings

    def add_room(self, room):
        self._rooms.append(room)

    def remove_room(self, room):
        to_cancel = [b for b in self._bookings if b.room == room]
        for b in to_cancel:
            b.cancel()
            self._bookings.remove(b)
        self._rooms.remove(room)

    def add_guest(self, guest):
        self._guests.append(guest)

    def remove_guest(self, guest):
        to_cancel = [b for b in self._bookings if b.guest == guest]
        for b in to_cancel:
            b.cancel()
            self._bookings.remove(b)
        self._guests.remove(guest)

    def add_booking(self, booking):
        self._bookings.append(booking)

    def remove_booking(self, booking):
        booking.cancel()
        self._bookings.remove(booking)

    def get_total_revenue(self):
        return sum(b.calculate_total() for b in self._bookings)

    def get_occupied_count(self):
        return sum(1 for r in self._rooms if r.is_occupied)