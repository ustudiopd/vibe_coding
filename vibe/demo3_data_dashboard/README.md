# 3. 교직원 데이터 분석 대시보드

## 실습 목표
- 파이썬과 GPT를 활용해 **교직원 데이터 분석 대시보드**를 직접 만들어봅니다.
- 코딩을 처음 접하는 초심자도 따라할 수 있도록, **단계별로 아주 자세하게** 안내합니다.
- 더미데이터 생성(엑셀/CSV 등)은 제외하고, 프로그램 구조와 코딩 실습에 집중합니다.

---

## 실습 준비
1. **폴더 구조 확인**
   - `demo3_data_dashboard` 폴더 안에 아래 파일들이 있는지 확인합니다.
     - `main.py` (메인 프로그램)
     - `requirements.txt` (필요한 패키지 목록)
     - `README.md` (이 안내문)
     - `staff_dummy.csv` (샘플 교직원 데이터)

2. **파이썬 설치**
   - [python.org](https://www.python.org/downloads/)에서 Python 3.x 버전을 설치합니다.
   - 설치 시 "Add Python to PATH" 옵션을 꼭 체크하세요.

3. **필요한 패키지 설치**
   - 명령 프롬프트(또는 PowerShell)에서 아래 명령어를 입력합니다.
     ```bash
     cd demo3_data_dashboard
     pip install -r requirements.txt
     ```

---

## 실습 플로우 (GPT 활용)

### 1. 프로그램 구조/기능 설계 프롬프트 예시
- **프롬프트 예시:**
  > "교직원 데이터를 분석하고 시각화하는 대시보드 프로그램을 파이썬 tkinter로 만들고 싶어요. 부서별, 성별, 연령대별로 그룹화하고, 필터링 기능도 넣어주세요. 그래프는 matplotlib으로 그려주세요. 코드 예시를 단계별로 알려주세요."

### 2. 코드 생성 및 설명 요청 프롬프트 예시
- **프롬프트 예시:**
  > "위 요구사항에 맞는 파이썬 코드를 한 파일로 만들어주세요. 각 부분(데이터 로딩, 필터링, 그래프 그리기, GUI 등)에 주석을 자세히 달아주세요."

- **프롬프트 예시:**
  > "그래프 그룹화 옵션(부서별/성별/연령대별)을 체크박스로 선택할 수 있게 해주세요."

### 3. 코드 실행 방법 안내
1. **폴더 이동**
   - 명령 프롬프트에서 아래처럼 입력합니다.
     ```bash
     cd demo3_data_dashboard
     ```
2. **프로그램 실행**
   - 아래 명령어로 프로그램을 실행합니다.
     ```bash
     python main.py
     ```
3. **실행 결과 확인**
   - 프로그램이 실행되면, 필터와 그룹화 옵션을 선택하여 데이터를 분석하고 시각화할 수 있습니다.
   - 엑셀로 내보내기 기능으로 현재 데이터를 저장할 수 있습니다.

### 4. 코드 수정/확장 요청 프롬프트 예시
- **프롬프트 예시:**
  > "그래프 색상과 스타일을 더 보기 좋게 수정해 주세요."
- **프롬프트 예시:**
  > "통계 정보(평균, 최대, 최소 등)를 더 자세히 보여주는 기능을 추가해 주세요."
- **프롬프트 예시:**
  > "창 크기를 조절할 때 그래프도 자동으로 크기가 조절되게 해주세요."

---

## 실습 TIP
- **프롬프트는 최대한 구체적으로, 하고 싶은 기능을 자연어로 설명하면 됩니다.**
- "~을 추가해줘", "~을 고쳐줘", "~처럼 만들어줘" 등 일상적인 말로 요청해도 GPT가 이해합니다.
- 코드를 복사해서 붙여넣을 때, 에러가 나면 에러 메시지를 그대로 GPT에게 보여주면 해결 방법을 안내해줍니다.

---

## 사용 기술
- Tkinter (GUI)
- pandas (데이터 처리)
- matplotlib (데이터 시각화)
- openpyxl (엑셀 파일 처리)

---

**이 안내문을 따라 차근차근 실습하면, 코딩을 처음 접하는 분도 GPT와 함께 데이터 분석 대시보드를 완성할 수 있습니다!** 