from .room import SingleRoom, DoubleRoom, SuiteRoom

class RoomFactory:
    @staticmethod
    def create_room(room_type: str, room_number: str):
        if room_type == "Single":
            return SingleRoom(room_number)
        elif room_type == "Double":
            return DoubleRoom(room_number)
        elif room_type == "Suite":
            return SuiteRoom(room_number)
        else:
            raise ValueError(f"Unknown room type: {room_type}")
        
    @staticmethod
    def get_room_types():
        return ["Single", "Double", "Suite"]