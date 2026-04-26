import customtkinter as ctk
from gui.utils import list_row, build_header, build_scrollable_list


class BillingFrame(ctk.CTkFrame):
    def __init__(self, parent, hotel):
        super().__init__(parent, fg_color="transparent")
        self._hotel = hotel

        build_header(self, "Billing", "Revenue overview and booking costs")
        self._build_stat_cards()
        self._billing_container = build_scrollable_list(self)
        self._render_billing()

    def _build_stat_cards(self):
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=10, pady=(20, 0))

        self._stat_bookings = self._make_stat_card(stats_row, "Total Bookings", "0")
        self._stat_revenue = self._make_stat_card(stats_row, "Total Revenue", "€0.00")
        self._stat_occupied = self._make_stat_card(stats_row, "Occupied Rooms", "0")

    def _make_stat_card(self, parent, label, initial_value):
        card = ctk.CTkFrame(parent, corner_radius=10, width=160, height=80)
        card.pack(side="left", padx=(0, 12), pady=5)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=label, text_color="gray", font=ctk.CTkFont(size=12)).pack(pady=(12, 2))
        value_label = ctk.CTkLabel(card, text=initial_value, font=ctk.CTkFont(size=22, weight="bold"))
        value_label.pack()
        return value_label

    def _render_billing(self):
        for widget in self._billing_container.winfo_children():
            widget.destroy()

        bookings = self._hotel.bookings
        self._stat_bookings.configure(text=str(len(bookings)))
        self._stat_revenue.configure(text=f"€{self._hotel.get_total_revenue():.2f}")
        self._stat_occupied.configure(text=str(self._hotel.get_occupied_count()))

        for i, booking in enumerate(bookings):
            row = list_row(self._billing_container, i)
            info = (
                f"Booking {booking.booking_id}  ·  {booking.guest.name}  ·  "
                f"Room {booking.room.room_number} ({booking.room.get_room_type()})  ·  "
                f"{booking.nights} nights from {booking.check_in_date}"
            )
            ctk.CTkLabel(row, text=info, font=ctk.CTkFont(size=13), justify="left").grid(
                row=0, column=0, padx=10, pady=10, sticky="w"
            )
            ctk.CTkLabel(
                row, text=f"€{booking.calculate_total():.2f}", font=ctk.CTkFont(size=15, weight="bold")
            ).grid(row=0, column=1, padx=15, pady=10, sticky="e")

    def on_show(self):
        self._render_billing()

    def refresh(self):
        self._render_billing()