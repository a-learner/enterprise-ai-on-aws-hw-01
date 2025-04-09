def handler(event, context):
    
    print(event)
    emailDomain = event['request']['userAttributes']['email'].split('@')[1]
    print("User email domain => ",emailDomain)
    if ( emailDomain == 'hidglobal.com' or emailDomain =='assaabloy.com'):
        print('email domain is valid.')
        return event
    else:
        print('email domain is invalid')
        raise Exception('Invalid email domain.')