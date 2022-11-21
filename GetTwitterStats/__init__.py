import json
import requests
import logging
import datetime
import os
import azure.functions as func

def main(timetrig: func.TimerRequest, twitterstats: func.Out[func.SqlRow]) -> None:
    # Note that this expects the body to be a JSON object which
    # have a property matching each of the columns in the table to upsert to.

    # get the date
    now = datetime.datetime.now()
    dt_string = now.strftime('%Y-%m-%dT%H:%M:%S')

    # call the twitter api
    token = os.environ["TwitterToken"]
    r =requests.get("https://api.twitter.com/2/users/by?usernames=jpomfret&user.fields=created_at%2Cpublic_metrics", headers={"Authorization": "Bearer {}".format(token)})
    robj = r.json()
    data = robj['data']
    stats = data[0]

    # call the mastadon api
    tokenMast = os.environ["MastadonToken"]
    rMast =requests.get("https://tech.lgbt/api/v1/accounts/109304329691833749/", headers={"Authorization": "Bearer {}".format(tokenMast)})
    robjMast = rMast.json()
    dataMast = robjMast['accounts']
    statsMast = dataMast[0]

    # save the data to the database
    dbRow = {'collectionDate': dt_string, 'name' : stats['name'], 'username': stats['username'], 'id': stats['id'], 'followersCount': stats['public_metrics']['followers_count'], 'followingCount': stats['public_metrics']['following_count'], 'tweetCount': stats['public_metrics']['tweet_count'], 'listedCount': stats['public_metrics']['listed_count'],'MastURL': statsMast['url'], 'MastUsername': statsMast['username'], 'MastFollowers': statsMast['followers_count'],'MastFollowing': statsMast['following_count'], 'MastStatusCount': statsMast['statuses_count']}
    row = func.SqlRow.from_dict(dbRow)
    twitterstats.set(row)
