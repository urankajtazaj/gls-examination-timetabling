class Penalty:
    def __init__(self, feature):
        self.feature = feature
        self.value = 0

    def get_value(self):
        return self.value

    def add_value(self):
        self.value += 1
