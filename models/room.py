from abc import ABC, abstractmethod

class Room(ABC):
    def __init__(self, room_number, base_price):
        self._room_number = room_number
        self._base_price = base_price
        self._is_occupied = False

    @property
    def room_number(self):
        return self._room_number

    @property
    def is_occupied(self):
        return self._is_occupied

    @property
    def base_price(self):
        return self._base_price

    @is_occupied.setter
    def is_occupied(self, status):
        self._is_occupied = status

    @abstractmethod
    def get_room_type(self):
        pass

    @abstractmethod
    def calculate_price(self, nights):
        pass

    def __str__(self):
        status = "Occupied" if self._is_occupied else "Available"
        return f"Room {self._room_number} ({self.get_room_type()}) - €{self._base_price}/night - {status}"

class SingleRoom(Room):
    def __init__(self, room_number):
        super().__init__(room_number, 100.0)

    def get_room_type(self):
        return "Single"

    def calculate_price(self, nights):
        return self._base_price * nights

class DoubleRoom(Room):
    def __init__(self, room_number):
        super().__init__(room_number, 150.0)

    def get_room_type(self):
        return "Double"

    def calculate_price(self, nights):
        return self._base_price * nights

class SuiteRoom(Room):
    def __init__(self, room_number):
        super().__init__(room_number, 250.0)

    def get_room_type(self):
        return "Suite"

    def calculate_price(self, nights):
        service_fee = 50.0
        return (self._base_price * nights) + service_fee