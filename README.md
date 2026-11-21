# 국방 AI 주간 브리핑

호별 목록에서 브리핑을 선택하면 한 장씩 넘겨 볼 수 있습니다. 제80호는 표지 1장, 요약 1장, 주제 개관 5장, 기사 23장, 정책 과제와 일정 각 1장으로 구성됩니다. 기사 화면에서 상세 보기를 펼치거나 원본 HTML을 열 수 있습니다.

## 다음 호 추가

1. 저장소의 `briefings/`에서 **Add file → Upload files**를 선택합니다.
2. 새 HTML을 올리고 기본 브랜치에 커밋합니다. 기존 호를 보존하려면 새 파일명을 사용하세요. 한글 파일명도 지원합니다.
3. **Actions → Weekly briefing**이 완료되면 실행 결과의 **briefing-website**를 내려받아 압축을 풀고 `index.html`을 엽니다. 배포가 완료되면 [브리핑 웹페이지](https://crayon-sim.github.io/defense-ai-newsletter-briefing/)의 목록도 갱신됩니다.

제80호와 같은 형식은 내장된 호수와 기사 데이터를 읽습니다. 일반 정적 HTML은 제목과 본문을 읽어 `section`, `.slide`, `h1`, `h2` 경계에서 텍스트 슬라이드를 나눕니다. 그림, 표의 배치와 독자적인 스크립트가 필요한 자료는 **원본 보기**로 열 수 있습니다. 별도 이미지가 있다면 HTML에서 사용하는 상대 경로대로 함께 올리세요. 일반 HTML의 호수는 제목이나 파일명에 `제81호` 또는 `issue-081`처럼 표시하세요. 목록은 호수 내림차순입니다.

## 발표

이전·다음 버튼이나 좌우 방향키로 넘깁니다. Home과 End는 첫 장과 마지막 장으로 이동합니다. 목차에서 원하는 장을 바로 선택할 수 있으며, 브라우저에서 지원하는 경우 전체 화면 버튼이 표시됩니다.

## 로컬에서 열기

Python 3.9 이상에서 저장소 루트의 `python3 build.py`를 실행한 뒤 `dist/index.html`을 엽니다. 새 호를 추가하거나 삭제한 후에는 빈 출력 폴더로 다시 빌드하세요. 원하는 위치는 `python3 build.py --out 폴더`로 지정합니다. GitHub Actions는 매번 새 작업 디렉터리에서 빌드합니다.

## GitHub Pages

공개 저장소의 기본 브랜치에 브리핑을 추가하면 GitHub Actions가 사이트를 빌드해 Pages에 게시합니다. 저장소의 **Settings → Pages → Build and deployment → Source**는 **GitHub Actions**로 설정합니다. 수동 재배포는 **Actions → Weekly briefing → Run workflow**에서 할 수 있습니다.
