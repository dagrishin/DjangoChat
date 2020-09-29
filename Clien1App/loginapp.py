import json

import requests

from wsrequestapp import WSRequests


class Login:
    ws_url = 'http://localhost:8000/auth-djoser/token/login/'

    def do_login(self, login, password):
        headers = {'content-type': 'application/json'}
        params = {
            'username': login,
            'password': password
        }
        response = requests.post(url=self.ws_url, data=json.dumps(params), headers=headers)
        if response.status_code == 200:
            token_dict = json.loads(response.text)
            print(token_dict)
            self.save_token(str=token_dict['auth_token'])
            ws_req = WSRequests()
            user_response = ws_req.get_ws_data(
                action_url='auth-djoser/users/me/',
                params={'username': login}
            )
            if user_response.resp_status == 403:
                return False, 'В доступе отказано'
            else:
                if user_response.result.get('id'):
                    self.save_user_data(user_response.result)
                    return True, 'Успешная авторизация'
        else:
            return False, 'Неправильное имя пользователя или пароль'

    def save_token(self, str):
        with open('token', 'w') as outfile:
            outfile.write(str)

    def save_user_data(self, result):
        with open('data.json', 'w') as outfile:
            json.dump(result, outfile)