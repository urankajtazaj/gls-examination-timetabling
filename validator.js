const path = require('path');
const fs = require('fs');
const [_, __, instanceName, solutionName] = process.argv;

if (!instanceName) {
  console.error('Instance name is required');
  process.exit(1);
}

if (!solutionName) {
  console.error('Solution name is required');
  process.exit(1);
}

let instance;
try {
  console.log(path.join(__dirname, instanceName));
  const file = fs.readFileSync(path.join(__dirname, instanceName), 'utf8');
  instance = JSON.parse(file);
} catch (error) {
  console.error(`Instance ${instanceName} not found or invalid`);
  process.exit(1);
}

let solution;
try {
  const file = fs.readFileSync(path.join(__dirname, solutionName), 'utf8');
  solution = JSON.parse(file);
} catch (error) {
  console.error(`Instance ${instanceName} not found or invalid`);
  process.exit(1);
}

const coursesNotAssigned = [];
const coursesWithWrongRooms = [];
const roomsAssignedTwice = [];
const coursesWithSameTeacher = [];
const coursesInPrimaryCurricula = [];
const coursesInSecondaryCurricula = [];
const coursesWithWrongDistance = [];

// check if all courses have an assignment
for (const course of instance.Courses) {
  const assignmentExists = solution.Assignments.some((x) => x.Course === course.Course);

  if (!assignmentExists) coursesNotAssigned.push(course.Course);
}

// check if rooms were assigned correctly
for (const course of solution.Assignments) {
  const courseFromInstance = instance.Courses.find((x) => x.Course === course.Course);
  const roomsAssigned = course.Room.split(', ').filter(Boolean);

  if (roomsAssigned.length !== courseFromInstance.RoomsRequested.Number) {
    coursesWithWrongRooms.push(course.Course);
    continue;
  }

  const roomSizes = roomsAssigned.map((x) => instance.Rooms.find((y) => y.Room === x).Type);

  if (roomSizes.some((x) => x !== courseFromInstance.RoomsRequested.Type)) {
    coursesWithWrongRooms.push(course.Course);
  }
}

for (let i = 0; i < solution.Assignments.length; i++) {
  for (let j = i + 1; j < solution.Assignments.length; j++) {
    const course1 = solution.Assignments[i];
    const course2 = solution.Assignments[j];
    const course1FromInstance = instance.Courses.find((x) => x.Course === course1.Course);
    const course2FromInstance = instance.Courses.find((x) => x.Course === course2.Course);

    const arePrimaryInSameCurriculum = instance.Curricula.some(
      (x) => x.PrimaryCourses.includes(course1.Course) && x.PrimaryCourses.includes(course2.Course)
    );

    const arePrimarySecondaryInSameCurriculum = instance.Curricula.some(
      (x) =>
        (x.PrimaryCourses.includes(course1.Course) &&
          x.SecondaryCourses.includes(course2.Course)) ||
        (x.PrimaryCourses.includes(course2.Course) && x.SecondaryCourses.includes(course1.Course))
    );

    if (course1.Period !== course2.Period) {
      const distance = Math.abs(course1.Period - course2.Period);
      if (
        (arePrimaryInSameCurriculum && distance < instance.PrimaryPrimaryDistance) ||
        (arePrimarySecondaryInSameCurriculum && distance < instance.PrimarySecondaryDistance)
      ) {
        coursesWithWrongDistance.push({
          course1: course1.Course,
          course2: course2.Course,
          distance: distance,
        });
      }
      continue;
    }

    const rooms1 = course1.Room.split(', ').filter(Boolean);
    const rooms2 = course2.Room.split(', ').filter(Boolean);

    // check if there is an overlap
    for (const room1 of rooms1) {
      for (const room2 of rooms2) {
        if (room1 === room2) {
          roomsAssignedTwice.push({
            room: room1,
            period: course1.Period,
          });
        }
      }
    }

    if (course1FromInstance.Teacher === course2FromInstance.Teacher) {
      coursesWithSameTeacher.push({
        course1: course1.Course,
        course2: course2.Course,
      });
    }

    if (arePrimaryInSameCurriculum) {
      coursesInPrimaryCurricula.push({
        course1: course1.Course,
        course2: course2.Course,
      });
    }

    if (arePrimarySecondaryInSameCurriculum) {
      coursesInSecondaryCurricula.push({
        course1: course1.Course,
        course2: course2.Course,
      });
      coursesWithWrongDistance.push({
        course1: course1.Course,
        course2: course2.Course,
        distance: 0,
      });
    }
  }
}

const logIfNotEmpty = (log, array) => {
  if (array.length) console.log(log, array);
};

logIfNotEmpty('Courses not assigned:', coursesNotAssigned);
logIfNotEmpty('Courses with wrong number or size of rooms:', coursesWithWrongRooms);
logIfNotEmpty('Rooms assigned twice in the same period:', roomsAssignedTwice);
logIfNotEmpty('Courses with same teacher assigned in the same period:', coursesWithSameTeacher);
logIfNotEmpty(
  'Courses in primary-primary relationship assigned in the same period:',
  coursesInPrimaryCurricula
);
logIfNotEmpty(
  'Courses in primary-secondary relationship assigned in the same period:',
  coursesInSecondaryCurricula
);
logIfNotEmpty('Courses with wrong distance:', coursesWithWrongDistance);

const totalHardConflicts =
  coursesNotAssigned.length +
  coursesWithWrongRooms.length +
  roomsAssignedTwice.length +
  coursesWithSameTeacher.length +
  coursesInPrimaryCurricula.length;
const totalSoftConflicts = coursesInSecondaryCurricula.length + coursesWithWrongDistance.length;

console.log('Total hard conflicts:', totalHardConflicts);
console.log('Total soft conflicts:', totalSoftConflicts);
