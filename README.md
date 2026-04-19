# Hotel Management System — OOP Coursework Report

**Course:** Object-Oriented Programming  
**Topic:** Hotel Management System  
**Language:** Python  

---

## Table of Contents

1. [Introduction](#introduction)
2. [Body / Analysis](#body--analysis)
3. [Results and Summary](#results-and-summary)
4. [Resources](#resources)

---

## Introduction

### What is this application?

This coursework project is a Hotel Management System built in Python using the CustomTkinter GUI framework. The goal of the application is to demonstrate practical use of Object-Oriented Programming principles — including all four OOP pillars, a design pattern, composition and aggregation, file persistence, and unit testing — through a realistic, functional program.

The system allows a hotel to manage its rooms, registered guests, and bookings through a graphical interface. It also provides a billing overview that calculates the total revenue from all active bookings.

### How to run the program

**Requirements:**

- Python 3.10 or higher
- CustomTkinter library

**Installation:**

```
pip install customtkinter
```

**Running the application:**

Navigate to the project root directory and run:

```
python main.py
```

**Running the tests:**

```
python -m unittest tests/test_hotel.py -v
```

### How to use the program

The application opens with a sidebar on the left containing four navigation sections: Rooms, Guests, Bookings, and Billing. At the bottom of the sidebar there are Save and Load buttons for persisting data between sessions.

**Rooms** — Click "Add Room" to open a configuration panel. Select a room type (Single, Double, or Suite) and enter a room number. Click Apply to confirm. Existing rooms can be edited or removed from the list.

**Guests** — Click "Add Guest" to register a new guest with a name, ID, and email address. Guests can be edited or removed. Removing a guest will automatically cancel any bookings associated with them.

**Bookings** — Click "Add Booking" to create a reservation. Select a guest and a room from the dropdowns, choose a check-in date using the date picker, and enter the number of nights. The system validates that the selected room is not already booked for the requested period and shows an estimated total before confirming. Bookings can be searched by guest name or room number.

**Billing** — Displays a live summary of total bookings, total revenue, and occupied room count, followed by a line-by-line breakdown of each booking and its cost.

**Save / Load** — The Save button writes all current rooms, guests, and bookings to CSV files in the `data/` folder. The Load button reads those files and restores the previous session state.

---

## Body / Analysis

### 1. Four OOP Pillars

#### Abstraction

Abstraction means hiding implementation details behind a common interface, exposing only what is necessary. In this project, the `Room` class is defined as an abstract base class using Python's `abc` module. It declares two abstract methods — `get_room_type()` and `calculate_price()` — which every concrete room subclass must implement. The `Room` class itself cannot be instantiated directly.

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

Any code that works with a room only needs to call `calculate_price()` — it does not need to know which subclass it is dealing with or how the price is computed internally.

#### Inheritance

Inheritance allows a class to derive behaviour and attributes from a parent class, extending or overriding them as needed. The three room types — `SingleRoom`, `DoubleRoom`, and `SuiteRoom` — all inherit from the abstract `Room` base class. Each subclass calls `super().__init__()` to set up the shared attributes and then implements the abstract methods with its own logic.

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

This avoids duplicating the shared room logic while still allowing each type to behave differently.

#### Polymorphism

Polymorphism means that the same method call can produce different behaviour depending on the object it is called on. Because all three room types implement `calculate_price()`, the `Hotel` class and the `Booking` class can call this method on any room without knowing its specific type. The correct version is resolved at runtime.

```python
def get_total_revenue(self):
    return sum(b.calculate_total() for b in self._bookings)
```

`calculate_total()` on a `Booking` calls `self._room.calculate_price(self._nights)`. Whether that room is a `SingleRoom`, `DoubleRoom`, or `SuiteRoom` is irrelevant — the right method is called automatically. This is also visible in the billing frame, where every booking's cost is displayed using the same call regardless of room type.

#### Encapsulation

Encapsulation means keeping an object's internal state private and controlling access through defined interfaces. Throughout the project, all instance attributes are prefixed with a single underscore to mark them as protected. In the `Guest` class, attributes are exposed through Python property decorators that include validation logic, preventing invalid data from ever entering the object.

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

The same pattern is used across `Room`, `Booking`, and `Hotel` — internal lists and values are never exposed directly for external modification.

---

### 2. Design Pattern — Factory Method

The Factory Method pattern centralises object creation behind a dedicated method, so that the calling code does not need to know which specific class to instantiate. Instead of writing `SingleRoom(number)` or `SuiteRoom(number)` directly throughout the codebase, all room creation is routed through `RoomFactory.create_room()`.

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

This pattern fits the project because room creation happens in multiple places — the GUI when a user adds a room, and the `FileManager` when loading saved data. In both cases, they call `RoomFactory.create_room()` with a type string and a room number. If a new room type were added in the future, only the factory would need updating, not every location that creates rooms.

The Singleton pattern was considered but rejected — there is no need to restrict instantiation of any class to a single instance. The Decorator pattern was also considered for adding extra charges to rooms, but since the price logic is simple and clearly defined per type, it would have added unnecessary complexity.

---

### 3. Composition and Aggregation

#### Aggregation

Aggregation is a relationship where one object holds references to other objects that exist independently of it. In this project, the `Booking` class holds a reference to a `Guest` and a `Room`, but neither is created by the `Booking` — they are passed in from outside and continue to exist if the booking is cancelled or deleted.

```python
class Booking:
    def __init__(self, guest, room, check_in_date: str, nights: int):
        self._guest = guest
        self._room = room
        self._check_in_date = check_in_date
        self._nights = nights
        self._room.is_occupied = True
```

The `Guest` and `Room` objects are not owned by the `Booking`. Cancelling a booking frees the room and removes the booking, but the guest and room remain registered in the system.

#### Composition

Composition is a stronger relationship where one object owns and manages the lifecycle of its parts. The `Hotel` class is responsible for creating and managing the collections of rooms, guests, and bookings. These lists are created inside `Hotel.__init__()` and are entirely managed through the hotel's own methods.

```python
class Hotel:
    def __init__(self, name="My Hotel"):
        self._name = name
        self._rooms = []
        self._guests = []
        self._bookings = []
```

When a room or guest is removed through the `Hotel` class, it also cascades to cancel any related bookings, enforcing data integrity from a single point of control. The `Hotel` owns its data — if the hotel instance is discarded, all of its data goes with it.

---

### 4. File Read and Write

Data persistence is handled by the `FileManager` class in `storage/file_manager.py`. It reads and writes three CSV files: `rooms.csv`, `guests.csv`, and `bookings.csv`, stored in a `data/` directory that is created automatically if it does not exist.

The `save()` method serialises each collection to its respective file:

```python
@staticmethod
def _save_bookings(bookings):
    with open(FileManager.BOOKINGS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["booking_id", "guest_id", "room_number", "check_in_date", "nights"])
        for b in bookings:
            writer.writerow([b.booking_id, b.guest.guest_id, b.room.room_number, b.check_in_date, b.nights])
```

The `load()` method reads back each file and reconstructs the objects. Bookings are loaded last because they depend on guest and room objects already existing in memory. The loading resolves foreign key references by matching `guest_id` and `room_number` to the already-loaded objects:

```python
guest = next((g for g in hotel.guests if g.guest_id == row["guest_id"]), None)
room = next((r for r in hotel.rooms if r.room_number == row["room_number"]), None)
if guest and room:
    b = Booking(guest, room, row["check_in_date"], int(row["nights"]))
    b._booking_id = row["booking_id"]
    hotel.add_booking(b)
```

The original booking ID is restored from the file to preserve continuity across sessions. Save and Load buttons are always visible at the bottom of the sidebar in the application.

---

### 5. Unit Testing

Unit tests are written using Python's built-in `unittest` framework and are located in `tests/test_hotel.py`. Tests cover all core business logic without touching the GUI layer. There are 32 tests across 6 test classes.

```
TestRoomTypes     — price calculations, occupied status, room type strings
TestRoomFactory   — correct class returned per type, invalid type handling
TestGuest         — validation logic for name, ID, and email
TestBooking       — creation, room occupation, cancellation, total calculation
TestHotel         — add/remove logic, cascading cancellation, revenue calculation
TestFileManager   — CSV save and load round-trip, missing file handling
```

An example test that verifies the Suite room's service fee is applied correctly:

```python
def test_suite_room_price_includes_service_fee(self):
    room = SuiteRoom("103")
    self.assertEqual(room.calculate_price(2), 550.0)
```

The `FileManager` tests use a temporary subdirectory and restore the original file paths in `tearDown()` to avoid interfering with real data:

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

All 32 tests pass successfully.

---

## Results and Summary

### Results

- A fully functional Hotel Management System was implemented in Python with a CustomTkinter graphical interface, covering all four management areas: rooms, guests, bookings, and billing.
- All four OOP pillars were applied in a meaningful and non-superficial way — abstraction and inheritance through the room class hierarchy, polymorphism through runtime method dispatch, and encapsulation through protected attributes and property validation.
- The Factory Method design pattern was successfully integrated into both the GUI and the file loading process, eliminating direct subclass references from the calling code and making the room creation logic easy to extend.
- One of the more technically interesting challenges was designing the booking overlap detection — ensuring that a room cannot be double-booked required comparing date ranges rather than just checking an `is_occupied` flag, since multiple bookings for the same room at different times are valid.
- Separating the GUI layer entirely from the business logic proved to be a significant structural decision. Passing a shared `Hotel` instance into every frame meant that all data mutations happen through a single object, which made the file save and load operations straightforward to implement.

### Conclusions

This coursework produced a working, structured Hotel Management System that demonstrates Object-Oriented Programming concepts through practical application rather than isolated examples. The program is usable — a user can open the application, add rooms and guests, make bookings, review billing, and save their session to disk.

The result confirms that OOP principles are not just academic constructs but genuinely useful tools for organising a codebase. The separation of models, services, storage, and GUI into distinct modules made the project easier to navigate, test, and debug.

Looking forward, the application could be extended in several directions. Room pricing could be made dynamic with seasonal rates or discount logic added to the factory. The booking system could be expanded to include check-out tracking and invoice generation as PDF exports. User authentication could be added to support multiple staff members with different permission levels. The CSV persistence layer could be replaced with a SQLite database with minimal changes to the rest of the architecture, since the `FileManager` class is already fully isolated from the rest of the system.

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