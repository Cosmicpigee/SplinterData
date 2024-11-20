import requests
import time
from binascii import hexlify
from beemgraphenebase.ecdsasig import sign_message
from datetime import datetime

usernames = ["cosmicpigee","cosmicpigee2", "cosmicpigee4", "cosmicpigee3"]
usernames2 = ["toxicdiamond", "moscowcow", "cmon777", "runner1", "runner2", "splinterlandsftw"
            ,"cosmicpigee","cosmicpigee2", "cosmicpigee4", "cosmicpigee3"]
urls = ['https://api.coingecko.com/api/v3/simple/price'
        ,'https://game-api.splinterlands.com/players/balances' 
        ,"https://api2.splinterlands.com/players/unclaimed_balances"
        ,'https://game-api.splinterlands.com/players/login'
        ,'https://api.splinterlands.com/players/balance_history'
        ]



querystring = {
    'ids': 'splinterlands,dark-energy-crystals',
    'vs_currencies': 'usd'
}
response_price = requests.get(urls[0], params=querystring)
price_data = response_price.json()

dec_price = price_data.get('dark-energy-crystals', {}).get('usd', 'Price not found')
sps_price = price_data.get("splinterlands", {}).get('usd', 'Price not found')

totaldec = 0
totalsps = 0
totalStaked = 0
TotalUnclaimed = 0
def sigComp(message, privatekey):
        signature =sign_message(message,privatekey)
        return hexlify(signature).decode('ascii')
def login(privatekey):
    ts = int(time.time() * 1000)
    message = "cosmicpigee" + str(ts)
    sig = sigComp(message, privatekey)
    urlFull=f'{urls[3]}?name=cosmicpigee&ts={ts}&sig={sig}'
    response = requests.get(urlFull)
    if response.status_code == 200:
        data = response.json()
        with open ("keys.txt","r+") as file:
            lines = file.readlines()
            for i,line in enumerate(file,start=1):
                if i == 2:
                    parts = line.split("=")   
                    expiredate = parts[1].strip() 
                    if len(expiredate) < 1:
                        JwtToken = data.get('jwt_token')
                        JwtExpire = data.get('jwt_expiration_dt')
                        lines[i] = f"{"jwttoken"}={JwtToken}\n"
                    else:
                        print(expiredate)
                        JwtToken = expiredate 
                        JwtExpire = data.get('jwt_expiration_dt')
                            
                    return JwtToken, JwtExpire ,response.json()



def getBalance (username):
    UserParam = {"username": username}
    responseBalance = requests.get(urls[1], params=UserParam)
    balances = responseBalance.json()
    
    decBalance = next((float(item['balance']) for item in balances if item['token'] == 'DEC'), 0.0)
    spsBalance = next((float(item['balance']) for item in balances if item['token'] == 'SPS'), 0.0)
    stakedSps = next((float(item['balance']) for item in balances if item['token'] == 'SPSP'), 0.0)
    meritsBalance = next((item['balance'] for item in balances if item['token'] == 'MERITS'),"not found")
    return decBalance, spsBalance ,stakedSps,meritsBalance
    
def getUnclaimedBalance(username):
    
    urlFull=f'{urls[2]}?token_type=SPS&username={username}'
    responseUnclaimed =requests.get(urlFull)
    
    Unclaimed = responseUnclaimed.json()
    
    UnclaimedKey =Unclaimed.get("unclaimed_balances", [])
    UnclaimedSps =0
    UnclaimedType = ['wild','modern','brawl']
    UnclaimedBalances=[]
    for UnclaimedType in UnclaimedType:
        for item in UnclaimedKey:
            if item.get("token") == "SPS" and item.get('type')==UnclaimedType:
                balance= float(item.get("balance",0))
                UnclaimedBalances.append({"type":UnclaimedType,"balance":balance})
                UnclaimedSps += balance
    return UnclaimedSps , UnclaimedBalances

def RentalData(username ,JwtToken):
    urlFull = f'{urls[4]}?username={username}&token_type=DEC&types=rental_payment&from=&last_update_date=&limit=50&token={JwtToken}'
    response = requests.get(urlFull)
    current_time = datetime.now().date()

# Print the current time
    print(current_time)
    return response.json()

for username in usernames:
    
    UnclaimedSps, UnclaimedBalances= getUnclaimedBalance(username)
    decBalance, spsBalance ,stakedSps ,merits = getBalance(username)
    
    TotalUnclaimed =  (round((UnclaimedSps),2))
    totaldec =  (round((totaldec + decBalance),2))
    totalsps =  (round((totalsps + spsBalance),2))
    totalStaked =  (round((totalStaked +stakedSps),2))
    
    print(f"\nUsername: {username}")
    print(f"DEC Balance: {decBalance}")
    print(f"SPS liquid: {spsBalance}")
    print(f'Staked SPs  {stakedSps}')
    print(f"Total sps {spsBalance+stakedSps+UnclaimedSps}")
    print(f"Unclaimed SPS  Total: {UnclaimedSps}")
    print(f"merits: {merits}")
    print(f"UnclaimedBalances: {UnclaimedBalances}") 

with open ("keys.txt","r") as file:
    firstline=  file.readline().strip()
    parts = firstline.split("=")  
    privatekey = parts[1].strip()  

print (privatekey)

JwtToken, JwtExpire, loginResponse = login(privatekey)
print(f"JWT Token: {JwtToken}")
print(f"JWT Expiration: {JwtExpire}")



response_price = requests.get(urls[1], params=querystring)
price_data = response_price.json()

decUsd = dec_price * totaldec
spsUsd = sps_price * totalsps
stakedUsd = sps_price * totalStaked

print('\n', totaldec ," Dec in usd :",round((decUsd),2))
print(totalsps ," SPS in usd :",round((spsUsd),2))

print("\n Total liquid in Usd :",round((decUsd+spsUsd),2))
print("\n Total everything in Usd :",round((decUsd+spsUsd+stakedUsd),2))