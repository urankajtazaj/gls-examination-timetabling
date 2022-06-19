class Feature:
    def __init__(self, course_obj, period):
        self.course_obj = course_obj
        self.period = period
        self.penalty = None

    def get_course(self):
        return self.course_obj['Course']

    def get_course_obj(self):
        return self.course_obj

    def get_period(self):
        return self.period

    def set_penalty(self, penalty):
        self.penalty = penalty

    def get_penalty(self):
        return self.penalty

    def __str__(self):
        return f"{self.course_obj['Course']}_{self.period}"
