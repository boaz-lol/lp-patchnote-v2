import csv
import requests
from bs4 import BeautifulSoup

url = "https://www.leagueoflegends.com/ko-kr/news/game-updates/patch-25-11-notes/"

# 요청 체크
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'html.parser')

# patch-change-block로 변경 사항 구분
patch_blocks = soup.find_all("div", class_="patch-change-block")
champion_data = []
item_data = []

for block in patch_blocks:
    # 챔피언/아이템 블록 구분
    if block.find("h3", class_="change-title"):
        # 챔피언 정보
        name = block.find("h3", class_="change-title").get_text(strip=True)
        summary = block.find("p", class_="summary")
        summary = summary.get_text(strip=True) if summary else ""
        details = block.find_all("ul")
        details = "\n".join(ul.get_text(" | ", strip=True) for ul in details)
        champion_data.append({
            "name": name,
            "summary": summary,
            "details": details
        })
    elif block.find("h4", class_="change-detail-title ability-title"):
        # 아이템 정보
        name = block.find("h4", class_="change-detail-title ability-title").get_text(strip=True)
        summary = block.find("blockquote", class_="blockquote context")
        summary = summary.get_text(strip=True) if summary else ""
        details = block.find_all("ul")
        details = "\n".join(ul.get_text(" | ", strip=True) for ul in details)
        item_data.append({
            "name": name,
            "summary": summary,
            "details": details
        })

# 결과 확인
for champ in champion_data:
    print(f"챔피언: {champ['name']}\n설명: {champ['summary']}\n상세: {champ['details']}\n")

for item in item_data:
    print(f"아이템: {item['name']}\n설명: {item['summary']}\n상세: {item['details']}\n")

with open('champion_changes.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["name", "summary", "details"])
    writer.writeheader()
    writer.writerows(champion_data)

with open('item_changes.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["name", "summary", "details"])
    writer.writeheader()
    writer.writerows(item_data)