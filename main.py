from apiclient.discovery import build
import json
import pandas as pd
import streamlit as st
from pandas.io.json import json_normalize
import base64
import datetime

st.sidebar.write("""
### APIKEYの入力""")
API_KEY= st.sidebar.text_input('APIKEY入力', '')



DEVELOPER_KEY = API_KEY



YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                developerKey=DEVELOPER_KEY)

def video_search(youtube, q='自動化', max_results=5):



    response = youtube.search().list(
        q=q,
        part='id,snippet',
        order='viewCount',
        type='video',
        maxResults=max_results
    ).execute()


    items_id = []
    items = response['items']
    for item in items:
        data =json.dumps(item, indent=2, ensure_ascii=False)
        info = json.loads(data)
        df = json_normalize(info)
        items_id.append(df)


    df_video = pd.concat(items_id)






    df_list = []

    for video_id in df_video['id.videoId']:
        response = youtube.videos().list(
          part = 'snippet,statistics',
          id = video_id
          ).execute()

        for item in response.get("items", []):
            if item["kind"] != "youtube#video":
                continue
                
            try :
                if  int(len(item["snippet"]["tags"])) > 0.1:
                    data =json.dumps(item, indent=2, ensure_ascii=False)
                    info = json.loads(data)
                    dfinfo = json_normalize(info) #Results contain the required data
                    

                    df_list.append(dfinfo)

                else :
                  pass
            except :
                    data1 =json.dumps(item, indent=2, ensure_ascii=False)
                    info1 = json.loads(data1)
                    df1 = json_normalize(info1) #Results contain the required data
                    # df1 = 
                    
                    
                    df_list.append(df1)

    df_all = pd.concat(df_list, axis=0, sort=False)





    channel_ids = df_all['snippet.channelId'].unique().tolist()


    subscriber_list = youtube.channels().list(
        id=','.join(channel_ids),
        part='statistics',
        # 必要なデータを絞り込み
        fields='items(id,statistics(subscriberCount))'
    ).execute()

    subscribers = []
    for item in subscriber_list['items']:
        subscriber = {}
        if len(item['statistics']) > 0:
            subscriber["snippet.channelId"] = item['id']
            subscriber['subscriber_count'] = int(item['statistics']['subscriberCount'])
        else:
            subscriber["snippet.channelId"] = item['id']
        subscribers.append(subscriber)

    df_subscribers = pd.DataFrame(subscribers)






    df = pd.merge(left=df_video, right=df_subscribers, on='snippet.channelId')
    df["id"] = df["id.videoId"]
    df = pd.merge(left=df, right=df_all, on='id')
    df = df[["snippet.publishedAt_x","snippet.channelTitle_y","subscriber_count","snippet.title_x","snippet.localized.description","statistics.viewCount","statistics.likeCount","statistics.commentCount","snippet.categoryId","id","snippet.defaultAudioLanguage","snippet.tags"]]
    



    results = df
    return results


def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv()



def downloader(df):
    csv = convert_df(df)
    st.download_button(
        label="Download",
        data=csv,
        file_name=f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.csv',
        mime='text/csv',
    )











st.title('YouTubeアプリ')



st.sidebar.write("""
検索結果数（API制限対策）""")
limits = st.sidebar.text_input('検索結果数を入力してください', '5')



st.sidebar.write("""
## クエリ""")
st.sidebar.write("""
### クエリの入力""")
query = st.sidebar.text_input('検索クエリを入力してください', 'Anna Takeuchi')




st.markdown('### 選択中のパラメータ')
st.markdown(f"""
- 検索クエリ: {query}
""")

results = video_search(youtube, q=query, max_results=limits)


st.write("### 分析結果", results)
st.write("### 動画再生")



video_id = st.text_input('動画IDを入力してください')
url = f"https://youtu.be/{video_id}"
video_field = st.empty()
video_field.write('こちらに動画が表示されます')

if st.button('ビデオ表示'):
    if len(video_id) > 0:
        try:
            video_field.video(url)
        except:
            st.error(
                """
                **おっと！何かエラーが起きているようです。** :(
            """
            )

st.write("### CSVダウンロード")



downloader(results)









