import json

from django.shortcuts import render
from openai import OpenAI
from pydantic import BaseModel

from settings.local_settings import OPENAI_BASE_URL, OPENAI_API_KEY, GOOGLE_SEARCH_API_KEY, MAX_API_CALL
from main.models import Goal, Task
from googleapiclient.discovery import build
# Create your views here.

def goal_moderation(goal: Goal = "", **kwargs):
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    if goal != "":
        text = f"{goal.title}  {goal.description}"
    else:
        text = kwargs.get("text")
    res = client.moderations.create(
        model="omni-moderation-latest",
        input=text
    )
    return res.results[0].flagged

def search_from_google(query):
    service = build("customsearch", "v1", developerKey=GOOGLE_SEARCH_API_KEY)
    res = (
        service.cse()
        .list(
            q = query,
            cx="c722acbfc2a38466b"
        ).execute()
    )
    result = []
    for item in res["items"]:
        result.append(
            {
                "title": item["title"],
                "snippet": item["snippet"],
                "url": item["htmlFormattedUrl"]
            }
        )
    return result


def create_task(goal:Goal,title, description, priority):
    task = Task.objects.create(
        goal=goal,
        title=title,
        description=description,
        priority=priority
    )
    return f"{task.title} は正常に作成されました。"


def function_call(response, goal, messages):
    calling = response.choices[0].message.tool_calls
    for call in calling:
        args = json.loads(call.function.arguments)
        name = call.function.name
        result = ""
        if name == "search_from_google":
            result = search_from_google(
                query=args.get("query")
            )
        if name == "create_task":
            result = create_task(
                goal=goal,
                title=args.get("title"),
                description=args.get("description"),
                priority=args.get("priority")
            )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),

            }
        )
    return messages



def task_fetch(goal:Goal):
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_from_google",
                "description": "Google検索を用いて、与えられたキーワードにヒットするWebサイトの一覧を取得します",
                "parameters": {
                    "type":"object",
                    "properties": {
                        "query":{
                            "type": "string",
                            "description": "Google上で検索する文字列"
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                },
                "strict": True
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "与えられた値からタスクを作成して保存する。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "タスクのタイトル"
                        },
                        "description":{
                            "type": "string",
                            "description": "タスクの端的でわかりやすい説明文"
                        },
                        "priority": {
                            "type": "number",
                            "description": "タスクの優先度(1~3の値で、小さいほど高優先度)"
                        }
                    },
                    "required": ["title","description", "priority"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    ]

    messages = [
        {
            "role": "user",
            "content": f"""
            あなたはユーザーの目標達成に対して適切なタスクを与えるアドバイザーです。
            ユーザーが登録した目標とその概要は以下のとおりです。
            目標: {goal.title}
            目標の概要: {goal.description}

            functionで定義されたGoogle検索を適切に用いて、5個以上のタスクを作成してください。
            """
        }
    ]
    for _ in range(MAX_API_CALL):
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
        )
        print(messages)
        if res.choices[0].message.tool_calls:
            messages.append(res.choices[0].message)
            messages = function_call(res, goal, messages)
        else:
            break
