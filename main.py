from services.hotel import Hotel
from storage.file_manager import FileManager
from gui.app import HotelApp


def main():
    hotel = Hotel()
    file_manager = FileManager()
    app = HotelApp(hotel, file_manager)
    app.mainloop()


if __name__ == "__main__":
    main()