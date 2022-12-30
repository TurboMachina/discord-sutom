from datetime import timedelta

# Represent one Sutom User, with every game he played and statistics
# This is what is stored and read in the results.json file
class SutomUser:
    def __init__(
        self,
        user_id=None,
        avg_time_to_guess: int = 0,
        avg_number_of_try: int = 0,
    ):
        self.user_id = user_id
        # game logic : {sutom_number, number_of_try, time_to_guess}
        self.games = []
        self.avg_time_to_guess = avg_time_to_guess
        self.avg_number_of_try = avg_number_of_try

    def add_game(self, sutom_number: int, number_of_try: int, time_to_win: int = -1):

        self.games.append((sutom_number, number_of_try, time_to_win))

        # Compute average time to guess
        total_time = 0
        no_time_game = 0
        for game in self.games:
            if game[2] == -1:
                no_time_game += 1
            else:
                total_time += game[2]
        self.avg_time_to_guess = total_time / (len(self.games) - no_time_game)

        # Compute average number of try
        total_try = 0
        for game in self.games:
            total_try += game[1]
        self.avg_number_of_try = total_try / len(self.games)

    def get_str_avg_time_to_guess(self):
        return str(timedelta(seconds=self.avg_time_to_guess)).partition(".")[0]

    def get_str_avg_number_of_try(self):
        return f"{self.avg_number_of_try:.2f}"

    def __str__(self) -> str:
        return f"ID: {self.user_id}, {self.games}, {(str(timedelta(seconds=self.avg_time_to_guess))).partition('.')[0]}, {self.avg_number_of_try}"
