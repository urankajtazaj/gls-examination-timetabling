from preprocess import *
from solve import *
import random
import time
from preprocess import print_initial_solution
from fitness import Fitness
from feature import *
from constant import *
from helper import *
from datetime import datetime


def generate_initial_solution(instance=None):
    instance_data = read_instance(get_file_path(instance))
    courses, periods, teachers, rooms, total_periods, primary_primary_distance, primary_secondary_distance = preprocess_instance(
        instance_data)

    solver = Solve(instance_data, courses, periods, teachers, rooms, total_periods, primary_primary_distance,
                   primary_secondary_distance)

    return solver.solve(), solver


def main():
    initial_solution, solver = generate_initial_solution()
    instance_looper(initial_solution, solver)


def instance_looper(initial_solution, solver):
    features = []
    penalties = {}

    for course in solver.courses:
        for period in solver.periods:
            feature = Feature(course, period)
            features.append(feature)
            penalties[str(feature)] = 0

    fitness_class = Fitness(solver.primary_primary_distance, solver.primary_secondary_distance, solver.rooms)

    solution = initial_solution
    best_solution = solution

    solver.print(solution)

    best_fitness = fitness_class.get_fitness(initial_solution)
    fitness = best_fitness

    times_slots = 10
    local_optimum_times = [random.randrange(MIN_LOCAL_OPTIMUM_TIME, MAX_LOCAL_OPTIMUM_TIME + 1) for _ in
                           range(times_slots)]

    ttr = 60 * 3  # Time To Run: 3 minutes
    start_time = time.time()
    while True:
        start_time_1 = time.time()
        elapsed_time_1 = 0
        while best_fitness != 0 and elapsed_time_1 < local_optimum_times[random.randrange(0, times_slots)]:
            elapsed_time_1 = time.time() - start_time_1
            neighbour = tweak(solution, solver)
            neighbour_fitness = fitness_class.get_fitness(neighbour)

            if neighbour_fitness < best_fitness:
                best_solution = neighbour
                best_fitness = neighbour_fitness
                print("New best fitness", best_fitness)

            if adjusted_quality(neighbour, features, penalties, neighbour_fitness) < \
                    adjusted_quality(solution,
                                     features,
                                     penalties,
                                     fitness):
                solution = neighbour
                fitness = neighbour_fitness

        print("-" * 25)
        fs = []
        for assignment in solution:
            fs.append(Feature(assignment.get_course(), assignment.get_period()))

        Cp = []
        feature_costs = {}

        for f in fs:
            max_feature = f
            for fj in fs:

                if str(f) not in feature_costs:
                    feature_costs[str(f)] = get_feature_cost(solution, f, solver)

                if str(fs) not in feature_costs:
                    feature_costs[str(fs)] = get_feature_cost(solution, fj, solver)

                solution_penalizability_f = penalizability(feature_costs[str(f)], penalties[str(f)])
                solution_penalizability_fj = penalizability(feature_costs[str(fs)], penalties[str(fj)])

                if solution_penalizability_f < solution_penalizability_fj:
                    max_feature = None

            if max_feature not in Cp and max_feature is not None:
                Cp.append(str(max_feature))

        for f in fs:
            if str(f) in Cp:
                penalties[str(f)] += 1

        elapsed_time = time.time() - start_time
        if best_fitness == 0 or elapsed_time > ttr:
            print_initial_solution(best_solution)
            break

    return best_fitness


def average(lst):
    return round(sum(lst) / len(lst), 2)


def get_feature_cost(solution, feature, solver):
    is_evaluated_c = []
    is_evaluated_t = []
    is_evaluated_ps = []
    is_evaluated_tc = []
    is_evaluated_p = []
    cost = 0

    for ass in solution:
        if feature.get_course() == ass.get_course_name():
            continue

        key1 = f"{feature.get_course()}_{ass.get_course_name()}"
        key2 = f"{ass.get_course_name()}_{feature.get_course()}"

        if abs(feature.get_period() - ass.get_period()) < solver.primary_primary_distance and \
                feature.get_course_obj()['IsPrimary'] and ass.is_primary() and \
                len(intersect(feature.get_course_obj()['PrimaryCurricula'], ass.get_primary_curricula())) and \
                ass.get_course_name() != feature.get_course() and \
                key1 not in is_evaluated_c and key2 not in is_evaluated_c:
            cost += SOFT_CONSTRAINT_WEIGHT
            is_evaluated_c.append(key1)
            is_evaluated_c.append(key2)

        if abs(feature.get_period() - ass.get_period()) < solver.primary_secondary_distance and \
                (len(intersect(feature.get_course_obj()['PrimaryCurricula'],
                               ass.get_secondary_curricula())) or len(
                    intersect(feature.get_course_obj()['SecondaryCurricula'], ass.get_primary_curricula()))) and \
                ass.get_course_name() != feature.get_course() and \
                key1 not in is_evaluated_t and key2 not in is_evaluated_t:
            cost += SOFT_CONSTRAINT_WEIGHT
            is_evaluated_t.append(key1)
            is_evaluated_t.append(key2)

        if feature.get_period() == ass.get_period() and (
                len(intersect(feature.get_course_obj()['PrimaryCurricula'],
                              feature.get_course_obj()['SecondaryCurricula'])) or len(
            intersect(feature.get_course_obj()['SecondaryCurricula'], ass.get_primary_curricula()))) and \
                feature.get_course() != ass.get_course_name() and \
                key1 not in is_evaluated_ps and key2 not in is_evaluated_ps:
            cost += SOFT_CONSTRAINT_WEIGHT
            is_evaluated_ps.append(key1)
            is_evaluated_ps.append(key2)

        if feature.get_period() == ass.get_period() and \
                feature.get_course_obj()['Teacher'] == ass.get_course()['Teacher'] and \
                feature.get_course() != ass.get_course_name() and \
                key1 not in is_evaluated_tc:
            cost += HARD_CONSTRAINT_WEIGHT
            is_evaluated_tc.append(key1)
            is_evaluated_tc.append(key2)

        if feature.get_period() == ass.get_period() and len(
                intersect(feature.get_course_obj()['PrimaryCurricula'], ass.get_primary_curricula())) and \
                key1 not in is_evaluated_p and feature.get_course() != ass.get_course_name():
            cost += HARD_CONSTRAINT_WEIGHT
            is_evaluated_p.append(key1)

    return cost


def tweak(sol, solver):
    neighbour = copy.deepcopy(sol)

    room_conflict_vars = list(filter(lambda a: a.has_room_conflict(), neighbour))

    if len(room_conflict_vars):
        rand_index = random.randrange(0, len(room_conflict_vars))
        assignment = room_conflict_vars[rand_index]
        assignment.set_rooms(solver.get_random_rooms(assignment.get_course()))
        return neighbour

    room_course_conflict_vars = list(filter(lambda a: a.has_room_course_conflict(), neighbour))

    if len(room_course_conflict_vars):
        rand_index = random.randrange(0, len(room_course_conflict_vars))
        assignment = room_course_conflict_vars[rand_index]
        assignment.set_rooms(solver.get_random_rooms(assignment.get_course()))
        return neighbour

    period_conflict_vars = list(filter(lambda a: a.has_period_conflict(), neighbour))

    if len(period_conflict_vars):
        rand_index = random.randrange(0, len(period_conflict_vars))
        period_conflict_vars[rand_index].set_period(solver.get_random_period())
        return neighbour

    teacher_period_conflict_vars = list(filter(lambda a: a.has_teacher_period_conflict(), neighbour))

    if len(teacher_period_conflict_vars):
        rand_index = random.randrange(0, len(teacher_period_conflict_vars))
        teacher_period_conflict_vars[rand_index].set_period(solver.get_random_period())
        return neighbour

    soft_conflict_vars = list(filter(lambda a: a.has_soft_conflict(), neighbour))

    if len(soft_conflict_vars):
        rand_index = random.randrange(0, len(soft_conflict_vars))
        assignment = soft_conflict_vars[rand_index]
        assignment.set_period(solver.get_random_period())
        return neighbour

    soft_distance_vars = list(filter(lambda a: a.has_distance_conflict(), neighbour))

    if len(soft_distance_vars):
        rand_index = random.randrange(0, len(soft_distance_vars))
        assignment = soft_distance_vars[rand_index]
        assignment.set_period(solver.get_random_period())
        return neighbour

    return neighbour


def penalizability(fitness, penalty):
    return fitness / (1 + penalty)


def adjusted_quality(assignments, feats, pens, f):
    assignments_copy = copy.deepcopy(assignments)
    b = random.random()

    fs = []
    for assignment in assignments_copy:
        fs.append(f"{assignment.get_course_name()}_{assignment.get_period()}")

    s = sum((1 if str(feat) in fs else 0) * pens[str(feat)] for feat in feats)

    return f + (b * s)


if __name__ == '__main__':
    main()
