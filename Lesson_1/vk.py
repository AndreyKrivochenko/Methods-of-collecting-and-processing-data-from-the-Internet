import json
import requests


ACCESS_TOKEN = '1208470b5ecdc6aa7618343ac234505fb8761624f7b4b00577995d151dd8e58360f4a725be02a211766bb'

def get_from_vk(url:str, param:dict={}) -> dict:

    params = {
        'v': '5.131',
        'access_token': ACCESS_TOKEN
    }

    params.update(param)
    response = requests.get(url=url, params=params)

    return response.json()


j_user_data = get_from_vk(url='https://api.vk.com/method/groups.get')

group_list = j_user_data.get('response').get('items')
group_list = ','.join(map(str, group_list))

j_user_groups = get_from_vk(
    url='https://api.vk.com/method/groups.getById',
    param={'group_ids': group_list}
)

with open('groups.json', 'w', encoding='utf-8') as f:
    json.dump(j_user_groups, f)

print('Группы пользователя:', end='\n\n')
for i, group in enumerate(j_user_groups.get('response')):
    print(f'{i + 1}. {group["name"]}')
