from datetime import datetime, timedelta
from collections import UserDict
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        if value:
            if not self.is_valid_birthday(value):
                raise ValueError("Invalid birthday format")
    
    @staticmethod
    def is_valid_birthday(value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
            return True
        except ValueError:
            return False    


class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if not self.is_valid_phone(value):
            raise ValueError("Invalid phone number format")
        
    @staticmethod
    def is_valid_phone(value):
        return len(value) == 10 and value.isdigit()

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        
    def add_phone(self, phone):
        self.phones.append(Phone(phone))
        
    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError(f"Phone number '{phone}' not found in record '{self.name.value}'")
    
    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return
        raise ValueError(f"Phone number '{old_phone}' not found in record '{self.name.value}'")
            
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        raise ValueError(f"Phone number '{phone}' not found in record '{self.name.value}'")

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    
    def add_birthday(self, birthday):
        if self.birthday:
            raise ValueError("Birthday already exists for this contact")
        self.birthday = Birthday(birthday)

class AddressBook(UserDict):
    def __init__(self):
        self.records = {}
        
    def add_record(self, record):
        self.records[record.name.value] = record
        
    def delete(self, name):
        if name in self.records:
            del self.records[name]
        else:
            raise KeyError(f"Record '{name}' not found")
        
    def find(self, name):
        if name in self.records:
            return self.records[name]
        else:
            raise KeyError(f"Record '{name}' not found")
        
    def search_records(self, **kwargs):
        results = []
        for record in self.records.values():
            if all(getattr(record, field, None) == value for field, value in kwargs.items()):
                results.append(record)
        return results
    
    def add_birthday(self, name, birthday):
        if name in self.records:
            record = self.find(name)
            record.add_birthday(birthday)
        else:
            raise KeyError(f"Record '{name}' not found")
        
    def get_birthdays_per_week(self):
        birthdays_per_week = []
        today = datetime.today().date()
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for record in self.records.values():
            if record.birthday:
                birthday = record.birthday.value
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                delta_days = (birthday_this_year - today).days

                if 0 <= delta_days <= 7:
                    day_of_week = birthday_this_year.strftime('%A')
                    if day_of_week in ['Saturday', 'Sunday']:
                        day_of_week = 'Monday'

                    birthdays_per_week.append((day_of_week, record.name.value))

        return birthdays_per_week

      
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Contact not found"
        except IndexError:
            return "Invalid command. Please enter a valid command."
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, address_book):
    name, phone = args
    if name in address_book.records:
        raise ValueError("Contact with this name already exists")
    else:
        record = Record(name)
        record.add_phone(phone)
        address_book.add_record(record)
        return "Contact added"

@input_error
def change_contact(args, address_book):
    name, new_phone = args
    if name in address_book.records:
        record = address_book.find(name)
        record.edit_phone(record.phones[0].value, new_phone)
        return "Contact updated"
    else:
        raise KeyError("Contact not found")
    
@input_error
def show_phone(args, address_book):
    name = args[0]
    if name in address_book.records:
        record = address_book.find(name)
        return record.phones[0].value
    else:
        raise KeyError("Contact not found")

  
def show_all(address_book):
    if not address_book.records:
        return "There are no contacts."
    else:
        for record in address_book.records.values():
            print(record)
            

@input_error
def add_birthday(args, address_book):
    name, birthday = args
    try:
        record = address_book.find(name)
        record.add_birthday(birthday)
        return f"Birthday added for {name}"
    except KeyError:
        return f"Contact '{name}' not found"
    except ValueError:
        return "Invalid birthday format"
    
@input_error
def show_birthday(args, address_book):
    name = args[0]
    if name in address_book.records:
        record = address_book.find(name)
        if record.birthday:
            return f"{name}'s birthday: {record.birthday.value}"
        else:
            return f"No birthday set for {name}"
    else:
        raise KeyError("Contact not found")      

def birthdays(address_book):
    return AddressBook.get_birthdays_per_week()

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            show_all(book.records)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))       
        else:
            print("Invalid command.")
            

if __name__ == "__main__":
    main()