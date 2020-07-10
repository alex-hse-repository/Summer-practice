import base64

def GetSnippet(msg):
    return msg['snippet']

def GetLabel(msg,user_label_ids):
    '''Получает лэйбл пиьма, подразумевается что он один(можно в последствии сделать несколько)'''
    for label_id in user_label_ids:
        if(label_id in msg['labelIds']):
            return label_id
    return None

def GetID(msg):
    return msg['id']

def GetSubject(msg):
    headers = msg['payload']['headers']
    subject = None 
    for header in headers:
        if(header['name'] == 'Subject'):
            subject = header['value']
    return subject        

def getSender(msg):
    headers = msg['payload']['headers']
    sender = None 
    for header in headers:
        if(header['name'] == 'From'):
            sender = header['value']
    return sender 
               
def pack_message(msg,user_label_ids):
    id = GetID(msg)
    label = GetLabel(msg,user_label_ids)
    snippet = GetSnippet(msg)
    sender = getSender(msg)
    subject = GetSubject(msg)
    parsed_msg = parse_msg(msg)
    msg_data = {'id' : id,'snippet' : snippet,'label':label,
                'sender':sender,'subject':subject,'text':parsed_msg},
    
    return msg_data

def parse_msg(msg):
    content = []
    payload = msg['payload']
    if(payload['mimeType']=='multipart/alternative'):
        for part in payload['parts']:
            if(part['mimeType'] == 'text/plain'):
                content.append(data_encoder(part['body']['data']))      
    else:
        if(payload['mimeType']=='text/plain'):
            content.append(data_encoder(payload['body']['data']))
    return ''.join(content)
    
def data_encoder(text):
    #TODO:посмотреть что там с кодировкой
    message = base64.urlsafe_b64decode(text)
    message = str(message, 'utf-8')
    return message


def CreateMsgLabels(msg_ids,label_ids):
  """Create object to update labels.
  Returns:
    A label update object.
  """
  return {'removeLabelIds': [], 'addLabelIds': label_ids,'ids':msg_ids}


