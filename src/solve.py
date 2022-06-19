import copy
import random
from assignment import Assignment


class Solve:
    def __init__(self, instance_data, courses, periods, teachers, rooms, total_periods, primary_primary_distance,
                 primary_secondary_distance):
        self.primary_primary_distance = primary_primary_distance
        self.primary_secondary_distance = primary_secondary_distance
        self.instance = instance_data
        self.courses = courses
        self.periods = periods
        self.teachers = teachers
        self.rooms = rooms
        self.total_periods = total_periods
        self.teacher_period_allocations = {}
        self.room_period_allocations = {}
        self.primary_primary_conflicts = [0 for x in range(total_periods)]
        self.period_course_allocations = {}
        for x in range(total_periods):
            self.period_course_allocations[x] = []
        for teacher in teachers:
            self.teacher_period_allocations[teacher] = [0 for x in range(total_periods)]
        for room in rooms:
            self.room_period_allocations[room['Room']] = [0 for x in range(total_periods)]

    def solve(self):
        assignments = []
        courses = copy.deepcopy(self.courses)
        while len(courses):
            rand = random.randrange(0, len(courses))
            course = courses[rand]
            period, rooms = self.assign_period_and_room(course)

            if course['IsPrimary']:
                self.primary_primary_conflicts[period] = 1
            if period:
                self.teacher_period_allocations[course['Teacher']][period] = 1
            if period and len(rooms):
                for room in rooms:
                    self.room_period_allocations[room][period] = 1

            assignments.append(Assignment(course['Course'], period, rooms, self.get_course_by_name(course['Course'])))

            courses.remove(course)

        return assignments

    def assign_period_and_room(self, course):
        room_assigned = False
        period = -1
        rooms = []
        while not room_assigned:
            period = self.get_course_period(course)
            if course.get('RoomsRequested') and course['RoomsRequested']['Number'] == 0:
                room_assigned = True
            else:
                rooms = self.get_room(course, period)
                if len(rooms) == course['RoomsRequested']['Number']:
                    room_assigned = True

        return period, rooms

    def get_course_period(self, course):
        if len(course['PossiblePeriods']) == 0:
            return None

        possible_periods_limited = list(
            filter(lambda val: random.randrange(0, len(self.periods)), self.periods))
        period = random.choice(possible_periods_limited)

        return period

    def get_room(self, course, period):

        room_number = course['RoomsRequested']['Number']
        rooms = []
        for i in range(room_number):
            room_taken = True

            # while room_taken:
            rand = random.randrange(0, len(course['PossibleRooms']))
            room = course['PossibleRooms'][rand]

            # if self.room_period_allocations[room][period] == 0:
            rooms.append(room)
                    # room_taken = False

        return rooms

    def get_course_by_name(self, course_name):
        return list(filter(lambda a: a['Course'] == course_name, self.courses))[0]

    def get_random_period(self):
        return random.randrange(0, len(self.periods))

    def get_random_rooms(self, course):
        rooms = list(filter(lambda r: r['Type'] == course['RoomsRequested']['Type'], self.rooms))
        rooms_copy = copy.deepcopy(rooms)
        room_number = course['RoomsRequested']['Number']

        course_rooms = []
        i = 0
        while i < room_number:
            random_room = rooms_copy[random.randrange(0, len(rooms_copy))]
            if random_room not in course_rooms:
                course_rooms.append(random_room['Room'])
                i += 1

        return course_rooms

    def print(self, assignments):
        for assignment in assignments:
            print(assignment.get_properties())
