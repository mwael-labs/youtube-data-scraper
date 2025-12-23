# YouTube Data Scraper

Scrapes YouTube video metadata using the **YouTube Data API v3** and prepares datasets for analysis, research, and machine learning projects.

## Requirements
- A YouTube Data API v3 key  
  Create one at: https://console.cloud.google.com/apis

## Collected Fields
- `video_id`
- `title`
- `description`
- `category_id`
- `views`
- `likes`
- `comments`
- `duration_sec`
- `publish_date`
- `channel_id`
- `channel_name`
- `subscriber_count`
- `thumbnail`

## Output
The script outputs structured data ready for:
- Data analysis
- NLP experiments
- Machine learning models
- Content performance research

## Dataset
A large dataset collected using this scraper is publicly available on Kaggle:
https://www.kaggle.com/datasets/mohamedwael001/youtube-videos-mega-dataset-40000-entries

## Notes
- YouTube API quotas apply. Generally 10,000 quotas daily
- This project is intended for educational and research use.
