FILE_RESULTS_PATH = "results.json"
from datetime import timedelta

# Represent one Sutom game. This is what the Discord Parser read in the user's message
class SutomRecord:
    def __init__(
        self,
        user_id=None,
        sutom_number=None,
        number_of_try=None,
        date_of_try=None,
        time_to_guess=0,
    ):
        self.user_id = user_id
        self.sutom_number = sutom_number
        self.number_of_try = number_of_try
        self.time_to_guess = time_to_guess
        self.date_of_try = date_of_try

    def __str__(self) -> str:
        return f"ID: {self.user_id}, #{self.sutom_number}, {self.number_of_try}/6 in {self.time_to_guess} on {self.date_of_try}"
