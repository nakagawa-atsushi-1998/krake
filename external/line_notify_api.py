import requests

class HttpClient:
    def __init__(self):
        self.URL:str='https://notify-api.line.me/api/notify'
    
    def authenticate(
        self,
        TOKEN:str
    ):
        self.TOKEN = {
            'Authorization':'Bearer '+TOKEN
        }

    def send_message(
        self,
        message:str
    ):
        message_dict = {
            'message': message
        }
        requests.post(
            self.URL,
            headers=self.TOKEN,
            data=message_dict
        )
        result = 'sent message'
        return result
    
    def send_image(
        self,
        message:str,
        image_path:str
    ):
        message_dict = {
            'message': message
        }
        with open(image_path, mode='rb') as binary_file:
            image_dict = {
                'imageFile': binary_file
            }
            requests.post(
                self.URL,
                headers=self.TOKEN,
                params=message_dict,
                files=image_dict
            )
        result = 'sent image'
        return result
