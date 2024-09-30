#-*- coding: utf-8 -*-
import re
import json
from hashlib import sha256
import mail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def send_email(getter, subject, message):
    msg = MIMEMultipart()
    msg['From'] = mail.login
    msg['To'] = getter
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    server.ehlo(mail.login)
    server.login(mail.login, mail.password)
    server.auth_plain()
    server.send_message(msg)
    server.quit()


def hashing(value):
    return sha256(value.encode('utf-8')).hexdigest()


def complement_phone_number(phone_number):
    preform = '+7-($)-$-$-$'
    lst = []
    substr = ""
    cnts = (1, 3, 3, 2, 2)
    cnt = 0
    i = 0
    for ch in phone_number:
        if ch.isdigit():
            substr += ch
            cnt += 1
            if cnt == cnts[i]:
                lst.append(substr)
                substr = ""
                cnt = 0
                i += 1
    lst = lst[1:]
    for el in lst:
        preform = preform.replace('$', el, 1)
    return preform


class User:
    __regular = {
        'name': r'[^0-9]+',
        'second_name': r'[^0-9]+',
        'third_name': r'[^0-9]+',
        'phone_number': r'\s*(\+7|8)\s*\-?\s*\(?\d{3}\)?\s*\-?\s*\d{3}\s*\-?\s*\d{2}\s*\-?\s*\d{2}\s*',
        'email': r'\w+@\w+\..+',
        'login': r'\w+',
        'password': r'(?=.*.{8}.*)(?=.*[a-z].*)(?=.*[A-Z].*)(?=.*\d.*)(?=.*[\s!\"#$%&\'\(\)*+,-./:;<=>?@\[\\\]\^_`{|}~].*).*'
    }

    def __init__(self):
        self.__name = None
        self.__second_name = None
        self.__third_name = None
        self.__phone_number = None
        self.__email = None
        self.__login = None
        self.__password = None

    def set_second_name(self, input_value):
        if status := self.__check_full_str('second_name', input_value):
            self.__second_name = input_value.capitalize()
        return status

    def set_name(self, input_value):
        if status := self.__check_full_str('name', input_value):
            self.__name = input_value.capitalize()
        return status

    def set_third_name(self, input_value):
        if status := self.__check_full_str('third_name', input_value):
            self.__third_name = input_value.capitalize()
        return status

    def set_phone_number(self, input_value):
        if status := self.__check_full_str('phone_number', input_value):
            self.__phone_number = complement_phone_number(input_value)
        return status

    def set_email(self, input_value):
        if status := self.__check_full_str('email', input_value):
            self.__email = input_value
        return status

    def set_login(self, input_value):
        if status := self.__check_full_str('login', input_value):
            self.__login = input_value
        return status

    def set_password(self, input_value):
        if status := self.__check_full_str('password', input_value):
            self.__password = hashing(input_value)
        return status

    def __check_full_str(self, field, input_value):
        return True if (re.fullmatch(User.__regular[field], input_value) is not None) else False

    def to_dict(self):
        user_dict = {
            'second_name': self.__second_name,
            'name': self.__name,
            'third_name': self.__third_name,
            'phone_number': self.__phone_number,
            'email': self.__email,
            'login': self.__login,
            'password': self.__password
        }
        return user_dict

    def copy_field(self, user_dict):
        self.__second_name = user_dict['second_name']
        self.__name = user_dict['name']
        self.__third_name = user_dict['third_name']
        self.__phone_number = user_dict['phone_number']
        self.__email = user_dict['email']
        self.__login = user_dict['login']
        self.__password = user_dict['password']

    def take_setter(self, field):
        match field:
            case 'name': return self.set_name
            case 'second_name': return self.set_second_name
            case 'third_name': return self.set_third_name
            case 'phone_number': return self.set_phone_number
            case 'email': return self.set_email
            case 'login': return self.set_login
            case 'password': return self.set_password


class App:
    __step_back = 'cd..'

    __output_for_user = {
        'second_name': ('введите фамилию: ', 'фамилия не должна содержать цифр или быть пустой строкой \nвведите фамилию: ',),
        'name': ('введите имя: ', 'имя не должно содержать цифр или быть пустой строкой \nвведите имя: '),
        'third_name': ('введите отчество: ', 'отчество не должно содержать цифр или быть пустой строкой \nвведите отчество: '),
        'phone_number': ('введите номер телефона: ', 'некорректный ввод \nвведите номер телефона: '),
        'email': ('введите email: ', 'некоректный ввод \nвведите email: '),
        'login': ('введите логин: ', 'некоректный ввод \nвведите логин: '),
        'password': ('введите пароль: ', 'пароль должен содержать не менее 8 символов, как минимум одну заглавную букву,\n'
                            'одну строчную, одну цифру, один специальный символ \nвведите пароль: ')
    }

    def __init__(self, file_name):
        self.__file_name = file_name
        with open(file_name, 'r') as file:
            self.__data = json.load(file)

    def __check_user_field_loop(self, user, field):
        again = False
        while True:
            input_value = input(App.__output_for_user[field][again])
            if input_value == App.__step_back:
                return False
            if user.take_setter(field)(input_value):
                return True
            again = True

    def __set_user(self, user):
        for field in ('second_name', 'name', 'third_name', 'phone_number', 'email', 'login', 'password'):
            keep_on = self.__check_user_field_loop(user, field)
            if not keep_on: return False
        return True

    def __str__(self):
        is_empty = True
        i = 1
        str_users = 'Список пользователей:\n'
        for user in self.__data:
            is_empty = False
            str_users += f'#{i}\n'
            i += 1
            for key, value in user.items():
                str_users += f'{key}: {value}\n'
            str_users += '\n'
            str_users = str_users[:-1]
        if is_empty:
            return 'список пользователей пуст\n'
        return str_users

    def __add_user(self):
        print('*Добавление пользователя')
        user = User()
        status = self.__set_user(user)
        if status:
            self.__data += [user.to_dict()]
            print('пользователь добавлен')
        print()

    def __search(self, *args):
        if len(args) == 2:
            for i in range(len(self.__data)):
                if self.__data[i][args[0]] == args[1]:
                    return i
        elif len(args) == 4:
            for i in range(len(self.__data)):
                if self.__data[i][args[0]] == args[1] and self.__data[i][args[2]] == args[3]:
                    return i
        print('пользователь не найден')
        return None

    def __choice_and_multiple_search(self):
        while True:
            print('Поиск:'
                  '\n   i.	по фамилии-имени'
                  '\n   ii.	по логину'
                  '\n   iii. по номеру телефона'
                  '\nШаг назад (работает во всей подпрограмме): "cd.."')
            key = input('\nвведите подпункт: ')
            match key:
                case 'i':
                    while True:
                        second_name = input('введите фамилию: ')
                        if second_name == App.__step_back:
                            print()
                            break
                        name = input('введите имя: ')
                        if name == App.__step_back:
                            print()
                            break
                        index = self.__search('second_name', second_name.capitalize(), 'name', name.capitalize())
                        if index is not None: return index
                case 'ii':
                    while True:
                        login = input('введите логин: ')
                        if login == App.__step_back:
                            print()
                            break
                        index = self.__search('login', login)
                        if index is not None: return index
                case 'iii':
                    while True:
                        phone_number = input('введите номер телефона: ')
                        if phone_number == App.__step_back:
                            print()
                            break
                        index = self.__search('phone_number', (complement_phone_number(phone_number)))
                        if index is not None: return index
                case App.__step_back: return None
                case _: print(f'\n"{key}" - неизвестная команда\n')

    def __check_password(self, index):
        while True:
            password = input('введите пароль: ')
            if password == App.__step_back: return False
            if hashing(password) == self.__data[index]['password']: return True
            print('неверный пароль')

    def __function_extension(self, func, title):
        print(title)
        keep_up = True
        while keep_up:
            index = self.__choice_and_multiple_search()
            if index is not None:
                if self.__check_password(index):
                    func(index)
                    keep_up = False
            else: keep_up = False
        print()

    def __delete_user(self):
        def func(index):
            self.__data.pop(index)
            print('пользователь удалён')
        self.__function_extension(func, '*Удаление пользователя')

    def __send_email(self):
        def func(index):
            subject = input('введите тему письма: ')
            if subject == App.__step_back: return None
            message = input('введите текст письма: ')
            if message == App.__step_back: return None
            try:
                send_email(self.__data[index]['email'], subject, message)
                print('сообщение отправлено')
            except:
                print('ошибка, сообщение не было отправлено')
        self.__function_extension(func, '*Отправка сообщения на e-mail пользователя')

    def __change_user(self):
        def func(index):
            user = User()
            user.copy_field(self.__data[index])
            while True:
                print('\nИзменить:\n1. имя\n2. фамилию\n3. отчество\n4. номер телефона'
                      '\n5. адрес эл.почты\n6. логин\n7. пароль\nШаг назад (работает во всей подпрограмме): "cd.."')
                is_change = False
                key = input('\nвведите подпункт: ')
                match key:
                    case '1': is_change = self.__check_user_field_loop(user, 'name')
                    case '2': is_change = self.__check_user_field_loop(user, 'second_name')
                    case '3': is_change = self.__check_user_field_loop(user, 'third_name')
                    case '4': is_change = self.__check_user_field_loop(user, 'phone_number')
                    case '5': is_change = self.__check_user_field_loop(user, 'email')
                    case '6': is_change = self.__check_user_field_loop(user, 'login')
                    case '7': is_change = self.__check_user_field_loop(user, 'password')
                    case App.__step_back: break
                    case _:
                        is_change = False
                        print(f'\n"{key}" - неизвестная команда\n')
                if is_change:
                    print('данные пользователя изменены')
                    self.__data[index] = user.to_dict()
        self.__function_extension(func, '*Изменение информации о пользователе')

    def __sort_data(self):
        print('*Сортировка')
        while True:
            print('Cортировать по:\n1. имени\n2. фамилии\n3. отчеству\n4. номеру телефона\n5. адресу электронной почты'
                  '\n6. логину\nШаг назад (работает во всей подпрограмме): "cd.."')
            valid_status = True
            key = input('\nвведите подпункт: ')
            match key:
                case '1': self.__data = sorted(self.__data, key=lambda user_map: user_map['name'])
                case '2': self.__data = sorted(self.__data, key=lambda user_map: user_map['second_name'])
                case '3': self.__data = sorted(self.__data, key=lambda user_map: user_map['third_name'])
                case '4': self.__data = sorted(self.__data, key=lambda user_map: user_map['phone_number'])
                case '5': self.__data = sorted(self.__data, key=lambda user_map: user_map['email'])
                case '6': self.__data = sorted(self.__data, key=lambda user_map: user_map['login'])
                case App.__step_back:
                    print()
                    break
                case _:
                    valid_status = False
                    print(f'\n"{key}" - неизвестная команда\n')
            if valid_status: print('данные отсортированы\n')

    def __save_data(self):
        with open(self.__file_name, 'w') as file:
            json.dump(self.__data, file, ensure_ascii=False, indent=4)
            print('данные сохранены\n')

    @staticmethod
    def draw_menu():
        print('a. Посмотреть список пользователей'
        '\nb. Добавить пользователя'
        '\nc. Удалить пользователя'
        '\n   i.	По фамилии-имени'
        '\n   ii.	По логину'
        '\n   iii.    По номеру телефона'
        '\nd. Изменить пользователя'
        '\n   i.	По фамилии-имени'
        '\n   ii.	По логину'
        '\n   iii.	По номеру телефона'
        '\ne. Сохранить изменения в файл'
        '\nf. Отправить сообщение на e-mail пользователя'
        '\n   i.	По фамилии-имени'
        '\n   ii.	По логину'
        '\n   iii.	По номеру телефона'
        '\ng. Отсортировать по выбранному полю'
        '\nh. Выход'
        '\ni. Меню'
        f'\nКоманда для возвращения на предыдущий шаг: "{App.__step_back}"\n')

    def main_process(self):
        print('*Главное меню\nДля просмотра Меню введите "i"')
        key = input('выберете пункт: ')
        print()
        match key:
            case 'a': print(self)
            case 'b': self.__add_user()
            case 'c': self.__delete_user()
            case 'd': self.__change_user()
            case 'e': self.__save_data()
            case 'f': self.__send_email()
            case 'g': self.__sort_data()
            case 'h': return False
            case 'i': App.draw_menu()
            case _: print(f'"{key}" - неизвестная команда\n')
        return True


if __name__ == '__main__':
    file_name = 'users.json'
    app = App(file_name)
    is_running = True
    app.draw_menu()
    while is_running:
        is_running = app.main_process()
    print('Конец выполнения программы')
