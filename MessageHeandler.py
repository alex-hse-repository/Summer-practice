import base64

def is_user_msg(msg):
    """
    Check whether Message is auto generated. 

    Parameters
    ----------
    msg : Message.
    
    Returns
    -------
    True if Message does not contain labels from blacklist, False in the other case.
    """
    black_list = ['TRASH','DRAFT','SPAM','CATEGORY_FORUMS','CATEGORY_UPDATES',
                  'CATEGORY_PERSONAL','CATEGORY_PROMOTIONS','CATEGORY_SOCIAL']
    for label in msg['labelIds']:
        if(label in black_list):
            return False
    return True

def get_snippet(msg):
    """
    Get snippet of the Message.

    Parameters
    ----------
    msg : Message.
    
    Returns
    -------
    Snippet.
    """
    return msg['snippet']

def get_label(msg,user_label_ids):
    """
    Get user's label of the Message.

    Parameters
    ----------
    msg : Message.
    user_label_ids : List of user LabelIds.
    
    Returns
    -------
    Label if the Message is labeled, "Unsorted" in the other case.
    """
    
    for label_id in user_label_ids:
        if(label_id in msg['labelIds']):
            return label_id
    return 'Unsorted'

def get_id(msg):
    """
    Get id of the Message.

    Parameters
    ----------
    msg : Message.
    
    Returns
    -------
    Id.
    """
    
    return msg['id']

def get_subject(msg):
    """
    Get subject of the Message.

    Parameters
    ----------
    msg : Message.
    
    Returns
    -------
    Subject.
    """
    
    headers = msg['payload']['headers']
    subject = None 
    for header in headers:
        if(header['name'] == 'Subject'):
            subject = header['value']
    return subject        

def get_sender(msg):
    """
    Get sender of the Message.

    Parameters
    ----------
    msg : Message.
    
    Returns
    -------
    Sender.
    """
    
    headers = msg['payload']['headers']
    sender = None 
    for header in headers:
        if(header['name'] == 'From'):
            sender = header['value']
    return sender 
def get_text(msg):
    """
    Get text from the Message.

    Parameters
    ----------
    msg : Message.
    
    Returns
    -------
    Text.
    """
    content = []
    payload = msg['payload']
    if(payload['mimeType']=='multipart/alternative'):
        for part in payload['parts']:
            if(part['mimeType'] == 'text/plain'):
                content.append(decode(part['body']['data']))      
    else:
        if(payload['mimeType']=='text/plain'):
            content.append(decode(payload['body']['data']))
    return ''.join(content)

def decode(text):
    """
    Decode Text of the Message.

    Parameters
    ----------
    text : Text in an RFC 2822 formatted and base64url encoded string.
        
    Returns
    -------
    message : Decoded text.

    """
    #TODO:посмотреть что там с кодировкой
    message = base64.urlsafe_b64decode(text)
    message = str(message, 'utf-8')
    return message

def pack_message(msg,user_label_ids):
    """
    Create Message object to be saved on the disk.

    Parameters
    ----------
    msg : Message.
    user_label_ids : List of user LabelIds.

    Returns
    -------
    msg_data : Message object.

    """
    id = get_id(msg)
    label = get_label(msg,user_label_ids)
    snippet = get_snippet(msg)
    sender = get_sender(msg)
    subject = get_subject(msg)
    text = get_text(msg)
    msg_data = {'id' : id,'snippet' : snippet,'label':label,
                'sender':sender,'subject':subject,'text':text},
    
    return msg_data

 
def create_msg_label(label_id):
    """
    Create object to update mails's label.

    Parameters
    ----------
    label_id : Label ID.

    Returns
    -------
    A label update object.
    """
    return {'removeLabelIds': [], 'addLabelIds': [label_id]}