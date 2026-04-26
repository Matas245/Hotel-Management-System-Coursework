import customtkinter as ctk
from gui.rooms_frame import RoomsFrame
from gui.guests_frame import GuestsFrame
from gui.bookings_frame import BookingsFrame
from gui.billing_frame import BillingFrame
from gui.utils import ghost_btn

_NAV_ITEMS = [
    ("Rooms", "rooms"),
    ("Guests", "guests"),
    ("Bookings", "bookings"),
    ("Billing", "billing"),
]


class HotelApp(ctk.CTk):
    def __init__(self, hotel, file_manager):
        super().__init__()
        self._hotel = hotel
        self._file_manager = file_manager
        self._active_button = None

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.title("Hotel Management System")
        self.geometry("900x600")
        self.minsize(800, 500)

        self._build_layout()
        self._show_frame("rooms")

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            sidebar,
            text="Hotel\nManagement\nSystem",
            font=ctk.CTkFont(size=20, weight="bold"),
            justify="left",
        ).grid(row=0, column=0, pady=(20, 30), padx=25)

        self._nav_buttons = {}
        for i, (label, key) in enumerate(_NAV_ITEMS, start=1):
            btn = ctk.CTkButton(
                sidebar,
                text=label,
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                height=50,
                font=ctk.CTkFont(size=14),
                command=lambda k=key: self._show_frame(k),
            )
            btn.grid(row=i, column=0, padx=10, pady=4, sticky="ew")
            self._nav_buttons[key] = btn

        save_load = ctk.CTkFrame(sidebar, fg_color="transparent")
        save_load.grid(row=6, column=0, padx=10, pady=(0, 20), sticky="ew")
        save_load.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            save_load, text="Save", width=80, height=32, command=self._save
        ).grid(row=0, column=0, padx=(0, 4))
        ghost_btn(save_load, "Load", self._load, width=80, height=32).grid(
            row=0, column=1, padx=(4, 0)
        )

    def _build_content_area(self):
        content = ctk.CTkFrame(self, corner_radius=10, fg_color=("gray95", "gray10"))
        content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        rooms = RoomsFrame(content, self._hotel)
        guests = GuestsFrame(content, self._hotel)
        bookings = BookingsFrame(content, self._hotel)
        billing = BillingFrame(content, self._hotel)

        rooms._bookings_frame = bookings
        rooms._billing_frame = billing
        guests._bookings_frame = bookings
        guests._billing_frame = billing

        self._frames = {
            "rooms": rooms,
            "guests": guests,
            "bookings": bookings,
            "billing": billing,
        }
        for frame in self._frames.values():
            frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def _show_frame(self, key):
        self._frames[key].tkraise()

        if self._active_button:
            self._active_button.configure(fg_color="transparent")
        self._active_button = self._nav_buttons[key]
        self._active_button.configure(fg_color=("gray70", "gray30"))

        if hasattr(self._frames[key], "on_show"):
            self._frames[key].on_show()

    def _save(self):
        self._file_manager.save(self._hotel)

    def _load(self):
        self._hotel._rooms.clear()
        self._hotel._guests.clear()
        self._hotel._bookings.clear()
        self._file_manager.load(self._hotel)
        for frame in self._frames.values():
            if hasattr(frame, "refresh"):
                frame.refresh()