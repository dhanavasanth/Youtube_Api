from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pymongo
import datetime

#api_key = 'AIzaSyCF0P1ry3HrKHwogRCxBpWcGEtQAYbdNmE'
#youtube = build('youtube', 'v3', developerKey=api_key)


def get_channel_data(youtube, channel_name):
    # Call the search.list method to retrieve matching channels
    search_response = youtube.search().list(
        q=channel_name,
        type='channel',
        part='id,snippet'
    ).execute()

    # Get the first matching channel
    channel_id = search_response['items'][0]['id']['channelId']

    # Call the channels.list method to retrieve channel data
    channels_response = youtube.channels().list(
        id=channel_id,
        part='snippet,statistics,contentDetails'
    ).execute()

    # Get the channel data
    channel = {
        'channel_id' : channel_id,
        'channel_name' : channels_response['items'][0]['snippet']['title'],
        'video_count' : channels_response['items'][0]['statistics']['videoCount'],
        'subscription_count' : channels_response['items'][0]['statistics']['subscriberCount'],
        'view_count' : channels_response['items'][0]['statistics']['viewCount'],
        'channel_description' : channels_response['items'][0]['snippet']['description'],
        'thumbnail_image' : channels_response['items'][0]['snippet']['thumbnails']['high']['url'],
        'PublishedAt' : channels_response['items'][0]['snippet']['publishedAt'],
        'playlists' : channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    }
    return channel

def get_latest(youtube, channel_id):
  # Make a request to retrieve the most recent video uploaded to the channel
  video_response = youtube.search().list(
      part='id',
      channelId=channel_id,
      order='date',
      type='video',
      maxResults=1
  ).execute()

  # Get the video ID from the response
  video_id = video_response['items'][0]['id']['videoId']

  # Make a request to retrieve the video details
  video_details_response = youtube.videos().list(
      part='snippet',
      id=video_id
  ).execute()

  # Get the video title and thumbnail URL from the response
  latest = {
    'video_title': video_details_response['items'][0]['snippet']['title'],
    'thumbnail_url' : video_details_response['items'][0]['snippet']['thumbnails']['high']['url'],
    'video_link' : f"https://www.youtube.com/watch?v={video_id}",
    'video_id' : video_id}

  return latest

def get_playlist_data(youtube,channel_id):
  playlist_info = []

  try:
      playlist_response = youtube.playlists().list(
          part='snippet',
          channelId=channel_id,
          maxResults=50
      ).execute()

      for item in playlist_response['items']:
          playlist_info.append({
              "Channel_Id": channel_id,
              "Playlist_Name": item['snippet']['title'],
              "Playlist_Id": item['id'],
          })
  except:
      pass  
  return playlist_info

def get_video_data(youtube, playlist_id, channel_id):
    videos = {}
    next_page_token = None
    
    # Retrieve playlist items
    while True:
        videos_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for video in videos_response['items']:
            video_id = video['snippet']['resourceId']['videoId']
            video_response = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()

            # Retrieve video information
            video_info = {
                "Playlist_Id": playlist_id,
                "Video_Id": video_id,
                "Video_Name": video_response['items'][0]['snippet']['title'],
                "Video_Description": video_response['items'][0]['snippet']['description'],
                "Tags": video_response['items'][0]['snippet'].get('tags', "Not Available"),
                "PublishedAt": video_response['items'][0]['snippet']['publishedAt'],
                "View_Count": video_response['items'][0]['statistics']['viewCount'],
                "Like_Count": video_response['items'][0]['statistics']['likeCount'],
                "Favorite_Count": video_response['items'][0]['statistics']['favoriteCount'],
                "Comment_Count": video_response['items'][0]['statistics'].get('commentCount', "Not Available"),
                "Duration": video_response['items'][0]['contentDetails']['duration'][2:].lower(),
                "Thumbnail": video_response['items'][0]['snippet']['thumbnails']['high']['url'],
                "Definition": video_response['items'][0]['contentDetails']['definition'],
                "Caption_Status": video_response['items'][0]['contentDetails'].get('caption', "Not Available"),
                "Comments": {},
            }
            
            # Retrieve comments for the video
            try:
                comments_response = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    textFormat='plainText',
                    maxResults=100
                ).execute()

                for comment in comments_response['items']:
                    comment_info = {
                        "Comment_Id": comment['snippet']['topLevelComment']['id'],
                        "Comment_Text": comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                        "Comment_Author": comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        "Comment_PublishedAt": comment['snippet']['topLevelComment']['snippet']['publishedAt']
                    }
                    video_info['Comments'][comment_info['Comment_Id']] = comment_info

                videos[video_id] = video_info

                while 'nextPageToken' in comments_response:
                    comments_response = youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        textFormat='plainText',
                        maxResults=100,
                        pageToken=comments_response['nextPageToken']
                    ).execute()

            except HttpError as e:
                if e.resp.status == 403:
                    # Comments are disabled for this video, skip it
                    continue
                else:
                    raise

        if 'nextPageToken' not in videos_response:
            break
        next_page_token = videos_response['nextPageToken']


      

    playlist_data = get_playlist_data(youtube,channel_id)
    final = {'Playlist_Data': playlist_data, 'video_Data': {"Total_Videos": len(videos), "Videos": videos}}
    return final

