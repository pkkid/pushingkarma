# encoding: utf-8
import datetime
from ninja import Schema
from typing import Optional
from pydantic import Field


class RepoSchema(Schema):
    name: str = Field(..., description='Full repo name as owner/repo')
    description: Optional[str] = Field(None, description='GitHub repo description')
    homepage: Optional[str] = Field(None, description='Homepage url set on the GitHub repo')
    language: Optional[str] = Field(None, description='Primary language of the repo')
    license: Optional[str] = Field(None, description='SPDX license id')
    stars: int = Field(..., description='Number of stargazers')
    forks: int = Field(..., description='Number of forks')
    issues: int = Field(..., description='Number of open issues and pull requests')
    pushed: Optional[datetime.datetime] = Field(None, description='Last push to any branch')
    modified: datetime.datetime = Field(..., description='Last time this repo was synced')
    icon: Optional[str] = Field(None, description='mdi icon class or raw <svg> markup')
    color: Optional[str] = Field(None, description='CSS color for the icon')


class RepoDetailSchema(RepoSchema):
    commits: dict = Field(..., description='Commit counts per day {YYYY-MM-DD: count}')
    contributors: list = Field(..., description='Top contributors [{login, avatar, commits}]')
