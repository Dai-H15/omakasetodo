from django import forms

class CreateGoalForm(forms.Form):
    title = forms.CharField(
        label="目標のタイトル",
        widget=forms.TextInput(
            attrs = {"placeholder": "CSS仕事でを使えるようになる  FPの資格を取る  ..."}
        )
    )
    description = forms.CharField(
        label="目標の説明・内容",
        widget=forms.Textarea(
            attrs={"placeholder": "〇〇ができるようになるために△△が必要になる。  FPはフィナンシャルプランナーの略であり、詳細は......  "}
        )
    )