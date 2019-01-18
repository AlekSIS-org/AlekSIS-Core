class Lesson(object):
    def __init__(self):
        self.filled = False
        self.id = None
        self.elements = []
        self.times = []

    def add_element(self, teacher, subject, rooms=[], classes=[]):
        el = LessonElement()
        el.create(teacher, subject, rooms, classes)
        self.elements.append(el)

    def add_time(self, day, hour, rooms=[]):
        el = LessonTime()
        el.create(day, hour, rooms)
        self.times.append(el)

    def create(self, raw_lesson, drive):
        self.filled = True

        # Split data (,)
        lesson_id = raw_lesson.lesson_id
        self.id = lesson_id
        raw_lesson_data = raw_lesson.lessonelement1.split(",")
        raw_time_data = raw_lesson.lesson_tt.split(",")

        rtd2 = []
        for el in raw_time_data:
            rtd2.append(el.split("~"))

        # print(rtd2)

        for el in rtd2:
            day = int(el[1])
            hour = int(el[2])
            room_ids = untis_split_third(el[3], conv=int)

            rooms = []
            for room_id in room_ids:
                r = drive["rooms"][room_id]
                rooms.append(r)

            self.add_time(day, hour, rooms)

        # print(raw_lesson_data)
        # print(raw_time_data)

        # Split data more (~)
        rld2 = []
        for el in raw_lesson_data:
            rld2.append(el.split("~"))

        # print(rld2)

        for i, el in enumerate(rld2):
            teacher_id = int(el[0])
            subject_id = int(el[2])
            room_ids = untis_split_third(el[4], int)
            class_ids = untis_split_third(el[17], conv=int)
            # print("TEACHER – ", teacher_id, "; SUBJECT – ", subject_id, "; ROOMS – ", room_ids, "; CLASSES – ",
            #       class_ids)

            if teacher_id != 0:
                teacher = drive["teachers"][teacher_id]
            else:
                teacher = None

            if subject_id != 0:
                subject = drive["subjects"][subject_id]
            else:
                subject = None

            # rooms = self.times[i].rooms[i]
            # for room_id in room_ids:
            #     r = drive["rooms"][room_id]
            #     rooms.append(r)
            rooms = []
            # for room in rooms:
            #     print(room)
            # print("--")

            classes = []
            for class_id in class_ids:
                c = drive["classes"][class_id]
                classes.append(c)

            # print("TEACHER – ", teacher, "; SUBJECT – ", subject, "; ROOMS – ", rooms,
            #       "; CLASSES – ", classes)

            self.add_element(teacher, subject, rooms, classes)


class LessonElement(object):
    def __init__(self):
        self.teacher = None
        self.subject = None
        self.rooms = []
        self.classes = []

    def create(self, teacher, subject, rooms=[], classes=[]):
        self.teacher = teacher
        self.subject = subject
        self.rooms = rooms
        self.classes = classes


class LessonTime(object):
    def __init__(self):
        self.hour = None
        self.day = None
        self.rooms = []

    def create(self, day, hour, rooms=[]):
        self.day = day
        self.hour = hour
        self.rooms = rooms


from .api import *
from .api_helper import untis_split_third


def build_drive():
    odrive = {
        "teachers": get_all_teachers(),
        "rooms": get_all_rooms(),
        "classes": get_all_classes(),
        "subjects": get_all_subjects(),
        "corridors": get_all_corridors(),
    }

    drive = {
        # "teachers": {},
        # "rooms": {},
        # "classes": {},
        # "subjects": {}
    }
    for key, value in odrive.items():
        drive[key] = {}
        for el in value:
            id = el.id
            drive[key][id] = el

    # print(drive)
    return drive


drive = build_drive()


def parse():
    global drive
    lessons = []
    raw_lessons = get_raw_lessons()

    for raw_lesson in raw_lessons:
        # print("[RAW LESSON]")
        # print("LESSON_ID      | ", raw_lesson.lesson_id)
        # print("LessonElement1 | ", raw_lesson.lessonelement1)
        # print("Lesson_TT      | ", raw_lesson.lesson_tt)

        if raw_lesson.lesson_tt and raw_lesson.lessonelement1:
            # Create object
            lesson_obj = Lesson()
            lesson_obj.create(raw_lesson, drive)

            lessons.append(lesson_obj)

    return lessons


def get_lesson_by_id(id):
    global drive
    lesson = Lesson()
    raw_lesson = run_one(models.Lesson.objects, filter_term=True).get(lesson_id=id)
    lesson.create(raw_lesson, drive)
    return lesson


def get_lesson_element_by_id_and_teacher(lesson_id, teacher, hour=None, weekday=None):
    # print(lesson_id)
    #print(hour, "LEWE", weekday)
    try:
        lesson = get_lesson_by_id(lesson_id)
    except Exception:
        return None, None
    el = None
    i = 0
    #print(lesson.elements)
    for i, element in enumerate(lesson.elements):
        #print(element.teacher.shortcode)
        if element.teacher.id == teacher.id:
            el = element
            break
    t = None
    # print(lesson.times)
    # print(weekday)
    #print(hour)
    for time in lesson.times:
        #print("DAY", time.day, time.hour)
        if time.day == weekday and time.hour == hour:
            t = time
    #print(t)
    room = None
    if t is not None and len(t.rooms) > i:
        print(t.rooms)
        print(len(t.rooms))
        room = t.rooms[i]

    if el is not None:
        return el, room
    return None, None
