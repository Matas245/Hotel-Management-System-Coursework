import customtkinter as ctk
from datetime import datetime, timedelta
from models.booking import Booking
from gui.utils import ghost_btn, list_row, field_label, build_header, build_scrollable_list, build_toggle_btn


class BookingsFrame(ctk.CTkFrame):
    def __init__(self, parent, hotel):
        super().__init__(parent, fg_color="transparent")
        self._hotel = hotel

        build_header(self, "Bookings", "Manage reservations")
        self._toggle_btn = build_toggle_btn(self, "Add Booking", self._show_config)
        self._bookings_container = build_scrollable_list(self)
        self._build_config_view()
        self._render_bookings()

    def _build_config_view(self):
        self._config_view = ctk.CTkFrame(self, fg_color="transparent")
        card = ctk.CTkFrame(self._config_view, corner_radius=12)
        card.pack(fill="x", padx=10, pady=10)
        card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            card, text="New Booking", font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 10), sticky="w")

        field_label(card, "Guest", row=1, col=0)
        field_label(card, "Room", row=1, col=1, padx=10)

        self._guest_var = ctk.StringVar(value="")
        self._guest_dropdown = ctk.CTkOptionMenu(
            card, variable=self._guest_var, values=[""], width=200
        )
        self._guest_dropdown.grid(row=2, column=0, padx=(15, 10), pady=(0, 12), sticky="w")

        self._room_var = ctk.StringVar(value="")
        self._room_dropdown = ctk.CTkOptionMenu(
            card,
            variable=self._room_var,
            values=[""],
            width=200,
            command=self._update_price_preview,
        )
        self._room_dropdown.grid(row=2, column=1, padx=10, pady=(0, 12), sticky="w")

        field_label(card, "Check-in Date (DD/MM/YYYY)", row=3, col=0)
        field_label(card, "Nights", row=3, col=1, padx=10)

        self._checkin_entry = ctk.CTkEntry(
            card, placeholder_text="e.g. 01/06/2026", width=200
        )
        self._checkin_entry.grid(row=4, column=0, padx=(15, 10), pady=(0, 8), sticky="w")

        nights_row = ctk.CTkFrame(card, fg_color="transparent")
        nights_row.grid(row=4, column=1, padx=10, pady=(0, 8), sticky="w")

        self._nights_entry = ctk.CTkEntry(nights_row, placeholder_text="1", width=80)
        self._nights_entry.pack(side="left", padx=(0, 8))
        self._nights_entry.bind("<KeyRelease>", lambda _e: self._update_price_preview())

        ctk.CTkButton(
            nights_row, text="Apply", width=90, command=self._apply
        ).pack(side="left")

        self._price_label = ctk.CTkLabel(
            card, text="", text_color="gray", font=ctk.CTkFont(size=12)
        )
        self._price_label.grid(row=5, column=0, columnspan=3, padx=15, pady=(0, 4), sticky="w")

        self._error_label = ctk.CTkLabel(
            card, text="", text_color="red", font=ctk.CTkFont(size=12)
        )
        self._error_label.grid(row=6, column=0, columnspan=3, padx=15, pady=(0, 12), sticky="w")

    def on_show(self):
        self._refresh_dropdowns()

    def _show_config(self):
        self._error_label.configure(text="")
        guests = self._hotel.guests
        rooms = self._hotel.rooms

        if not guests or not rooms:
            self._guest_dropdown.configure(values=[""])
            self._room_dropdown.configure(values=[""])
            self._guest_var.set("")
            self._room_var.set("")
            self._bookings_container.pack_forget()
            self._config_view.pack(fill="both", expand=True)
            self._toggle_btn.configure(text="Cancel", command=self._show_main)
            self._error_label.configure(text="Please add at least one Guest and Room first.")
            return

        self._guest_dropdown.configure(
            values=[f"{g.name} (ID: {g.guest_id})" for g in guests]
        )
        self._room_dropdown.configure(
            values=[f"Room {r.room_number} — {r.get_room_type()}" for r in rooms]
        )
        self._checkin_entry.delete(0, "end")
        self._nights_entry.delete(0, "end")
        self._price_label.configure(text="")

        self._bookings_container.pack_forget()
        self._config_view.pack(fill="both", expand=True)
        self._toggle_btn.configure(text="Cancel", command=self._show_main)

    def _show_main(self):
        self._config_view.pack_forget()
        self._bookings_container.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        self._toggle_btn.configure(text="Add Booking", command=self._show_config)

    def _refresh_dropdowns(self):
        guests = self._hotel.guests
        rooms = self._hotel.rooms
        if guests:
            self._guest_dropdown.configure(
                values=[f"{g.name} (ID: {g.guest_id})" for g in guests]
            )
        if rooms:
            self._room_dropdown.configure(
                values=[f"Room {r.room_number} — {r.get_room_type()}" for r in rooms]
            )

    def _update_price_preview(self, *_args):
        try:
            nights = int(self._nights_entry.get().strip())
            room_labels = [f"Room {r.room_number} — {r.get_room_type()}" for r in self._hotel.rooms]
            room = self._hotel.rooms[room_labels.index(self._room_var.get())]
            self._price_label.configure(text=f"Estimated total: €{room.calculate_price(nights):.2f}")
        except (ValueError, IndexError):
            self._price_label.configure(text="")

    def _apply(self):
        guest_sel = self._guest_var.get()
        room_sel = self._room_var.get()
        check_in_str = self._checkin_entry.get().strip()
        nights_str = self._nights_entry.get().strip()

        if not guest_sel or not room_sel:
            self._error_label.configure(text="Please select a valid Guest and Room.")
            return
        if not check_in_str:
            self._error_label.configure(text="Please enter a check-in date.")
            return

        try:
            check_in = datetime.strptime(check_in_str, "%d/%m/%Y")
        except ValueError:
            self._error_label.configure(text="Date must be in DD/MM/YYYY format.")
            return

        if not nights_str.isdigit() or int(nights_str) < 1:
            self._error_label.configure(text="Nights must be a positive number.")
            return

        nights = int(nights_str)
        check_out = check_in + timedelta(days=nights)

        guests = self._hotel.guests
        rooms = self._hotel.rooms
        guest_labels = [f"{g.name} (ID: {g.guest_id})" for g in guests]
        room_labels = [f"Room {r.room_number} — {r.get_room_type()}" for r in rooms]

        try:
            guest = guests[guest_labels.index(guest_sel)]
            room = rooms[room_labels.index(room_sel)]
        except (ValueError, IndexError):
            self._error_label.configure(text="Error identifying Guest or Room.")
            return

        latest_checkout = None
        for booking in self._hotel.bookings:
            if booking.room != room:
                continue
            b_in = datetime.strptime(booking.check_in_date, "%d/%m/%Y")
            b_out = b_in + timedelta(days=booking.nights)
            if latest_checkout is None or b_out > latest_checkout:
                latest_checkout = b_out
            if check_in < b_out and check_out > b_in:
                next_free = latest_checkout.strftime("%d/%m/%Y") if latest_checkout else "Unknown"
                self._error_label.configure(text=f"Room already booked. Next available: {next_free}")
                return

        self._hotel.add_booking(Booking(guest, room, check_in_str, nights))
        self._render_bookings()
        self._show_main()

    def _cancel_booking(self, booking):
        self._hotel.remove_booking(booking)
        self._render_bookings()

    def _render_bookings(self):
        for widget in self._bookings_container.winfo_children():
            widget.destroy()

        for i, booking in enumerate(self._hotel.bookings):
            row = list_row(self._bookings_container, i)
            info = (
                f"Booking {booking.booking_id}  ·  {booking.guest.name}  ·  "
                f"Room {booking.room.room_number} ({booking.room.get_room_type()})  ·  "
                f"{booking.nights} nights from {booking.check_in_date}"
            )
            label = ctk.CTkLabel(row, text=info, font=ctk.CTkFont(size=13), justify="left")
            label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
            ghost_btn(
                row, "Cancel", command=lambda b=booking: self._cancel_booking(b)
            ).grid(row=0, column=1, padx=10, pady=10, sticky="e")
            row.bind("<Configure>", lambda e, lbl=label: lbl.configure(wraplength=max(150, e.width - 130)))

    def refresh(self):
        self._render_bookings()