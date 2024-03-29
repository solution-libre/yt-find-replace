#!/usr/bin/env python3

# =======================================
# =    YT description find + replace    =
# =   https://twitter.com/telepathics   =
# =======================================

# -*- coding: utf-8 -*-

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "oauth_client.json"

new_line = "\n- - - - - -\n"
class YouTubeHandler(object):
    def __init__(self):
      # Get credentials and create an API client
      flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
      credentials = flow.run_console()

      self.yt = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
      self.channel_info = self.get_channel_info()

    def get_channel_info(self):
        request = self.yt.channels().list(
          part="snippet,contentDetails,statistics",
          mine=True
        )
        return request.execute()

    def get_playlist_videos(self, next_page_token=None):
        upload_playlist = self.channel_info["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        request = self.yt.playlistItems().list(
          part="snippet",
          playlistId=upload_playlist,
          maxResults=50,
          pageToken=next_page_token
        )
        return request.execute()

    def desc_find_replace(self, find_text, replace_text):
      response = self.get_playlist_videos()

      print(new_line)

      while ("nextPageToken" in response):
        for item in response["items"]:
          if find_text in item["snippet"]["description"]:
            print("updating video: " + item["snippet"]["title"] + " https://www.youtube.com/watch?v=" + item["snippet"]["resourceId"]["videoId"])
            self.replace_video_description(item["snippet"], find_text, replace_text)
        response = self.get_playlist_videos(response["nextPageToken"])

      for item in response["items"]:
          if find_text in item["snippet"]["description"]:
            print("updating video: " + item["snippet"]["title"] + " https://www.youtube.com/watch?v=" + item["snippet"]["resourceId"]["videoId"])
            self.replace_video_description(item["snippet"], find_text, replace_text)

    def replace_video_description(self, snippet, find_text, replace_text):
        request = self.yt.videos().update(
          part="snippet",
          body={
            "id": snippet["resourceId"]["videoId"],
            "snippet": {
              "title": snippet["title"],
              "categoryId": "24",
              "defaultLanguage": "en",
              "description": snippet["description"].replace(find_text, replace_text)
            }
          }
        )
        return request.execute()

def menu():
  print(new_line)
  find_text = input("Find: ")
  print("")
  replace_text = input("Replace: ")
  print(new_line)

  yt = YouTubeHandler()
  yt.desc_find_replace(find_text, replace_text)

  print(new_line)
  print("Done! thanks.")

def main():
    running = True
    while running:
      running = menu()

if __name__ == "__main__":
    main()