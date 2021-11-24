# from TikTokApi import TikTokApi
# import string
# import random
# did=''.join(random.choice(string.digits) for num in range(19))
# verifyFp="verify_ZfTtW5xtJdQ4sJOk0t6xGWiV45jXUaArNuEALw_wcB"
# api = TikTokApi.get_instance(custom_verifyFp=verifyFp, use_selenium=True)
# # custom_device_id=did
# tiktoks = api.trending()
# print(tiktoks)
# for i in range(len(tiktoks)):
#     data = api.get_Video_By_TikTok(tiktoks[i])# bytes of the video
#     with open("downloads/{}.mp4".format(str(i)), 'wb') as output:
#         output.write(data) # saves data to the mp4 file


# from TikTokApi import TikTokApi
# api = TikTokApi.get_instance()
# # If playwright doesn't work for you try to use selenium
# api = TikTokApi.get_instance(use_selenium=True)

# results = 10

# # Since TikTok changed their API you need to use the custom_verifyFp option. 
# # In your web browser you will need to go to TikTok, Log in and get the s_v_web_id value.
# trending = api.trending(count=results, custom_verifyFp="ZfTtW5xtJdQ4sJOk0t6xGWiV45jXUaArNuEALw_wcB")

# for tiktok in trending:
#     # Prints the id of the tiktok
#     print(tiktok['id'])

# print(len(trending))

# from TikTokApi import TikTokApi
# import os
# executablePath = '/Users/genkisystem/Downloads/chromedriver'
# os.chmod(executablePath, 755)
# api = TikTokApi.get_instance(use_selenium=True, executablePath=executablePath)

# count = 30
# tiktoks = api.byHashtag('cat', count=count)

# for tiktok in tiktoks:
#     print(tiktok)

def simple_dict(tiktok_dict):
  to_return = {}
  to_return['user_name'] = tiktok_dict['author']['uniqueId']
  to_return['user_id'] = tiktok_dict['author']['id']
  to_return['video_id'] = tiktok_dict['id']
  to_return['video_desc'] = tiktok_dict['desc']
  to_return['video_time'] = tiktok_dict['createTime']
  to_return['video_length'] = tiktok_dict['video']['duration']
  to_return['video_link'] = 'https://www.tiktok.com/@{}/video/{}?lang=en'.format(to_return['user_name'], to_return['video_id'])
  to_return['n_likes'] = tiktok_dict['stats']['diggCount']
  to_return['n_shares'] = tiktok_dict['stats']['shareCount']
  to_return['n_comments'] = tiktok_dict['stats']['commentCount']
  to_return['n_plays'] = tiktok_dict['stats']['playCount']
  return to_return
 
import pandas as pd

from TikTokApi import TikTokApi

api = TikTokApi.get_instance() 
n_videos = 100
username = 'washingtonpost'
# user_videos = api.byUsername(username, count=n_videos)
trending = api.by_trending(count=n_videos, custom_verifyFp="")

user_videos = [simple_dict(v) for v in trending]
user_videos_df = pd.DataFrame(user_videos)
user_videos_df.to_csv('{}_videos.csv'.format(username),index=False)

for tiktok in trending:
    # Prints the id of the tiktok
    print(simple_dict(tiktok))

print(len(trending))