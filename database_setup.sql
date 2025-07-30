-- 새로운 database_setup.sql - 기존 파일 내용을 모두 지우고 이것으로 교체

-- MySQL 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS calendar_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE calendar_db;

-- 기존 데이터 정리 (필요한 경우)
-- DELETE FROM schedules WHERE schedule_id LIKE 'sample_%';
-- DELETE FROM calendars WHERE calendar_code LIKE 'sample_%';
-- DELETE FROM users WHERE user_id IN ('sample_user1', 'sample_user2');

-- 샘플 사용자 데이터 추가
INSERT IGNORE INTO users (user_id, name, email, password_hash, user_type, phone, profile, created_at) 
VALUES 
-- sch_001 사용자 (비밀번호: user123)
('sch_001', '조정후', 'jeonghoo@example.com', 
 'scrypt:32768:8:1$mK5qPvQvJqX9xqQM$f9e8a5d2c3b1a0e9f8d7c6b5a4e3f2e1d0c9b8a7f6e5d4c3b2a1', 
 'user', '010-2345-6789', 'UX/UI 디자이너', NOW()),

-- admin001 사용자 (비밀번호: admin123) 
('admin001', '관리자', 'admin@example.com',
 'scrypt:32768:8:1$mK5qPvQvJqX9xqQM$f9e8a5d2c3b1a0e9f8d7c6b5a4e3f2e1d0c9b8a7f6e5d4c3b2a1',
 'admin', '010-1234-5678', '시스템 관리자', NOW()),

-- 다른 샘플 사용자들
('user002', '김철수', 'chulsoo@example.com',
 'scrypt:32768:8:1$mK5qPvQvJqX9xqQM$f9e8a5d2c3b1a0e9f8d7c6b5a4e3f2e1d0c9b8a7f6e5d4c3b2a1',
 'user', '010-3456-7890', '백엔드 개발자', NOW()),

('user003', '박영희', 'younghee@example.com',
 'scrypt:32768:8:1$mK5qPvQvJqX9xqQM$f9e8a5d2c3b1a0e9f8d7c6b5a4e3f2e1d0c9b8a7f6e5d4c3b2a1',
 'user', '010-4567-8901', '프론트엔드 개발자', NOW());

-- 샘플 캘린더 추가
INSERT IGNORE INTO calendars (calendar_code, calendar_name, description, created_at, user_id) 
VALUES 
-- sch_001의 캘린더들
('sample_sch_personal', '조정후 개인 일정', '조정후의 개인적인 약속과 디자인 작업', NOW(),
 (SELECT id FROM users WHERE user_id = 'sch_001')),

('sample_sch_work', '조정후 업무 일정', '디자인 프로젝트 및 클라이언트 미팅', NOW(),
 (SELECT id FROM users WHERE user_id = 'sch_001')),

-- 다른 사용자들 캘린더
('sample_admin_personal', '관리자 개인 일정', '관리자의 개인적인 약속과 일정', NOW(),
 (SELECT id FROM users WHERE user_id = 'admin001')),

('sample_user002_work', '김철수 업무 일정', '개발 업무 및 팀 회의', NOW(),
 (SELECT id FROM users WHERE user_id = 'user002'));

-- sch_001 사용자의 샘플 일정들 추가
INSERT IGNORE INTO schedules (
    schedule_id, date_info, start_time, end_time, title, description, 
    location_data, participants_data, estimated_cost, tags, importance, notes, calendar_id
) VALUES 

-- sch_001 개인 일정
('sample_sch_design_001', '2025-08-06', '09:00:00', '12:00:00', 
 '🎨 피그마 UI 디자인 작업', 'E-commerce 앱 메인 화면 디자인 작업',
 '{"name": "홈 오피스", "address": "서울시 강남구 집"}', 
 '[]', 0, '["디자인", "피그마", "UI/UX"]', 8, '모바일 우선 디자인으로 진행',
 (SELECT id FROM calendars WHERE calendar_code = 'sample_sch_personal')),

('sample_sch_meeting_001', '2025-08-07', '14:00:00', '16:00:00',
 '🤝 클라이언트 미팅', 'ABC 회사 웹사이트 리뉴얼 프로젝트 논의',
 '{"name": "ABC 회사", "address": "서울시 강남구 테헤란로 456", "phone": "02-9876-5432"}',
 '[{"name": "김대표", "contact": "010-1111-2222", "relation": "클라이언트"}]',
 50000, '["미팅", "클라이언트", "웹디자인"]', 9, '포트폴리오 준비하기',
 (SELECT id FROM calendars WHERE calendar_code = 'sample_sch_work')),

('sample_sch_study_001', '2025-08-08', '10:30:00', '11:30:00',
 '📚 디자인 시스템 스터디', '동료 디자이너들과 디자인 시스템 공부',
 '{"name": "카페 봄", "address": "서울시 강남구 논현로 123"}',
 '[{"name": "이수정", "contact": "010-3333-4444", "relation": "동료"}]',
 15000, '["스터디", "디자인시스템", "동료"]', 7, '아토믹 디자인 방법론 리뷰',
 (SELECT id FROM calendars WHERE calendar_code = 'sample_sch_personal')),

('sample_sch_chicken_001', '2025-08-09', '19:00:00', '21:00:00',
 '🍗 친구들과 치킨 파티', '대학 동기들과 오랜만에 만나는 날',
 '{"name": "교촌치킨 강남점", "address": "서울시 강남구 테헤란로 789", "phone": "02-1234-5678"}',
 '[{"name": "지훈", "contact": "010-5555-6666", "relation": "대학동기"}, {"name": "민서", "contact": "010-7777-8888", "relation": "대학동기"}]',
 35000, '["친구", "치킨", "대학동기"]', 6, '지훈이 승진 축하하기',
 (SELECT id FROM calendars WHERE calendar_code = 'sample_sch_personal')),

('sample_sch_workout_001', '2025-08-10', '07:00:00', '08:30:00',
 '💪 헬스장 운동', '주말 아침 운동 루틴',
 '{"name": "라이프 피트니스", "address": "서울시 강남구 역삼로 456"}',
 '[]', 0, '["운동", "헬스", "건강"]', 5, '하체 운동 집중',
 (SELECT id FROM calendars WHERE calendar_code = 'sample_sch_personal')),

('sample_sch_prototype_001', '2025-08-11', '15:00:00', '18:00:00',
 '🔧 프로토타입 제작', '모바일 앱 인터랙션 프로토타이핑',
 '{"name": "홈 오피스", "address": "서울시 강남구 집"}',
 '[]', 0, '["프로토타이핑", "모바일", "인터랙션"]', 8, 'Framer로 애니메이션 구현',
 (SELECT id FROM calendars WHERE calendar_code = 'sample_sch_work')),

-- 다른 사용자들 일정 (sch_001이 볼 수 있도록)
('sample_admin_meeting_001', '2025-08-07', '09:00:00', '10:00:00',
 '📋 전체 팀 회의', '월간 전체 팀 미팅 및 성과 발표',
 '{"name": "대회의실", "address": "서울시 강남구 회사 본사 10층"}',
 '[{"name": "전체팀", "contact": "", "relation": "동료"}]',
 0, '["회의", "팀미팅", "월간보고"]', 9, '월간 성과 보고서 준비',
 (SELECT id FROM calendars WHERE calendar_code = 'sample_admin_personal')),

('sample_dev_scrum_001', '2025-08-08', '13:00:00', '14:00:00',
 '💻 개발팀 스크럼', '일일 스크럼 미팅',
 '{"name": "개발팀 회의실", "address": "서울시 강남구 회사 5층"}',
 '[{"name": "개발팀", "contact": "", "relation": "팀원"}]',
 0, '["개발", "스크럼", "일일미팅"]', 7, '스프린트 진행상황 공유',
 (SELECT id FROM calendars WHERE calendar_code = 'sample_user002_work'));

-- 결과 확인
SELECT '=== 생성된 샘플 데이터 확인 ===' as message;
SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(*) as total_calendars FROM calendars;
SELECT COUNT(*) as total_schedules FROM schedules;

SELECT '=== sch_001 사용자 일정 목록 ===' as message;
SELECT s.title, s.date_info, s.start_time, c.calendar_name 
FROM schedules s 
JOIN calendars c ON s.calendar_id = c.id 
JOIN users u ON c.user_id = u.id 
WHERE u.user_id = 'sch_001'
ORDER BY s.date_info, s.start_time;