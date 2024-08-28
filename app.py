
#from crypt import methods
import pandas as pd
import time
import datetime
import requests
from datetime import date
#from dateutil.parser import parse
from sklearn.model_selection import train_test_split

#from xgboost import XGBClassifier
#from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import classification_report
import pickle


from flask import Flask,redirect,url_for,render_template,request,render_template_string

#variables

    
features=['protected', 'verified', 'geo_enabled', 'profile_use_background_image',
       'default_profile', 'followers_count', 'friends_count', 'listed_count',
       'favourites_count', 'statuses_count']

xgb=pickle.load(open('twitter_bot.pickle', 'rb'))




# helper functions

def get_profile_information(url,header):
    user=url.split('/')[-1]
    
    r=requests.get('https://api.twitter.com/2/users/by/username/{}'.format(user), headers=header)
    if r.status_code != 200 or 'errors' in r.json().keys():
        return (r.status_code)
    
    user_id=r.json()['data']['id']
    r=requests.get('https://api.twitter.com/1.1/users/show.json?user_id={}'.format(user_id), headers=header)
    information=r.json()
    return information


def information_to_features(info,feat):
    df=pd.DataFrame(columns=feat)
    
    for f in feat:
        try:
            df.loc[0,f]=info[f]
        except:
            df.loc[0,f]=0
    #df['created_at']=df['created_at'].map(time_since_profile_creation)
    df=df.replace({'True':1,'False':0})
    df=df.replace({True:1,False:0})
    df=df.astype('int64')
    df=df.fillna(0)
    
    
    return df
        
def get_profile(url,header,feat):
    info=get_profile_information(url,header)
    if type(info)==int:
        return info
        
    df=information_to_features(info,feat)
    return df
    
    
    



app=Flask(__name__, template_folder='templates')
@app.route('/',methods=['POST','GET'])
def home():
    headers={}
    with open('bearer_token.txt') as f:
        token = f.readline().strip()



    headers['Authorization']='Bearer '+token

    if request.method=='GET':
        
        return render_template('index copy.html')

    else:
        
        url=str(request.form['url'])
        
        url=url.split('/status')[0]
        x=get_profile(url,headers,features)
        

        if type(x)==int:
            if x not in [429,401]:
                x=200
            return render_template('{}.html'.format(x))
            #return str(x)
        
        probability=xgb.predict_proba(x)[:,1][0]
        if probability>=0.5:
            bot='a bot'
        else:
            bot='not a bot'
        return render_template('simple.html',bot=bot, probability=round(probability*100))
        #return str(probability)
        
               

    
if __name__ =='main':
    app.run(debug=True)