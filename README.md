<img align="top" height = 200 alt="Coding" width="900" src="https://media.giphy.com/media/13Nc3xlO1kGg3S/giphy.gif">

<h1 align="center">YOUTUBE - API</h1>


## Description

Fetching youtube channel data's via API and make store in MongoDB and make it in a Structured way to analyse it in faster way using SQLITE3 and to create this using a web-interface dynamic streamlit applictaion and make answer some query's


## Deployment

To deploy this project run

```bash
from googleapiclient.discovery import build
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
```
# Youtube - API
To connect with youtube API via API_KEY and build library and get the required parameter resource from youtube data 
```
API_KEY = 'YOUR_API_KEY'
youtube = build('youtube', 'v3', developerKey=API_KEY)
```
# Stramlit Interface



## Screenshots
![home](https://github.com/dhanavasanth/Youtube_Api/assets/117557948/70f2e214-9a7a-4917-b7f6-80a1726a58ce)


# MongoDB Atlas

## Unstructured Data

![App Screenshot]()

# SQLITE3

## Structuring four diffrent table

![sqltable](https://github.com/dhanavasanth/Youtube_Api/assets/117557948/3c3a7d98-7fff-4a3c-96b8-8c10a009e530)


# SQLITE3 - Query

## Query from SQLite3 table

![query](https://github.com/dhanavasanth/Youtube_Api/assets/117557948/b7388f5a-4e5f-49cb-b2b6-e924fc89831c)



# QRCODE

## Generating QRcode for corresponding channel's 

![qrcode](https://github.com/dhanavasanth/Youtube_Api/assets/117557948/54cc71b9-55eb-46f8-8947-0f3add4763b5)



## Support

For support, email danavasanth@gmail.com


