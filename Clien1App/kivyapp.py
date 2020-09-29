import json
from pprint import pprint

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
import socket_client
from loginapp import Login
from wsrequestapp import WSRequests

kivy.require("1.11.1")




ID_BY_LABEL = dict()

class ScrollableLabel(ScrollView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols=1, size_hint_y=None)


        self.chat_message_box = Label(size_hint_y=None, markup=True)
        self.scroll_to_point = Label()
        self.layout.add_widget(self.chat_message_box)
        self.layout.add_widget(self.scroll_to_point)

        self.add_widget(self.layout)

    def update_chat_message_box(self, message):
        self.chat_message_box.text += '\n' + message


        # self.chat_message_box.texture_size[1] += 20

        self.layout.height = self.chat_message_box.texture_size[1] + 20
        self.chat_message_box.height = self.chat_message_box.texture_size[1]
        self.chat_message_box.text_size = (self.chat_message_box.width*0.98, None)

        self.scroll_to(self.scroll_to_point)

    def update_chat_message_box_layout(self, _=None):

        self.layout.height = self.chat_message_box.texture_size[1] + 15
        self.chat_message_box.height = self.chat_message_box.texture_size[1]
        self.chat_message_box.text_size = (self.chat_message_box.width * 0.98, None)

class ChatPage(GridLayout):

    def __init__(self, chat_id, **kwargs):

        super().__init__(**kwargs)
        self.chat_id = chat_id
        self.cols = 1
        self.rows = 5
        self.get_chat_message()
        self.get_user_data()
        ws_token = WSRequests()
        self.token = ws_token.load_token()

        self.back_button = Button(text="Вергуться к списку чатов", size=(200, 20))
        self.back_button.bind(on_press=self.back_page)
        self.add_widget(self.back_button)

        self.title_chat = Label(text=self.title)

        self.add_widget(self.title_chat)

        self.participants = Label(text=f'Учасники чата: {self.get_participants()}')
        self.add_widget(self.participants)

        self.message_box = ScrollableLabel(height=Window.size[1]*0.7, size_hint_y=None)
        self.add_widget(self.message_box)

        self.new_message = TextInput(width=Window.size[0]*0.8, size_hint_x=None, multiline=False)

        self.send = Button(text="Send")
        self.send.bind(on_press=self.send_message)

        bottom_line = GridLayout(cols=2)
        bottom_line.add_widget(self.new_message)
        bottom_line.add_widget(self.send)
        self.add_widget(bottom_line)



        Clock.schedule_once(self.ccc, 0)

        Clock.schedule_once(self.focus_text_input, 1)

        socket_client.start_listening(self.incoming_message, self.chat_id, self.token, self.user_name)

        self.bind(size=self.adjust_fields)
        Clock.schedule_once(self.adjust_fields1, 0.01)
        Window.bind(on_key_down=self.on_key_down)

    def adjust_fields(self, *_):

        if Window.size[1] * 0.1 < 50:
            new_height = Window.size[1] - 50
        else:
            new_height = Window.size[1] * 0.8
        self.message_box.height = new_height

        if Window.size[0] * 0.2 < 160:
            new_width = Window.size[0] - 160
        else:
            new_width = Window.size[0] * 0.8
        self.new_message.width = new_width
        Clock.schedule_once(self.message_box.update_chat_message_box_layout, 0.01)

    def adjust_fields1(self, *_):


        new_height = Window.size[1] * 0.7
        self.message_box.height = new_height

        new_width = Window.size[0] * 0.8
        self.new_message.width = new_width
        Clock.schedule_once(self.message_box.update_chat_message_box_layout, 0.01)

    def back_page(self, _):
        mess_app.create_chats_page()
        mess_app.screen_manager.current = 'Chats'


    def ccc(self, _):
        self.fill_in_message_box()

    def fill_in_message_box(self):
        for mess in self.message_list:
            message = mess['content']
            username = mess['contact']['user']['username']
            # self.incoming_message(username, message)

            self.incoming_message(username, message)



    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40:
            self.send_message(None)

    def send_message(self, _):
        if self.new_message.text:
            message = self.new_message.text
            data = socket_client.send(self.chat_id, message, self.token)
            print(data)

            self.message_box.update_chat_message_box(f"[color=dd2020]{self.user_name}[/color] > {message}")
        self.new_message.text = ''

        # self.fill_in_message_box()


        Clock.schedule_once(self.focus_text_input, 1)

        # socket_client.start_listening(self.incoming_message)

    def incoming_message(self, username, message):
        # Update chat history with username and message, green color for username
        if username == self.user_name:
            color = 'dd2020'
        else:
            color = '20dd20'
        self.message_box.update_chat_message_box(f'[color={color}]{username}[/color] > {message}')

    def focus_text_input(self, _):
        self.new_message.focus = True


    def get_participants(self):
        result = []
        for user in self.chat_participants:
            result.append(user['user']['username'])
        return ', '.join(result)
    # def get_chat_id(self, chat):
    #     self.chat_id_label.text = chat.id
    #     self.chat_id = chat.id

    def get_user_data(self):
        with open('data.json') as json_file:
            data = json.load(json_file)
            self.user_id = data['id']
            self.user_name = data['username']

    def get_chat_message(self):
        ws_req = WSRequests()
        print(self.chat_id)
        user_response = ws_req.get_ws_data(

            action_url=f'api/v1/chat/?chat={self.chat_id}',
            params={'username': '123'}
        )
        if user_response.resp_status == 403:
            return False, 'В доступе отказано'
        else:
            # self.chat_id_list = list()
            # self.title_list = list()
            self.message_list = user_response.result[0]['messages']
            self.chat_participants = user_response.result[0]['participants']
            self.title = user_response.result[0]['title']

            # for line in user_response.result:
            #     # self.chat_id_list.append(line.get('id'))
            #     # self.title_list.append(line.get('title'))
            #     print(line)
            #     print()


class ChatsMenuPage(GridLayout):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        print('chats page')
        self.cols = 1
        self.padding = 30
        # self.size_hint_y = (None)
        self.add_widget(Label(text='Chats', height=40))

        self.get_chats_list()
        self.get_user_data()
        mess_app.title = self.user_name
        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=30)
        # Make sure the height is such that there is something to scroll.
        self.layout.bind(minimum_height=self.layout.setter('height'))
        # self.layout.add_widget(Label(text='Chats', height=40))
        for i, title in enumerate(self.title_list):
            self.button = Button(text=title, size_hint_y=None, height=40)
            self.button.id = str(self.chat_id_list[i])
            self.button.bind(on_press=self.button_click)

            ID_BY_LABEL[self.button.id] = self.button

            self.layout.add_widget(self.button)
        self.scroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.scroll.add_widget(self.layout)

        self.add_widget(self.scroll)


    def button_click(self, chat_id):
        mess_app.create_chat_page(chat_id.id)
        # mess_app.chat_page.get_chat_id(chat_id)
        mess_app.screen_manager.current = 'Chat'

    def get_chats_list(self):

        ws_req = WSRequests()
        user_response = ws_req.get_ws_data(
            action_url='api/v1/chats/',
            params={'username': '123'}
        )
        if user_response.resp_status == 403:
            return False, 'В доступе отказано'
        else:
            self.chat_id_list = list()
            self.title_list = list()
            for line in user_response.result:
                self.chat_id_list.append(line.get('id'))
                self.title_list.append(line.get('title'))
            # if user_response.result.get('id'):
            #     return True, 'Успешная авторизация'
            # else:
            #     return False,

    def get_user_data(self):
        with open('data.json') as json_file:
            data = json.load(json_file)
            self.user_id = data['id']
            self.user_name = data['username']

def token_true():
    ws_req = WSRequests()
    user_response = ws_req.get_ws_data(
        action_url='auth-djoser/users/me/',
        params={'username': '123'}
    )
    if user_response.resp_status == 403:
        return False, 'В доступе отказано'
    else:
        print(user_response.result)
        if user_response.result.get('id'):
            return True, 'Успешная авторизация'
        else:
            return False,



class LoginPage(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2

        self.add_widget(Label(text="Username"))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)

        self.add_widget(Label(text="Password"))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)

        self.login = Button(text="Log in")
        self.login.bind(on_press=self.log_in_button)
        self.status_text = Label(text='')
        self.add_widget(self.status_text)
        self.add_widget(self.login)

    def log_in_button(self, instance):
        self.status_text.text = ''
        username = self.username.text
        password = self.password.text
        log_in = Login()
        status, message = log_in.do_login(username, password)
        if status:
            mess_app.create_chats_page()
            mess_app.screen_manager.current = 'Chats'
            # app = App.get_running_app()
            # app.root_window.remove_widget(app.root)
            # chats_window = ChatsPage()
            # app.root_window.add_widget(chats_window)
        else:
            self.status_text.text = message


class MessengerApp(App):

    def build(self):
        self.screen_manager = ScreenManager()

        self.login_page = LoginPage()
        screen = Screen(name='Login')
        screen.add_widget(self.login_page)
        self.screen_manager.add_widget(screen)

        if token_true()[0]:
            self.create_chats_page()
            self.screen_manager.current = 'Chats'

        return self.screen_manager
        # if token_true()[0]:
        #     return ChatsPage()
        # return LoginPage()

    def create_chats_page(self):
        try:
            self.screen_manager.clear_widgets()
        except:
            pass
        self.chats_page = ChatsMenuPage()
        screen = Screen(name='Chats')
        screen.add_widget(self.chats_page)
        self.screen_manager.add_widget(screen)

    def create_chat_page(self, chat_id):
        try:
            self.screen_manager.clear_widgets()
        except:
            pass
        self.chat_page = ChatPage(chat_id=chat_id)
        print('chat_id =', chat_id)
        screen = Screen(name='Chat')
        screen.add_widget(self.chat_page)
        self.screen_manager.add_widget(screen)


if __name__ == "__main__":
    mess_app = MessengerApp()
    mess_app.run()
