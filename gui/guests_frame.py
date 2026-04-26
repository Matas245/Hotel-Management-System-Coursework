import customtkinter as ctk
from models.guest import Guest
from gui.utils import ghost_btn, list_row, field_label, build_header, build_scrollable_list, build_toggle_btn


class GuestsFrame(ctk.CTkFrame):
    def __init__(self, parent, hotel):
        super().__init__(parent, fg_color="transparent")
        self._hotel = hotel
        self._editing_guest = None
        self._bookings_frame = None
        self._billing_frame = None

        build_header(self, "Guests", "Here you can manage Guests")
        self._toggle_btn = build_toggle_btn(self, "Add Guest", self._show_config)
        self._guests_container = build_scrollable_list(self)
        self._build_config_view()
        self._render_guests()

    def _build_config_view(self):
        self._config_view = ctk.CTkFrame(self, fg_color="transparent")
        card = ctk.CTkFrame(self._config_view, corner_radius=12)
        card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            card, text="Configure Guest", font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, columnspan=4, padx=15, pady=(15, 10), sticky="w")

        field_label(card, "Full Name", row=1, col=0)
        field_label(card, "Guest ID", row=1, col=1, padx=10)
        field_label(card, "Email", row=1, col=2, padx=10)

        self._name_entry = ctk.CTkEntry(card)
        self._name_entry.grid(row=2, column=0, padx=(15, 10), pady=(0, 8))

        self._id_entry = ctk.CTkEntry(card)
        self._id_entry.grid(row=2, column=1, padx=10, pady=(0, 8))

        self._email_entry = ctk.CTkEntry(card, width=175)
        self._email_entry.grid(row=2, column=2, padx=10, pady=(0, 8))

        ctk.CTkButton(
            card, text="Apply", width=90, command=self._apply
        ).grid(row=2, column=3, padx=(10, 15), pady=(0, 8))

        self._error_label = ctk.CTkLabel(
            card, text="", text_color="red", font=ctk.CTkFont(size=12)
        )
        self._error_label.grid(row=3, column=0, columnspan=4, padx=15, pady=(0, 10), sticky="w")

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
        self._toggle_btn.configure(text="Cancel", command=self._show_main)

    def _show_main(self):
        self._editing_guest = None
        self._config_view.pack_forget()
        self._guests_container.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        self._toggle_btn.configure(text="Add Guest", command=self._show_config)

    def _apply(self):
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
        if any(g.guest_id == guest_id and g != self._editing_guest for g in self._hotel.guests):
            self._error_label.configure(text=f"Guest ID {guest_id} already exists.")
            return

        try:
            new_guest = Guest(name, guest_id, email)
        except ValueError as exc:
            self._error_label.configure(text=str(exc))
            return

        if self._editing_guest:
            self._hotel.remove_guest(self._editing_guest)
            if self._bookings_frame:
                self._bookings_frame.refresh()

        self._hotel.add_guest(new_guest)
        self._render_guests()
        self._show_main()

    def _remove_guest(self, guest):
        self._hotel.remove_guest(guest)
        if self._bookings_frame:
            self._bookings_frame.refresh()
        if self._billing_frame:
            self._billing_frame.refresh()
        self._render_guests()

    def _render_guests(self):
        for widget in self._guests_container.winfo_children():
            widget.destroy()

        for i, guest in enumerate(self._hotel.guests):
            row = list_row(self._guests_container, i)
            ctk.CTkLabel(
                row,
                text=f"{guest.name}  ·  ID: {guest.guest_id}  ·  {guest.email}",
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            ctk.CTkButton(
                row, text="Edit", width=80, command=lambda g=guest: self._show_config(g)
            ).grid(row=0, column=1, padx=10, pady=10)
            ghost_btn(
                row, "Remove", command=lambda g=guest: self._remove_guest(g)
            ).grid(row=0, column=2, padx=10, pady=10)

    def refresh(self):
        self._render_guests()