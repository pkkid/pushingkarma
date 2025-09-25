# encoding: utf-8
from datetime import datetime
from ninja import Schema
from typing import Optional
from pydantic import Field


class RedditNewsSchema(Schema):
    class RedditQuerySchema(Schema):
        subreddit: str = Field(..., description='Subreddit name to query')
        count: int = Field(15, description='Number of posts to retrieve')
        maxtitle: Optional[int] = Field(9999, description='Maximum title length')
        mintext: Optional[int] = Field(0, description='Minimum selftext length')
        maxtext: Optional[int] = Field(9999, description='Maximum selftext length')
    queries: list[RedditQuerySchema] = Field(..., description='List of subreddit queries')


class RedditPostSchema(Schema):
    url: Optional[str] = Field(None, description='External URL for the post')
    redditurl: str = Field(..., description='Reddit URL for the post')
    subreddit: str = Field(..., description='Subreddit this post was in')
    title: str = Field(..., description='Title of the note')
    created: datetime = Field(..., description='Datetime of this post')
    selftext: Optional[str] = Field(None, description='Self text for this reddit post')
    score: Optional[int] = Field(None, description='Score for this post')
