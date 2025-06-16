import streamlit as st
import pyrebase
import time
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# ---------------------
# Firebase 설정
# ---------------------
firebase_config = {
    "apiKey": "AIzaSyCswFmrOGU3FyLYxwbNPTp7hvQxLfTPIZw",
    "authDomain": "sw-projects-49798.firebaseapp.com",
    "databaseURL": "https://sw-projects-49798-default-rtdb.firebaseio.com",
    "projectId": "sw-projects-49798",
    "storageBucket": "sw-projects-49798.appspot.com",
    "messagingSenderId": "812186368395",
    "appId": "1:812186368395:web:be2f7291ce54396209d78e"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
firestore = firebase.database()
storage = firebase.storage()

# ---------------------
# 세션 상태 초기화
# ---------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.id_token = ""
    st.session_state.user_name = ""
    st.session_state.user_gender = "선택 안함"
    st.session_state.user_phone = ""
    st.session_state.profile_image_url = ""

# ---------------------
# 홈 페이지 클래스
# ---------------------
class Home:
    def __init__(self, login_page, register_page, findpw_page):
        st.title("🏠 Home")
        if st.session_state.get("logged_in"):
            st.success(f"{st.session_state.get('user_email')}님 환영합니다.")

        # 인구 추세 데이터셋 소개
        st.markdown("""
                ---
                **인구 추세 데이터셋**  
                - 설명: 지역별, 연도별 인구 추이를 분석할 수 있는 데이터셋  
                - 주요 변수:  
                  - `year`: 연도  
                  - `region`: 지역  
                  - `population`: 인구 수  
                - 분석 가능한 내용:
                  - 연도별 전체 인구 추이
                  - 지역별 인구 분포
                  - 인구 변화량 및 증감률
                  - 지역별 인구 누적 추이
                """)

# ---------------------
# 로그인 페이지 클래스
# ---------------------
class Login:
    def __init__(self):
        st.title("🔐 로그인")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.id_token = user['idToken']

                user_info = firestore.child("users").child(email.replace(".", "_")).get().val()
                if user_info:
                    st.session_state.user_name = user_info.get("name", "")
                    st.session_state.user_gender = user_info.get("gender", "선택 안함")
                    st.session_state.user_phone = user_info.get("phone", "")
                    st.session_state.profile_image_url = user_info.get("profile_image_url", "")

                st.success("로그인 성공!")
                time.sleep(1)
                st.rerun()
            except Exception:
                st.error("로그인 실패")

# ---------------------
# 회원가입 페이지 클래스
# ---------------------
class Register:
    def __init__(self, login_page_url):
        st.title("📝 회원가입")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        name = st.text_input("성명")
        gender = st.selectbox("성별", ["선택 안함", "남성", "여성"])
        phone = st.text_input("휴대전화번호")

        if st.button("회원가입"):
            try:
                auth.create_user_with_email_and_password(email, password)
                firestore.child("users").child(email.replace(".", "_")).set({
                    "email": email,
                    "name": name,
                    "gender": gender,
                    "phone": phone,
                    "role": "user",
                    "profile_image_url": ""
                })
                st.success("회원가입 성공! 로그인 페이지로 이동합니다.")
                time.sleep(1)
                st.switch_page(login_page_url)
            except Exception:
                st.error("회원가입 실패")

# ---------------------
# 비밀번호 찾기 페이지 클래스
# ---------------------
class FindPassword:
    def __init__(self):
        st.title("🔎 비밀번호 찾기")
        email = st.text_input("이메일")
        if st.button("비밀번호 재설정 메일 전송"):
            try:
                auth.send_password_reset_email(email)
                st.success("비밀번호 재설정 이메일을 전송했습니다.")
                time.sleep(1)
                st.rerun()
            except:
                st.error("이메일 전송 실패")

# ---------------------
# 사용자 정보 수정 페이지 클래스
# ---------------------
class UserInfo:
    def __init__(self):
        st.title("👤 사용자 정보")

        email = st.session_state.get("user_email", "")
        new_email = st.text_input("이메일", value=email)
        name = st.text_input("성명", value=st.session_state.get("user_name", ""))
        gender = st.selectbox(
            "성별",
            ["선택 안함", "남성", "여성"],
            index=["선택 안함", "남성", "여성"].index(st.session_state.get("user_gender", "선택 안함"))
        )
        phone = st.text_input("휴대전화번호", value=st.session_state.get("user_phone", ""))

        uploaded_file = st.file_uploader("프로필 이미지 업로드", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            file_path = f"profiles/{email.replace('.', '_')}.jpg"
            storage.child(file_path).put(uploaded_file, st.session_state.id_token)
            image_url = storage.child(file_path).get_url(st.session_state.id_token)
            st.session_state.profile_image_url = image_url
            st.image(image_url, width=150)
        elif st.session_state.get("profile_image_url"):
            st.image(st.session_state.profile_image_url, width=150)

        if st.button("수정"):
            st.session_state.user_email = new_email
            st.session_state.user_name = name
            st.session_state.user_gender = gender
            st.session_state.user_phone = phone

            firestore.child("users").child(new_email.replace(".", "_")).update({
                "email": new_email,
                "name": name,
                "gender": gender,
                "phone": phone,
                "profile_image_url": st.session_state.get("profile_image_url", "")
            })

            st.success("사용자 정보가 저장되었습니다.")
            time.sleep(1)
            st.rerun()

# ---------------------
# 로그아웃 페이지 클래스
# ---------------------
class Logout:
    def __init__(self):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.id_token = ""
        st.session_state.user_name = ""
        st.session_state.user_gender = "선택 안함"
        st.session_state.user_phone = ""
        st.session_state.profile_image_url = ""
        st.success("로그아웃 되었습니다.")
        time.sleep(1)
        st.rerun()

# ---------------------
# EDA 페이지 클래스
# ---------------------
class EDA:
    def __init__(self):
        st.title("📊 Population Trends Analysis")
        
        # 로그인 체크
        if not st.session_state.get("logged_in"):
            st.warning("로그인이 필요합니다.")
            return
            
        uploaded = st.file_uploader("데이터셋 업로드 (population_trends.csv)", type="csv")
        if not uploaded:
            st.info("population_trends.csv 파일을 업로드 해주세요.")
            return

        df = pd.read_csv(uploaded)
        
        # Firebase에 데이터 저장
        try:
            data = df.to_dict('records')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            firestore.child("population_data").child(timestamp).set(data)
            st.success("데이터가 Firebase에 저장되었습니다.")
        except Exception as e:
            st.error(f"Firebase 저장 중 오류 발생: {str(e)}")

        tabs = st.tabs([
            "1. 기초 통계",
            "2. 연도별 추이",
            "3. 지역별 분석",
            "4. 변화량 분석",
            "5. 시각화"
        ])

        # 1. 기초 통계
        with tabs[0]:
            st.header("📈 기초 통계")
            
            # 데이터 구조 확인
            st.subheader("데이터 구조")
            buffer = io.StringIO()
            df.info(buf=buffer)
            st.text(buffer.getvalue())

            # 결측치 확인
            st.subheader("결측치 확인")
            missing = df.isnull().sum()
            st.bar_chart(missing)
            
            # 중복 확인
            duplicates = df.duplicated().sum()
            st.write(f"- 중복 행 개수: {duplicates}개")

            # 기초 통계량
            st.subheader("기초 통계량")
            st.dataframe(df.describe())

        # 2. 연도별 추이
        with tabs[1]:
            st.header("📅 연도별 추이")
            
            # 연도별 전체 인구 추이 그래프
            yearly_total = df.groupby('year')['population'].sum().reset_index()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(data=yearly_total, x='year', y='population', marker='o')
            plt.title('연도별 전체 인구 추이')
            plt.xlabel('연도')
            plt.ylabel('인구')
            plt.grid(True)
            st.pyplot(fig)

            # 연도별 통계
            st.subheader("연도별 통계")
            yearly_stats = df.groupby('year').agg({
                'population': ['mean', 'min', 'max', 'std']
            }).round(2)
            st.dataframe(yearly_stats)

        # 3. 지역별 분석
        with tabs[2]:
            st.header("🗺️ 지역별 분석")
            
            # 지역별 평균 인구
            region_avg = df.groupby('region')['population'].mean().sort_values(ascending=False)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.barplot(x=region_avg.index, y=region_avg.values)
            plt.title('지역별 평균 인구')
            plt.xticks(rotation=45)
            plt.xlabel('지역')
            plt.ylabel('평균 인구')
            st.pyplot(fig)

            # 지역별 최대/최소 인구
            st.subheader("지역별 최대/최소 인구")
            region_stats = df.groupby('region').agg({
                'population': ['max', 'min']
            }).round(2)
            st.dataframe(region_stats)

        # 4. 변화량 분석
        with tabs[3]:
            st.header("📊 변화량 분석")
            
            # 연도별 변화량 계산
            df['year'] = pd.to_numeric(df['year'])
            df = df.sort_values(['region', 'year'])
            df['population_change'] = df.groupby('region')['population'].diff()
            df['change_rate'] = (df['population_change'] / df['population'].shift(1) * 100).round(2)

            # 변화량 상위 지역
            st.subheader("인구 변화량 상위 지역")
            top_changes = df.nlargest(10, 'population_change')[['region', 'year', 'population_change']]
            st.dataframe(top_changes)

            # 증감률 상위 지역
            st.subheader("인구 증감률 상위 지역")
            top_rates = df.nlargest(10, 'change_rate')[['region', 'year', 'change_rate']]
            st.dataframe(top_rates)

        # 5. 시각화
        with tabs[4]:
            st.header("🎨 시각화")
            
            # 누적 영역 그래프
            st.subheader("지역별 인구 누적 추이")
            pivot_df = df.pivot(index='year', columns='region', values='population')
            
            fig, ax = plt.subplots(figsize=(12, 6))
            pivot_df.plot(kind='area', stacked=True, ax=ax)
            plt.title('지역별 인구 누적 추이')
            plt.xlabel('연도')
            plt.ylabel('인구')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            st.pyplot(fig)

            # 히트맵
            st.subheader("연도-지역 인구 히트맵")
            pivot_df = df.pivot_table(index='year', columns='region', values='population')
            
            fig, ax = plt.subplots(figsize=(12, 8))
            sns.heatmap(pivot_df, annot=True, fmt='.0f', cmap='YlOrRd')
            plt.title('연도-지역 인구 히트맵')
            st.pyplot(fig)


# ---------------------
# 페이지 객체 생성
# ---------------------
Page_Login    = st.Page(Login,    title="Login",    icon="🔐", url_path="login")
Page_Register = st.Page(lambda: Register(Page_Login.url_path), title="Register", icon="📝", url_path="register")
Page_FindPW   = st.Page(FindPassword, title="Find PW", icon="🔎", url_path="find-password")
Page_Home     = st.Page(lambda: Home(Page_Login, Page_Register, Page_FindPW), title="Home", icon="🏠", url_path="home", default=True)
Page_User     = st.Page(UserInfo, title="My Info", icon="👤", url_path="user-info")
Page_Logout   = st.Page(Logout,   title="Logout",  icon="🔓", url_path="logout")
Page_EDA      = st.Page(EDA,      title="EDA",     icon="📊", url_path="eda")

# ---------------------
# 네비게이션 실행
# ---------------------
if st.session_state.logged_in:
    pages = [Page_Home, Page_User, Page_Logout, Page_EDA]
else:
    pages = [Page_Home, Page_Login, Page_Register, Page_FindPW]

selected_page = st.navigation(pages)
selected_page.run()