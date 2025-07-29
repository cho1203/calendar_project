-- MySQL 데이터베이스 생성 스크립트
CREATE DATABASE IF NOT EXISTS calendar_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE calendar_db;

-- 샘플 사용자 데이터 추가 (sch_001)
INSERT INTO users (user_id, name, email, password_hash, user_type, phone, profile, created_at) 
VALUES (
    'sch_001', 
    '조정후', 
    'ellena89@naver.com', 
    'scrypt:32768:8:1$mK5qPvQvJqX9xqQM$f9e8a5d2c3b1a0e9f8d7c6b5a4e3f2e1d0c9b8a7f6e5d4c3b2a1', 
    'user', 
    '010-1234-5678', s
    '안녕하세요 조정후입니다', 
    NOW()
);

-- sch_001의 기본 캘린더 추가
INSERT INTO calendars (calendar_code, calendar_name, description, created_at, user_id)
VALUES (
    'sch_001_default', 
    '내 캘린더', 
    '기본 캘린더', 
    NOW(), 
    (SELECT id FROM users WHERE user_id = 'sch_001')
);

-- 샘플 일정 추가
INSERT INTO schedules (
    schedule_id, 
    date_info, 
    start_time, 
    end_time, 
    title, 
    description, 
    location_data, 
    importance, 
    calendar_id
) VALUES 
(
    'sample_001', 
    '2025-07-28', 
    '09:00:00', 
    '10:00:00', 
    '회의', 
    '팀 미팅', 
    '{"name": "회의실 A"}', 
    5, 
    (SELECT id FROM calendars WHERE calendar_code = 'sch_001_default')
),
(
    'sample_002', 
    '2025-07-29', 
    '14:00:00', 
    '15:30:00', 
    '점심 약속', 
    '친구와 점심', 
    '{"name": "카페"}', 
    3, 
    (SELECT id FROM calendars WHERE calendar_code = 'sch_001_default')
);
INSERT INTO events (user_id, title, start, end)
VALUES ('sch_001', '회의 일정', '2025-08-01 10:00:00', '2025-08-01 11:00:00');