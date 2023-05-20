import requests
import time
import os

class YandexDisk:
    def __init__(self):
        self.token = input("Enter Yandex token:")
        self.count = 5

    def get_json(self):
        URL = 'https://api.vk.com/method/photos.get'
        owner_id = int(input("Enter owner_id:"))
        params = {
            'owner_id': owner_id,
            'access_token': 'vk1.a.-haKCVFit-zFNbRVOEQ21KCZv7Orl2txenO_7Vnw4V672E6ULxstMuZHzq7kJE5gNutd13KnaHtFM5MeuVrHypLVG4776aQVuzhjT2O224oBEBY-tdqy0BzlJ7ET4_zNL64ArLpZ5QfWNkCtID-DfXh8lptDEI7Y-mmJsa-xYGGb8Sw5GxG6CFs07KmxZUxvlCYUceA_c144I3laIH2gcw',
            'v': '5.131',
            'album_id': 'wall',
            'count': self.count,
            'extended': 1,
            'rev': 1
        }
        res = requests.get(URL, params=params)
        if res.status_code == 200:
            print('Request photo successful')
        return res

    def choose_photo(self):
        res = self.get_json()
        item_likes = []
        json_response = []
        count = self.count

        while count:
            item_dict = {}
            item = res.json()['response']['items'][count-1]['id']
            item_sizes = res.json()['response']['items'][count-1]['sizes']
            item_like = res.json()['response']['items'][count-1]['likes']['count']

            max_size = 0
            for type_size in item_sizes:
                item_size = (type_size['height']) * (type_size['width'])
                if item_size > max_size:
                    max_size = item_size
                    max_url = type_size['url']
                    max_like = item_like
                    max_type = type_size['type']

            if max_like in item_likes:
                new_item_name = str(max_like) + '_likes_' + time.strftime("%d-%m-%Y_%H_%M_%S", time.localtime(res.json()['response']['items'][count-1]['date']))
            else:
                new_item_name = str(max_like) + '_likes'

            item_likes.append(item_like)
            count-=1

            item_dict['item_id'] = res.json()['response']['items'][count-1]['id']
            item_dict['item_size'] = max_size
            item_dict['item_size_type'] = max_type
            item_dict['item_url'] = max_url
            item_dict['item like'] = max_like
            item_dict['new_photo_name'] = new_item_name

            json_response.append(item_dict)

            with open('json_data_file.json', 'w') as file:
                file.writelines(str(json_response))

        return json_response

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def get_files_list(self):
        files_url = 'https://cloud-api.yandex.net/v1/disk/resources/files'
        headers = self.get_headers()
        response = requests.get(url=files_url, headers=headers)
        return response.json()

    def get_upload_link(self, disk_file_path):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': disk_file_path, 'overwrite': 'true'}
        response = requests.get(url=upload_url, headers=headers, params=params)
        return response.json()

    def create_path(self):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        # path_name = 'Test_Netology/' + time.strftime("%d-%m-%Y_%H_%M_%S", time.localtime()) + '/'
        path_name = time.strftime("%d-%m-%Y_%H_%M_%S", time.localtime()) + '/'
        response = requests.put(f'{url}?path={path_name}', headers=headers)
        return str(path_name)

    def upload_file(self):
        photo_json = self.choose_photo()
        path_for_upload = self.create_path()

        for i in range(len(photo_json)):
            filename = photo_json[i]['new_photo_name']+ '.jpg'
            response_photo = requests.get(photo_json[i]['item_url'])

            with open(filename, 'wb') as file:
                file.write(response_photo.content)
                disk_file_path = path_for_upload + photo_json[i]['new_photo_name']
                data = self.get_upload_link(disk_file_path)
                url = data.get('href')
                response = requests.put(url=url, data=open(filename, 'rb'))

                if response.status_code == 201:
                    print(f'{i+1} files uploaded ({round(((i+1)*100)/len(photo_json))}%)')

        json_data = 'json_data_file.json'
        disk_json_path = path_for_upload + json_data
        data = self.get_upload_link(disk_json_path)
        url = data.get('href')
        response_json = requests.put(url=url, data=open(json_data, 'rb'))

ya = YandexDisk()
ya.upload_file ()
