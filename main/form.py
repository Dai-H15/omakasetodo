from django import forms
from main.models import Task

class CreateGoalForm(forms.Form):
    title = forms.CharField(
        label="目標のタイトル",
        widget=forms.TextInput(
            attrs = {"placeholder": "例: CSSを仕事でを使えるようになる  FPの資格を取る  ..."}
        )
    )
    description = forms.CharField(
        label="目標の説明・内容",
        widget=forms.Textarea(
            attrs={"placeholder": "例: 〇〇ができるようになるために△△が必要になる。  FPはフィナンシャルプランナーの略であり、詳細は......  "}
        )
    )

class TaskForm(forms.Form):
    title = forms.CharField(max_length=200, label="タスクタイトル", widget=forms.TextInput(attrs={"readonly": "readonly"}))
    description = forms.CharField(max_length=200, label="タスク概要", widget=forms.Textarea(attrs={"readonly": "readonly"}))
    start_date = forms.DateField(label="タスク開始日", widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}), required=False)
    priority = forms.IntegerField(label="タスク優先度: 1に近づくほど高優先度")
    done_flag = forms.BooleanField(label="完了フラグ", required=False)