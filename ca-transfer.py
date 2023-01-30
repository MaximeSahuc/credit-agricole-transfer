import sys
import json
import urllib3
import requests
from termcolor import colored

# Recipent infos
RECIPENT_IBAN = 'FR76 1830 XXXX XXXX XXXX XXXX XXXX'
RECIPENT_BIC = 'AGRIFRPP883'
RECIPENT_LABEL = '' # Recipent name

# Transfer infos
TRANSFER_AMOUNT = 1
TRANSFER_AMOUNT = "{:.2f}".format(TRANSFER_AMOUNT)
TRANSFER_MOTIF = 'Test'
TRANSFER_ADDITIONAL_MOTIF = 'Test 2'

# Credentials
refresh_token = ''
hashid = ''


# Disable insecure request warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_tokens():
    headers = {
        'Content-Type': 'application/json',
        'Correlationid': '0',
        'Hashid': '' + hashid + '',
        'Connection': 'close',
    }

    json_data = {'refresh_token': '' + refresh_token + ''}

    response = requests.post(
        'https://nmb.credit-agricole.fr/authentication/v1/refresh_token',
        headers=headers,
        json=json_data,
        verify=False,
    )

    return response.json()['access_token'], response.json()['refresh_token']


def get_source_accounts(access_token):
    headers = {
        'Content-Type': 'application/json',
        'Correlationid': '0',
        'Authorization': 'Bearer ' + access_token + '',
        'Hashid': '' + hashid + '',
        'Connection': 'close',
    }

    response = requests.get('https://nmb.credit-agricole.fr/transfer/v1/source_accounts', headers=headers, verify=False)
    
    # If error, exit
    if response.status_code >= 300:
        print('Error : ' + response.json()['cause'])
        sys.exit()

    return response.json()


def check_transfer(source_bic_code, source_label, source_iban, source_contract_number, transfer_flow_id, access_token):
    headers = {
        'Content-Type': 'application/json',
        'Correlationid': '0',
        'Authorization': 'Bearer ' + access_token + '',
        'Hashid': '' + hashid + '',
        'Connection': 'close',
    }

    json_data = {
        'recipient_account': {
            'external': {
                'bic_code': '' + RECIPENT_BIC + '',
                'iban': '' + RECIPENT_IBAN.replace(' ', '') + '',
                'label': '' + RECIPENT_LABEL + ''
                }
        },
        'amount': '' + TRANSFER_AMOUNT + '',
        'motif': '' + TRANSFER_MOTIF + '',
        'additional_motif': '' + TRANSFER_ADDITIONAL_MOTIF + '',
        'date': 0,
        'source_account': {
            'bic_code': '' + source_bic_code + '',
            'label': '' + source_label + '',
            'iban': '' + source_iban + '',
            'contract_number': '' + source_contract_number + '',
        },
        'transfer_flow_id': '' + transfer_flow_id + ''
    }

    response = requests.post('https://nmb.credit-agricole.fr/transfer/v1/check', headers=headers, json=json_data, verify=False)

    # Print status code
    print('[', response.status_code, ']')

    # If error, exit
    if response.status_code >= 300:
        print('Error : ' + response.json()['cause'])
        sys.exit()


def send_transfer(transfer_flow_id, access_token):
    headers = {
        'Content-Type': 'application/json',
        'Correlationid': '0',
        'Authorization': 'Bearer ' + access_token + '',
        'Hashid': '' + hashid + '',
        'Connection': 'close',
    }

    json_data = {
        'transfer_flow_id': '' + transfer_flow_id + '',
    }

    response = requests.post('https://nmb.credit-agricole.fr/transfer/v1/send', headers=headers, json=json_data, verify=False)
    
    # Print status code
    print('[', response.status_code, ']')

    # If error, exit
    if response.status_code >= 300:
        print('Error : ' + response.json()['cause'])
        sys.exit()


# Requesting access and refresh tokens
print('Requesting access and refresh token')
tokens = get_tokens()

access_token = tokens[0]
refresh_token = tokens[1]

# Getting source accounts
print('\nGetting source accounts infos:')
source_accounts = get_source_accounts(access_token)

# Getting transfer flow id
transfer_flow_id = source_accounts['transfer_flow_id']
print('  Transfer flow id : ' + transfer_flow_id)

# Getting main account contract number
source_contract_number = source_accounts['my_accounts'][0]['accounts'][0]['contract_number']
print('\n  Contract number : ' + source_contract_number)

# Getting main account IBAN
source_iban = source_accounts['my_accounts'][0]['accounts'][0]['iban']
print('  IBAN : ' + source_iban)

# Getting main account BIC code
source_bic_code = source_accounts['my_accounts'][0]['accounts'][0]['bic_code']

# Recipent details
print('\nRecipent infos:')
print('  Recipent IBAN : ' + RECIPENT_IBAN)
print('  Recipent BIC code : ' + RECIPENT_BIC)

# Transfer details
print('\nTransfer details:')

print('  Amount : ' + TRANSFER_AMOUNT)
print('  Motif : ' + TRANSFER_MOTIF)
print('  Additional motif : ' + TRANSFER_ADDITIONAL_MOTIF)

# Check transfer
print('\nChecking transfer')
check_transfer(source_bic_code, 'Compte de Dépôt', source_iban, source_contract_number, transfer_flow_id, access_token)

# Send transfer
print('\nSending transfer')
send_transfer(transfer_flow_id, access_token)

print('Done!')