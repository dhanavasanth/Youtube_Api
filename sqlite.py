#from googleapiclient.discovery import build
import sqlite3
import pymongo
import pandas as pd

#api_key = 'AIzaSyB-eWgMMUBrntXsG83NoBB1FYo6Ph_TJwo'
#youtube = build('youtube', 'v3', developerKey=api_key)

# Connect to MongoDB
MongoClient = pymongo.MongoClient('mongodb+srv://danavasanth:Krishnaveni@cluster0.0azflq3.mongodb.net/')
db = MongoClient['youtube_api']
collection = db['channel_data']




def sql_channel_table():
  doct = []
  for doc in db.channel_data.find():
      data = {
              'Channel_Name' : doc['channel_name'],
              'Channel_Id': doc['channel_data']['channel_id'],
              'Video_Count' : doc['channel_data']['video_count'],
              'Subscription_Count' : doc['channel_data']['subscription_count'],
              'Channel_Views'  : doc['channel_data']['view_count'],
              'Channel_Description' : doc['channel_data']['channel_description'],
              'Published_At' : doc['channel_data']['PublishedAt'],
              'Thumbnail_Image' : doc['channel_data']['thumbnail_image']
        
      }

      doct.append(data)
      df_channel_data = pd.DataFrame(doct)
  return df_channel_data

def sql_playlist_table():
  documents = collection.find()
  data = []
  # Iterate through the documents
  for document in documents:
      # Extract playlist information from each document
      channel_name = document['channel_name']
      playlists = document['playlists']

      # Iterate through the playlists array
      for playlist in playlists:
        doct = {
            'channel_id' :playlist['Channel_Id'],
            'playlist_id' : playlist['Playlist_Id'],
            'playlist_name' :playlist['Playlist_Name']}

        data.append(doct)
        df_playlists = pd.DataFrame(data)
  return df_playlists

def sql_video_table():
    documents = collection.find()

    videos_data = []

    # Iterate through the documents
    for document in documents:
        # Extract channel name
        channel_name = document['channel_name']

        # Extract video data
        video_data = document.get('video_Data')

        if video_data:
            total_videos = video_data.get('Total_Videos')
            videos = video_data.get('Videos')

            # Iterate through the videos
            for video_id, video_info in videos.items():
                data = {
                    'channel_name': channel_name,
                    'video_playlist_id': video_info.get('Playlist_Id'),
                    'video_id': video_info.get('Video_Id'),
                    'video_name': video_info.get('Video_Name'),
                    'video_description': video_info.get('Video_Description'),
                    'published_at': video_info.get('PublishedAt'),
                    'view_count': video_info.get('View_Count'),
                    'like_count': video_info.get('Like_Count'),
                    'comment_count': video_info.get('Comment_Count'),
                    'duration': video_info.get('Duration'),
                    'Thumbnail': video_info.get('Thumbnail')
                }

                videos_data.append(data)

    df_videos = pd.DataFrame(videos_data)
    return df_videos

def sql_comment_table():
    documents = collection.find()

    channel_data = []

    # Iterate through the documents
    for document in documents:
        # Extract channel name
        channel_name = document['channel_name']

        # Extract video data
        video_data = document.get('video_Data')

        if video_data:
            total_videos = video_data.get('Total_Videos')
            videos = video_data.get('Videos')

            # Iterate through the videos
            for video_id, video_info in videos.items():
                data = {
                    'video_id': video_info.get('Video_Id'),
                    }

                # Extract comments data
                comments = video_info.get('Comments')

                if comments:
                    # Iterate through the comments
                    for comment_id, comment_info in comments.items():
                        comment_data = {
                            'video_id': video_info.get('Video_Id'),
                            'comment_id': comment_id,
                            'comment_author': comment_info.get('Comment_Author'),
                            'comment_text': comment_info.get('Comment_Text'),
                            'comment_published_at': comment_info.get('Comment_PublishedAt'),
                        }

                        # Add comment data to the list
                        channel_data.append(comment_data)
                else:
                    # Add video data without comments to the list
                    channel_data.append(data)

    df_channel_data = pd.DataFrame(channel_data)
    return df_channel_data