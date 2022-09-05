import sys
import csv
import re
import pickle

class Person:
    def __init__(self, last: str, first: str, middle: str, id: str, phone: str):
        self.last = last
        self.first = first
        self.middle = middle
        self.id = id
        self.phone = phone

    def print_person(self):
        print('Employee id: ' + self.id)
        print('\t\t\t ' + self.first + ' ' + self.middle + ' ' + self.last)
        print('\t\t\t ' + self.phone)



def read_data_csv():
    person_dict = dict()
    with open(str(sys.argv[1])) as csvfile:
        lines = csv.reader(csvfile)
        # read over each line and populate the dictionary
        for line_count, row in enumerate(lines):
            if line_count < 1:
                continue

            # capitalize first name
            row[0] = row[0].capitalize()

            # capitalize last name
            row[1] = row[1].capitalize()

            # Check if middle initial is a valid character
            if re.match('^[a-zA-Z]$', row[2]):
                row[2] = row[2].capitalize()
            else:
                row[2] = 'X'

            # Check for valid ID
            while not re.match('^[a-zA-Z]{2}[0-9]{4}$', row[3]):
                print('ID invalid: ' + row[3])
                print('ID is two letters followed by 4 digits')
                row[3] = input('Please enter a valid id: ')
                row[3] = row[3].upper()

            # Check for valid phone
            while not re.match('^[1-9]\d{2}-\d{3}-\d{4}$', row[4]):
                print('Phone ' + row[4] + ' is invalid')
                print('Enter phone number in form 123-456-7890')
                row[4] = input('Enter phone number: ')

            # create a new person object with the inputs from the csv
            person_obj = Person(row[0], row[1], row[2], row[3], row[4])

            # add person object to the dictionary
            person_dict[person_obj.id] = person_obj

    return person_dict

if __name__ == "__main__":
    if not len(sys.argv) > 1:
        print("There is no file location in the argument")
    else:
        person_dict = read_data_csv()

        # pickle saving
        pickle.dump(person_dict, open('dict.p', 'wb'))

        # pickle reading
        dict_in = pickle.load(open('dict.p', 'rb'))

        # Print out the employees
        print()
        print('Employee list:\n')
        for person in dict_in.values():
            person.print_person()
            print()
