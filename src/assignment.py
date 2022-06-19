class Assignment:
    def __init__(self, course, period, rooms, course_obj, period_conflict=False, soft_conflict=False,
                 room_conflict=False, distance_conflict=False, room_course_conflict=False, teacher_period_conflict=False):
        self.period_conflict = None
        self.soft_conflict = None
        self.course = course
        self.period = period
        self.rooms = rooms
        self.course_obj = course_obj
        self.room_conflict = room_conflict
        self.room_course_conflict = room_course_conflict
        self.distance_conflict = distance_conflict
        self.teacher_period_conflict = teacher_period_conflict

    def get_rooms(self):
        return self.rooms

    def set_rooms(self, rooms):
        self.rooms = rooms

    def get_course(self):
        return self.course_obj

    def set_soft_conflict(self, value):
        self.soft_conflict = value

    def has_soft_conflict(self):
        return self.soft_conflict

    def set_distance_conflict(self, value):
        self.distance_conflict = value

    def has_distance_conflict(self):
        return self.distance_conflict

    def set_room_conflict(self, value):
        self.room_conflict = value

    def has_room_course_conflict(self):
        return self.room_course_conflict

    def set_room_course_conflict(self, value):
        self.room_course_conflict = value

    def has_room_conflict(self):
        return self.room_conflict

    def set_period_conflict(self, value):
        self.period_conflict = value

    def has_period_conflict(self):
        return self.period_conflict

    def set_teacher_period_conflict(self, value):
        self.teacher_period_conflict = value

    def has_teacher_period_conflict(self):
        return self.teacher_period_conflict

    def set_period(self, period):
        self.period = period

    def get_period(self):
        return self.period

    def get_course_name(self):
        return self.get_course()['Course']

    def is_primary(self):
        return self.get_course()['IsPrimary']

    def get_curricula(self):
        return list(set(self.get_course()['PrimaryCurricula'] + self.get_course()['SecondaryCurricula']))

    def get_primary_curricula(self):
        return self.get_course()['PrimaryCurricula']

    def get_secondary_curricula(self):
        return self.get_course()['SecondaryCurricula']

    def get_properties(self):
        return {
            'Course': self.course,
            'Period': self.period,
            'Room': ", ".join(self.rooms),
        }
