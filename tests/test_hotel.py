import unittest
import os
from models.room import SingleRoom, DoubleRoom, SuiteRoom
from models.guest import Guest
from models.booking import Booking
from models.room_factory import RoomFactory
from services.hotel import Hotel
from storage.file_manager import FileManager


class TestRoomTypes(unittest.TestCase):
    def test_single_room_price(self):
        self.assertEqual(SingleRoom("101").calculate_price(3), 300.0)

    def test_double_room_price(self):
        self.assertEqual(DoubleRoom("102").calculate_price(2), 300.0)

    def test_suite_room_price_includes_service_fee(self):
        self.assertEqual(SuiteRoom("103").calculate_price(2), 550.0)

    def test_room_get_type(self):
        self.assertEqual(SingleRoom("101").get_room_type(), "Single")
        self.assertEqual(DoubleRoom("102").get_room_type(), "Double")
        self.assertEqual(SuiteRoom("103").get_room_type(), "Suite")


class TestRoomFactory(unittest.TestCase):
    def test_creates_correct_room_types(self):
        self.assertIsInstance(RoomFactory.create_room("Single", "101"), SingleRoom)
        self.assertIsInstance(RoomFactory.create_room("Double", "102"), DoubleRoom)
        self.assertIsInstance(RoomFactory.create_room("Suite", "103"), SuiteRoom)

    def test_invalid_type_raises_error(self):
        with self.assertRaises(ValueError):
            RoomFactory.create_room("Penthouse", "104")


class TestGuest(unittest.TestCase):
    def test_valid_guest_creation(self):
        guest = Guest("John Smith", "G001", "john@email.com")
        self.assertEqual(guest.name, "John Smith")
        self.assertEqual(guest.guest_id, "G001")

    def test_empty_name_raises_error(self):
        with self.assertRaises(ValueError):
            Guest("", "G001", "john@email.com")

    def test_invalid_email_raises_error(self):
        with self.assertRaises(ValueError):
            Guest("John", "G001", "notanemail")


class TestBooking(unittest.TestCase):
    def setUp(self):
        self._guest = Guest("Anna", "G001", "anna@email.com")
        self._room = SingleRoom("101")

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


class TestHotel(unittest.TestCase):
    def setUp(self):
        self._hotel = Hotel("Test Hotel")
        self._guest = Guest("Maria", "G001", "maria@email.com")
        self._room = SingleRoom("101")
        self._hotel.add_room(self._room)
        self._hotel.add_guest(self._guest)

    def test_remove_room_also_cancels_bookings(self):
        booking = Booking(self._guest, self._room, "01/06/2025", 2)
        self._hotel.add_booking(booking)
        self._hotel.remove_room(self._room)
        self.assertNotIn(booking, self._hotel.bookings)
        self.assertFalse(self._room.is_occupied)

    def test_remove_guest_also_cancels_bookings(self):
        booking = Booking(self._guest, self._room, "01/06/2025", 2)
        self._hotel.add_booking(booking)
        self._hotel.remove_guest(self._guest)
        self.assertNotIn(booking, self._hotel.bookings)

    def test_get_total_revenue(self):
        self._hotel.add_booking(Booking(self._guest, self._room, "01/06/2025", 4))
        self.assertEqual(self._hotel.get_total_revenue(), 400.0)

    def test_get_occupied_count(self):
        room2 = DoubleRoom("102")
        self._hotel.add_room(room2)
        Booking(self._guest, self._room, "01/06/2025", 1)
        self.assertEqual(self._hotel.get_occupied_count(), 1)


class TestFileManager(unittest.TestCase):
    TEST_DIR = "data/test_tmp"

    def setUp(self):
        os.makedirs(self.TEST_DIR, exist_ok=True)
        FileManager.ROOMS_FILE = f"{self.TEST_DIR}/rooms.csv"
        FileManager.GUESTS_FILE = f"{self.TEST_DIR}/guests.csv"
        FileManager.BOOKINGS_FILE = f"{self.TEST_DIR}/bookings.csv"

        self._hotel = Hotel()
        guest = Guest("Leo", "G001", "leo@email.com")
        room = DoubleRoom("201")
        self._hotel.add_guest(guest)
        self._hotel.add_room(room)
        self._hotel.add_booking(Booking(guest, room, "15/07/2025", 3))

    def tearDown(self):
        for f in [FileManager.ROOMS_FILE, FileManager.GUESTS_FILE, FileManager.BOOKINGS_FILE]:
            if os.path.exists(f):
                os.remove(f)
        os.rmdir(self.TEST_DIR)
        FileManager.ROOMS_FILE = "data/rooms.csv"
        FileManager.GUESTS_FILE = "data/guests.csv"
        FileManager.BOOKINGS_FILE = "data/bookings.csv"

    def test_save_and_load_roundtrip(self):
        FileManager.save(self._hotel)
        new_hotel = Hotel()
        FileManager.load(new_hotel)
        self.assertEqual(new_hotel.rooms[0].room_number, "201")
        self.assertEqual(new_hotel.guests[0].name, "Leo")
        self.assertEqual(new_hotel.bookings[0].nights, 3)

    def test_load_missing_files_does_not_crash(self):
        new_hotel = Hotel()
        FileManager.load(new_hotel)
        self.assertEqual(len(new_hotel.rooms), 0)
        self.assertEqual(len(new_hotel.guests), 0)
        self.assertEqual(len(new_hotel.bookings), 0)


if __name__ == "__main__":
    unittest.main()