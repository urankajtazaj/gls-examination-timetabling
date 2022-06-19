import copy
import json


def preprocess_instance(instance):
    courses = instance['Courses']
    curricula = instance['Curricula']
    total_periods = instance['Periods']
    rooms = instance['Rooms']
    slots_per_day = instance['SlotsPerDay']
    teachers = instance['Teachers']
    primary_primary_distance = instance['PrimaryPrimaryDistance']
    primary_secondary_distance = instance['PrimarySecondaryDistance']
    rooms_dict = {
        'Large': list(filter(lambda r: r['Type'] == 'Large', rooms)),
        'Small': list(filter(lambda r: r['Type'] == 'Small', rooms)),
        'Medium': list(filter(lambda r: r['Type'] == 'Medium', rooms))
    }

    periods = list(range(0, total_periods))
    courses = split_courses(courses, curricula, two_part_course_periods(periods, slots_per_day))
    courses = add_possible_rooms(courses, rooms_dict)
    return courses, periods, teachers, rooms, total_periods, primary_primary_distance, primary_secondary_distance


def split_courses(course_list, curricula, periods):
    courses = copy.deepcopy(course_list)
    courses_list = []
    for course in courses:
        course['IsPrimary'] = is_course_primary(course['Course'], curricula)
        course['PrimaryCurricula'], course['SecondaryCurricula'] = get_course_curricula(course['Course'], curricula)
        courses_list.append(course)
        course['PossiblePeriods'] = periods

    return courses_list


def add_possible_rooms(courses, room_list):
    # rooms = copy.deepcopy(room_list)
    for course in courses:
        course['PossibleRooms'] = []

        if course['RoomsRequested']['Number'] > 0:
            possible_rooms = room_list[course['RoomsRequested']['Type']]
            course['PossibleRooms'] = [sub['Room'] for sub in possible_rooms]

        # possible_rooms = list(filter(lambda val: course['RoomsRequested']['Number'] > 0 and
        #                                          val['Type'] == course['RoomsRequested']['Type'], rooms))

    return courses


def two_part_course_periods(period_list, slots_per_day):
    periods = period_list.copy()
    return list(set(periods) - set(list(filter(lambda val: val % slots_per_day != 0, periods))))


def print_initial_solution(solution):
    sol = []
    for assignment in solution:
        sol.append(assignment.get_properties())

    initial_solution = json.dumps({"Assignments": sol}, indent=2)
    with open("initial_solution.json", "w") as initial_solution_output:
        initial_solution_output.write(initial_solution)


def is_course_primary(course, curricula):
    for curricula in curricula:
        for c in curricula['PrimaryCourses']:
            if c == course:
                return True
    return False


def get_course_curricula(course, curricula):
    course_primary_curricula = []
    course_secondary_curricula = []
    curricula = copy.deepcopy(list(curricula))
    for c in curricula:
        for c1 in c['PrimaryCourses']:
            if c1 == course:
                course_primary_curricula.append(c['Curriculum'])
                break
        for c2 in c['SecondaryCourses']:
            if c2 == course:
                course_secondary_curricula.append(c['Curriculum'])
                break

    return course_primary_curricula, course_secondary_curricula
