from constant import *
from helper import *


class Fitness:
    def __init__(self, primary_primary_distance, primary_secondary_distance, rooms):
        self.primary_primary_distance = primary_primary_distance
        self.primary_secondary_distance = primary_secondary_distance
        self.rooms = rooms

    def get_fitness(self, assignments):
        return self.distance_fitness(assignments) + \
               self.period_fitness(assignments) + \
               self.primary_secondary_relationship(assignments) + \
               self.primary_primary_relationship(assignments) + \
               self.room_period_fitness(assignments) + \
               self.room_course_conflict(assignments)

    def primary_secondary_relationship(self, assignments):
        cost = 0
        is_evaluated = []
        for assignment in assignments:
            for assignment2 in assignments:
                key = f"{assignment.get_course_name()}_{assignment2.get_course_name()}"
                if assignment.get_period() == assignment2.get_period() and (
                        len(intersect(assignment.get_primary_curricula(),
                                      assignment2.get_secondary_curricula())) or len(
                    intersect(assignment.get_secondary_curricula(), assignment2.get_primary_curricula()))) and \
                        key not in is_evaluated and assignment.get_course_name() != assignment2.get_course_name():
                    cost += SOFT_CONSTRAINT_WEIGHT
                    is_evaluated.append(key)
                    is_evaluated.append(f"{assignment2.get_course_name()}_{assignment.get_course_name()}")

            assignment.set_soft_conflict(cost > 0)

        return cost

    def primary_primary_relationship(self, assignments):
        cost = 0
        is_evaluated = []
        for assignment in assignments:

            for assignment2 in assignments:
                key = f"{assignment.get_course_name()}_{assignment2.get_course_name()}"
                if assignment.get_period() == assignment2.get_period() and len(
                        intersect(assignment.get_primary_curricula(), assignment2.get_primary_curricula())) and \
                        key not in is_evaluated and assignment.get_course_name() != assignment2.get_course_name():
                    cost += HARD_CONSTRAINT_WEIGHT
                    is_evaluated.append(key)
                    is_evaluated.append(f"{assignment2.get_course_name()}_{assignment.get_course_name()}")

            assignment.set_period_conflict(cost > 0)

        return cost

    def room_period_fitness(self, assignments):
        cost = 0
        is_evaluated = []

        for assignment in assignments:
            rooms = []
            assignment_cost = 0
            for assignment2 in assignments:
                key = f"{assignment.get_course_name()}_{assignment2.get_course_name()}"
                if assignment.get_period() == assignment2.get_period() and \
                        key not in is_evaluated and assignment.get_course_name() != assignment2.get_course_name():

                    for room in intersect(assignment2.get_rooms(), assignment.get_rooms()):
                        if room not in rooms:
                            assignment_cost += HARD_CONSTRAINT_WEIGHT
                            rooms.append(room)

                    is_evaluated.append(key)
                    is_evaluated.append(f"{assignment2.get_course_name()}_{assignment.get_course_name()}")

            cost += assignment_cost
            assignment.set_room_conflict(assignment_cost > 0)
        return cost

    def room_course_conflict(self, assignments):
        cost = 0
        for assignment in assignments:
            course = assignment.get_course()
            rooms = assignment.get_rooms()

            if len(rooms) != course['RoomsRequested']['Number'] and course['RoomsRequested']['Number'] > 0:
                cost += HARD_CONSTRAINT_WEIGHT

            for room_name in rooms:
                room = get_room_by_name(room_name, self.rooms)

                if room['Type'] != course['RoomsRequested']['Type']:
                    cost += HARD_CONSTRAINT_WEIGHT

            assignment.set_room_course_conflict(cost > 0)
        return cost

    def period_fitness(self, assignments):
        cost = 0
        is_evaluated_t = []
        for assignment in assignments:
            assignment_cost = 0
            for assignment2 in assignments:
                key = f"{assignment.get_course_name()}_{assignment2.get_course_name()}"

                if assignment.get_period() == assignment2.get_period() and \
                        assignment.get_course()['Teacher'] == assignment2.get_course()['Teacher'] and \
                        assignment.get_course_name() != assignment2.get_course_name() and \
                        key not in is_evaluated_t:
                    assignment_cost += HARD_CONSTRAINT_WEIGHT
                    cost += HARD_CONSTRAINT_WEIGHT
                    is_evaluated_t.append(key)
                    is_evaluated_t.append(f"{assignment2.get_course_name()}_{assignment.get_course_name()}")
            assignment.set_teacher_period_conflict(assignment_cost > 0)

        return cost

    def distance_fitness(self, assignments):
        cost = 0

        is_evaluated = []
        is_evaluated_s = []
        for assignment in assignments:
            without_self = list(
                filter(lambda a: a.get_course()['Course'] != assignment.get_course()['Course'], assignments))
            assignment_cost = self.evaluate_primary_distance(assignment, without_self, is_evaluated)
            assignment_cost += self.evaluate_secondary_distance(assignment, without_self, is_evaluated_s)

            assignment.set_distance_conflict(assignment_cost > 0)

            cost += assignment_cost

        return cost

    def evaluate_secondary_distance(self, assignment, assignments, is_evaluated):
        cost = 0
        for ass in assignments:
            if abs(assignment.get_period() - ass.get_period()) < self.primary_secondary_distance and \
                    (len(intersect(assignment.get_primary_curricula(), ass.get_secondary_curricula())) or len(
                        intersect(assignment.get_secondary_curricula(), ass.get_primary_curricula()))) and \
                    f"{assignment.get_course_name()}_{ass.get_course_name()}" not in is_evaluated:
                cost += SOFT_CONSTRAINT_WEIGHT
                is_evaluated.append(f"{assignment.get_course_name()}_{ass.get_course_name()}")
                is_evaluated.append(f"{ass.get_course_name()}_{assignment.get_course_name()}")

        return cost

    def evaluate_primary_distance(self, assignment, assignments, is_evaluated):
        cost = 0
        for ass in assignments:
            if abs(assignment.get_period() - ass.get_period()) < self.primary_primary_distance and \
                    assignment.is_primary() and ass.is_primary() and \
                    len(intersect(assignment.get_primary_curricula(), ass.get_primary_curricula())) and \
                    f"{assignment.get_course_name()}_{ass.get_course_name()}" not in is_evaluated:
                cost += SOFT_CONSTRAINT_WEIGHT
                is_evaluated.append(f"{assignment.get_course_name()}_{ass.get_course_name()}")
                is_evaluated.append(f"{ass.get_course_name()}_{assignment.get_course_name()}")

        return cost
