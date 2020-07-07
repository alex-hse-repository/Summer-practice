def GetSnippet(msg):
    return msg['snippet']

def GetLabels(msg):
    return msg['labelIds']

def GetID(msg):
    return msg['id']

def GetSubject(msg):
    headers = msg['payload']['headers']
    subject = 'Unknon'# Specail constant 
    for header in headers:
        if(header['name'] == 'Subject'):
            subject = header['value']
    return subject        

def getSender(msg):
    headers = msg['payload']['headers']
    sender = 'Unknon'# Specail constant 
    for header in headers:
        if(header['name'] == 'From'):
            sender = header['value']
    return sender 
               
def pack_message(msg,miem_msg):
    id = GetID(msg)
    labels = GetLabels(msg)
    snippet = GetSnippet(msg)
    sender = getSender(msg)
    subject = GetSubject(msg)
    raw = miem_msg
    msg_data = {'id' : id,'snippet' : snippet,'labels':labels,'sender':sender,'subject':subject,'raw':raw}
    return msg_data

def parse_msg(msg):
    '''Return text(plain and html) content of msg'''
    
    content = {'text':[],'html':[]}
    for part in msg.walk():
        if(part.is_multipart()):
            continue
        else:
            content_type = part.get_content_type()
            text = part.get_payload()
            if(content_type == 'text/plain'):
                content['text'].append(text)
            elif(content_type == 'text/html'):
                content['html'].append(text)            
    return content  

def CreateMsgLabels(labelIds):
  """Create object to update labels.
  Returns:
    A label update object.
  """
  return {'removeLabelIds': [], 'addLabelIds': labelIds}
