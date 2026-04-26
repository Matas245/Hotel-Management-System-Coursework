import customtkinter as ctk


def ghost_btn(parent, text, command, width=80, height=28):
    return ctk.CTkButton(
        parent,
        text=text,
        width=width,
        height=height,
        fg_color="transparent",
        border_width=1,
        text_color=("gray10", "gray90"),
        hover_color=("gray70", "gray30"),
        command=command,
    )


def list_row(container, i):
    row = ctk.CTkFrame(container, corner_radius=8)
    row.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
    row.grid_columnconfigure(0, weight=1)
    return row


def field_label(parent, text, row, col, padx=(15, 10)):
    ctk.CTkLabel(parent, text=text).grid(
        row=row, column=col, padx=padx, pady=(5, 2), sticky="w"
    )


def build_header(parent, title, subtitle):
    ctk.CTkLabel(
        parent, text=title, font=ctk.CTkFont(size=28, weight="bold")
    ).pack(anchor="w", padx=10, pady=(10, 5))
    ctk.CTkLabel(
        parent, text=subtitle, text_color="gray"
    ).pack(anchor="w", padx=10)


def build_scrollable_list(parent):
    container = ctk.CTkScrollableFrame(parent, label_text="")
    container.pack(fill="both", expand=True, padx=10, pady=(15, 10))
    container.grid_columnconfigure(0, weight=1)
    return container


def build_toggle_btn(parent, text, command):
    btn = ctk.CTkButton(parent, text=text, width=130, command=command)
    btn.pack(anchor="w", padx=10, pady=(20, 0))
    return btn