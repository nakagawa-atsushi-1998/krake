#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#標準モジュール
import datetime
#外部モジュール
import requests

class Synapse:
    def __init__(self):
        self.__url:str='https://notify-api.line.me/api/notify'
    
    def auth(
        self,
        token:str
    ):
        self.__token = {
            'Authorization': 'Bearer '+token
        }

    def send_message(
        self,
        message:str
    ):
        message_dict = {
            'message': message
        }
        requests.post(
            self.__url,
            headers=self.__token,
            data=message_dict
        )
        result = 'sent message.'
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
                self.__url,
                headers=self.__token,
                params=message_dict,
                files=image_dict
            )
        result = 'sent image.'
        return result

