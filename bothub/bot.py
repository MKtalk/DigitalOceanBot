# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

from bothub_client.bot import BaseBot
from bothub_client.messages import Message

from .doapi import DigitalOcean


class Bot(BaseBot):

    def handle_message(self, event, context):
        message = event.get('content')
        
        if message == '/start':
            self.set_start_message(event)
        elif message == 'Create Droplet':
            self.set_image(event)
        elif message == 'List all Droplets':
            self.list_droplets(event)
        elif message.startswith('/delete '):
            _, droplet_id = message.split()
            self.delete_droplet(droplet_id, event)
        elif message.startswith('/region '):
            _, image = message.split()
            self.set_data('image', image)
            self.set_region(event)
        elif message.startswith('/name '):
            _, region = message.split()
            self.set_data('region', region)
            self.set_name(event)
        # in case of natural language
        else:
            data = self.get_user_data()
            api_key = data.get('api')
            set_name = data.get('set_name')
            if api_key:
                self.verify_api(message, event)
                return
            elif set_name:
                self.create_droplet(message, event)
                return
            self.send_error_message()
  
    def set_start_message(self, event):
        data = self.get_user_data()
        data['api'] = True
        self.set_user_data(data)
        self.send_message('DigitalOcean Droplet 관리를 시작합니다.\n' \
                          'API사용을 위해 Access token을 입력해주세요.')

    def verify_api(self, api_key, event):
        d = DigitalOcean(api_key)
        res = d.get_droplets()
        if res == 401:
            self.send_message('Access token이 올바르지 않습니다.\n'\
                              '다시 입력해주세요.')
        else:
            data = self.get_user_data()
            data['api'] = False
            data['api_key'] = api_key
            self.set_user_data(data)
            message = Message(event).set_text('등록이 완료되었습니다.')
            message.add_keyboard_button('Create Droplet')
            message.add_keyboard_button('List all Droplets')
            self.send_message(message)
        
    def set_data(self, type, value):
        data = self.get_user_data()
        data[type] = value
        self.set_user_data(data)
        
    def set_image(self, event):
        images = self.get_project_data()['image']
        message = Message(event).set_text('Ubuntu 이미지를 선택해주세요.')
        
        for image in images:
            message.add_postback_button(image, '/region {}'.format(image))
        
        self.send_message(message)
        
    def set_region(self, event):
        regions = self.get_project_data()['region']
        message = Message(event).set_text('데이터센터 지역을 선택해주세요.')

        for region in regions:
            message.add_postback_button(region, '/name {}'.format(region))    
        
        self.send_message(message)
    
    def set_name(self, event):
        self.send_message('Hostname을 입력해주세요.')
        data = self.get_user_data()
        data['set_name'] = True
        self.set_user_data(data)

    def create_droplet(self, name, event):
        d = DigitalOcean(self.api_key())
        image = self.get_user_data()['image']
        region = self.get_user_data()['region']
        self.send_message(image, region)
        droplet = d.create_droplet(name, region, image)
        if not droplet:
            self.send_message('Droplet 생성에 실패했습니다.')
            data = self.get_user_data()
            data['set_name'] = False
            self.set_user_data(data)
            return
        
        self.send_message('id: {} name: {} status: {}\n생성이 완료되었습니다.'.format(droplet['droplet']['id'], \
                                                                                    droplet['droplet']['name'], droplet['droplet']['status']))
        data = self.get_user_data()
        data['set_name'] = False
        self.set_user_data(data)

    def list_droplets(self, event):
        d = DigitalOcean(self.api_key())
        droplets = d.simplify(d.get_droplets())
        if not droplets:
            self.send_message('생성된 Droplet이 없습니다.')
            return

        for droplet in droplets:
            msg = Message(event).set_text('id: {} name: {} status: {}'.format(droplet['id'], droplet['name'], droplet['status'])) \
                                .add_quick_reply('Delete', '/delete {}'.format(droplet['id']))
            self.send_message(msg)
      
    def delete_droplet(self, droplet_id, event):
        d = DigitalOcean(self.api_key())
        res = d.delete_droplet(droplet_id)
        if res == 204:
            self.send_message('id: {} Droplet 삭제되었습니다.'.format(droplet_id))
        elif res == 404:
            self.send_message('id: {} Droplet이 존재하지 않습니다.'.format(droplet_id))
        else:
            self.send_message('에러 발생. Droplet 목록을 다시 확인해주세요.')
    
    def api_key(self):
        api_key = self.get_user_data()['api_key']
        return api_key

    def send_error_message(self):
        self.send_message('지원되지 않는 기능입니다.')