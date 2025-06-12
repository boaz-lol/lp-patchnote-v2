import json
from os import major
from textwrap import dedent

import requests
from bs4 import BeautifulSoup

# 패치 버전 읽기
def read_patch_version(filename="current_patch.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().strip()

# 패치 버전 자동 증가
def increase_patch_version(patch_version):
    parts = patch_version.split("-")
    if len(parts) != 2:
        raise ValueError("패치 버전 형식이 xx-yy이어야 합니다.")
    major, minor = int(parts[0]), int(parts[1])
    minor += 1
    return f"{major}-{minor:02d}"

# 패치노트 url 템플릿
def get_patch_url(version):
    return f"https://www.leagueoflegends.com/ko-kr/news/game-updates/patch-{version}-notes/"

# 크롤링
def crawl_patch(url, patch_version):
    # 요청 체크
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # patch-change-block로 변경 사항 구분
    patch_blocks = soup.find_all("div", class_="patch-change-block")
    champion_data, item_data = [], []

    def extract_changes(ul):
        changes = []
        if not ul:
            return changes
        for li in ul.find_all("li"):
            strong = li.find("strong")
            key = strong.get_text(strip=True) if strong else ""
            if strong:
                strong.extract()
            value = li.get_text(strip=True)
            if key:
                changes.append({key: value})
            else:
                changes.append(value)
        return changes

    for block in patch_blocks:
        # 챔피언/아이템 블록 구분
        champ_title = block.find("h3", class_="change-title")
        if champ_title:
            champ_name = champ_title.get_text(strip=True)
            skills = []

            for h4 in block.find_all("h4", class_="change-detail-title"):
                skill_name = h4.get_text(strip=True)
                ul = h4.find_next_sibling("ul")
                changes = extract_changes(ul)
                if changes:
                    skills.append({
                        "skill_name": skill_name,
                        "changes": changes
                    })
            champion_data.append({
                "name": champ_name,
                "skills": skills
            })
            continue

        item_title = block.find("h4", class_="change-detail-title ability-title")
        if item_title:
            item_name = item_title.get_text(strip=True)
            uls = block.find_all("ul")
            changes = []
            for ul in uls:
                changes += extract_changes(ul)
            item_data.append({
                "name": item_name,
                "changes": changes
            })
            continue

    for champ in champion_data:
        print(f"챔피언: {champ['name']}")
        for skill in champ['skills']:
            print(f"  - {skill['skill_name']}:")
            for c in skill['changes']:
                print(f"    • {c}")
        print()

    for item in item_data:
        print(f"아이템: {item['name']}")
        for c in item['changes']:
            print(f"  • {c}")
        print()

    with open(f'champion_patch_{patch_version}.json', 'w', encoding='utf-8') as f:
        json.dump(champion_data, f, ensure_ascii=False, indent=2)

    with open(f'item_patch_{patch_version}.json', 'w', encoding='utf-8') as f:
        json.dump(item_data, f, ensure_ascii=False, indent=2)

    return True

if __name__ == "__main__":
    patch_version = read_patch_version()
    url = get_patch_url(patch_version)
    print(f"Try Crawling: {patch_version} ({url}")
    try:
        crwal_success = crawl_patch(url, patch_version)
        if crwal_success:
            next_version = increase_patch_version(patch_version)
            with open("current_patch.txt", "w", encoding="utf-8") as f:
                f.write(next_version)
            print(f"Crawling Success! Next Patch Version is {next_version}")
    except Exception as e:
        print(f"Crawling Fail: {e}")

