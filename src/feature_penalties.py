from feature import Feature
from penalties import Penalty


class FeaturePenalties:
    def __init__(self, courses, periods):
        self.courses = courses
        self.periods = periods
        self.penalties = []
        self.features = []

        for course in self.courses:
            for period in self.periods:
                feature = Feature(course['Course'], period)
                penalty = Penalty(feature)
                feature.set_penalty(penalty)

                self.penalties.append(penalty)
                self.features.append(feature)

    def penalize(self, solution, cost):
        pass

    def get_penalties(self):
        return self.penalties

    def get_features(self):
        return self.features

    def indicator(self, assignments, feature):
        return 1 if len(list(filter(
            lambda a: feature.get_period() == a.get_period() and feature.get_course() == a.get_course()['Course'],
            assignments))) > 0 else 0

    def penalizability(self, solution, feature, cost):
        return self.indicator(solution, feature) * (cost / (1 + feature.get_penalty().get_value()))

    def extended_move_evaluation_function(self, solution, beta, fitness):
        result = fitness
        for feature in self.get_features():
            result += beta * feature.get_penalty().get_value() * self.indicator(solution, feature)
        return result
