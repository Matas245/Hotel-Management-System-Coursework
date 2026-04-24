# Hotel Management System — OOP Coursework Report

---

## Introduction

### What is this application?

A Hotel Management System built in Python using CustomTkinter. It covers all four OOP pillars, a design pattern, composition and aggregation, file persistence, and unit testing through a working GUI application.

The system manages rooms, guests, and bookings, with a billing overview calculating total revenue.

### How to run the program

**Requirements:** Python 3.10+

```
python main.py
```

**Tests:**

```
python -m unittest tests/test_hotel.py -v
```

### How to use the program

The sidebar has four sections — Rooms, Guests, Bookings, Billing — with Save/Load buttons at the bottom.

**Rooms** — Add, edit, or remove rooms. Choose a type (Single, Double, Suite) and enter a room number.

**Guests** — Register guests with a name, ID, and email. Removing a guest automatically cancels their bookings.

**Bookings** — Pick a guest, room, check-in date, and number of nights. The system checks for overlapping bookings and shows the total before confirming. Searchable by guest name or room number.

**Billing** — Shows total bookings, revenue, and occupied rooms, with a per-booking cost breakdown.

**Save / Load** — Saves/loads all data to CSV files in `data/`.

---

## Body / Analysis

### 1. Four OOP Pillars

#### Abstraction

`Room` is an abstract base class with two abstract methods — `get_room_type()` and `calculate_price()`. It cannot be instantiated directly; all concrete room types must implement these methods.

```python
from abc import ABC, abstractmethod

class Room(ABC):
    def __init__(self, room_number, base_price):
        self._room_number = room_number
        self._base_price = base_price
        self._is_occupied = False

    @abstractmethod
    def get_room_type(self):
        pass

    @abstractmethod
    def calculate_price(self, nights):
        pass
```

#### Inheritance

`SingleRoom`, `DoubleRoom`, and `SuiteRoom` all inherit from `Room`, call `super().__init__()` for shared setup, and implement their own pricing logic.

```python
class SingleRoom(Room):
    def __init__(self, room_number):
        super().__init__(room_number, 100.0)

    def get_room_type(self):
        return "Single"

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
```

#### Polymorphism

All room types implement `calculate_price()`, so `Hotel` and `Booking` can call it on any room without knowing its type.

```python
def get_total_revenue(self):
    return sum(b.calculate_total() for b in self._bookings)
```

`calculate_total()` calls `self._room.calculate_price(self._nights)` — the correct version is resolved at runtime regardless of room type.

#### Encapsulation

All instance attributes use a `_` prefix. The `Guest` class exposes them through property decorators with validation.

```python
class Guest:
    def __init__(self, name, guest_id, email):
        self.name = name
        self.guest_id = guest_id
        self.email = email

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not isinstance(value, str) or "@" not in value:
            raise ValueError("Email must be a valid email address.")
        self._email = value.strip()
```

The same pattern is used across `Room`, `Booking`, and `Hotel`.

---

### 2. Design Pattern — Factory Method

All room creation goes through `RoomFactory.create_room()` rather than instantiating subclasses directly.

```python
class RoomFactory:
    @staticmethod
    def create_room(room_type: str, room_number: str):
        if room_type == "Single":
            return SingleRoom(room_number)
        elif room_type == "Double":
            return DoubleRoom(room_number)
        elif room_type == "Suite":
            return SuiteRoom(room_number)
        else:
            raise ValueError(f"Unknown room type: {room_type}")
```

Both the GUI and `FileManager` use this factory, so adding a new room type only requires updating one place.

The Singleton and Decorator patterns were considered but rejected — neither fit the project's needs without adding unnecessary complexity.

---

### 3. Composition and Aggregation

#### Aggregation

`Booking` holds references to a `Guest` and a `Room` that are passed in from outside. Cancelling a booking frees the room, but both the guest and room remain in the system.

```python
class Booking:
    def __init__(self, guest, room, check_in_date: str, nights: int):
        self._guest = guest
        self._room = room
        self._check_in_date = check_in_date
        self._nights = nights
        self._room.is_occupied = True
```

#### Composition

`Hotel` owns and manages its collections of rooms, guests, and bookings — all created inside `__init__()`.

```python
class Hotel:
    def __init__(self, name="My Hotel"):
        self._name = name
        self._rooms = []
        self._guests = []
        self._bookings = []
```

Removing a room or guest cascades to cancel related bookings. If the `Hotel` instance is discarded, all data goes with it.

---

### 4. File Read and Write

`FileManager` in `storage/file_manager.py` handles saving and loading three CSV files — `rooms.csv`, `guests.csv`, `bookings.csv` — in a `data/` directory that's created automatically.

```python
@staticmethod
def _save_bookings(bookings):
    with open(FileManager.BOOKINGS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["booking_id", "guest_id", "room_number", "check_in_date", "nights"])
        for b in bookings:
            writer.writerow([b.booking_id, b.guest.guest_id, b.room.room_number, b.check_in_date, b.nights])
```

Bookings are loaded last since they depend on guests and rooms already being in memory. References are resolved by matching IDs:

```python
guest = next((g for g in hotel.guests if g.guest_id == row["guest_id"]), None)
room = next((r for r in hotel.rooms if r.room_number == row["room_number"]), None)
if guest and room:
    b = Booking(guest, room, row["check_in_date"], int(row["nights"]))
    b._booking_id = row["booking_id"]
    hotel.add_booking(b)
```

---

### 5. Unit Testing

Tests are in `tests/test_hotel.py` using Python's `unittest` framework. 32 tests across 6 classes, all covering business logic only — no GUI layer.

```
TestRoomTypes     — price calculations, occupied status, room type strings
TestRoomFactory   — correct class returned per type, invalid type handling
TestGuest         — validation logic for name, ID, and email
TestBooking       — creation, room occupation, cancellation, total calculation
TestHotel         — add/remove logic, cascading cancellation, revenue calculation
TestFileManager   — CSV save and load round-trip, missing file handling
```

Example test:

```python
def test_suite_room_price_includes_service_fee(self):
    room = SuiteRoom("103")
    self.assertEqual(room.calculate_price(2), 550.0)
```

`FileManager` tests use a temporary directory and clean up in `tearDown()`:

```python
def tearDown(self):
    for f in [self.ROOMS_FILE, self.GUESTS_FILE, self.BOOKINGS_FILE]:
        if os.path.exists(f):
            os.remove(f)
    os.rmdir(self.TEST_DIR)
    FileManager.ROOMS_FILE = "data/rooms.csv"
    FileManager.GUESTS_FILE = "data/guests.csv"
    FileManager.BOOKINGS_FILE = "data/bookings.csv"
```

All 32 tests pass.

---

## Results and Summary

### Results

- Fully functional Hotel Management System with a CustomTkinter GUI covering rooms, guests, bookings, and billing.
- All four OOP pillars applied meaningfully — abstraction and inheritance through the room hierarchy, polymorphism through runtime dispatch, encapsulation through property validation.
- Factory Method pattern used in both the GUI and file loader, keeping subclass references out of calling code.
- Booking overlap detection compares date ranges rather than just an `is_occupied` flag, since a room can have multiple valid bookings at different times.
- A single shared `Hotel` instance passed into every GUI frame keeps all data mutations centralised, making save/load straightforward.

### Conclusions

The project produces a working Hotel Management System that applies OOP through a real program rather than isolated examples. Splitting models, storage, and GUI into separate modules made the code easier to test and debug.

Possible extensions: dynamic room pricing, check-out tracking, PDF invoices, user authentication, or swapping the CSV layer for SQLite — which would be straightforward since `FileManager` is already isolated from the rest of the system.

---

## Resources

- [Python ABC documentation](https://docs.python.org/3/library/abc.html)
- [CustomTkinter documentation](https://customtkinter.tomschimansky.com/)
- [Python CSV module documentation](https://docs.python.org/3/library/csv.html)
- [Python unittest documentation](https://docs.python.org/3/library/unittest.html)
- [PEP8 Style Guide](https://peps.python.org/pep-0008/)
- [Refactoring Guru — Factory Method](https://refactoring.guru/design-patterns/factory-method)
- [Refactoring Guru — Design Patterns](https://refactoring.guru/design-patterns)
- [Real Python — OOP in Python](https://realpython.com/python3-object-oriented-programming/)