import unittest
import os
import csv
from models.room import SingleRoom, DoubleRoom, SuiteRoom
from models.guest import Guest
from models.booking import Booking
from models.room_factory import RoomFactory
from services.hotel import Hotel
from storage.file_manager import FileManager


class TestRoomTypes(unittest.TestCase):
    def test_single_room_price(self):
        room = SingleRoom("101")
        self.assertEqual(room.calculate_price(3), 300.0)

    def test_double_room_price(self):
        room = DoubleRoom("102")
        self.assertEqual(room.calculate_price(2), 300.0)

    def test_suite_room_price_includes_service_fee(self):
        room = SuiteRoom("103")
        self.assertEqual(room.calculate_price(2), 550.0)

    def test_room_default_not_occupied(self):
        room = SingleRoom("101")
        self.assertFalse(room.is_occupied)

    def test_room_occupied_setter(self):
        room = SingleRoom("101")
        room.is_occupied = True
        self.assertTrue(room.is_occupied)

    def test_room_get_type(self):
        self.assertEqual(SingleRoom("101").get_room_type(), "Single")
        self.assertEqual(DoubleRoom("102").get_room_type(), "Double")
        self.assertEqual(SuiteRoom("103").get_room_type(), "Suite")


class TestRoomFactory(unittest.TestCase):
    def test_creates_single_room(self):
        room = RoomFactory.create_room("Single", "101")
        self.assertIsInstance(room, SingleRoom)

    def test_creates_double_room(self):
        room = RoomFactory.create_room("Double", "102")
        self.assertIsInstance(room, DoubleRoom)

    def test_creates_suite_room(self):
        room = RoomFactory.create_room("Suite", "103")
        self.assertIsInstance(room, SuiteRoom)

    def test_invalid_type_raises_error(self):
        with self.assertRaises(ValueError):
            RoomFactory.create_room("Penthouse", "104")

    def test_get_room_types_returns_all(self):
        types = RoomFactory.get_room_types()
        self.assertIn("Single", types)
        self.assertIn("Double", types)
        self.assertIn("Suite", types)


class TestGuest(unittest.TestCase):
    def test_valid_guest_creation(self):
        guest = Guest("John Smith", "G001", "john@email.com")
        self.assertEqual(guest.name, "John Smith")
        self.assertEqual(guest.guest_id, "G001")
        self.assertEqual(guest.email, "john@email.com")

    def test_empty_name_raises_error(self):
        with self.assertRaises(ValueError):
            Guest("", "G001", "john@email.com")

    def test_invalid_email_raises_error(self):
        with self.assertRaises(ValueError):
            Guest("John", "G001", "notanemail")

    def test_name_strips_whitespace(self):
        guest = Guest("  John  ", "G001", "john@email.com")
        self.assertEqual(guest.name, "John")


class TestBooking(unittest.TestCase):
    def setUp(self):
        self._guest = Guest("Anna", "G001", "anna@email.com")
        self._room = SingleRoom("101")

    def test_booking_creation(self):
        booking = Booking(self._guest, self._room, "01/06/2025", 3)
        self.assertEqual(booking.guest, self._guest)
        self.assertEqual(booking.room, self._room)
        self.assertEqual(booking.nights, 3)
        self.assertEqual(booking.check_in_date, "01/06/2025")

    def test_booking_marks_room_occupied(self):
        Booking(self._guest, self._room, "01/06/2025", 3)
        self.assertTrue(self._room.is_occupied)

    def test_booking_cancel_frees_room(self):
        booking = Booking(self._guest, self._room, "01/06/2025", 3)
        booking.cancel()
        self.assertFalse(self._room.is_occupied)

    def test_booking_calculate_total(self):
        booking = Booking(self._guest, self._room, "01/06/2025", 5)
        self.assertEqual(booking.calculate_total(), 500.0)

    def test_booking_id_generated(self):
        booking = Booking(self._guest, self._room, "01/06/2025", 2)
        self.assertIsNotNone(booking.booking_id)
        self.assertEqual(len(booking.booking_id), 8)


class TestHotel(unittest.TestCase):
    def setUp(self):
        self._hotel = Hotel("Test Hotel")
        self._guest = Guest("Maria", "G001", "maria@email.com")
        self._room = SingleRoom("101")

    def test_add_and_get_room(self):
        self._hotel.add_room(self._room)
        self.assertIn(self._room, self._hotel.rooms)

    def test_add_and_get_guest(self):
        self._hotel.add_guest(self._guest)
        self.assertIn(self._guest, self._hotel.guests)

    def test_add_booking(self):
        self._hotel.add_room(self._room)
        self._hotel.add_guest(self._guest)
        booking = Booking(self._guest, self._room, "01/06/2025", 2)
        self._hotel.add_booking(booking)
        self.assertIn(booking, self._hotel.bookings)

    def test_remove_room_also_cancels_bookings(self):
        self._hotel.add_room(self._room)
        self._hotel.add_guest(self._guest)
        booking = Booking(self._guest, self._room, "01/06/2025", 2)
        self._hotel.add_booking(booking)
        self._hotel.remove_room(self._room)
        self.assertNotIn(booking, self._hotel.bookings)
        self.assertFalse(self._room.is_occupied)

    def test_remove_guest_also_cancels_bookings(self):
        self._hotel.add_room(self._room)
        self._hotel.add_guest(self._guest)
        booking = Booking(self._guest, self._room, "01/06/2025", 2)
        self._hotel.add_booking(booking)
        self._hotel.remove_guest(self._guest)
        self.assertNotIn(booking, self._hotel.bookings)

    def test_get_total_revenue(self):
        self._hotel.add_room(self._room)
        self._hotel.add_guest(self._guest)
        booking = Booking(self._guest, self._room, "01/06/2025", 4)
        self._hotel.add_booking(booking)
        self.assertEqual(self._hotel.get_total_revenue(), 400.0)

    def test_get_occupied_count(self):
        room2 = DoubleRoom("102")
        self._hotel.add_room(self._room)
        self._hotel.add_room(room2)
        self._hotel.add_guest(self._guest)
        Booking(self._guest, self._room, "01/06/2025", 1)
        self.assertEqual(self._hotel.get_occupied_count(), 1)


class TestFileManager(unittest.TestCase):
    TEST_DIR = "data/test_tmp"
    ROOMS_FILE = f"{TEST_DIR}/rooms.csv"
    GUESTS_FILE = f"{TEST_DIR}/guests.csv"
    BOOKINGS_FILE = f"{TEST_DIR}/bookings.csv"

    def setUp(self):
        os.makedirs(self.TEST_DIR, exist_ok=True)
        FileManager.ROOMS_FILE = self.ROOMS_FILE
        FileManager.GUESTS_FILE = self.GUESTS_FILE
        FileManager.BOOKINGS_FILE = self.BOOKINGS_FILE

        self._hotel = Hotel()
        self._guest = Guest("Leo", "G001", "leo@email.com")
        self._room = DoubleRoom("201")
        self._hotel.add_guest(self._guest)
        self._hotel.add_room(self._room)
        booking = Booking(self._guest, self._room, "15/07/2025", 3)
        self._hotel.add_booking(booking)

    def tearDown(self):
        for f in [self.ROOMS_FILE, self.GUESTS_FILE, self.BOOKINGS_FILE]:
            if os.path.exists(f):
                os.remove(f)
        os.rmdir(self.TEST_DIR)
        FileManager.ROOMS_FILE = "data/rooms.csv"
        FileManager.GUESTS_FILE = "data/guests.csv"
        FileManager.BOOKINGS_FILE = "data/bookings.csv"

    def test_save_creates_csv_files(self):
        FileManager.save(self._hotel)
        self.assertTrue(os.path.exists(self.ROOMS_FILE))
        self.assertTrue(os.path.exists(self.GUESTS_FILE))
        self.assertTrue(os.path.exists(self.BOOKINGS_FILE))

    def test_save_and_load_rooms(self):
        FileManager.save(self._hotel)
        new_hotel = Hotel()
        FileManager.load(new_hotel)
        self.assertEqual(len(new_hotel.rooms), 1)
        self.assertEqual(new_hotel.rooms[0].room_number, "201")
        self.assertEqual(new_hotel.rooms[0].get_room_type(), "Double")

    def test_save_and_load_guests(self):
        FileManager.save(self._hotel)
        new_hotel = Hotel()
        FileManager.load(new_hotel)
        self.assertEqual(len(new_hotel.guests), 1)
        self.assertEqual(new_hotel.guests[0].name, "Leo")
        self.assertEqual(new_hotel.guests[0].guest_id, "G001")

    def test_save_and_load_bookings(self):
        FileManager.save(self._hotel)
        new_hotel = Hotel()
        FileManager.load(new_hotel)
        self.assertEqual(len(new_hotel.bookings), 1)
        self.assertEqual(new_hotel.bookings[0].nights, 3)
        self.assertEqual(new_hotel.bookings[0].check_in_date, "15/07/2025")

    def test_load_missing_files_does_not_crash(self):
        new_hotel = Hotel()
        FileManager.load(new_hotel)
        self.assertEqual(len(new_hotel.rooms), 0)
        self.assertEqual(len(new_hotel.guests), 0)
        self.assertEqual(len(new_hotel.bookings), 0)


if __name__ == "__main__":
    unittest.main()