import os
import json
import concurrent.futures
from urllib.parse import urlencode
from urllib.request import urlopen
""" 
需要两份相同的文件,
一份用于查找并翻译,
一份用于写入翻译内容.
也就是复制两份pagckage.json
 """
source_file_path = r"C:\package.json"
target_file_path = r"C:\package1.json"
if not os.path.exists(source_file_path):
    print("源文件不存在！")
else:
    with open(source_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)


def translate_text_s(text, target_lang):
    api_url = 'https://translate.googleapis.com/translate_a/single'
    params = {
        'client': 'gtx',
        'dt': 't',
        'sl': 'auto',
        'tl': target_lang,
        'q': text
    }
    full_url = api_url + '?' + urlencode(params)
    try:
        response = urlopen(full_url)
        data = response.read().decode('utf-8')
        translated_text = ''.join(
            item[0] for item in json.loads(data.replace("'", "\u2019"))[0])
        print(translated_text)
        return translated_text
    except Exception as e:
        print(f"翻译错误：{e}")
        return None


translations = {}


def find_keys(data, path=[]):
    if isinstance(data, dict):
        for key, value in data.items():
            if any(keyword in key.lower() for keyword in ['description', 'title', 'deprecationmessage']):
                if isinstance(value, str):
                    translations[tuple(path + [key])] = value
            find_keys(value, path + [key])
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            if isinstance(item, str):
                parent_key = path[-1] if path else None
                if isinstance(data, list) and parent_key and ('description' in parent_key.lower() or 'title' in parent_key.lower()):
                    translations[tuple(path + [idx])] = item
            else:
                find_keys(item, path + [idx])


find_keys(data)
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(lambda text: translate_text_s(
        text, "zh-CN"), translations.values()))
for (path, original_value), translated_value in zip(translations.items(), results):
    if translated_value:
        temp = data
        for key in path[:-1]:
            if isinstance(key, int):
                while len(temp) <= key:
                    temp.append({})
            else:
                if key not in temp:
                    temp[key] = {}
            temp = temp[key]
        temp[path[-1]] = translated_value
with open(target_file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
print(f"翻译完成，结果已写入 {target_file_path} 文件。")
