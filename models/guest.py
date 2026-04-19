class Guest:
    def __init__(self, name, guest_id, email):
        self.name = name
        self.guest_id = guest_id
        self.email = email

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("Name cannot be empty.")
        self._name = value.strip()

    @property
    def guest_id(self):
        return self._guest_id

    @guest_id.setter
    def guest_id(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Guest ID cannot be empty.")
        self._guest_id = value.strip()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not isinstance(value, str) or "@" not in value:
            raise ValueError("Email must be a valid email address.")
        self._email = value.strip()

    def __str__(self):
        return f"Guest {self._guest_id}: {self._name} ({self._email})"