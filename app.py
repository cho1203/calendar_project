from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # 이 줄 추가
from datetime import datetime, date, time
import json
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

print("=== 🚀 Flask 애플리케이션 시작 ===")

app = Flask(__name__)
print("✅ Flask 앱 생성 완료")

try:
    app.config.from_object(Config)
    print("✅ Config 로드 완료")
    print(f"📊 데이터베이스 URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
except Exception as e:
    print(f"❌ Config 로드 실패: {e}")

try:
    CORS(app)
    print("✅ CORS 설정 완료")
except Exception as e:
    print(f"❌ CORS 설정 실패: {e}")

try:
    db = SQLAlchemy(app)
    print("✅ SQLAlchemy 초기화 완료")
except Exception as e:
    print(f"❌ SQLAlchemy 초기화 실패: {e}")

# 토큰에서 사용자 ID 추출하는 헬퍼 함수 추가
def extract_user_id_from_token(token):
    """
    토큰에서 사용자 ID를 안전하게 추출
    토큰 형식: token_USER_ID_TIMESTAMP
    예: token_sch_001_1753656376.965785 -> sch_001
    """
    try:
        parts = token.split('_')
        if len(parts) >= 3 and parts[0] == 'token':
            # 첫 번째는 'token', 마지막은 timestamp, 중간은 모두 user_id
            user_id_parts = parts[1:-1]  # timestamp 제외하고 user_id 부분들
            user_id = '_'.join(user_id_parts)
            print(f"🔧 토큰 파싱: {token} -> {user_id}")
            return user_id
        return None
    except Exception as e:
        print(f"❌ 토큰 파싱 오류: {e}")
        return None

# 프론트엔드 라우트
@app.route('/')
def index():
    print("📱 메인 페이지 요청")
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    print(f"📁 정적 파일 요청: {filename}")
    return send_from_directory('static', filename)

# 데이터베이스 모델 정의 (기존 구조와 호환)
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), default='user')
    phone = db.Column(db.String(20))
    profile = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    calendars = db.relationship('Calendar', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'user_type': self.user_type,
            'phone': self.phone,
            'profile': self.profile,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'calendars': [calendar.to_dict() for calendar in self.calendars]
        }

class Calendar(db.Model):
    __tablename__ = 'calendars'
    
    id = db.Column(db.Integer, primary_key=True)
    calendar_code = db.Column(db.String(50), unique=True, nullable=False)
    calendar_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    schedules = db.relationship('Schedule', backref='calendar', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'calendar_code': self.calendar_code,
            'calendar_name': self.calendar_name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'schedules': [schedule.to_dict() for schedule in self.schedules]
        }

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.String(50), unique=True, nullable=False)
    date_info = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    # 기존 구조에 맞게 수정 (location_data, participants_data 사용)
    location_data = db.Column(db.JSON)
    participants_data = db.Column(db.JSON)
    estimated_cost = db.Column(db.Integer)
    tags = db.Column(db.JSON)
    importance = db.Column(db.Integer, default=5)
    notes = db.Column(db.Text)
    recurring = db.Column(db.String(100))
    
    # 기존 JSON 컬럼들 (필요시 사용)
    exercise_plan = db.Column(db.JSON)
    health_goals = db.Column(db.JSON)
    family_activities = db.Column(db.JSON)
    gifts_to_bring = db.Column(db.JSON)
    meeting_agenda = db.Column(db.JSON)
    attendees = db.Column(db.JSON)
    preparation_items = db.Column(db.JSON)
    presentation_materials = db.Column(db.JSON)
    client_info = db.Column(db.JSON)
    success_metrics = db.Column(db.JSON)
    study_details = db.Column(db.JSON)
    study_members = db.Column(db.JSON)
    goals = db.Column(db.JSON)
    lesson_details = db.Column(db.JSON)
    equipment_needed = db.Column(db.JSON)
    practice_goals = db.Column(db.JSON)
    medical_info = db.Column(db.JSON)
    insurance_info = db.Column(db.JSON)
    preparation = db.Column(db.JSON)
    
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.id'), nullable=False)
    
    def to_dict(self):
        return {
            'schedule_id': self.schedule_id,
            'date_info': self.date_info.isoformat() if self.date_info else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'title': self.title,
            'description': self.description,
            'location': self.location_data,  # JSON으로 저장된 location_data 사용
            'participants': self.participants_data,  # JSON으로 저장된 participants_data 사용
            'estimated_cost': self.estimated_cost,
            'importance': self.importance,
            'notes': self.notes,
            'recurring': self.recurring,
            'tags': self.tags
        }

print("✅ 데이터베이스 모델 정의 완료")

# JSON 데이터 출력 API - 메인 엔드포인트
@app.route('/json-data', methods=['GET'])
def get_json_data():
    print("\n=== 🌐 JSON 데이터 요청 시작 ===")
    try:
        print("1️⃣ 데이터베이스 연결 테스트...")
        # SQLAlchemy를 사용한 연결 확인
        db.session.execute(text('SELECT 1'))
        print("2️⃣ 데이터베이스 연결 성공")
        
        print("3️⃣ 모든 사용자 조회 중...")
        users = User.query.all()
        print(f"4️⃣ 찾은 사용자 수: {len(users)}")
        
        print("5️⃣ 모든 캘린더 조회 중...")
        calendars = Calendar.query.all()
        print(f"6️⃣ 찾은 캘린더 수: {len(calendars)}")
        
        print("7️⃣ 모든 일정 조회 중...")
        schedules = Schedule.query.all()
        print(f"8️⃣ 찾은 일정 수: {len(schedules)}")
        
        # 사용자 데이터 변환
        users_data = []
        for user in users:
            user_data = {
                'id': user.id,
                'user_id': user.user_id,
                'name': user.name,
                'email': user.email,
                'user_type': user.user_type,
                'phone': user.phone,
                'profile': user.profile,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
            users_data.append(user_data)
            print(f"9️⃣ 사용자 추가: {user.name} ({user.user_id})")
        
        # 캘린더 데이터 변환
        calendars_data = []
        for calendar in calendars:
            calendar_data = {
                'id': calendar.id,
                'calendar_code': calendar.calendar_code,
                'calendar_name': calendar.calendar_name,
                'description': calendar.description,
                'created_at': calendar.created_at.isoformat() if calendar.created_at else None,
                'user_id': calendar.user_id
            }
            calendars_data.append(calendar_data)
            print(f"🔟 캘린더 추가: {calendar.calendar_name} ({calendar.calendar_code})")
        
        # 일정 데이터 변환
        schedules_data = []
        for schedule in schedules:
            # 날짜와 시간을 결합하여 완전한 datetime 생성
            start_datetime = datetime.combine(schedule.date_info, schedule.start_time)
            end_datetime = datetime.combine(schedule.date_info, schedule.end_time)
            
            # location_data와 participants_data 안전하게 처리
            location_str = ""
            if schedule.location_data:
                if isinstance(schedule.location_data, dict):
                    location_str = schedule.location_data.get('name', '')
                else:
                    location_str = str(schedule.location_data)
            
            participants_list = []
            if schedule.participants_data:
                if isinstance(schedule.participants_data, list):
                    participants_list = schedule.participants_data
                else:
                    participants_list = [str(schedule.participants_data)]
            
            schedule_data = {
                'id': schedule.id,
                'schedule_id': schedule.schedule_id,
                'title': schedule.title,
                'description': schedule.description,
                'date_info': schedule.date_info.isoformat(),
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'start_datetime': start_datetime.isoformat(),
                'end_datetime': end_datetime.isoformat(),
                'location_data': schedule.location_data,
                'location_str': location_str,
                'participants_data': schedule.participants_data,
                'participants_list': participants_list,
                'estimated_cost': schedule.estimated_cost,
                'tags': schedule.tags,
                'importance': schedule.importance,
                'notes': schedule.notes,
                'recurring': schedule.recurring,
                'calendar_id': schedule.calendar_id,
                # 추가 JSON 필드들
                'exercise_plan': schedule.exercise_plan,
                'health_goals': schedule.health_goals,
                'family_activities': schedule.family_activities,
                'meeting_agenda': schedule.meeting_agenda,
                'attendees': schedule.attendees,
                'preparation_items': schedule.preparation_items,
                'medical_info': schedule.medical_info
            }
            schedules_data.append(schedule_data)
            print(f"1️⃣1️⃣ 일정 추가: {schedule.title} ({schedule.schedule_id})")
        
        # 데이터베이스 통계 계산
        print("1️⃣2️⃣ 통계 계산 중...")
        
        # 사용자별 캘린더 수 계산
        user_calendar_stats = {}
        for user in users:
            calendar_count = Calendar.query.filter_by(user_id=user.id).count()
            user_calendar_stats[user.user_id] = calendar_count
        
        # 캘린더별 일정 수 계산
        calendar_schedule_stats = {}
        for calendar in calendars:
            schedule_count = Schedule.query.filter_by(calendar_id=calendar.id).count()
            calendar_schedule_stats[calendar.calendar_code] = schedule_count
        
        # 최종 JSON 데이터 구성
        json_data = {
            'success': True,
            'message': '🌐 API 연결 상태 - ✅ Flask MySQL 백엔드 연결됨',
            'timestamp': datetime.utcnow().isoformat(),
            'database_info': {
                'connection_status': 'connected',
                'database_type': 'MySQL',
                'orm': 'SQLAlchemy',
                'total_tables': 3,
                'table_list': ['users', 'calendars', 'schedules']
            },
            'statistics': {
                'total_users': len(users_data),
                'total_calendars': len(calendars_data),
                'total_schedules': len(schedules_data),
                'user_calendar_stats': user_calendar_stats,
                'calendar_schedule_stats': calendar_schedule_stats,
                'avg_calendars_per_user': len(calendars_data) / len(users_data) if len(users_data) > 0 else 0,
                'avg_schedules_per_calendar': len(schedules_data) / len(calendars_data) if len(calendars_data) > 0 else 0
            },
            'data': {
                'users': users_data,
                'calendars': calendars_data,
                'schedules': schedules_data
            },
            'relationships': {
                'user_calendars': user_calendar_stats,
                'calendar_schedules': calendar_schedule_stats
            }
        }
        
        print("1️⃣3️⃣ 최종 JSON 데이터 생성 완료")
        print(f"1️⃣4️⃣ 총 사용자: {len(users_data)}명")
        print(f"1️⃣5️⃣ 총 캘린더: {len(calendars_data)}개")
        print(f"1️⃣6️⃣ 총 일정: {len(schedules_data)}개")
        print(f"1️⃣7️⃣ 평균 사용자당 캘린더: {len(calendars_data) / len(users_data) if len(users_data) > 0 else 0:.2f}개")
        print(f"1️⃣8️⃣ 평균 캘린더당 일정: {len(schedules_data) / len(calendars_data) if len(calendars_data) > 0 else 0:.2f}개")
        
        return jsonify(json_data), 200
        
    except Exception as e:
        print(f"❌ JSON 데이터 조회 오류: {e}")
        print(f"❌ 오류 타입: {type(e).__name__}")
        print(f"❌ 오류 상세: {repr(e)}")
        
        error_data = {
            'success': False,
            'message': '❌ JSON 데이터 조회 중 오류 발생',
            'error': str(e),
            'error_type': type(e).__name__,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(error_data), 500

# 간단한 JSON 요약 데이터 (기존 코드와 호환)
@app.route('/json-summary', methods=['GET'])
def get_json_summary():
    print("\n=== 📊 JSON 요약 데이터 요청 ===")
    try:
        print("1️⃣ 데이터베이스 연결 확인...")
        db.session.execute(text('SELECT 1'))
        print("2️⃣ 연결 성공")
        
        # 간단한 통계 조회
        users_count = User.query.count()
        calendars_count = Calendar.query.count()
        schedules_count = Schedule.query.count()
        
        print(f"3️⃣ 통계 조회 완료: 사용자 {users_count}명, 캘린더 {calendars_count}개, 일정 {schedules_count}개")
        
        summary_data = {
            'success': True,
            'message': '🌐 API 연결 상태 - ✅ Flask MySQL 백엔드 연결됨',
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_users': users_count,
                'total_calendars': calendars_count,
                'total_schedules': schedules_count,
                'database_status': 'connected',
                'server_status': 'running',
                'orm': 'SQLAlchemy'
            }
        }
        
        print(f"✅ 요약 데이터 생성 완료")
        return jsonify(summary_data), 200
        
    except Exception as e:
        print(f"❌ 요약 데이터 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': '요약 데이터 조회 중 오류 발생',
            'error': str(e)
        }), 500

# 사용자별 상세 JSON 데이터 조회
@app.route('/json-data/users/<user_id>', methods=['GET'])
def get_user_json_data(user_id):
    print(f"\n=== 👤 사용자별 JSON 데이터 요청: {user_id} ===")
    try:
        print("1️⃣ 사용자 검색 중...")
        user = User.query.filter_by(user_id=user_id).first()
        
        if not user:
            print("❌ 사용자 없음")
            return jsonify({
                'success': False,
                'message': '사용자를 찾을 수 없습니다.'
            }), 404
        
        print("2️⃣ 사용자 캘린더 조회 중...")
        calendars = Calendar.query.filter_by(user_id=user.id).all()
        print(f"3️⃣ 찾은 캘린더 수: {len(calendars)}")
        
        print("4️⃣ 사용자 일정 조회 중...")
        all_schedules = []
        for calendar in calendars:
            schedules = Schedule.query.filter_by(calendar_id=calendar.id).all()
            all_schedules.extend(schedules)
        print(f"5️⃣ 찾은 일정 수: {len(all_schedules)}")
        
        # 데이터 변환
        user_data = user.to_dict()
        calendars_data = [calendar.to_dict() for calendar in calendars]
        schedules_data = [schedule.to_dict() for schedule in all_schedules]
        
        json_data = {
            'success': True,
            'message': f'🌐 사용자 {user_id} 데이터 조회 완료',
            'timestamp': datetime.utcnow().isoformat(),
            'user_info': user_data,
            'statistics': {
                'calendars_count': len(calendars),
                'schedules_count': len(all_schedules)
            },
            'data': {
                'calendars': calendars_data,
                'schedules': schedules_data
            }
        }
        
        print(f"✅ 사용자 {user_id} 데이터 조회 완료")
        return jsonify(json_data), 200
        
    except Exception as e:
        print(f"❌ 사용자 JSON 데이터 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': '사용자 데이터 조회 중 오류 발생',
            'error': str(e)
        }), 500

# API 상태 확인 (SQL 오류 수정)
@app.route('/api/db/status', methods=['GET'])
def api_status():
    print("\n=== 🔍 API 상태 확인 시작 ===")
    try:
        print("1️⃣ 데이터베이스 연결 테스트 시작...")
        # text() 함수 사용으로 SQL 오류 해결
        result = db.session.execute(text('SELECT 1'))
        print(f"2️⃣ 데이터베이스 쿼리 실행 성공: {result}")
        print("3️⃣ 성공 응답 준비 중...")
        
        response_data = {
            'success': True,
            'message': 'Flask MySQL API 연결됨',
            'database': 'MySQL',
            'status': 'connected'
        }
        print(f"4️⃣ 응답 데이터: {response_data}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패!")
        print(f"❌ 오류 타입: {type(e).__name__}")
        print(f"❌ 오류 메시지: {str(e)}")
        print(f"❌ 오류 상세: {repr(e)}")
        
        error_response = {
            'success': False,
            'message': 'DB 연결 오류',
            'error': str(e),
            'error_type': type(e).__name__
        }
        print(f"❌ 오류 응답: {error_response}")
        
        return jsonify(error_response), 500

# 로그인 API (프론트엔드용)
@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    print("\n=== 🔐 로그인 요청 시작 ===")
    try:
        print("1️⃣ 요청 데이터 파싱 중...")
        data = request.get_json()
        print(f"2️⃣ 받은 데이터: {data}")
        
        user_id = data.get('userId')
        password = data.get('password')
        print(f"3️⃣ 로그인 시도: {user_id}")
        
        print("4️⃣ 사용자 검색 중...")
        user = User.query.filter_by(user_id=user_id).first()
        print(f"5️⃣ 사용자 검색 결과: {user}")
        
        if user:
            print("6️⃣ 비밀번호 확인 중...")
            password_check = user.check_password(password)
            print(f"7️⃣ 비밀번호 확인 결과: {password_check}")
            
            if password_check:
                print("8️⃣ 토큰 생성 중...")
                token = f"token_{user.user_id}_{datetime.utcnow().timestamp()}"
                print(f"9️⃣ 생성된 토큰: {token}")
                
                response_data = {
                    'success': True,
                    'message': '로그인 성공',
                    'data': {
                        'token': token,
                        'user': {
                            'userId': user.user_id,
                            'name': user.name,
                            'email': user.email,
                            'userType': user.user_type
                        }
                    }
                }
                print(f"🔟 성공 응답: {response_data}")
                return jsonify(response_data), 200
            else:
                print("❌ 비밀번호 불일치")
        else:
            print("❌ 사용자 없음")
            
        error_response = {
            'success': False,
            'message': '사용자 ID 또는 비밀번호가 틀렸습니다.'
        }
        print(f"❌ 실패 응답: {error_response}")
        return jsonify(error_response), 401
            
    except Exception as e:
        print(f"❌ 로그인 처리 중 오류: {e}")
        print(f"❌ 오류 상세: {repr(e)}")
        return jsonify({
            'success': False,
            'message': '로그인 처리 중 오류 발생',
            'error': str(e)
        }), 500

# 회원가입 API (프론트엔드 JavaScript가 요청하는 엔드포인트)
@app.route('/api/users', methods=['POST'])
def create_user():
    print("\n=== 👤 회원가입 요청 시작 ===")
    try:
        print("1️⃣ 요청 데이터 파싱 중...")
        data = request.get_json()
        print(f"2️⃣ 받은 데이터: {data}")
        
        # 필수 필드 검증
        required_fields = ['user_id', 'name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field}는 필수 항목입니다.'
                }), 400
        
        # 사용자 ID 중복 확인
        print("3️⃣ 사용자 ID 중복 확인 중...")
        existing_user = User.query.filter_by(user_id=data['user_id']).first()
        if existing_user:
            print("❌ 사용자 ID 중복")
            return jsonify({
                'success': False,
                'error': '이미 사용 중인 사용자 ID입니다.'
            }), 409
        
        # 이메일 중복 확인
        print("4️⃣ 이메일 중복 확인 중...")
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email:
            print("❌ 이메일 중복")
            return jsonify({
                'success': False,
                'error': '이미 사용 중인 이메일입니다.'
            }), 409
        
        # 새 사용자 생성
        print("5️⃣ 새 사용자 생성 중...")
        new_user = User(
            user_id=data['user_id'],
            name=data['name'],
            email=data['email'],
            user_type=data.get('user_type', 'user'),
            phone=data.get('phone'),
            profile=data.get('profile')
        )
        
        # 비밀번호 해시화
        new_user.set_password(data['password'])
        
        # 데이터베이스에 저장
        print("6️⃣ 데이터베이스 저장 중...")
        db.session.add(new_user)
        db.session.commit()
        print(f"7️⃣ 사용자 생성 완료: {new_user.user_id}")
        
        # 기본 캘린더 생성 (선택사항)
        print("8️⃣ 기본 캘린더 생성 중...")
        default_calendar = Calendar(
            calendar_code=f"{new_user.user_id}_default",
            calendar_name="내 캘린더",
            description="기본 캘린더",
            user_id=new_user.id
        )
        db.session.add(default_calendar)
        db.session.commit()
        print(f"9️⃣ 기본 캘린더 생성 완료: {default_calendar.calendar_code}")
        
        response_data = {
            'success': True,
            'message': 'User created successfully',
            'data': {
                'user_id': new_user.user_id,
                'name': new_user.name,
                'email': new_user.email,
                'user_type': new_user.user_type
            }
        }
        print(f"🔟 성공 응답: {response_data}")
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"❌ 회원가입 처리 중 오류: {e}")
        print(f"❌ 오류 상세: {repr(e)}")
        db.session.rollback()  # 오류 시 롤백
        return jsonify({
            'success': False,
            'error': '회원가입 처리 중 오류가 발생했습니다.',
            'message': str(e)
        }), 500

# 사용자 ID 중복 확인 API (프론트엔드의 checkUserIdAvailability 함수용)
@app.route('/api/users/<user_id>', methods=['GET'])
def check_user_exists(user_id):
    print(f"\n=== 🔍 사용자 ID 확인: {user_id} ===")
    try:
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            print("✅ 사용자 존재")
            return jsonify({
                'success': True,
                'exists': True,
                'data': {
                    'user_id': user.user_id,
                    'name': user.name
                }
            }), 200
        else:
            print("❌ 사용자 없음")
            return jsonify({
                'success': False,
                'exists': False,
                'message': '사용자를 찾을 수 없습니다.'
            }), 404
            
    except Exception as e:
        print(f"❌ 사용자 확인 오류: {e}")
        return jsonify({
            'success': False,
            'error': '사용자 확인 중 오류 발생',
            'message': str(e)
        }), 500

# 로그아웃 API
@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    print("🚪 로그아웃 요청")
    return jsonify({
        'success': True,
        'message': '로그아웃 성공'
    }), 200

# 캘린더 목록 조회 (프론트엔드용) - 수정된 토큰 파싱
@app.route('/api/calendars', methods=['GET'])
def get_calendars():
    print("\n=== 📅 캘린더 목록 조회 시작 ===")
    try:
        print("1️⃣ 인증 헤더 확인 중...")
        auth_header = request.headers.get('Authorization')
        print(f"2️⃣ 인증 헤더: {auth_header}")
        
        if not auth_header:
            print("❌ 인증 헤더 없음")
            return jsonify({'success': False, 'message': '인증 토큰이 필요합니다.'}), 401
        
        print("3️⃣ 토큰 파싱 중...")
        token = auth_header.replace('Bearer ', '')
        print(f"4️⃣ 원본 토큰: {token}")
        
        # 개선된 토큰 파싱
        user_id = extract_user_id_from_token(token)
        print(f"5️⃣ 추출된 사용자 ID: {user_id}")
        
        if not user_id:
            print("❌ 토큰에서 사용자 ID 추출 실패")
            return jsonify({'success': False, 'message': '유효하지 않은 토큰입니다.'}), 401
        
        print("6️⃣ 사용자 검색 중...")
        user = User.query.filter_by(user_id=user_id).first()
        print(f"7️⃣ 사용자 검색 결과: {user}")
        
        if not user:
            print("❌ 사용자 없음")
            return jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다.'}), 404
        
        print("8️⃣ 캘린더 검색 중...")
        calendars = Calendar.query.filter_by(user_id=user.id).all()
        print(f"9️⃣ 찾은 캘린더 수: {len(calendars)}")
        
        calendar_list = []
        for calendar in calendars:
            calendar_data = {
                'calendar_id': calendar.calendar_code,
                'calendarId': calendar.calendar_code,
                'calendar_name': calendar.calendar_name,
                'calendarName': calendar.calendar_name,
                'description': calendar.description,
                'created_at': calendar.created_at.isoformat() if calendar.created_at else None
            }
            calendar_list.append(calendar_data)
            print(f"🔟 캘린더 추가: {calendar_data}")
        
        response_data = {
            'success': True,
            'data': {
                'calendars': calendar_list
            }
        }
        print(f"✅ 최종 응답: {response_data}")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ 캘린더 조회 오류: {e}")
        print(f"❌ 오류 상세: {repr(e)}")
        return jsonify({
            'success': False,
            'message': '캘린더 조회 중 오류 발생',
            'error': str(e)
        }), 500

# 캘린더 생성 API (프론트엔드용)
@app.route('/api/calendars', methods=['POST'])
def create_calendar():
    print("\n=== 📅 캘린더 생성 시작 ===")
    try:
        print("1️⃣ 인증 헤더 확인 중...")
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            print("❌ 인증 헤더 없음")
            return jsonify({'success': False, 'message': '인증 토큰이 필요합니다.'}), 401
        
        print("2️⃣ 토큰 파싱 중...")
        token = auth_header.replace('Bearer ', '')
        user_id = extract_user_id_from_token(token)
        print(f"3️⃣ 추출된 사용자 ID: {user_id}")
        
        if not user_id:
            print("❌ 토큰에서 사용자 ID 추출 실패")
            return jsonify({'success': False, 'message': '유효하지 않은 토큰입니다.'}), 401
        
        print("4️⃣ 사용자 검색 중...")
        user = User.query.filter_by(user_id=user_id).first()
        
        if not user:
            print("❌ 사용자 없음")
            return jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다.'}), 404
        
        print("5️⃣ 요청 데이터 파싱 중...")
        data = request.get_json()
        print(f"6️⃣ 받은 데이터: {data}")
        
        calendar_name = data.get('calendarName', '새 캘린더')
        description = data.get('description', '')
        
        print("7️⃣ 새 캘린더 생성 중...")
        new_calendar = Calendar(
            calendar_code=f"{user_id}_{datetime.utcnow().timestamp()}",
            calendar_name=calendar_name,
            description=description,
            user_id=user.id
        )
        
        print("8️⃣ 데이터베이스 저장 중...")
        db.session.add(new_calendar)
        db.session.commit()
        print(f"9️⃣ 캘린더 생성 완료: {new_calendar.calendar_code}")
        
        response_data = {
            'success': True,
            'message': '캘린더가 생성되었습니다.',
            'data': {
                'calendar': {
                    'calendar_id': new_calendar.calendar_code,
                    'calendar_name': new_calendar.calendar_name,
                    'description': new_calendar.description,
                    'created_at': new_calendar.created_at.isoformat()
                }
            }
        }
        print(f"✅ 최종 응답: {response_data}")
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"❌ 캘린더 생성 오류: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '캘린더 생성 중 오류 발생',
            'error': str(e)
        }), 500

# 일정 목록 조회 (프론트엔드용) - 기존 스키마와 호환, 수정된 토큰 파싱
@app.route('/api/schedules/<calendar_id>', methods=['GET'])
def get_schedules_by_calendar(calendar_id):
    print(f"\n=== 📝 일정 목록 조회 시작 (캘린더: {calendar_id}) ===")
    try:
        print("1️⃣ 인증 헤더 확인 중...")
        auth_header = request.headers.get('Authorization')
        print(f"2️⃣ 인증 헤더: {auth_header}")
        
        if not auth_header:
            print("❌ 인증 헤더 없음")
            return jsonify({'success': False, 'message': '인증 토큰이 필요합니다.'}), 401
        
        print("3️⃣ 토큰 파싱 중...")
        token = auth_header.replace('Bearer ', '')
        print(f"4️⃣ 원본 토큰: {token}")
        
        # 개선된 토큰 파싱
        user_id = extract_user_id_from_token(token)
        print(f"5️⃣ 추출된 사용자 ID: {user_id}")
        
        if not user_id:
            print("❌ 토큰에서 사용자 ID 추출 실패")
            return jsonify({'success': False, 'message': '유효하지 않은 토큰입니다.'}), 401
        
        print("6️⃣ 사용자 검색 중...")
        user = User.query.filter_by(user_id=user_id).first()
        print(f"7️⃣ 사용자 검색 결과: {user}")
        
        if not user:
            print("❌ 사용자 없음")
            return jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다.'}), 404
        
        print("8️⃣ 캘린더 검색 중...")
        calendar = Calendar.query.filter_by(calendar_code=calendar_id).first()
        print(f"9️⃣ 캘린더 검색 결과: {calendar}")
        
        if not calendar:
            print("❌ 캘린더 없음")
            return jsonify({'success': False, 'message': '캘린더를 찾을 수 없습니다.'}), 404
        
        # 캘린더 소유자 확인
        if calendar.user_id != user.id:
            print("❌ 캘린더 접근 권한 없음")
            return jsonify({'success': False, 'message': '캘린더에 접근할 권한이 없습니다.'}), 403
        
        print("🔟 일정 검색 중...")
        schedules = Schedule.query.filter_by(calendar_id=calendar.id).all()
        print(f"1️⃣1️⃣ 찾은 일정 수: {len(schedules)}")
        
        schedule_list = []
        for schedule in schedules:
            start_datetime = datetime.combine(schedule.date_info, schedule.start_time)
            end_datetime = datetime.combine(schedule.date_info, schedule.end_time)
            
            # 기존 JSON 구조와 호환되도록 수정
            location_str = ""
            if schedule.location_data:
                if isinstance(schedule.location_data, dict):
                    location_str = schedule.location_data.get('name', '')
                else:
                    location_str = str(schedule.location_data)
            
            participants_str = ""
            if schedule.participants_data:
                if isinstance(schedule.participants_data, list):
                    participants_str = ", ".join([p.get('name', '') for p in schedule.participants_data if isinstance(p, dict)])
                else:
                    participants_str = str(schedule.participants_data)
            
            schedule_data = {
                'id': schedule.schedule_id,
                'title': schedule.title,
                'description': schedule.description,
                'start_time': start_datetime.isoformat(),
                'startTime': start_datetime.isoformat(),
                'end_time': end_datetime.isoformat(),
                'endTime': end_datetime.isoformat(),
                'location': location_str,
                'color': '#667eea',
                'notification': True,
                'importance': schedule.importance,
                'participants': participants_str,
                'notes': schedule.notes,
                'tags': schedule.tags
            }
            schedule_list.append(schedule_data)
            print(f"1️⃣2️⃣ 일정 추가: {schedule_data}")
        
        response_data = {
            'success': True,
            'data': {
                'schedules': schedule_list
            }
        }
        print(f"✅ 최종 응답: {response_data}")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ 일정 조회 오류: {e}")
        print(f"❌ 오류 상세: {repr(e)}")
        return jsonify({
            'success': False,
            'message': '일정 조회 중 오류 발생',
            'error': str(e)
        }), 500

# 일정 추가 API (프론트엔드용)
@app.route('/api/schedules/<calendar_id>', methods=['POST'])
def add_schedule_to_calendar(calendar_id):
    print(f"\n=== 📝 일정 추가 시작 (캘린더: {calendar_id}) ===")
    try:
        print("1️⃣ 인증 헤더 확인 중...")
        auth_header = request.headers.get('Authorization')
        print(f"2️⃣ 인증 헤더: {auth_header}")
        
        if not auth_header:
            print("❌ 인증 헤더 없음")
            return jsonify({'success': False, 'message': '인증 토큰이 필요합니다.'}), 401
        
        print("3️⃣ 토큰 파싱 중...")
        token = auth_header.replace('Bearer ', '')
        print(f"4️⃣ 원본 토큰: {token}")
        
        # 토큰에서 사용자 ID 추출
        user_id = extract_user_id_from_token(token)
        print(f"5️⃣ 추출된 사용자 ID: {user_id}")
        
        if not user_id:
            print("❌ 토큰에서 사용자 ID 추출 실패")
            return jsonify({'success': False, 'message': '유효하지 않은 토큰입니다.'}), 401
        
        print("6️⃣ 사용자 검색 중...")
        user = User.query.filter_by(user_id=user_id).first()
        print(f"7️⃣ 사용자 검색 결과: {user}")
        
        if not user:
            print("❌ 사용자 없음")
            return jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다.'}), 404
        
        print("8️⃣ 캘린더 검색 중...")
        calendar = Calendar.query.filter_by(calendar_code=calendar_id).first()
        print(f"9️⃣ 캘린더 검색 결과: {calendar}")
        
        if not calendar:
            print("❌ 캘린더 없음")
            return jsonify({'success': False, 'message': '캘린더를 찾을 수 없습니다.'}), 404
        
        # 캘린더 소유자 확인
        if calendar.user_id != user.id:
            print("❌ 캘린더 접근 권한 없음")
            return jsonify({'success': False, 'message': '캘린더에 접근할 권한이 없습니다.'}), 403
        
        print("🔟 요청 데이터 파싱 중...")
        data = request.get_json()
        print(f"1️⃣1️⃣ 받은 일정 데이터: {data}")
        
        # 필수 필드 검증
        required_fields = ['title', 'startTime', 'endTime']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field}는 필수 항목입니다.'
                }), 400
        
        print("1️⃣2️⃣ 날짜/시간 파싱 중...")
        # 시작 시간 파싱
        start_datetime = datetime.fromisoformat(data['startTime'].replace('Z', '+00:00'))
        end_datetime = datetime.fromisoformat(data['endTime'].replace('Z', '+00:00'))
        
        print(f"1️⃣3️⃣ 시작 시간: {start_datetime}")
        print(f"1️⃣4️⃣ 종료 시간: {end_datetime}")
        
        # 새 일정 생성
        print("1️⃣5️⃣ 새 일정 생성 중...")
        new_schedule = Schedule(
            schedule_id=f"schedule_{user_id}_{datetime.utcnow().timestamp()}",
            date_info=start_datetime.date(),
            start_time=start_datetime.time(),
            end_time=end_datetime.time(),
            title=data['title'],
            description=data.get('description', ''),
            location_data={'name': data.get('location', '')},
            participants_data=[],
            estimated_cost=0,
            importance=5,
            notes=data.get('notes', ''),
            calendar_id=calendar.id
        )
        
        print("1️⃣6️⃣ 데이터베이스 저장 중...")
        db.session.add(new_schedule)
        db.session.commit()
        print(f"1️⃣7️⃣ 일정 생성 완료: {new_schedule.schedule_id}")
        
        # 응답 데이터 생성
        schedule_data = {
            'id': new_schedule.schedule_id,
            'title': new_schedule.title,
            'description': new_schedule.description,
            'start_time': start_datetime.isoformat(),
            'startTime': start_datetime.isoformat(),
            'end_time': end_datetime.isoformat(),
            'endTime': end_datetime.isoformat(),
            'location': data.get('location', ''),
            'color': '#667eea',
            'notification': True,
            'importance': new_schedule.importance,
            'notes': new_schedule.notes
        }
        
        response_data = {
            'success': True,
            'message': '일정이 추가되었습니다.',
            'data': {
                'schedule': schedule_data
            }
        }
        print(f"✅ 최종 응답: {response_data}")
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"❌ 일정 추가 오류: {e}")
        print(f"❌ 오류 상세: {repr(e)}")
        db.session.rollback()  # 오류 시 롤백
        return jsonify({
            'success': False,
            'message': '일정 추가 중 오류 발생',
            'error': str(e)
        }), 500

# 사용자별 캘린더 생성 API (test_api.py용)
@app.route('/api/users/<user_id>/calendars', methods=['POST'])
def create_user_calendar(user_id):
    print(f"\n=== 📅 사용자별 캘린더 생성: {user_id} ===")
    try:
        data = request.get_json()
        print(f"받은 데이터: {data}")
        
        # 사용자 확인
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다.'}), 404
        
        # 캘린더 생성
        new_calendar = Calendar(
            calendar_code=data['calendar_code'],
            calendar_name=data['calendar_name'],
            description=data.get('description', ''),
            user_id=user.id
        )
        
        db.session.add(new_calendar)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '캘린더가 생성되었습니다.',
            'data': {
                'calendar_code': new_calendar.calendar_code,
                'calendar_name': new_calendar.calendar_name
            }
        }), 201
        
    except Exception as e:
        print(f"❌ 캘린더 생성 오류: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# 캘린더별 일정 생성 API (test_api.py용)
@app.route('/api/calendars/<calendar_code>/schedules', methods=['POST'])
def create_schedule_by_calendar_code(calendar_code):
    print(f"\n=== 📝 캘린더별 일정 생성: {calendar_code} ===")
    try:
        data = request.get_json()
        print(f"받은 데이터: {data}")
        
        # 캘린더 확인
        calendar = Calendar.query.filter_by(calendar_code=calendar_code).first()
        if not calendar:
            return jsonify({'success': False, 'message': '캘린더를 찾을 수 없습니다.'}), 404
        
        # 날짜/시간 파싱
        date_info = datetime.strptime(data['date_info'], '%Y-%m-%d').date()
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        # 일정 생성
        new_schedule = Schedule(
            schedule_id=data['schedule_id'],
            date_info=date_info,
            start_time=start_time,
            end_time=end_time,
            title=data['title'],
            description=data.get('description', ''),
            location_data=data.get('location', {}),
            participants_data=data.get('participants', []),
            estimated_cost=data.get('estimated_cost', 0),
            tags=data.get('tags', []),
            importance=data.get('importance', 5),
            notes=data.get('notes', ''),
            calendar_id=calendar.id
        )
        
        db.session.add(new_schedule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '일정이 생성되었습니다.',
            'data': {
                'schedule_id': new_schedule.schedule_id,
                'title': new_schedule.title
            }
        }), 201
        
    except Exception as e:
        print(f"❌ 일정 생성 오류: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    

# 사용자별 일정 조회 API (test_api.py용)  
@app.route('/api/users/<user_id>/schedules', methods=['GET'])
def get_user_schedules(user_id):
    print(f"\n=== 📝 사용자별 일정 조회: {user_id} ===")
    try:
        # 사용자 확인
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다.'}), 404
        
        # 사용자의 모든 캘린더 조회
        calendars = Calendar.query.filter_by(user_id=user.id).all()
        
        all_schedules = []
        for calendar in calendars:
            schedules = Schedule.query.filter_by(calendar_id=calendar.id).all()
            for schedule in schedules:
                start_datetime = datetime.combine(schedule.date_info, schedule.start_time)
                end_datetime = datetime.combine(schedule.date_info, schedule.end_time)
                
                schedule_data = {
                    'schedule_id': schedule.schedule_id,
                    'title': schedule.title,
                    'description': schedule.description,
                    'date_info': schedule.date_info.isoformat(),
                    'start_time': schedule.start_time.strftime('%H:%M'),
                    'end_time': schedule.end_time.strftime('%H:%M'),
                    'start_datetime': start_datetime.isoformat(),
                    'end_datetime': end_datetime.isoformat(),
                    'location': schedule.location_data,
                    'participants': schedule.participants_data,
                    'estimated_cost': schedule.estimated_cost,
                    'tags': schedule.tags,
                    'importance': schedule.importance,
                    'notes': schedule.notes,
                    'calendar_name': calendar.calendar_name,
                    'calendar_code': calendar.calendar_code
                }
                all_schedules.append(schedule_data)
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'schedules': all_schedules,
                'total_count': len(all_schedules)
            }
        }), 200
        
    except Exception as e:
        print(f"❌ 일정 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("\n=== 🏁 메인 실행 시작 ===")
    try:
        with app.app_context():
            print("1️⃣ 앱 컨텍스트 생성")
            print("2️⃣ 기존 데이터베이스 사용 (테이블 생성 생략)")
    except Exception as e:
        print(f"❌ 초기화 중 오류: {e}")
        print(f"❌ 오류 상세: {repr(e)}")
    
    print("3️⃣ 서버 시작...")
    print("🌐 JSON 데이터: http://localhost:5000/json-data")
    print("📊 요약 데이터: http://localhost:5000/json-summary")
    print("🔍 API 상태: http://localhost:5000/api/db/status")
    app.run(debug=True, host='0.0.0.0', port=5000)