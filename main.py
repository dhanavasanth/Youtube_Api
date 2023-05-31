from googleapiclient.discovery import build
from channel_data import get_channel_data, get_latest,get_video_data
from sqlite import sql_channel_table, sql_playlist_table, sql_video_table,sql_comment_table
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import pymongo
import datetime
import base64
from PIL import Image
import pandas as pd
import json
import sqlite3
import requests
import qrcode
from io import BytesIO


st.set_page_config(page_title="YouTube Data", page_icon="📺", layout="wide", initial_sidebar_state="auto", menu_items=None)
st.title("YouTube API Data processing")

def get_img_as_base64(file):
    with open(file,"rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
img = get_img_as_base64("media/bg.jpg")

def load_lottiefile(filepath:str):
    with open(filepath,"r") as f:
        return json.load(f)

def build_youtube_client(api_key):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        return youtube
    except Exception as e:
        st.error("Error occurred while building the YouTube API client.")
        st.error(str(e))
        return None

page_bg_img = f"""

<style>
[data-testid="stAppViewContainer"] > .main {{
background-image :url("data:image/png;base64,{img}");
background-size : cover;
}}
[data-testid="stHeader"]{{
background:rgba(0,0,0,0);
}}
</style>

"""
st.markdown(page_bg_img, unsafe_allow_html=True)

connection = sqlite3.connect('youtube_data.db')
cursor = connection.cursor()

#with st.sidebar
choice = option_menu(
    menu_icon="cast",
    menu_title=None,
    options=["YOUTUBE API","CHANNEL","SQL_TABLE's","SQL_QUERY's","QR_DATA","ABOUT "],
    orientation="horizontal",
    default_index=0,
    icons=["youtube", "broadcast","cast" ,"magic",  "qr-code", "archive"],

)

if choice == "YOUTUBE API":
    col1,col2 = st.columns(2)
    with col1:
        lottie1 = load_lottiefile("media/youtube.json")
        st_lottie(lottie1, height=500)
    with col2:
        st.title("YouTube..!")
        st.write("---")
        st.subheader("YouTube is a popular online video-sharing platform that has revolutionized the way we consume and share video content. With billions of users worldwide, it has amassed a massive data size consisting of a vast collection of videos, comments, likes, and user interactions."
                "Over the years, YouTube's data size has grown exponentially as more creators and users contribute to the platform, resulting in a diverse and extensive library of videos covering various topics and genres."
                "This growth has prompted advancements in data storage and processing technologies to efficiently handle and analyze the enormous volume of data generated daily on YouTube." 
                "As YouTube continues to evolve, its data size and complexity pose exciting challenges and opportunities for content creators, researchers, and data analysts to explore and leverage the rich insights hidden within this vast digital ecosystem.")
    st.write("---")
    col1,col2 = st.columns(2)
    with col1:
        st.title("YOUTUBE API")
        st.write("---")
        st.subheader("The YouTube API facilitates seamless access to YouTube's vast data."
                "It empowers developers to retrieve video, channel, and user information programmatically."
                "The API offers functionality for searching, uploading, and managing videos."
                "It enables data collection at scale, enhancing research and analytics capabilities."
                "Developers can retrieve metrics such as views, likes, and comments for comprehensive analysis."
                "Overall, the YouTube API streamlines data collection, empowering developers to harness valuable insights from the platform.")
    with col2:
        lottie1 = load_lottiefile("media/api.json")
        st_lottie(lottie1, height=500)




if choice == "CHANNEL":
    API = st.text_input("Enter API Key",type="password")
    if not API:
        st.info("Enter API Key")
    else:
        api_key = API
        youtube = build('youtube', 'v3', developerKey=api_key)
        if youtube:
            channel_name = st.text_input("Enter Channel Name")
            if channel_name:
                data = get_channel_data(youtube,channel_name)
                col1,col2,col3 = st.columns(3)
                with col1:
                    st.image(data['thumbnail_image'],width=500)
                with col2:
                    st.title(data['channel_name'])
                    st.write("---")
                    st.write(data)
                with col3:
                    latest = get_latest(youtube,data['channel_id'])
                    st.header("Watch my Latest Video")
                    st.image(latest['thumbnail_url'],width=500)
                    st.header(latest['video_title'])
                    st.markdown("[Watch Now](https://www.youtube.com/watch?v="+latest['video_id']+")")
                    st.button("Subscribe",on_click=lambda:st.balloons())
                    col=st.columns(2)
                    with col2:
                        if st.button("SAVE THIS CHANNEL"):
                            MongoClient = pymongo.MongoClient('mongodb+srv://danavasanth:Krishnaveni@cluster0.0azflq3.mongodb.net/')
                            db = MongoClient['youtube_api']
                            collection = db['channel_data']
                            date = datetime.datetime.now()
                            video = get_video_data(youtube,data['playlists'],data['channel_id'])
                            Total_data = {"channel_name":data['channel_name'],
                                        "Date":date,
                                        "channel_data":data,
                                        "playlists":video['Playlist_Data'],
                                        "video_Data":video['video_Data']
                                        }
                            
                            collection.insert_one(Total_data)
                            st.success("Data Saved Successfully")
    

if choice == "SQL_TABLE's":
    st.subheader("click 'create TABLE' to create table in sqlite")
    if st.button('create TABLES'):
        channel_table = sql_channel_table()
        channel_table.to_sql('channel_table',connection,if_exists='replace',index=False)
        st.subheader("CHANNEL-TABLE :")
        st.dataframe(channel_table)
        playlist_table = sql_playlist_table()
        playlist_table.to_sql('playlist_table',connection,if_exists='replace',index=False)
        st.subheader("PLAYLIST-TABLE :")
        st.dataframe(playlist_table)
        video_table = sql_video_table()
        video_table.to_sql('video_table',connection,if_exists='replace',index=False)
        st.subheader("VIDEO-TABLE :")
        st.dataframe(video_table)
        comment_table = sql_comment_table()
        comment_table.to_sql('comment_table',connection,if_exists='replace',index=False)
        st.subheader("COMMENT-TABLE :")
        st.dataframe(comment_table)


if choice == "SQL_QUERY's":
    st.write("----")
    st.subheader("Let's know some basic insights about the collective channel_data")
    options = ["--select--","What are the names of all the videos and their corresponding channels?","Which channels have the most number of videos, and how many videos do they have?",
               "What are the top 10 most viewed videos and their respective channels?","How many comments were made on each video, and what are their corresponding video names?",
               "Which videos have the highest number of likes, and what are their corresponding channel names?","What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
               "What is the total number of views for each channel, and what are their corresponding channel names?","What are the names of all the channels that have published videos in the year 2022?",
               "What is the average duration of all videos in each channel, and what are their corresponding channel names?","Which videos have the highest number of comments, and what are their corresponding channel names?"]

    select = st.selectbox("Select the query to get answer's",options)

    if select == "What are the names of all the videos and their corresponding channels?":
        cursor.execute("SELECT DISTINCT channel_name,video_name FROM video_table")
        df = pd.DataFrame(cursor.fetchall(),columns=['channel_name','video_name'])
        st.dataframe(df)
    if select == "Which channels have the most number of videos, and how many videos do they have?":
        cursor.execute("SELECT channel_name,COUNT(video_name) FROM video_table GROUP BY channel_name ORDER BY COUNT(video_name) DESC;")
        df = pd.DataFrame(cursor.fetchall(),columns=['channel_name','video_count'])
        st.dataframe(df)
    if select == "What are the top 10 most viewed videos and their respective channels?":
        cursor.execute("SELECT  channel_name,video_name, view_count FROM video_table ORDER BY CAST(view_count AS INTEGER) DESC LIMIT 10;")
        df = pd.DataFrame(cursor.fetchall(),columns=['channel_name','video_name','view_count'])
        st.dataframe(df)
    if select == "How many comments were made on each video, and what are their corresponding video names?":
        cursor.execute("SELECT v.video_name, COUNT(c.comment_id) AS comment_count FROM video_table v JOIN comment_table c ON v.video_id = c.video_id GROUP BY v.video_name ORDER BY comment_count DESC;")
        df = pd.DataFrame(cursor.fetchall(),columns=['video_name','comment_count'])
        st.dataframe(df)
    if select == "Which videos have the highest number of likes, and what are their corresponding channel names?":
        cursor.execute("SELECT DISTINCT channel_name,video_name, like_count FROM video_table ORDER BY CAST(like_count AS INTEGER)  DESC;")
        df = pd.DataFrame(cursor.fetchall(),columns=['channel_name','video_name','like_count'])
        st.dataframe(df)
    if select == "What is the total number of likes and dislikes for each video, and what are their corresponding video names?":
        cursor.execute("SELECT DISTINCT video_name, like_count FROM video_table ORDER BY CAST(like_count AS INTEGER)  DESC;")
        df = pd.DataFrame(cursor.fetchall(),columns=['video_name','like_count'])
        st.dataframe(df)
    if select == "What is the total number of views for each channel, and what are their corresponding channel names?":
        cursor.execute("SELECT DISTINCT channel_name,Channel_Views FROM channel_table ORDER BY Channel_Views DESC;")
        df = pd.DataFrame(cursor.fetchall(),columns=['channel_name','channel_views'])
        st.dataframe(df)
    if select == "What are the names of all the channels that have published videos in the year 2022?":
        cursor.execute("SELECT DISTINCT channel_name,video_name,published_at FROM video_table WHERE strftime('%Y', Published_At) = '2022' ORDER BY published_at;")
        df = pd.DataFrame(cursor.fetchall(),columns=['channel_name','video_name','Publish_At'])
        st.dataframe(df)    
    if select == "What is the average duration of all videos in each channel, and what are their corresponding channel names?":
        cursor.execute("SELECT DISTINCT channel_name,AVG(duration) FROM video_table GROUP BY channel_name;")
        df = pd.DataFrame(cursor.fetchall(),columns=['channel_name','avg_duration'])
        st.dataframe(df)
    if select == "Which videos have the highest number of comments, and what are their corresponding channel names?":
        cursor.execute("SELECT DISTINCT channel_name,video_name,comment_count FROM video_table ORDER BY CAST(comment_count AS INTEGER)  DESC;")
        df = pd.DataFrame(cursor.fetchall(),columns=['channel_name','video_name','comment_count'])
        st.dataframe(df)
        

if choice == "QR_DATA":
    st.subheader("Select your favorite channel to know more...!")
    cursor.execute("SELECT DISTINCT channel_name, channel_id, Thumbnail_Image FROM channel_table;")
    df_name = pd.DataFrame(cursor.fetchall(), columns=['channel_name', 'channel_id', 'Thumbnail_Image'])
    channel_names = df_name['channel_name'].to_list()
    menu = st.selectbox("Select your favorite channel", channel_names)
    if menu:
        cursor.execute("SELECT channel_description,channel_id, Thumbnail_Image FROM channel_table WHERE channel_name = ?;", (menu,))
        df_channel = pd.DataFrame(cursor.fetchall(), columns=['channel_description', 'channel_id', 'Thumbnail_Image'])
        channel_id = df_channel['channel_id'].iloc[0]
        thumbnail_image = df_channel['Thumbnail_Image'].iloc[0]
        data = f"https://www.youtube.com/channel/{channel_id}"
        response = requests.get(thumbnail_image)
        image = Image.open(BytesIO(response.content)).convert("RGBA")
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        resized_image = image.resize(qr_image.size)
        combined_image = Image.blend(qr_image, resized_image, alpha=0.5)
        col1,col2,col3 = st.columns(3)
        with col1:
            st.subheader("Scan QR Code to Know Me More..!")
        with col2:
            st.image(combined_image)
        with col3:
            st.subheader(df_channel['channel_description'].iloc[0])



         

