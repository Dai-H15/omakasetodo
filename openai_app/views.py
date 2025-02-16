import json
import secrets

from django.shortcuts import render
from openai import OpenAI
from pydantic import BaseModel

from settings.local_settings import OPENAI_BASE_URL, OPENAI_API_KEY, GOOGLE_SEARCH_API_KEY, MAX_API_CALL
from main.models import Goal, Task, TaskHelp
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
                "url": item["link"]
            }
        )
    return result


def create_task(goal:Goal,title, description, priority):
    task = Task.objects.create(
        task_id=secrets.token_urlsafe(32),
        goal=goal,
        title=title,
        description=description,
        priority=priority
    )
    return f"{task.title} は正常に作成されました。"

def create_task_help(task, title, help_text, related_url):
    task_help = TaskHelp.objects.create(
        task = task,
        title = title,
        help_text = help_text,
        related_url=related_url
    )
    return f"{task_help.title} は正常に作成されました。"


def function_call(response, goal, messages, **kwargs):
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
        if name == "create_task_help":
            result = create_task_help(
                task=kwargs.get("task"),
                title=args.get("title"),
                help_text=args.get("help_text"),
                related_url=args.get("related_url")
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


def task_help_fetch(goal:Goal, task: Task):
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
                "name": "create_task_help",
                "description": "与えられた値からタスクのアドバイスなどを保存する。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "アドバイスのタイトル"
                        },
                        "help_text":{
                            "type": "string",
                            "description": "アドバイスや関連情報の内容"
                        },
                        "related_url": {
                            "type": "string",
                            "description": """
                            検索を用いる等で発見した関連情報や役に立つ情報へのリンク集
                            [資料のタイトル]: <URL>,
                            [資料のタイトル]: <URL>,....
                            のような 形式で保存することが可能
                            """
                        }
                    },
                    "required": ["title","help_text", "related_url"],
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
            
            ユーザーは上記の目標を達成するために、以下のタスクに取り組んでいます
            タスク名: {task.title}
            タスクの概要: {task.description}
            
            このタスクを実行する際に、ユーザーは追加の情報やアドバイスを求めています。
            functionで定義されたGoogle検索を適切に用いて、適切なアドバイスや、関連情報の提供を正確に行ってください。
            なお、アドバイスや情報提供は複数作成することができます。
            複数保存する場合は、1トピックごとにfunctionで定義されている保存機能を用いて保存してください。
            """
        }
    ]
    for _ in range(MAX_API_CALL):
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools,
            )
            print(messages)
            if res.choices[0].message.tool_calls:
                messages.append(res.choices[0].message)
                messages = function_call(res, goal, messages, task=task)
            else:
                break
        except Exception as e:
            print(e)
    task.task_help_create_completed = True
    task.save()
