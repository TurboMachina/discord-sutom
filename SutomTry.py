FILE_RESULTS_PATH = "results.json"
class SutomTry:
    def __init__(self, user_id = None, sutom_number = None, number_of_try = None, word_len = None, date_of_try = None, time_to_guess = '00:00:00'):
        self.user_id = user_id
        self.sutom_number = sutom_number
        self.number_of_try = number_of_try
        self.word_len = word_len
        self.time_to_guess = time_to_guess
        self.date_of_try = date_of_try
    def __str__(self) -> str:
        return f"ID: {self.user_id}, #{self.sutom_number}, {self.number_of_try}/{self.word_len} in {self.time_to_guess} on {self.date_of_try}"