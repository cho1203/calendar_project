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
    """일정 조회 테스트"""
    response = requests.get(f'{BASE_URL}/users/admin001/schedules')
    print("일정 조회:", response.status_code, response.json())

def test_get_user():
    """사용자 조회 테스트"""
    response = requests.get(f'{BASE_URL}/users/sch_001')
    print("사용자 조회:", response.status_code, response.json())

def test_get_schedules():
    """일정 조회 테스트"""
    response = requests.get(f'{BASE_URL}/users/sch_001/schedules')
    print("일정 조회:", response.status_code, response.json())

if __name__ == '__main__':
    print("=== Flask 캘린더 API 테스트 ===")
    test_create_user()
    test_create_calendar()
    test_create_schedule()
    test_get_user()
    test_get_schedules()
    print("=== 테스트 완료 ===")