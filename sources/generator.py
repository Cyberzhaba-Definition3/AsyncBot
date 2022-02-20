from PIL import Image
import asyncio
import config
import json
import os
import random
import threading
import messages
import zipfile


class Generator:
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.loop = asyncio.get_event_loop()

        self.threads = []
        for i in range(config.workers):
            t = threading.Thread(target=self.target)
            t.start()

    def target(self):
        while True:
            if len(self.queue) == 0:
                continue

            task = self.queue.pop(0)
            self.loop.create_task(self.bot.send_message(
                task["user_id"], messages.processing_started))

            msg = task['msg']
            filename = f'temp/{msg.document.file_id}.zip'
            zip = filename[5:]
            with zipfile.ZipFile(f'temp/{zip}', 'r') as zip_ref:
                zip_ref.extractall(f'unzipped/{zip[:-4]}')
            first_dir = f'unzipped/{zip[:-4]}'
            folder_inside = os.listdir(first_dir)
            result = os.listdir(f'{first_dir}/{folder_inside[0]}')
            folder = f'{first_dir}/{folder_inside[0]}'
            if 'template.json' in result and len(result) > 1:
                self.loop.create_task(self.bot.send_message(
                    task["user_id"], messages.archive_checked))
                os.remove(f'temp/{zip}')

                # generator.py
                number_of_all = 10000

                all_info = json.load(open(f"{folder}/template.json", "r"))
                number_of_all, all_info = all_info["num_of_all"], all_info["generation"]
                number_of_all = 50000
                new_info = [[] for _ in range(len(all_info.keys()))]
                counter = 0
                for key, layer in all_info.items():
                    counter_for_layer = 0
                    for item in layer:
                        if counter_for_layer == 0:
                            diapason = f'1-{int(100*item["rarity"])}'
                            new_info[counter].append(
                                {diapason: item['name']})
                            prev = int(float(diapason.split('-')[1]))
                        else:
                            diapason = f'{prev+1}-{prev+int(100*item["rarity"])}'
                            new_info[counter].append(
                                {diapason: item['name']})
                            prev = int(float(diapason.split('-')[1]))
                        counter_for_layer += 1
                    counter += 1

                print(new_info)
                combinations = []
                counter = 0
                for _ in range(number_of_all):
                    output = []
                    for layer in new_info:
                        num = random.randint(1, 100)
                        for item in layer:
                            prob = list(item.keys())[0].split('-')
                            if int(prob[0]) <= num <= int(prob[1]):
                                counter += 1
                                output.append(list(item.values())[0])
                                break
                    output = ':'.join(output)
                    combinations.append(output)

                def migrate(back, front):
                    back = back.copy()
                    front = front.copy()

                    back.paste(front, (0, 0), front)
                    return back.copy()

                def clear_all(l):
                    try:
                        os.mkdir(f'export/{filename}')
                    except Exception as e:
                        print(e)
                    for photo in l:
                        try:
                            photo.save(
                                f'export/{filename}/{random.randint(0,10000000)}.png')
                        except:
                            photo.save(
                                f'export/{filename}/{random.randint(0,10000000)}.png')
                    return []

                all_done = []
                counter = 0  # just to see progress

                for item in combinations:
                    print(f'progress ... {counter/60}%')

                    if counter % 10 == 0:
                        all_done = clear_all(all_done)
                        print('all_done saved and cleared')

                    layers = item.split(':')
                    for ind in range(len(layers)-1):
                        if ind == 0:
                            lay_1 = Image.open(f'{folder}/{layers[ind]}')
                            lay_2 = Image.open(f'{folder}/{layers[ind+1]}')
                            result = migrate(lay_1, lay_2)
                        else:
                            lay_1 = result.copy()
                            lay_2 = Image.open(f'{folder}/{layers[ind+1]}')
                            result = migrate(lay_1, lay_2)

                    all_done.append(result)
                    counter += 1

                print(len(all_done))
            else:
                self.loop.create_task(self.bot.send_message(
                    task["user_id"], messages.bad_archive))
