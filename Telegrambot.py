import json
import requests

def get_updates(api_url, offset = None):
    updates_url = api_url + 'getUpdates'
    if offset:
        updates_url = f'{updates_url}?offset={offset}'
    
    get_url = requests.get(updates_url).content
    updates_json =json.loads(get_url)
    return updates_json

def offset(updates):
    update_id = []
    for update in updates['result']:
        update_id.append(update['update_id'])
    return max(update_id)+1

def send_message(api_url, telegramargs, args):
    params = {}
    params['chat_id'] = telegramargs.get('chatId')
    params['text'] = args.get('text')
    msg_url = api_url+f'sendMessage'
    requests.post(msg_url, params= params)

def get_fileid(api_url, telegramargs, getAllfile = False):
    args = {}
    if telegramargs.get('photo'):
        args['text'] = 'photo id: ' + telegramargs.get('photo')[0].get('file_id')

    if telegramargs.get('video'):
        args['text'] = 'video id: ' + telegramargs.get('video').get('file_id')

    if telegramargs.get('voice'):
        args['text'] = 'voice id: ' + telegramargs.get('voice').get('file_id')

    if telegramargs.get('document'):
        args['text'] = 'file id: ' + telegramargs.get('document').get('file_id')

    if telegramargs.get('audio'):
        args['text'] = 'audio id: ' + telegramargs.get('audio').get('file_id')

    if getAllfile:
        if args.get('text'):
            send_message(api_url, telegramargs,args)

    if telegramargs.get('caption'):
        if '/get_fileid' in telegramargs.get('caption'):
            send_message(api_url, telegramargs, args)

    
def send_video(api_url, telegramargs, args):
    params = {}
    params['video'] = args.get('video')
    params['chat_id'] = telegramargs.get('chatId')
    params['caption'] = args.get('caption')
    video_url = api_url+f'sendVideo'
    requests.post(video_url, params= params)


def send_photo(api_url, telegramargs, args):
    params = {}
    params['photo'] = args.get('photo')
    params['caption'] = args.get('caption')
    params['chat_id'] = telegramargs.get('chatId')
    photo_url = api_url+f'sendPhoto'
    requests.post(photo_url, params= params)

def send_file(api_url, telegramargs, args):
    params = {}
    params['document'] = args.get('document')
    params['caption'] = args.get('caption')
    params['chat_id'] = telegramargs.get('chatId')
    file_url = api_url+f'sendDocument'
    requests.post(file_url, params= params)

def send_media_group(api_url, telegramargs, args):
    params = {}
    params['media'] = json.dumps(args.get('media'))
    params['chat_id'] = telegramargs.get('chatId')
    media_url = api_url+f'sendMediaGroup'
    requests.post(media_url, params= params)



def response(api_url, list, telegramargs):
    message = ''
    if telegramargs.get('text'):
        message = telegramargs.get('text')
    if telegramargs.get('caption'):
        message = telegramargs.get('caption')
    for dict in list:
        if dict['name'] in message:
            dict['function'](api_url, telegramargs, dict['args'])

def responses(api_url, list, updates, getAllfiles = False):
    for update in updates['result']:
        telegramargs = {}
        telegramargs['chatId'] = update.get('message').get('chat').get('id')
        telegramargs['text'] = update.get('message').get('text')
        telegramargs['caption'] = update.get('message').get('caption')
        telegramargs['photo'] = update.get('message').get('photo')
        telegramargs['video'] = update.get('message').get('video')
        telegramargs['voice'] = update.get('message').get('voice')
        telegramargs['audio'] = update.get('message').get('audio')
        telegramargs['document'] = update.get('message').get('document')

        get_fileid(api_url, telegramargs, getAllfiles)
        response(api_url, list, telegramargs)
    


def main(token, list):
    offsets = None
    api_url = f'https://api.telegram.org/bot{token}/'
    getAllfiles = False
    while True:
        updates = get_updates(api_url, offsets)
        if updates['ok'] != False:
            if len(updates['result']) > 0:
                for update in updates.get('result'):
                    if update.get('message').get('text'):
                        if '/get_all_fileid' in update.get('message').get('text'):
                            getAllfiles = True
                        elif 'get_no_fileid' in update.get('message').get('text'):
                            getAllfiles = False
                offsets = offset(updates)
                responses(api_url, list, updates, getAllfiles)
