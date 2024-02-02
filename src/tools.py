
import os
from dotenv import load_dotenv
from xrpl.clients import WebsocketClient
from xrpl.models import Subscribe
from xrpl.models.requests.account_tx import AccountTx
from xrpl.account import get_balance
from xrpl.clients import JsonRpcClient
from langchain.tools import tool
from xrpl.models.requests.account_lines import AccountLines
from datetime import date
from xrpl.models.transactions import Payment
from xrpl.wallet import Wallet
from xrpl.transaction import submit_and_wait
from xrpl.wallet import generate_faucet_wallet


from xrpl.utils import drops_to_xrp, ripple_time_to_datetime, xrp_to_drops
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from typing import Literal, Union


load_dotenv()


RPCTYPE = Literal['MAINNET', 'TESTNET']


ALLOWED_TRANSACTION = [
    "TrustSet",
]

UNAUTHORIZED_TRANSACTIONS = [
    "Payment",
]


UNAUTHORIZED_ACCOUNTS = [
    "r4MPsJ8SmQZGzk4dFxEoJHEF886bfX4rhu",
]

NETWORKS = {
    "MAINNET": {
        "explorer": "https://livenet.xrpl.org/",
        "rpc": "https://s2.ripple.com:51234/"
    },
    "TESTNET": {
        "explorer": "https://testnet.xrpl.org/",
        "rpc": "https://s.altnet.rippletest.net:51234/"
    }
}

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1, streaming=True, verbose=True)


@tool
def check_acct_bal(user_address:str):
    """
    Function to check a user account xrp balance
    """
    try:
        client = JsonRpcClient('https://s.altnet.rippletest.net:51234/')
        balance = get_balance(user_address, client)
        return drops_to_xrp(str(balance))
    except:
        return ("return there was error ") 
   

@tool
def send_slack_notification(address:str):
    "function to send notification to slack"
    return f"this user has send an unauthorized transaction to this account {address}"

@tool
def check_asset_trustline(address:str, asset_code:str, asset_issuer:str):
    """
    check if the provided address has a trustline to an asset
    """
    try:
        
        client = JsonRpcClient('https://s.altnet.rippletest.net:51234/')
        c = AccountLines(account=address, ledger_index="validated")

        lines = client.request(c)
        for line in lines.result['lines']:
            if line['account'] == asset_issuer and line['currency'] == asset_code:
                return "this line was found ", line;

        return False
    except:
        return "there was an error with your query"

@tool
def return_transaction_on_an_account(acct:str, limit:int):
    """
    function that return list of transaction on an account, the limit is used limit the amount of transaction returned
    """
    try:
        
        transactions = []
        client = JsonRpcClient('https://s.altnet.rippletest.net:51234/')
        tx = AccountTx(account=acct, limit=limit)
        req = client.request(tx)
        for tx in req.result["transactions"]:
            indiTx = tx['tx']
            transactions.append(indiTx)
        return transactions
    except:
        return "there was an error with your query"




@tool
def unauthorized_accounts():
    """
    function that return list of unauthorized and watchlist accounts.
    This account are blacklisted and under sanctions
    """
    return UNAUTHORIZED_ACCOUNTS

@tool
def get_network(rpc:RPCTYPE):
    """
    function to return specified rpc for mainnet or testnet, choices are between mainnet and testnet. 
    """
    rpc = NETWORKS[rpc]['rpc']
    return rpc
    

@tool
def allowed_transaction():
    """
    function that return list of allowed transactions
    """
    return ALLOWED_TRANSACTION


@tool
def unauthorized_transactions():
    """
    function that return list of unauthorized transactions
    """
    return UNAUTHORIZED_TRANSACTIONS

# adc = check_transaction_details("rMb2MQbhwP8E4MihHLg6RkK7Tb2C4pRo3T")
# print(adc)


# @tool
# def subscribe_To_A_Single_Account(address:str):
#     """
#     function to subscribe to a single account on the blockchain and get every transaction this account is sending or receiving on the blockchain 
    
#     """
#     req = Subscribe(accounts=[address])
#     url = "wss://s.altnet.rippletest.net:51233/"
#     with WebsocketClient(url) as client:
#         client.send(req)
#         for message in client:
#             print(message)
#             # return message




@tool
def convert_ripple_time(xrpl_time:int):
    """
    function to convert xrpl time to human readable time
    """
    return ripple_time_to_datetime(xrpl_time)

@tool
def current_time_and_date():
    """
    function to return current time and date
    """
    today = date.today()
    return f"Today's date: {today}"



@tool
def send_payment(address:str, amount:int):
    """
    function to send payment to an address on the xrpl, 
    it takes in address- the destination address and the amount
    """
    client = JsonRpcClient('https://s.altnet.rippletest.net:51234/')
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    keyPair = Wallet.from_seed(PRIVATE_KEY)
    my_tx_payment = Payment(
        account=keyPair.classic_address,
        amount=xrp_to_drops(amount),
        destination=address,
    )
    tx_response = submit_and_wait(my_tx_payment, client=client, wallet=keyPair)
    return tx_response

@tool
def generate_xrpl_keys():
    """
    function to generate xrpl keys,
    It also the function that generate new wallets on xrpl
    """
    keyPair = Wallet.create()
    return {
        "classic_address": keyPair.classic_address,
        "private_key": keyPair.seed
    }
    
@tool
def fund_testnet_account():
    """
    Function used to create a testnet account on the xrpl, this will create the wallet and automatically fund it 
    """
    fund_acct = generate_faucet_wallet(client=JsonRpcClient(get_network("TESTNET")), debug=True)
    # print(fund_acct)
    return {
        "classic_address": fund_acct.classic_address,
        "private":fund_acct.seed,
        "public":fund_acct.public_key
    }
    
    
@tool
def convert_drop_to_xrpl(drop_bal:Union[str, int]):
    """
    Every transaction on xrpl, will be returned as drop, this function is used to convert every balance from a query to the xrpl to an actual amount.
    it takes a string as an argument
    """
    
    return drops_to_xrp(drop_bal)


register_tools = [
    get_network, check_acct_bal, check_asset_trustline, 
    current_time_and_date, convert_ripple_time, send_slack_notification,
    send_payment, return_transaction_on_an_account, allowed_transaction, 
    unauthorized_accounts, unauthorized_transactions,
    generate_xrpl_keys,
    fund_testnet_account,
    convert_drop_to_xrpl
    ]


# print(fund_testnet_account())

