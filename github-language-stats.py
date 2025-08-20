import requests, os
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

token = os.environ.get("GH_TOKEN")
headers = {"Authorization": f"token {token}"}

repos = requests.get("https://api.github.com/user/repos?per_page=100", headers=headers).json()

langs = {}
for repo in repos:
    if not repo["fork"]:
        lang = repo["language"]
        if lang and lang not in ["TeX"]:
            if lang == "Jupyter Notebook":
                lang = "Python"
            langs[lang] = langs.get(lang, 0) + 1

from collections import Counter

activity = Counter()

for repo in repos:
    if not repo["fork"]:
        pushed = repo.get("pushed_at")
        if pushed:
            month = pushed[:7]  
            activity[month] += 1

activity = dict(sorted(activity.items()))

df_activity = pd.DataFrame(
    sorted(activity.items()), columns=["Month", "Commits"]
)

# ---------- Plotly Figures ----------

# Donut chart for languages
fig1 = px.pie(
    names=list(langs.keys()),
    values=list(langs.values()),
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Plotly,
)
fig1.update_traces(textinfo='percent+label', textfont_size=14,
                   marker=dict(line=dict(color='black', width=1)))

fig1.update_layout(
    title_text="My GitHub Languages",
    title_font=dict(size=20, color='white'),
    paper_bgcolor='black',    
    plot_bgcolor='black',     
    font_color='white',       
    legend=dict(title="Languages", font=dict(color='white'))
)

fig1.write_image("github_stats.png", scale=2)
