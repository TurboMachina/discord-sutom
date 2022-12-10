import discord

class SutomTry:
    def __init__(self, user_id, sutom_number, number_of_try, word_len, date_of_try, time_of_try, time_to_guess = '00:00:00'):
        self.user_id = user_id
        self.sutom_number = sutom_number
        self.number_of_try = number_of_try
        self.word_len = word_len
        self.time_to_guess = time_to_guess
        self.date_of_try = date_of_try
        self.time_of_try = time_of_try


def handle_sutom_message(sutom_message: discord.message) -> int:
    # Parse the message
    sutom_try = SutomTry()
    # TODO : delete the space before the first #
    # -> discord ID
    sutom_try.user_id = sutom_message.author.id
    # -> sutom number
    if (sutom_message.content[7] == '#'):
        s_number = ""
        digit_in_sutom_number = 0
        while (sutom_message.content[digit_in_sutom_number].isnumeric()):
            s_number = s_number + sutom_message.content[digit_in_sutom_number]
            digit_in_sutom_number += 1
        sutom_try.sutom_number = s_number
    else:
        return -1
    # -> number of try
    if (sutom_message.content[9 + digit_in_sutom_number]):
        pass
    sutom_try.number_of_try