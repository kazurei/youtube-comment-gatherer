import streamlit as st
import pandas as pd
from yt_comment_dl import YoutubeCommentDownloader
import re

st.set_page_config(
    page_title="YouTube コメント取得ツール",
    layout="wide"
)

st.title("YouTube コメント取得ツール")

st.write("YouTube動画のコメントを取得してCSV保存できます。")

# URL入力
youtube_url = st.text_input(
    "YouTube動画URLを入力してください"
)

# 取得件数
max_comments = st.number_input(
    "取得件数",
    min_value=10,
    max_value=5000,
    value=100,
    step=10
)

def extract_video_id(url):
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"shorts/([a-zA-Z0-9_-]{11})"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None

if st.button("コメント取得"):

    if not youtube_url:
        st.error("URLを入力してください")
        st.stop()

    video_id = extract_video_id(youtube_url)

    if not video_id:
        st.error("動画IDを取得できませんでした")
        st.stop()

    try:
        downloader = YoutubeCommentDownloader()

        comments = []
        count = 0

        with st.spinner("コメント取得中..."):

            for comment in downloader.get_comments(video_id):

                comments.append({
                    "author": comment.get("author"),
                    "comment": comment.get("text"),
                    "likes": comment.get("votes"),
                    "time": comment.get("time")
                })

                count += 1

                if count >= max_comments:
                    break

        if len(comments) == 0:
            st.warning("コメントを取得できませんでした")
            st.stop()

        df = pd.DataFrame(comments)

        st.success(f"{len(df)}件のコメントを取得しました")

        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="CSVダウンロード",
            data=csv,
            file_name=f"{video_id}_comments.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"エラー: {e}")
