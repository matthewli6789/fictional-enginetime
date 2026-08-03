import numpy as np
import csv
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from math import prod
from itertools import product
from colorsys import hsv_to_rgb

def course_paste(paste_into):
    def a_or_p(time):
        if time[5:7] == 'PM' and time[0:2] != '12':
            return f'{str(int(time[0:2]) + 12)}:{time[3:5]}'
        else:
            return time[0:5]

    file_list = []
    add_list = []

    with open('course_paste.txt', 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for line in reader:
            file_list += line

    try:
        course = file_list[0][:9]
        matching = None
        if file_list[1] == '[Matching between Lecture & Lab required]':
            matching = 'LLA'
        elif file_list[1] == '[Matching between Lecture & Tutorial required]':
            matching = 'LT'

        add_list.append([course, matching])

        section = ''
        durations = []
        for i, item in enumerate(file_list):
            if i < 2:
                continue  # First two lines are course title and matching requirement

            if len(item) >= 9 and item[-6] == '(' and item[-1] == ')':
                if durations:
                    # Add previous section
                    add_list.append([section] + durations)

                # Retrieve section
                section = item[:-7]
                durations = []

            if ' - ' in item:
                if len(item) == 20:
                    # Retrieve 1 duration
                    durations.append(f'{item[0:2]} {a_or_p(item[3:10])} {a_or_p(item[13:20])}')
                elif len(item) == 22:
                    # Retrieve 2 durations
                    durations.append(f'{item[0:2]} {a_or_p(item[5:12])} {a_or_p(item[15:22])}')
                    durations.append(f'{item[2:4]} {a_or_p(item[5:12])} {a_or_p(item[15:22])}')

        # Add last section
        add_list.append([section] + durations)

        with open(paste_into, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(add_list)

    except Exception as e:
        raise Exception(f'#### Unable to paste course info: {e}')
    else:
        print('Course successfully pasted')



class TimetablePlanner:

    def __init__(self, year, semester):

        self.letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.numbers = '0123456789'

        self.valid_days = ['MO', 'TU', 'WE', 'TH', 'FR']
        self.valid_matching = [None, 'LLA', 'LT']

        self.valid_times = []
        for hour in range(9, 21):
            for minute in range(00, 60, 10):
                self.valid_times.append(f'{str(hour).zfill(2)}:{str(minute).zfill(2)}')

        self.year = None
        for i in range(25, 29):
            # Most of this part is unnecessary but allows the academic year to be typed in any format
            if str(i) in year and str(i + 1) in year:
                self.year = f'{2000 + i}-{i + 1}'
        if self.year is None:
            raise Exception('#### Invalid: Year not valid')

        self.semester = None
        semester = semester.upper()
        if semester == 'AUTUMN':
            semester = 'FALL'
        if semester in ['FALL', 'WINTER', 'SPRING', 'SUMMER']:
            self.semester = semester
        if self.semester is None:
            print('#### Invalid: Semester not valid')
            quit()

        file_name_list = {
            '2025-26': {
                'FALL': '2526F.csv',
                'SPRING': '2526S.csv',
            },
            '2026-27': {
                'FALL': '2627F.csv',
                'SPRING': '',
            },
            '2027-28': {
                'FALL': '',
                'SPRING': '',
            },
            '2028-29': {
                'FALL': '',
                'SPRING': '',
            },
        }

        # Check for matching text file
        self.file_name = file_name_list[self.year][self.semester]
        if not self.file_name:
            raise Exception(f'#### Invalid: No file found')

        self.courses = []
        self.course_matching = {}
        self.classes = {}

        # Make dictionary of classes
        with (open(self.file_name, 'r') as f):
            reader = csv.reader(f)

            for line_no, line in enumerate(reader):

                # Read file
                try:

                    # Except blank line
                    if not line:
                        raise Exception(f'Line blank')

                    # Convert to uppercase
                    line = list(item.upper() for item in line)

                    if 1 <= len(line) <= 2 and 8 <= len(line[0]) <= 9:
                        # Course name and matching

                        course = line[0]
                        if len(line) == 1:
                            matching = None
                        else:
                            if line[1] == '':
                                matching = None
                            else:
                                matching = line[1]

                        # Add space in course name if space was not included
                        if len(course) == 8:
                            line = f'{course[:4]} {course[4:]}'

                        # Check for valid course name
                        if not len(course) == 9:
                            raise Exception(
                                f'Course name not in valid format (length)')
                        if not all(c in self.letters for c in course[:4]):
                            raise Exception(f'Course name not in valid format (letters)')
                        if not course[4] == ' ':
                            raise Exception(f'Course name not in valid format (space)')
                        if not all(c in self.numbers for c in course[5:]):
                            raise Exception(f'Course name not in valid format (numbers)')

                        # Check for valid matching requirement
                        if not (matching in self.valid_matching):
                            raise Exception(f'Invalid matching requirement')

                        self.courses.append(course)
                        self.course_matching[course] = matching

                    elif len(line) >= 2:

                        section = line[0]
                        section_durations = line[1:]

                        # Check that section name length is at least 2
                        if not len(section) >= 2:
                            raise Exception(f'Section not in valid format')

                        # Check that section name starts with one or two letters
                        if (section[0] in self.letters) and (section[1] in self.letters):
                            # Check that section contains a number
                            if not ((section[2:].isdecimal())
                                    or (section[2:-1].isdecimal() and section[-1] in self.letters)):
                                raise Exception(f'Section not in valid format')

                        elif not section[0].isdecimal():
                            # Check that section contains a number
                            if not ((section[1:].isdecimal())
                                    or (section[1:-1].isdecimal() and section[-1] in self.letters)):
                                raise Exception(f'Section not in valid format')

                        else:
                            raise Exception(f'Section not in valid format')

                        # Check for duplicate section type
                        if (course, section) in self.classes:
                            raise Exception(f'Duplicate section')

                        durations_formatted = []
                        # Check for valid time name
                        for i, d in enumerate(section_durations):
                            if not d:
                                continue
                            if not len(d) == 14:
                                print(line)
                                raise Exception(f'Course time not in valid format (Time {i})')
                            if d[:2] not in self.valid_days:
                                raise Exception(f'Invalid weekday (Time {i})')
                            if d[3:8] not in self.valid_times or d[9:14] not in self.valid_times:
                                raise Exception(f'Invalid time (Time {i})')
                            durations_formatted.append((d[:2], d[3:8], d[9:14]))

                        if not self.courses:
                            raise Exception('Section has no associated course')
                        self.classes[(course, section)] = durations_formatted

                except Exception as e:
                    print(f'#### Invalid: {e} (File {self.file_name} Line {line_no + 1})')

        self.blank = np.zeros((5, len(self.valid_times)))


    def find_timetables(self, print_valid=False, plot=False, whitelist=None, blacklist=None):

        def create_timetable():
            return np.zeros((5, len(self.valid_times)))

        def find_section_type(section):
            if section[1] in self.numbers:
                return section[0:1]
            else:
                return section[0:2]

        def find_duration_index(duration):
            return (self.valid_days.index(duration[0]),
                    self.valid_times.index(duration[1]),
                    self.valid_times.index(duration[2]))

        def overlap(table, course, section):
            for duration in self.classes[(course, section)]:
                day, start, end = find_duration_index(duration)
                if np.any(table[day, start:end]):
                    return True
            else:
                return False

        def add_class(table, course, section):
            for duration in self.classes[(course, section)]:
                day, start, end = find_duration_index(duration)
                table[day, start:end] = 1
            return table

        def all_product(whitelist, blacklist):

            all_course_products = []

            for course in self.courses:
                current_course_products = []

                # Find all section types in course
                sections = [key[1] for key in self.classes if key[0] == course]
                section_types = list(set(find_section_type(key) for key in sections))
                section_types.sort()

                if any(wl_c == course for wl_c, _ in whitelist):
                    sections = list(
                        s for s in sections if not(
                                any(
                                    wl_c == course
                                    and find_section_type(wl_s) == find_section_type(s)
                                    for wl_c, wl_s in whitelist
                                )
                                and (course, s) not in whitelist
                        )
                    )
                sections = list(s for s in sections if (course, s) not in blacklist)

                # Raise error if a section type has no section (due to combination of whitelist and blacklist)
                if missing := set(section_types) - set(find_section_type(key) for key in sections):
                    raise Exception(f'No valid sections {missing} in {course}')

                if self.course_matching[course] == 'LLA':
                    for l_section in list(s for s in sections if find_section_type(s) == 'L'):
                        for la_section in list(
                                s for s in sections if find_section_type(s) == 'LA' and l_section[1:] in s):
                            current_course_products.append([(course, l_section), (course, la_section)])

                    section_types.remove('L')
                    section_types.remove('LA')
                    all_course_products.append(current_course_products)

                elif self.course_matching[course] == 'LT':
                    for l_section in list(s for s in sections if find_section_type(s) == 'L'):
                        for t_section in list(
                                s for s in sections if find_section_type(s) == 'T' and l_section[1:] in s):
                            current_course_products.append([(course, l_section), (course, t_section)])

                    section_types.remove('L')
                    section_types.remove('T')
                    all_course_products.append(current_course_products)

                for section_type in section_types:
                    all_course_products.append(
                        list([(course, s)] for s in sections if find_section_type(s) == section_type))

            return all_course_products

        def plot_timetable(ar_no, invalid, p_courses):

            def custom_colour():

                def colour_formula(course):
                    h, s, v = (
                        self.letters.index(course[0]) / 26 + int(course[7]) * 0.02,
                        1 - int(course[6]) * 0.07 - int(course[8]) * 0.02,
                        1 - int(course[5]) * 0.15
                    )
                    return h, s, v

                t = self.courses

                t = np.array(list(colour_formula(course) for course in t))
                t += np.random.uniform(-0.01, 0.01, np.shape(t))
                def tooclose(x):
                    return abs(1 / (30 + 300 * abs(x))) * (x / abs(x))

                a = np.array([t] * len(t))
                a = a[np.where(1 - np.eye(len(t)))]

                a = np.reshape(a, (-1, int(len(a) ** 0.5), 3))
                a = tooclose(np.expand_dims(t, axis=1) - a)

                t = t + np.sum(a, axis=1)
                t[np.where(t > 1)] = 1
                t[np.where(t < 0)] = 0

                return t

            custom_colours = custom_colour()
            rgb_values = list(hsv_to_rgb(*colour) for colour in custom_colours)

            unique_courses = list(set(course for course, section in p_courses))
            for (course, section) in p_courses:
                cur_course = unique_courses.index(course)
                for duration in self.classes[(course, section)]:
                    day, start, end = find_duration_index(duration)

                    # Plot bar
                    plt.bar(day, end - start, bottom=start, color=rgb_values[self.courses.index(course)], alpha=0.6)

            legend_values = list(
                Patch(facecolor=rgb_values[self.courses.index(course)], alpha=0.6, label=course) for i, course in
                enumerate(unique_courses))
            plt.legend(handles=legend_values)


            title = f'Timetable {ar_no} ({'Invalid' if invalid else 'Valid'})'
            for i, (course, section) in enumerate(p_courses):
                if i % 4 == 0:
                    title += '\n'
                title += f'{course} {section}  '

            plt.title(title, fontsize='small')

            plt.xlim(-0.5, len(self.valid_days) - 0.5)
            plt.ylim(-0.5, len(self.valid_times) - 0.5)
            plt.xticks(np.arange(0, len(self.valid_days), 1), self.valid_days)
            plt.yticks(np.arange(0, len(self.valid_times), 9),
                       list(self.valid_times[i] for i in range(0, len(self.valid_times), 9)))

            plt.grid(which='major', axis='y', alpha=0.75)

            plt.show()

        a_p = all_product(whitelist, blacklist)

        if not list(len(sub) for sub in a_p):
            raise Exception('No combinations created')
        total = prod(len(sub) for sub in a_p)

        total_valid = 0
        choose = random.randint(0, total-1)

        for i, p_courses in enumerate(product(*a_p)):
            p_courses = list(x for sub in p_courses for x in sub)

            timetable = create_timetable()
            invalid = False
            for course, section in p_courses:
                if overlap(timetable, course, section):
                    invalid = True
                    break
                else:
                    timetable = add_class(timetable, course, section)

            if not invalid:
                total_valid += 1
                if print_valid:
                    print(i, '\t'.join(f'{course} {section}' for course, section in p_courses))

            if i == choose and plot:
                plot_timetable(i, invalid, p_courses)
        if print_valid:
            print(f'Found {total_valid} valid out of {total} total timetables')


def main():

    #course_paste('2627F.csv')

    t = TimetablePlanner('2026-2027', 'Fall')


    t.find_timetables(
        print_valid=True,
        plot=True,
        whitelist=[],
        blacklist=[]
    )

if __name__ == '__main__':
    main()
