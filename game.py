from random import sample, choice
from config import TRAVEL_ROUTE_LENGTH, STARTING_LIVES

class GameState:
    def __init__(self, user_id, countries_dict):
        self.user_id = user_id
        self.countries_dict = countries_dict
        self.score = 0
        self.lives = STARTING_LIVES
        self.route = []
        self.progress = 0
        self.current_country = None
        self.current_capital = None
        self.in_travel = False

    def start_travel(self):
        keys = list(self.countries_dict.keys())
        # безопасно выбираем случайный маршрут
        self.route = sample(keys, min(TRAVEL_ROUTE_LENGTH, len(keys)))
        self.score = 0
        self.lives = STARTING_LIVES
        self.progress = 0
        self.in_travel = True
        return self.route

    def next_question(self):
        if not self.in_travel:
            raise RuntimeError("Not in travel mode")
        if self.progress >= len(self.route):
            return None
        country = self.route[self.progress]
        self.current_country = country
        self.current_capital = self.countries_dict[country]["capital"]
        return country, self.current_capital

    def answer(self, text):
        correct = text.strip().lower() == (self.current_capital or "").lower()
        if correct:
            self.score += 10
        else:
            self.lives -= 1
        self.progress += 1
        if self.lives <= 0:
            self.in_travel = False
            finished = True
        elif self.progress >= len(self.route):
            self.in_travel = False
            finished = True
        else:
            finished = False
        return correct, finished