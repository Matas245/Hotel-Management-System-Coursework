import customtkinter as ctk
from models.room_factory import RoomFactory
from gui.utils import ghost_btn, list_row, field_label, build_header, build_scrollable_list, build_toggle_btn


class RoomsFrame(ctk.CTkFrame):
    def __init__(self, parent, hotel):
        super().__init__(parent, fg_color="transparent")
        self._hotel = hotel
        self._editing_room = None
        self._bookings_frame = None
        self._billing_frame = None

        build_header(self, "Rooms", "Here you can manage Rooms")
        self._toggle_btn = build_toggle_btn(self, "Add Room", self._show_config)
        self._rooms_container = build_scrollable_list(self)
        self._build_config_view()
        self._render_rooms()

    def _build_config_view(self):
        self._config_view = ctk.CTkFrame(self, fg_color="transparent")
        card = ctk.CTkFrame(self._config_view, corner_radius=12)
        card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            card, text="Configure Room", font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 10), sticky="w")

        field_label(card, "Room Type", row=1, col=0)
        field_label(card, "Room Number", row=1, col=1, padx=10)

        self._type_var = ctk.StringVar(value="Single")
        ctk.CTkOptionMenu(
            card, values=RoomFactory.get_room_types(), variable=self._type_var
        ).grid(row=2, column=0, padx=(15, 10), pady=(0, 8))

        self._number_entry = ctk.CTkEntry(card, placeholder_text="e.g. 101")
        self._number_entry.grid(row=2, column=1, padx=10, pady=(0, 8))

        ctk.CTkButton(
            card, text="Apply", width=90, command=self._apply
        ).grid(row=2, column=2, padx=(15, 10), pady=(0, 8))

        self._error_label = ctk.CTkLabel(
            card, text="", text_color="red", font=ctk.CTkFont(size=12)
        )
        self._error_label.grid(row=3, column=0, columnspan=3, padx=15, pady=(0, 10), sticky="w")

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
        self._toggle_btn.configure(text="Cancel", command=self._show_main)

    def _show_main(self):
        self._editing_room = None
        self._config_view.pack_forget()
        self._rooms_container.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        self._toggle_btn.configure(text="Add Room", command=self._show_config)

    def _apply(self):
        number = self._number_entry.get().strip()
        room_type = self._type_var.get()

        if not number:
            self._error_label.configure(text="Room number cannot be empty.")
            return
        if not number.isdigit():
            self._error_label.configure(text="Room number must be numeric.")
            return
        if any(r.room_number == number and r != self._editing_room for r in self._hotel.rooms):
            self._error_label.configure(text=f"Room {number} already exists.")
            return

        if self._editing_room:
            self._hotel.remove_room(self._editing_room)
            if self._bookings_frame:
                self._bookings_frame.refresh()

        self._hotel.add_room(RoomFactory.create_room(room_type, number))
        self._render_rooms()
        self._show_main()

    def _remove_room(self, room):
        self._hotel.remove_room(room)
        if self._bookings_frame:
            self._bookings_frame.refresh()
        if self._billing_frame:
            self._billing_frame.refresh()
        self._render_rooms()

    def _render_rooms(self):
        for widget in self._rooms_container.winfo_children():
            widget.destroy()

        for i, room in enumerate(self._hotel.rooms):
            row = list_row(self._rooms_container, i)
            ctk.CTkLabel(
                row,
                text=f"Room {room.room_number} — {room.get_room_type()}",
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            ctk.CTkButton(
                row, text="Edit", width=80, command=lambda r=room: self._show_config(r)
            ).grid(row=0, column=1, padx=10, pady=10)
            ghost_btn(
                row, "Remove", command=lambda r=room: self._remove_room(r)
            ).grid(row=0, column=2, padx=10, pady=10)

    def refresh(self):
        self._render_rooms()