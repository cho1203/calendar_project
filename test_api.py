import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_create_user():
    """사용자 생성 테스트"""
    user_data = {
        "user_id": "admin001",
        "name": "관리자",
        "email": "admin@calendar.com",
        "password": "admin123",
        "user_type": "admin",
        "phone": "010-1111-1111",
        "profile": "시스템 관리자입니다."
    }
        
    response = requests.post(f'{BASE_URL}/users', json=user_data)
    print("사용자 생성:", response.status_code, response.json())

def test_create_calendar():
    """캘린더 생성 테스트"""
    calendar_data = {
        "calendar_code": "cal_personal_001",
        "calendar_name": "개인 일정",
        "description": "개인적인 약속과 일상 기록"
    }
        
    response = requests.post(f'{BASE_URL}/users/admin001/calendars', json=calendar_data)
    print("캘린더 생성:", response.status_code, response.json())

def test_create_schedule():
    """일정 생성 테스트"""
    schedule_data = {
        "schedule_id": "sch_001",
        "date_info": "2025-08-01",
        "start_time": "19:00",
        "end_time": "21:00",
        "title": "친구들과 치킨 먹기",
        "description": "대학 동기들과 오랜만에 만나서 치킨과 맥주",
        "location": {
            "name": "교촌치킨 강남점",
            "address": "서울시 강남구 테헤란로 123",
            "phone": "02-1234-5678"
        },
        "participants": [
            {
                "name": "지훈",
                "contact": "010-2222-3333",
                "relation": "대학동기"
            }
        ],
        "estimated_cost": 35000,
        "tags": ["친구", "치킨", "대학동기"],
        "importance": 7,
        "notes": "지훈이가 새 직장 구한 거 축하하기"
    }
        
    response = requests.post(f'{BASE_URL}/calendars/cal_personal_001/schedules', json=schedule_data)
    print("일정 생성:", response.status_code, response.json())

def test_get_user():
    """사용자 조회 테스트"""
    response = requests.get(f'{BASE_URL}/users/admin001')
    print("사용자 조회:", response.status_code, response.json())

def test_get_schedules():
    """일정 조회 테스트 - 사용자별 모든 일정"""
    response = requests.get(f'{BASE_URL}/users/admin001/schedules')
    print("사용자별 일정 조회:", response.status_code, response.json())

def test_get_calendar_schedules():
    """캘린더별 일정 조회 테스트"""
    response = requests.get(f'{BASE_URL}/schedules/cal_personal_001')
    print("캘린더별 일정 조회:", response.status_code, response.json())

def test_create_another_user():
    """다른 사용자 생성 테스트"""
    user_data = {
        "user_id": "user002",
        "name": "김철수",
        "email": "user002@calendar.com",
        "password": "user123",
        "user_type": "user",
        "phone": "010-2222-2222",
        "profile": "일반 사용자입니다."
    }
        
    response = requests.post(f'{BASE_URL}/users', json=user_data)
    print("다른 사용자 생성:", response.status_code, response.json())

def test_create_another_calendar():
    """다른 사용자의 캘린더 생성 테스트"""
    calendar_data = {
        "calendar_code": "cal_work_001",
        "calendar_name": "업무 일정",
        "description": "회사 업무 관련 일정"
    }
        
    response = requests.post(f'{BASE_URL}/users/user002/calendars', json=calendar_data)
    print("다른 사용자 캘린더 생성:", response.status_code, response.json())

def test_create_another_schedule():
    """다른 사용자의 일정 생성 테스트"""
    schedule_data = {
        "schedule_id": "sch_002",
        "date_info": "2025-08-02",
        "start_time": "09:00",
        "end_time": "10:00",
        "title": "팀 회의",
        "description": "주간 팀 미팅",
        "location": {
            "name": "회의실 A",
            "address": "서울시 강남구 회사빌딩 5층",
            "phone": "02-1234-9999"
        },
        "participants": [
            {
                "name": "박대리",
                "contact": "010-3333-4444",
                "relation": "동료"
            }
        ],
        "estimated_cost": 0,
        "tags": ["업무", "회의", "팀"],
        "importance": 8,
        "notes": "주간 진행사항 공유"
    }
        
    response = requests.post(f'{BASE_URL}/calendars/cal_work_001/schedules', json=schedule_data)
    print("다른 사용자 일정 생성:", response.status_code, response.json())

def test_check_all_schedules():
    """모든 일정이 보이는지 확인 - admin001로 조회"""
    print("\n=== admin001이 볼 수 있는 모든 일정 확인 ===")
    response = requests.get(f'{BASE_URL}/users/admin001/schedules')
    result = response.json()
    
    if result.get('success'):
        schedules = result.get('data', {}).get('schedules', [])
        print(f"총 일정 수: {len(schedules)}")
        
        for schedule in schedules:
            owner_info = "내 일정" if schedule.get('is_my_schedule') else f"{schedule.get('owner_name')}님의 일정"
            print(f"- {schedule.get('title')} ({owner_info}) - {schedule.get('date_info')}")
    else:
        print("일정 조회 실패:", result)

if __name__ == '__main__':
    print("=== Flask 캘린더 API 테스트 ===")
    
    # 기본 테스트
    print("\n1. 기본 사용자 및 일정 생성")
    test_create_user()
    test_create_calendar()
    test_create_schedule()
    
    # 다른 사용자 생성하여 일정 다양화
    print("\n2. 다른 사용자 및 일정 생성")
    test_create_another_user()
    test_create_another_calendar()
    test_create_another_schedule()
    
    # 조회 테스트
    print("\n3. 조회 테스트")
    test_get_user()
    test_get_schedules()
    test_get_calendar_schedules()
    
    # 모든 일정 표시 확인
    print("\n4. 모든 일정 표시 확인")
    test_check_all_schedules()
    
    print("\n=== 테스트 완료 ===")
    print("\n📌 이제 웹 브라우저에서 http://localhost:5000 접속하여")
    print("   admin001로 로그인하면 모든 사용자의 일정이 보입니다!")
    print("   - 파란색: 내 일정 (admin001)")
    print("   - 초록색: 다른 사람 일정 (user002)")