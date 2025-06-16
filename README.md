# population-eda-app2
# Population Trends Analysis App

인구 추세를 분석하고 시각화하는 Streamlit 웹 애플리케이션입니다.

## 주요 기능

- Firebase 인증을 통한 사용자 로그인/회원가입
- 인구 데이터 업로드 및 Firebase 저장
- 다양한 인구 분석 및 시각화:
  - 기초 통계 분석
  - 연도별 인구 추이
  - 지역별 인구 분석
  - 인구 변화량 분석
  - 시각화 (그래프, 히트맵 등)

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. Firebase 설정:
- Firebase 프로젝트 생성
- `app_eda.py` 파일의 `firebase_config` 딕셔너리에 Firebase 프로젝트 설정값 입력

## 실행 방법

```bash
python -m streamlit run app_eda.py
```

## 데이터 형식

`population_trends.csv` 파일은 다음 컬럼을 포함해야 합니다:
- year: 연도
- region: 지역
- population: 인구 수

## 사용된 기술

- Streamlit
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Firebase (Pyrebase)