import customtkinter as ctk
from models.room_factory import RoomFactory
from models.guest import Guest
from models.booking import Booking
from datetime import datetime, timedelta

def _ghost_btn(parent, text, command, width=80, height=28):
    return ctk.CTkButton(
        parent, text=text, width=width, height=height,
        fg_color="transparent", border_width=1,
        text_color=("gray10", "gray90"),
        hover_color=("gray70", "gray30"),
        command=command,
    )

def _list_row(container, i):
    row = ctk.CTkFrame(container, corner_radius=8)
    row.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
    row.grid_columnconfigure(0, weight=1)
    return row

def _field_lbl(parent, text, row, col, padx=(15, 10)):
    ctk.CTkLabel(parent, text=text).grid(row=row, column=col, padx=padx, pady=(5, 2), sticky="w")

class HotelApp(ctk.CTk):
    def __init__(self, hotel, file_manager):
        super().__init__()
        self._hotel = hotel
        self._file_manager = file_manager
        self.title("Hotel Management System")
        self.geometry("900x600")
        self.minsize(800, 500)
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        self._active_button = None
        self._setup_layout()
        self._show_frame("rooms")

    def _setup_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            sidebar, text="Hotel\nManagement\nSystem",
            font=ctk.CTkFont(size=20, weight="bold"), justify="left"
        ).grid(row=0, column=0, pady=(20, 30), padx=25)

        self._nav_buttons = {}
        for i, (label, key) in enumerate([("Rooms", "rooms"), ("Guests", "guests"), ("Bookings", "bookings"), ("Billing", "billing")], start=1):
            btn = ctk.CTkButton(
                sidebar, text=label, anchor="w",
                fg_color="transparent", text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"), height=50,
                font=ctk.CTkFont(size=14), command=lambda k=key: self._show_frame(k)
            )
            btn.grid(row=i, column=0, padx=10, pady=4, sticky="ew")
            self._nav_buttons[key] = btn

        save_load = ctk.CTkFrame(sidebar, fg_color="transparent")
        save_load.grid(row=6, column=0, padx=10, pady=(0, 20), sticky="ew")
        save_load.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(save_load, text="Save", width=80, height=32, command=self._save_data).grid(row=0, column=0, padx=(0, 4))
        _ghost_btn(save_load, "Load", self._load_data, width=80, height = 32).grid(row=0, column=1, padx=(4, 0), ipady=6)

        content = ctk.CTkFrame(self, corner_radius=10, fg_color=("gray95", "gray10"))
        content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        rooms_frame = RoomsFrame(content, self._hotel)
        guests_frame = GuestsFrame(content, self._hotel)
        bookings_frame = BookingsFrame(content, self._hotel)
        billing_frame = BillingFrame(content, self._hotel)

        rooms_frame._bookings_frame = bookings_frame
        rooms_frame._billing_frame = billing_frame
        guests_frame._bookings_frame = bookings_frame
        guests_frame._billing_frame = billing_frame

        self._frames = {
            "rooms": rooms_frame,
            "guests": guests_frame,
            "bookings": bookings_frame,
            "billing": billing_frame,
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

    def _save_data(self):
        self._file_manager.save(self._hotel)

    def _load_data(self):
        self._hotel._rooms.clear()
        self._hotel._guests.clear()
        self._hotel._bookings.clear()
        self._file_manager.load(self._hotel)
        for frame in self._frames.values():
            if hasattr(frame, "refresh"):
                frame.refresh()

class RoomsFrame(ctk.CTkFrame):
    def __init__(self, parent, hotel):
        super().__init__(parent, fg_color="transparent")
        self._hotel = hotel
        self._editing_room = None

        ctk.CTkLabel(self, text="Rooms", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(self, text="Here you can manage Rooms", text_color="gray").pack(anchor="w", padx=10)

        self._openclose_button = ctk.CTkButton(self, text="Add Room", width=120, command=self._show_config)
        self._openclose_button.pack(anchor="w", padx=10, pady=(20, 0))

        self._rooms_container = ctk.CTkScrollableFrame(self, label_text="")
        self._rooms_container.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        self._rooms_container.grid_columnconfigure(0, weight=1)

        self._config_view = ctk.CTkFrame(self, fg_color="transparent")
        card = ctk.CTkFrame(self._config_view, corner_radius=12)
        card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(card, text="Configure Room", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 10), sticky="w")
        _field_lbl(card, "Room Type", 1, 0)
        _field_lbl(card, "Room Number", 1, 1, padx=10)

        self._type_var = ctk.StringVar(value="Single")
        self._type_dropdown = ctk.CTkOptionMenu(card, values=RoomFactory.get_room_types(), variable=self._type_var)
        self._type_dropdown.grid(row=2, column=0, padx=(15, 10), pady=(0, 8))

        self._number_entry = ctk.CTkEntry(card, placeholder_text="e.g. 101")
        self._number_entry.grid(row=2, column=1, padx=10, pady=(0, 8))

        ctk.CTkButton(card, text="Apply", width=90, command=self._add_room).grid(row=2, column=2, padx=(15, 10), pady=(0, 8))

        self._error_label = ctk.CTkLabel(card, text="", text_color="red", font=ctk.CTkFont(size=12))
        self._error_label.grid(row=2, column=3, padx=(15, 10), pady=(0, 8))

        self._render_rooms()

    def _show_config(self, room=None):
        self._editing_room = room
        self._error_label.configure(text="")
        self._number_entry.delete(0, "end")
        if room:
            self._type_var.set(room.get_room_type())
            self._number_entry.insert(0, room.room_number)
        else:
            self._type_var.set("Single")
        self._rooms_container.pack_forget()
        self._config_view.pack(fill="both", expand=True)
        self._openclose_button.configure(text="Cancel", command=self._show_main)

    def _show_main(self):
        self._editing_room = None
        self._config_view.pack_forget()
        self._rooms_container.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        self._openclose_button.configure(text="Add Room", command=self._show_config)

    def _add_room(self):
        number = self._number_entry.get().strip()
        room_type = self._type_var.get()
        if not number:
            self._error_label.configure(text="Room number cannot be empty.")
            return
        if not number.isdigit():
            self._error_label.configure(text="Room number must be numeric.")
            return
        for room in self._hotel.rooms:
            if room.room_number == number and room != self._editing_room:
                self._error_label.configure(text=f"Room {number} already exists.")
                return
        if self._editing_room:
            self._hotel.remove_room(self._editing_room)
            if hasattr(self, '_bookings_frame'):
                self._bookings_frame.refresh()
        self._hotel.add_room(RoomFactory.create_room(room_type, number))
        self._render_rooms()
        self._show_main()

    def _remove_room(self, room):
        self._hotel.remove_room(room)
        for attr in ('_bookings_frame', '_billing_frame'):
            if hasattr(self, attr):
                getattr(self, attr).refresh()
        self._render_rooms()

    def _render_rooms(self):
        for w in self._rooms_container.winfo_children():
            w.destroy()
        for i, room in enumerate(self._hotel.rooms):
            row = _list_row(self._rooms_container, i)
            ctk.CTkLabel(row, text=f"Room {room.room_number} - {room.get_room_type()}", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            ctk.CTkButton(row, text="Edit", width=80, command=lambda r=room: self._show_config(r)).grid(row=0, column=1, padx=10, pady=10)
            _ghost_btn(row, "Remove", lambda r=room: self._remove_room(r)).grid(row=0, column=2, padx=10, pady=10)

    def refresh(self):
        self._render_rooms()


class GuestsFrame(ctk.CTkFrame):
    def __init__(self, parent, hotel):
        super().__init__(parent, fg_color="transparent")
        self._hotel = hotel
        self._editing_guest = None

        ctk.CTkLabel(self, text="Guests", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(self, text="Here you can manage Guests", text_color="gray").pack(anchor="w", padx=10)

        self._openclose_button = ctk.CTkButton(self, text="Add Guest", width=120, command=self._show_config)
        self._openclose_button.pack(anchor="w", padx=10, pady=(20, 0))

        self._guests_container = ctk.CTkScrollableFrame(self, label_text="")
        self._guests_container.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        self._guests_container.grid_columnconfigure(0, weight=1)

        self._config_view = ctk.CTkFrame(self, fg_color="transparent")
        card = ctk.CTkFrame(self._config_view, corner_radius=12)
        card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(card, text="Configure Guest", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, columnspan=4, padx=15, pady=(15, 10), sticky="w")
        _field_lbl(card, "Full Name", 1, 0)
        _field_lbl(card, "Guest ID", 1, 1, padx=10)
        _field_lbl(card, "Email", 1, 2, padx=10)

        self._name_entry = ctk.CTkEntry(card)
        self._name_entry.grid(row=2, column=0, padx=(15, 10), pady=(0, 8))
        self._id_entry = ctk.CTkEntry(card)
        self._id_entry.grid(row=2, column=1, padx=10, pady=(0, 8))
        self._email_entry = ctk.CTkEntry(card, width=175)
        self._email_entry.grid(row=2, column=2, padx=10, pady=(0, 8))

        ctk.CTkButton(card, text="Apply", width=90, command=self._add_guest).grid(row=2, column=3, padx=(10, 15), pady=(0, 8))

        self._error_label = ctk.CTkLabel(card, text="", text_color="red", font=ctk.CTkFont(size=12))
        self._error_label.grid(row=3, column=0, columnspan=4, padx=15, pady=(0, 10), sticky="w")

        self._render_guests()

    def _show_config(self, guest=None):
        self._editing_guest = guest
        self._error_label.configure(text="")
        for entry in (self._name_entry, self._id_entry, self._email_entry):
            entry.delete(0, "end")
        if guest:
            self._name_entry.insert(0, guest.name)
            self._id_entry.insert(0, guest.guest_id)
            self._email_entry.insert(0, guest.email)
        self._guests_container.pack_forget()
        self._config_view.pack(fill="both", expand=True)
        self._openclose_button.configure(text="Cancel", command=self._show_main)

    def _show_main(self):
        self._editing_guest = None
        self._config_view.pack_forget()
        self._guests_container.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        self._openclose_button.configure(text="Add Guest", command=self._show_config)

    def _add_guest(self):
        name = self._name_entry.get().strip()
        guest_id = self._id_entry.get().strip()
        email = self._email_entry.get().strip()
        if not name:
            self._error_label.configure(text="Name cannot be empty.")
            return
        if not guest_id:
            self._error_label.configure(text="Guest ID cannot be empty.")
            return
        if not email or "@" not in email:
            self._error_label.configure(text="Email must be a valid email address.")
            return
        for guest in self._hotel.guests:
            if guest.guest_id == guest_id and guest != self._editing_guest:
                self._error_label.configure(text=f"Guest ID {guest_id} already exists.")
                return
        try:
            new_guest = Guest(name, guest_id, email)
        except ValueError as e:
            self._error_label.configure(text=str(e))
            return
        if self._editing_guest:
            self._hotel.remove_guest(self._editing_guest)
            if hasattr(self, '_bookings_frame'):
                self._bookings_frame.refresh()
        self._hotel.add_guest(new_guest)
        self._render_guests()
        self._show_main()

    def _remove_guest(self, guest):
        self._hotel.remove_guest(guest)
        for attr in ('_bookings_frame', '_billing_frame'):
            if hasattr(self, attr):
                getattr(self, attr).refresh()
        self._render_guests()

    def _render_guests(self):
        for w in self._guests_container.winfo_children():
            w.destroy()
        for i, guest in enumerate(self._hotel.guests):
            row = _list_row(self._guests_container, i)
            ctk.CTkLabel(row, text=f"{guest.name}  ·  ID: {guest.guest_id}  ·  {guest.email}", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            ctk.CTkButton(row, text="Edit", width=80, command=lambda g=guest: self._show_config(g)).grid(row=0, column=1, padx=10, pady=10)
            _ghost_btn(row, "Remove", lambda g=guest: self._remove_guest(g)).grid(row=0, column=2, padx=10, pady=10)

    def refresh(self):
        self._render_guests()


class BookingsFrame(ctk.CTkFrame):
    def __init__(self, parent, hotel):
        super().__init__(parent, fg_color="transparent")
        self._hotel = hotel

        ctk.CTkLabel(self, text="Bookings", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(self, text="Manage and search reservations", text_color="gray").pack(anchor="w", padx=10)

        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=10, pady=(20, 0))
        self._openclose_button = ctk.CTkButton(controls, text="Add Booking", width=130, command=self._show_config)
        self._openclose_button.pack(side="left")
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)
        ctk.CTkEntry(controls, placeholder_text="Search by guest name or room...", width=250, textvariable=self._search_var).pack(side="right")

        self._bookings_container = ctk.CTkScrollableFrame(self, label_text="")
        self._bookings_container.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        self._bookings_container.grid_columnconfigure(0, weight=1)

        self._config_view = ctk.CTkFrame(self, fg_color="transparent")
        card = ctk.CTkFrame(self._config_view, corner_radius=12)
        card.pack(fill="x", padx=10, pady=10)
        card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(card, text="New Booking", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 10), sticky="w")
        _field_lbl(card, "Guest", 1, 0)
        _field_lbl(card, "Room", 1, 1, padx=10)

        self._guest_var = ctk.StringVar(value="")
        self._guest_dropdown = ctk.CTkOptionMenu(card, variable=self._guest_var, values=[""], width=200)
        self._guest_dropdown.grid(row=2, column=0, padx=(15, 10), pady=(0, 12), sticky="w")

        self._room_var = ctk.StringVar(value="")
        self._room_dropdown = ctk.CTkOptionMenu(card, variable=self._room_var, values=[""], width=200, command=self._update_price_preview)
        self._room_dropdown.grid(row=2, column=1, padx=10, pady=(0, 12), sticky="w")

        _field_lbl(card, "Check-in Date (DD/MM/YYYY)", 3, 0)
        _field_lbl(card, "Nights", 3, 1, padx=10)

        self._checkin_entry = ctk.CTkEntry(card, placeholder_text="e.g. 01/06/2026", width=200)
        self._checkin_entry.grid(row=4, column=0, padx=(15, 10), pady=(0, 8), sticky="w")

        nights_apply = ctk.CTkFrame(card, fg_color="transparent")
        nights_apply.grid(row=4, column=1, padx=10, pady=(0, 8), sticky="w")
        self._nights_entry = ctk.CTkEntry(nights_apply, placeholder_text="1", width=80)
        self._nights_entry.pack(side="left", padx=(0, 8))
        self._nights_entry.bind("<KeyRelease>", lambda e: self._update_price_preview())
        ctk.CTkButton(nights_apply, text="Apply", width=90, command=self._add_booking).pack(side="left")

        self._price_label = ctk.CTkLabel(card, text="", text_color="gray", font=ctk.CTkFont(size=12))
        self._price_label.grid(row=5, column=0, columnspan=3, padx=15, pady=(0, 4), sticky="w")
        self._error_label = ctk.CTkLabel(card, text="", text_color="red", font=ctk.CTkFont(size=12))
        self._error_label.grid(row=6, column=0, columnspan=3, padx=15, pady=(0, 12), sticky="w")

        self._render_bookings()

    def on_show(self):
        self._refresh_dropdowns()

    def _refresh_dropdowns(self):
        guests, rooms = self._hotel.guests, self._hotel.rooms
        if guests:
            self._guest_dropdown.configure(values=[f"{g.name} (ID: {g.guest_id})" for g in guests])
        if rooms:
            self._room_dropdown.configure(values=[f"Room {r.room_number} - {r.get_room_type()}" for r in rooms])

    def _show_config(self):
        guests, rooms = self._hotel.guests, self._hotel.rooms
        self._error_label.configure(text="")
        self._bookings_container.pack_forget()
        self._config_view.pack(fill="both", expand=True)
        self._openclose_button.configure(text="Cancel", command=self._show_main)
        if not guests or not rooms:
            self._error_label.configure(text="Please add at least one Guest and Room first.")
            self._guest_dropdown.configure(values=[""])
            self._room_dropdown.configure(values=[""])
            self._guest_var.set("")
            self._room_var.set("")
            return
        self._guest_dropdown.configure(values=[f"{g.name} (ID: {g.guest_id})" for g in guests])
        self._room_dropdown.configure(values=[f"Room {r.room_number} - {r.get_room_type()}" for r in rooms])
        self._checkin_entry.delete(0, "end")
        self._nights_entry.delete(0, "end")
        self._price_label.configure(text="")

    def _show_main(self):
        self._config_view.pack_forget()
        self._bookings_container.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        self._openclose_button.configure(text="Add Booking", command=self._show_config)

    def _update_price_preview(self, *_):
        try:
            if not self._room_var.get():
                return
            nights = int(self._nights_entry.get().strip())
            rooms = self._hotel.rooms
            idx = [f"Room {r.room_number} - {r.get_room_type()}" for r in rooms].index(self._room_var.get())
            self._price_label.configure(text=f"Estimated total: €{rooms[idx].calculate_price(nights):.2f}")
        except (ValueError, IndexError):
            self._price_label.configure(text="")

    def _add_booking(self):
        nights_str = self._nights_entry.get().strip()
        guest_sel = self._guest_var.get()
        room_sel = self._room_var.get()
        check_in_str = self._checkin_entry.get().strip()

        if not guest_sel or not room_sel:
            self._error_label.configure(text="Please select a valid Guest and Room.")
            return
        if not check_in_str:
            self._error_label.configure(text="Please enter a check-in date.")
            return
        try:
            req_check_in = datetime.strptime(check_in_str, "%d/%m/%Y")
        except ValueError:
            self._error_label.configure(text="Date must be in DD/MM/YYYY format.")
            return
        if not nights_str.isdigit() or int(nights_str) < 1:
            self._error_label.configure(text="Nights must be a positive number.")
            return

        nights = int(nights_str)
        req_check_out = req_check_in + timedelta(days=nights)
        guests, rooms = self._hotel.guests, self._hotel.rooms

        try:
            guest = guests[[f"{g.name} (ID: {g.guest_id})" for g in guests].index(guest_sel)]
            room = rooms[[f"Room {r.room_number} - {r.get_room_type()}" for r in rooms].index(room_sel)]
        except (ValueError, IndexError):
            self._error_label.configure(text="Error identifying Guest or Room.")
            return

        latest_checkout = None
        for b in self._hotel.bookings:
            if b.room == room:
                b_in = datetime.strptime(b.check_in_date, "%d/%m/%Y")
                b_out = b_in + timedelta(days=b.nights)
                if latest_checkout is None or b_out > latest_checkout:
                    latest_checkout = b_out
                if req_check_in < b_out and req_check_out > b_in:
                    next_free = latest_checkout.strftime("%d/%m/%Y") if latest_checkout else "Unknown"
                    self._error_label.configure(text=f"Room booked. Next available: {next_free}")
                    return

        self._hotel.add_booking(Booking(guest, room, check_in_str, nights))
        self._render_bookings()
        self._show_main()

    def _on_search_change(self, *args):
        self._render_bookings(search_query=self._search_var.get().lower())

    def _cancel_booking(self, booking):
        self._hotel.remove_booking(booking)
        self._render_bookings()

    def _render_bookings(self, search_query=""):
        for w in self._bookings_container.winfo_children():
            w.destroy()
        filtered = [
            b for b in self._hotel.bookings
            if search_query in b.guest.name.lower() or search_query in str(b.room.room_number)
        ]
        for i, booking in enumerate(filtered):
            row = _list_row(self._bookings_container, i)
            row.grid_columnconfigure(1, weight=0)
            info = (f"Booking {booking.booking_id}  ·  {booking.guest.name}  ·  "
                    f"Room {booking.room.room_number} ({booking.room.get_room_type()})  ·  "
                    f"{booking.nights} nights from {booking.check_in_date}")
            label = ctk.CTkLabel(row, text=info, font=ctk.CTkFont(size=13), justify="left")
            label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
            _ghost_btn(row, "Cancel", lambda b=booking: self._cancel_booking(b)).grid(row=0, column=1, padx=10, pady=10, sticky="e")
            row.bind("<Configure>", lambda e, lbl=label: lbl.configure(wraplength=max(150, e.width - 130)))

    def refresh(self):
        self._render_bookings()


class BillingFrame(ctk.CTkFrame):
    def __init__(self, parent, hotel):
        super().__init__(parent, fg_color="transparent")
        self._hotel = hotel

        ctk.CTkLabel(self, text="Billing", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(self, text="Revenue overview and booking costs", text_color="gray").pack(anchor="w", padx=10)

        self._stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._stats_frame.pack(fill="x", padx=10, pady=(20, 0))
        self._stat_bookings = self._make_stat_card("Total Bookings", "0")
        self._stat_revenue = self._make_stat_card("Total Revenue", "€0.00")
        self._stat_occupied = self._make_stat_card("Occupied Rooms", "0")

        self._billing_container = ctk.CTkScrollableFrame(self, label_text="")
        self._billing_container.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        self._billing_container.grid_columnconfigure(0, weight=1)

        self._render_billing()

    def _make_stat_card(self, label, value):
        card = ctk.CTkFrame(self._stats_frame, corner_radius=10, width=160, height=80)
        card.pack(side="left", padx=(0, 12), pady=5)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=label, text_color="gray", font=ctk.CTkFont(size=12)).pack(pady=(12, 2))
        val_lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"))
        val_lbl.pack()
        return val_lbl

    def _render_billing(self):
        for w in self._billing_container.winfo_children():
            w.destroy()
        bookings = self._hotel.bookings
        self._stat_bookings.configure(text=str(len(bookings)))
        self._stat_revenue.configure(text=f"€{self._hotel.get_total_revenue():.2f}")
        self._stat_occupied.configure(text=str(self._hotel.get_occupied_count()))
        for i, booking in enumerate(bookings):
            row = _list_row(self._billing_container, i)
            left = (f"Booking {booking.booking_id}  ·  {booking.guest.name}  ·  "
                    f"Room {booking.room.room_number} ({booking.room.get_room_type()})  ·  "
                    f"{booking.nights} nights from {booking.check_in_date}")
            ctk.CTkLabel(row, text=left, font=ctk.CTkFont(size=13), justify="left").grid(row=0, column=0, padx=10, pady=10, sticky="w")
            ctk.CTkLabel(row, text=f"€{booking.calculate_total():.2f}", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=1, padx=15, pady=10, sticky="e")

    def on_show(self):
        self._render_billing()

    def refresh(self):
        self._render_billing()