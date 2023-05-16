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


def get_video_data(youtube, channel_id, playlists): 
    try:   
        playlist_response = youtube.playlists().list(
            part='snippet',
            channelId=channel_id,
            maxResults=50
        ).execute()
        
        # Get the playlist names and ids
        playlist_info = []
        for item in playlist_response['items']:
            playlist_info.append({
                "Channel_Id": channel_id,
                "Playlist_Name": item['snippet']['title'],
                "Playlist_Id": item['id'],

            })
    except:
        pass
    
    # Get the video data for each playlist
    videos = {}
    for playlist in playlist_info:
        playlist_videos = []
        next_page_token = None
        while True:
            playlist_videos_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlists,
                maxResults=100,
                pageToken=next_page_token
            ).execute()
            playlist_videos.extend(playlist_videos_response['items'])
            next_page_token = playlist_videos_response.get('nextPageToken')
            if not next_page_token:
                break
                
        for item in playlist_videos:
            video_id = item['snippet']['resourceId']['videoId']
            video_response = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()
            
            if video_response['items']:
                video_info = {
                    # "Playlist_Name": playlist['Playlist_Name'],
                    "Playlist_Id": playlists,
                    "Video_Id": video_id,
                    "Video_Name": video_response['items'][0]['snippet']['title'] if 'title' in video_response['items'][0]['snippet'] else "Not Available",
                    "Video_Description": video_response['items'][0]['snippet']['description'],
                    "Tags": video_response['items'][0]['snippet']['tags'] if 'tags' in video_response['items'][0]['snippet'] else "Not Available",
                    "PublishedAt": video_response['items'][0]['snippet']['publishedAt'],
                    "View_Count": video_response['items'][0]['statistics']['viewCount'],
                    "Like_Count": video_response['items'][0]['statistics']['likeCount'] if 'likeCount' in video_response['items'][0]['statistics'] else "Not Available",
                    "Comment_Count": video_response['items'][0]['statistics']['commentCount'],
                    "Duration": video_response['items'][0]['contentDetails']['duration'][2:].lower(),
                    "Thumbnail": video_response['items'][0]['snippet']['thumbnails']['high']['url'],
                    "Comments": {}
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
                            "Video_Id": video_id,
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
                        print("Comments for this video have been disabled")
                    else:
                        raise e

    return{"Playlist_Data": playlist_info,'video_Data': {"Total_Videos": len(videos), "Videos": videos}}
