import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen

class DigitalOcean(object):
    base_url = 'https://api.digitalocean.com/v2/droplets'

    def __init__(self, api_key):
        self.headers = {
            'content-type': 'application/json',
            'authorization': 'Bearer {}'.format(api_key)
        }

    def get_droplets(self):
        req = Request(url='{}?page=1&per_page=5'.format(self.base_url), headers = self.headers)
        try:
            with urlopen(req) as response:
                return json.loads(response.read().decode('utf8'))
        except HTTPError as e:
            return e.code
        
    def delete_droplet(self, droplet_id):
        req = Request(url='{}/{}'.format(self.base_url, droplet_id), headers=self.headers, method='DELETE')
        try:
            with urlopen(req) as response:
                return response.getcode()
        except HTTPError as e:
            return e.code
    
    def create_droplet(self, name, region, image):
        values = {'name': name, 'region': region, 'size': '512mb', 'image': 'ubuntu-{}'.format(image)}
        data = json.dumps(values).encode('utf8')
        req = Request(self.base_url, data=data, headers=self.headers)

        with urlopen(req) as response:
            return json.loads(response.read().decode('utf8'))

    def simplify(self, result):
        return [
            {
                'id': entry.get('id'),
                'name': entry.get('name'),
                'status': entry.get('status')
            }
            for entry in result.get('droplets')
        ]
