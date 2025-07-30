# create_sample_data.py - 샘플 데이터 자동 생성

import sys
import os
from datetime import datetime, date, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Calendar, Schedule

def create_sample_data():
    print("=== 🎯 샘플 데이터 생성 시작 ===")
    
    with app.app_context():
        try:
            # 1. 샘플 사용자 생성
            print("1️⃣ 샘플 사용자 생성 중...")
            
            sample_users = [
                {
                    'user_id': 'admin001',
                    'name': '관리자',
                    'email': 'admin@example.com',
                    'password': 'admin123',
                    'user_type': 'admin',
                    'phone': '010-1234-5678',
                    'profile': '시스템 관리자'
                },
                {
                    'user_id': 'sch_001',
                    'name': '조정후',
                    'email': 'jeonghoo@example.com',
                    'password': 'user123',
                    'user_type': 'user',
                    'phone': '010-2345-6789',
                    'profile': 'UX/UI 디자이너'
                },
                {
                    'user_id': 'user002',
                    'name': '김철수',
                    'email': 'chulsoo@example.com',
                    'password': 'user123',
                    'user_type': 'user',
                    'phone': '010-3456-7890',
                    'profile': '백엔드 개발자'
                },
                {
                    'user_id': 'user003',
                    'name': '박영희',
                    'email': 'younghee@example.com',
                    'password': 'user123',
                    'user_type': 'user',
                    'phone': '010-4567-8901',
                    'profile': '프론트엔드 개발자'
                }
            ]
            
            created_users = {}
            for user_data in sample_users:
                existing_user = User.query.filter_by(user_id=user_data['user_id']).first()
                if not existing_user:
                    new_user = User(
                        user_id=user_data['user_id'],
                        name=user_data['name'],
                        email=user_data['email'],
                        user_type=user_data['user_type'],
                        phone=user_data['phone'],
                        profile=user_data['profile']
                    )
                    new_user.set_password(user_data['password'])
                    db.session.add(new_user)
                    db.session.flush()  # ID 생성을 위해
                    created_users[user_data['user_id']] = new_user
                    print(f"   ✅ 사용자 생성: {user_data['name']} ({user_data['user_id']})")
                else:
                    created_users[user_data['user_id']] = existing_user
                    print(f"   ⚡ 기존 사용자: {existing_user.name} ({user_data['user_id']})")
            
            # 2. 샘플 캘린더 생성
            print("\n2️⃣ 샘플 캘린더 생성 중...")
            
            sample_calendars = [
                {
                    'calendar_code': 'sample_admin_personal',
                    'calendar_name': '관리자 개인 일정',
                    'description': '관리자의 개인적인 약속과 일정',
                    'user_id': 'admin001'
                },
                {
                    'calendar_code': 'sample_sch_personal',
                    'calendar_name': '조정후 개인 일정',
                    'description': '조정후의 개인적인 약속과 디자인 작업',
                    'user_id': 'sch_001'
                },
                {
                    'calendar_code': 'sample_sch_work',
                    'calendar_name': '조정후 업무 일정',
                    'description': '디자인 프로젝트 및 클라이언트 미팅',
                    'user_id': 'sch_001'
                },
                {
                    'calendar_code': 'sample_user002_work',
                    'calendar_name': '김철수 업무 일정',
                    'description': '개발 업무 및 팀 회의',
                    'user_id': 'user002'
                }
            ]
            
            created_calendars = {}
            for cal_data in sample_calendars:
                existing_cal = Calendar.query.filter_by(calendar_code=cal_data['calendar_code']).first()
                if not existing_cal:
                    user = created_users[cal_data['user_id']]
                    new_calendar = Calendar(
                        calendar_code=cal_data['calendar_code'],
                        calendar_name=cal_data['calendar_name'],
                        description=cal_data['description'],
                        user_id=user.id
                    )
                    db.session.add(new_calendar)
                    db.session.flush()
                    created_calendars[cal_data['calendar_code']] = new_calendar
                    print(f"   ✅ 캘린더 생성: {cal_data['calendar_name']}")
                else:
                    created_calendars[cal_data['calendar_code']] = existing_cal
                    print(f"   ⚡ 기존 캘린더: {existing_cal.calendar_name}")
            
            # 3. 샘플 일정 생성 (sch_001 중심)
            print("\n3️⃣ 샘플 일정 생성 중...")
            
            sample_schedules = [
                # sch_001 개인 일정
                {
                    'schedule_id': 'sample_sch_design_001',
                    'date_info': date(2025, 8, 1),
                    'start_time': time(9, 0),
                    'end_time': time(12, 0),
                    'title': '피그마 UI 디자인 작업',
                    'description': 'E-commerce 앱 메인 화면 디자인',
                    'location_data': {'name': '홈 오피스', 'address': '서울시 강남구 집'},
                    'participants_data': [],
                    'estimated_cost': 0,
                    'tags': ['디자인', '피그마', 'UI/UX'],
                    'importance': 8,
                    'notes': '모바일 우선 디자인으로 진행',
                    'calendar_code': 'sample_sch_personal'
                },
                {
                    'schedule_id': 'sample_sch_meeting_001',
                    'date_info': date(2025, 8, 1),
                    'start_time': time(14, 0),
                    'end_time': time(16, 0),
                    'title': '클라이언트 미팅',
                    'description': 'ABC 회사 웹사이트 리뉴얼 프로젝트 킥오프',
                    'location_data': {'name': 'ABC 회사', 'address': '서울시 강남구 테헤란로 456', 'phone': '02-9876-5432'},
                    'participants_data': [{'name': '김대표', 'contact': '010-1111-2222', 'relation': '클라이언트'}],
                    'estimated_cost': 50000,
                    'tags': ['미팅', '클라이언트', '웹디자인'],
                    'importance': 9,
                    'notes': '포트폴리오 준비하기',
                    'calendar_code': 'sample_sch_work'
                },
                {
                    'schedule_id': 'sample_sch_study_001',
                    'date_info': date(2025, 8, 2),
                    'start_time': time(10, 30),
                    'end_time': time(11, 30),
                    'title': '디자인 시스템 스터디',
                    'description': '동료 디자이너들과 디자인 시스템 공부',
                    'location_data': {'name': '카페 봄', 'address': '서울시 강남구 논현로 123'},
                    'participants_data': [{'name': '이수정', 'contact': '010-3333-4444', 'relation': '동료'}],
                    'estimated_cost': 15000,
                    'tags': ['스터디', '디자인시스템', '동료'],
                    'importance': 7,
                    'notes': '아토믹 디자인 방법론 리뷰',
                    'calendar_code': 'sample_sch_personal'
                },
                {
                    'schedule_id': 'sample_sch_chicken_001',
                    'date_info': date(2025, 8, 3),
                    'start_time': time(19, 0),
                    'end_time': time(21, 0),
                    'title': '친구들과 치킨 파티',
                    'description': '대학 동기들과 오랜만에 만나는 날',
                    'location_data': {'name': '교촌치킨 강남점', 'address': '서울시 강남구 테헤란로 789', 'phone': '02-1234-5678'},
                    'participants_data': [
                        {'name': '지훈', 'contact': '010-5555-6666', 'relation': '대학동기'},
                        {'name': '민서', 'contact': '010-7777-8888', 'relation': '대학동기'}
                    ],
                    'estimated_cost': 35000,
                    'tags': ['친구', '치킨', '대학동기'],
                    'importance': 6,
                    'notes': '지훈이 승진 축하하기',
                    'calendar_code': 'sample_sch_personal'
                },
                {
                    'schedule_id': 'sample_sch_prototype_001',
                    'date_info': date(2025, 8, 5),
                    'start_time': time(15, 0),
                    'end_time': time(18, 0),
                    'title': '프로토타입 제작',
                    'description': '모바일 앱 인터랙션 프로토타이핑',
                    'location_data': {'name': '홈 오피스', 'address': '서울시 강남구 집'},
                    'participants_data': [],
                    'estimated_cost': 0,
                    'tags': ['프로토타이핑', '모바일', '인터랙션'],
                    'importance': 8,
                    'notes': 'Framer로 애니메이션 구현',
                    'calendar_code': 'sample_sch_work'
                },
                # 다른 사용자 일정
                {
                    'schedule_id': 'sample_admin_meeting_001',
                    'date_info': date(2025, 8, 2),
                    'start_time': time(9, 0),
                    'end_time': time(10, 0),
                    'title': '전체 팀 회의',
                    'description': '월간 전체 팀 미팅 및 성과 발표',
                    'location_data': {'name': '대회의실', 'address': '서울시 강남구 회사 본사 10층'},
                    'participants_data': [{'name': '전체팀', 'contact': '', 'relation': '동료'}],
                    'estimated_cost': 0,
                    'tags': ['회의', '팀미팅', '월간보고'],
                    'importance': 9,
                    'notes': '월간 성과 보고서 준비',
                    'calendar_code': 'sample_admin_personal'
                },
                {
                    'schedule_id': 'sample_dev_scrum_001',
                    'date_info': date(2025, 8, 1),
                    'start_time': time(13, 0),
                    'end_time': time(14, 0),
                    'title': '개발팀 스크럼',
                    'description': '일일 스크럼 미팅',
                    'location_data': {'name': '개발팀 회의실', 'address': '서울시 강남구 회사 5층'},
                    'participants_data': [{'name': '개발팀', 'contact': '', 'relation': '팀원'}],
                    'estimated_cost': 0,
                    'tags': ['개발', '스크럼', '일일미팅'],
                    'importance': 7,
                    'notes': '스프린트 진행상황 공유',
                    'calendar_code': 'sample_user002_work'
                }
            ]
            
            created_count = 0
            for sch_data in sample_schedules:
                existing_sch = Schedule.query.filter_by(schedule_id=sch_data['schedule_id']).first()
                if not existing_sch:
                    calendar = created_calendars[sch_data['calendar_code']]
                    new_schedule = Schedule(
                        schedule_id=sch_data['schedule_id'],
                        date_info=sch_data['date_info'],
                        start_time=sch_data['start_time'],
                        end_time=sch_data['end_time'],
                        title=sch_data['title'],
                        description=sch_data['description'],
                        location_data=sch_data['location_data'],
                        participants_data=sch_data['participants_data'],
                        estimated_cost=sch_data['estimated_cost'],
                        tags=sch_data['tags'],
                        importance=sch_data['importance'],
                        notes=sch_data['notes'],
                        calendar_id=calendar.id
                    )
                    db.session.add(new_schedule)
                    created_count += 1
                    print(f"   ✅ 일정 생성: {sch_data['title']} ({sch_data['date_info']})")
                else:
                    print(f"   ⚡ 기존 일정: {existing_sch.title}")
            
            # 4. 커밋
            db.session.commit()
            print(f"\n🎉 샘플 데이터 생성 완료!")
            print(f"   - 사용자: {len(sample_users)}명")
            print(f"   - 캘린더: {len(sample_calendars)}개") 
            print(f"   - 새 일정: {created_count}개")
            
            # 5. 결과 확인
            print(f"\n📊 최종 데이터 현황:")
            total_users = User.query.count()
            total_calendars = Calendar.query.count()
            total_schedules = Schedule.query.count()
            print(f"   - 전체 사용자: {total_users}명")
            print(f"   - 전체 캘린더: {total_calendars}개")
            print(f"   - 전체 일정: {total_schedules}개")
            
            # sch_001 사용자 일정 확인
            sch_user = User.query.filter_by(user_id='sch_001').first()
            if sch_user:
                sch_calendars = Calendar.query.filter_by(user_id=sch_user.id).all()
                sch_schedule_count = 0
                for cal in sch_calendars:
                    sch_schedule_count += Schedule.query.filter_by(calendar_id=cal.id).count()
                print(f"   - sch_001 사용자 일정: {sch_schedule_count}개")
            
        except Exception as e:
            print(f"❌ 샘플 데이터 생성 오류: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_sample_data()