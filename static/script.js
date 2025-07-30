let currentDate = new Date();
let schedules = [];
let calendars = [];
let currentCalendarId = null;
let authToken = null;

// Flask API 베이스 URL 설정
const API_BASE = 'http://localhost:5000/api';

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('페이지 로드 완료');
    
    // 저장된 토큰 확인
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
        authToken = savedToken;
        console.log('저장된 토큰 발견:', authToken);
    }
    
    checkApiConnection();
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('quickDate').value = today;
    
    // 회원가입 폼 이벤트 리스너 추가
    setupSignupForm();
});

// 회원가입 폼 설정
function setupSignupForm() {
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignupSubmit);
    }
    
    const signupUserId = document.getElementById('signupUserId');
    if (signupUserId) {
        signupUserId.addEventListener('blur', checkUserIdAvailability);
    }
}

// API 연결 확인
async function checkApiConnection() {
    console.log('API 연결 확인 시작...');
    try {
        const response = await fetch(`${API_BASE}/db/status`);
        const result = await response.json();
        
        console.log('API 상태 응답:', result);
        
        if (result.success) {
            document.getElementById('apiStatus').textContent = '✅ Flask MySQL 백엔드 연결됨';
            document.getElementById('apiStatus').className = 'api-status connected';
            console.log('✅ API 연결 성공');
        } else {
            throw new Error('API 응답 실패');
        }
    } catch (error) {
        console.error('❌ API 연결 실패:', error);
        document.getElementById('apiStatus').textContent = '❌ Flask MySQL 백엔드 연결 실패';
        document.getElementById('apiStatus').className = 'api-status error';
    }
}

// 빠른 로그인 (관리자 계정)
async function quickLogin() {
    console.log('관리자 로그인 시도...');
    await loginUser('admin001', 'admin123');
}

// 빠른 로그인 (일반 사용자)
async function quickLoginUser() {
    console.log('테스트 사용자 로그인 시도...');
    await loginUser('test001', 'test123');
}

// 회원가입 모달 표시
function showSignupModal() {
    document.getElementById('signupModal').style.display = 'block';
    // 폼 초기화
    document.getElementById('signupForm').reset();
}

// 회원가입 폼 처리
async function handleSignupSubmit(e) {
    e.preventDefault();
    
    // 폼 데이터 수집
    const formData = {
        user_id: document.getElementById('signupUserId').value.trim(),
        name: document.getElementById('signupName').value.trim(),
        email: document.getElementById('signupEmail').value.trim(),
        password: document.getElementById('signupPassword').value,
        passwordConfirm: document.getElementById('signupPasswordConfirm').value,
        phone: document.getElementById('signupPhone').value.trim(),
        profile: document.getElementById('signupProfile').value.trim(),
        user_type: document.getElementById('signupUserType').value
    };
    
    console.log('회원가입 폼 데이터:', formData);
    
    // 입력값 검증
    if (!validateSignupForm(formData)) {
        return;
    }
    
    try {
        console.log('회원가입 요청 시작...');
        
        const response = await fetch(`${API_BASE}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: formData.user_id,
                name: formData.name,
                email: formData.email,
                password: formData.password,
                phone: formData.phone || null,
                profile: formData.profile || null,
                user_type: formData.user_type
            })
        });
        
        const result = await response.json();
        console.log('회원가입 응답:', result);
        
        if (response.ok && (result.success || result.message === 'User created successfully')) {
            showMessage('🎉 회원가입이 완료되었습니다!\n로그인해주세요.', 'success');
            closeModal('signupModal');
            document.getElementById('signupForm').reset();
            
            // 추가 성공 메시지
            setTimeout(() => {
                showMessage(`✅ 계정 생성 완료!\nID: ${formData.user_id}\n이름: ${formData.name}`, 'success');
            }, 2000);
        } else {
            const errorMessage = result.error || result.message || '회원가입에 실패했습니다.';
            showMessage(`❌ ${errorMessage}`, 'error');
        }
    } catch (error) {
        console.error('회원가입 오류:', error);
        showMessage('🚫 회원가입 중 네트워크 오류가 발생했습니다.', 'error');
    }
}

// 회원가입 폼 검증
function validateSignupForm(data) {
    console.log('폼 검증 시작:', data);
    
    // 필수 필드 검사
    if (!data.user_id || !data.name || !data.email || !data.password) {
        showMessage('❗ 필수 항목을 모두 입력해주세요.', 'error');
        return false;
    }
    
    // 사용자 ID 검증
    if (data.user_id.length < 4 || data.user_id.length > 20) {
        showMessage('❗ 사용자 ID는 4-20자 사이여야 합니다.', 'error');
        return false;
    }
    
    if (!/^[a-zA-Z0-9_]+$/.test(data.user_id)) {
        showMessage('❗ 사용자 ID는 영문자, 숫자, 언더스코어(_)만 사용 가능합니다.', 'error');
        return false;
    }
    
    // 비밀번호 검증
    if (data.password.length < 6) {
        showMessage('❗ 비밀번호는 6자 이상이어야 합니다.', 'error');
        return false;
    }
    
    if (data.password !== data.passwordConfirm) {
        showMessage('❗ 비밀번호가 일치하지 않습니다.', 'error');
        return false;
    }
    
    // 이메일 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
        showMessage('❗ 올바른 이메일 주소를 입력해주세요.', 'error');
        return false;
    }
    
    // 전화번호 검증 (선택사항)
    if (data.phone && !/^010-\d{4}-\d{4}$/.test(data.phone)) {
        if (!/^\d{3}-\d{4}-\d{4}$/.test(data.phone)) {
            showMessage('❗ 전화번호는 010-1234-5678 형식으로 입력해주세요.', 'error');
            return false;
        }
    }
    
    console.log('✅ 폼 검증 통과');
    return true;
}

// ID 중복 확인 (선택적 기능)
async function checkUserIdAvailability() {
    const userId = document.getElementById('signupUserId').value.trim();
    
    if (userId.length < 4) {
        return;
    }
    
    try {
        console.log(`ID 중복 확인: ${userId}`);
        const response = await fetch(`${API_BASE}/users/${userId}`);
        
        if (response.status === 404) {
            // 사용자가 없으면 사용 가능
            showMessage('✅ 사용 가능한 ID입니다.', 'success');
        } else if (response.ok) {
            // 사용자가 있으면 중복
            showMessage('❌ 이미 사용 중인 ID입니다.', 'error');
        }
    } catch (error) {
        console.log('ID 중복 확인 중 오류:', error);
    }
}

// 일반 로그인
async function login() {
    const userId = document.getElementById('loginUserId').value;
    const password = document.getElementById('loginPassword').value;
    
    if (!userId || !password) {
        showMessage('❗ 사용자 ID와 비밀번호를 입력해주세요.', 'error');
        return;
    }
    
    await loginUser(userId, password);
}

// 로그인 실행 - 토큰 localStorage 저장 추가
async function loginUser(userId, password) {
    try {
        console.log(`로그인 시도: ${userId}`);
        
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                userId: userId, 
                password: password 
            })
        });
        
        console.log('로그인 응답 상태:', response.status);
        
        const result = await response.json();
        console.log('로그인 응답 데이터:', result);
        
        if (result.success) {
            authToken = result.data.token;
            // localStorage에도 저장
            localStorage.setItem('token', result.data.token);
            
            console.log('✅ 로그인 성공, 토큰:', authToken);
            
            showMessage(`🎉 ${result.data.user.name}님 환영합니다! (Flask MySQL)`, 'success');
            
            // UI 전환
            document.getElementById('loginSection').style.display = 'none';
            document.getElementById('mainContent').style.display = 'grid';
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('userInfo').style.display = 'flex';
            document.getElementById('userName').textContent = result.data.user.name;
            
            // 사용자 정보 업데이트
            document.getElementById('currentUser').textContent = result.data.user.name;
            document.getElementById('userType').textContent = result.data.user.userType;
            
            // 데이터 로드
            await loadCalendars();
            renderCalendar();
        } else {
            console.log('❌ 로그인 실패:', result.message);
            showMessage(`❌ ${result.message}`, 'error');
        }
    } catch (error) {
        console.error('로그인 중 오류:', error);
        showMessage('🚫 로그인 중 오류가 발생했습니다.', 'error');
    }
}

// 로그아웃 - localStorage 정리 추가
async function logout() {
    try {
        await fetch(`${API_BASE}/auth/logout`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
    } catch (error) {
        console.error('로그아웃 오류:', error);
    }
    
    // 모든 토큰 정리
    authToken = null;
    localStorage.removeItem('token');
    schedules = [];
    calendars = [];
    currentCalendarId = null;
    
    // UI 초기화
    document.getElementById('loginSection').style.display = 'block';
    document.getElementById('mainContent').style.display = 'none';
    document.getElementById('loginForm').style.display = 'flex';
    document.getElementById('userInfo').style.display = 'none';
    document.getElementById('loginUserId').value = '';
    document.getElementById('loginPassword').value = '';
    
    showMessage('👋 로그아웃되었습니다.', 'success');
}

// 개선된 메시지 표시 함수
function showMessage(message, type = 'info') {
    console.log(`메시지 표시: ${type} - ${message}`);
    
    // 기존 메시지 제거
    const existingMessage = document.querySelector('.message-popup');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // 새 메시지 생성
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-popup ${type}`;
    messageDiv.innerHTML = `
        <div class="message-content">
            <span class="message-text">${message}</span>
            <button class="message-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // 페이지에 추가
    document.body.appendChild(messageDiv);
    
    // 자동 제거 (성공 메시지는 4초, 에러는 6초)
    const autoRemoveTime = type === 'success' ? 4000 : 6000;
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, autoRemoveTime);
    
    // 기존 메시지 div도 업데이트 (호환성)
    const legacyMessageDiv = document.getElementById('message');
    if (legacyMessageDiv) {
        legacyMessageDiv.textContent = message;
        legacyMessageDiv.className = `message ${type}`;
        legacyMessageDiv.style.display = 'block';
        setTimeout(() => {
            legacyMessageDiv.style.display = 'none';
        }, 3000);
    }
}

// 모달 닫기 함수
function closeModal(modalId) {
    console.log(`모달 닫기: ${modalId}`);
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// 🎨 일관된 캘린더 색상 반환 함수 (모든 곳에서 동일하게 사용)
function getCalendarColor(calendarName) {
    console.log('색상 결정 중인 캘린더 이름:', calendarName);
    
    if (!calendarName) {
        console.log('캘린더 이름이 없음, 기본 색상 사용');
        return '#667eea'; // 기본 색상
    }
    
    const name = calendarName.toLowerCase().trim();
    
    // 더 정확한 매칭 로직
    if (name.includes('내 캘린더') || name.includes('my calendar') || name.includes('내캘린더')) {
        console.log('내 캘린더로 인식 - 초록색');
        return '#10b981'; // 초록색
    } else if (name.includes('개인') || name.includes('personal') || name.includes('private')) {
        console.log('개인 캘린더로 인식 - 파란색');
        return '#3b82f6'; // 파란색
    } else if (name.includes('업무') || name.includes('work') || name.includes('business') || name.includes('office')) {
        console.log('업무 캘린더로 인식 - 핑크색');
        return '#ec4899'; // 핑크색
    } else if (name.includes('조정부') || name.includes('부서') || name.includes('팀')) {
        console.log('부서/팀 캘린더로 인식 - 초록색');
        return '#10b981'; // 초록색 (내 캘린더와 동일)
    }
    
    console.log('기타 캘린더로 인식 - 기본 색상');
    return '#667eea'; // 기본 색상
}

// 🎨 일관된 캘린더 아이콘 반환 함수
function getCalendarIcon(calendarName) {
    if (!calendarName) return '📋';
    
    const name = calendarName.toLowerCase().trim();
    
    if (name.includes('내 캘린더') || name.includes('my calendar') || name.includes('내캘린더')) return '🏠';
    if (name.includes('개인') || name.includes('personal') || name.includes('private')) return '👤';
    if (name.includes('업무') || name.includes('work') || name.includes('business') || name.includes('office')) return '💼';
    if (name.includes('조정부') || name.includes('부서') || name.includes('팀')) return '🏠';
    return '📋';
}

// 🎨 일관된 캘린더 테두리 색상 반환 함수
function getCalendarBorderColor(calendarName) {
    if (!calendarName) return '#4338ca';
    
    const name = calendarName.toLowerCase().trim();
    
    if (name.includes('내 캘린더') || name.includes('my calendar') || name.includes('내캘린더')) {
        return '#059669'; // 진한 초록색
    } else if (name.includes('개인') || name.includes('personal') || name.includes('private')) {
        return '#1d4ed8'; // 진한 파란색
    } else if (name.includes('업무') || name.includes('work') || name.includes('business') || name.includes('office')) {
        return '#be185d'; // 진한 핑크색
    } else if (name.includes('조정부') || name.includes('부서') || name.includes('팀')) {
        return '#059669'; // 진한 초록색
    }
    return '#4338ca'; // 기본 진한 색상
}

// 캘린더 목록 로드
async function loadCalendars() {
    try {
        const token = authToken || localStorage.getItem('token');
        
        if (!token) {
            console.log('❌ 토큰이 없습니다.');
            return;
        }
        
        const response = await fetch('/api/calendars', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        console.log('캘린더 목록:', data);
        
        if (data.success) {
            calendars = data.data.calendars;
            
            const calendarSelect = document.getElementById('calendarSelect');
            calendarSelect.innerHTML = '';
            
            // 캘린더 수 업데이트
            document.getElementById('calendarCount').textContent = calendars.length;
            
            // 전체 일정 보기 옵션 추가
            const allOption = document.createElement('option');
            allOption.value = 'ALL_CALENDARS';
            allOption.textContent = '📅 전체 일정 보기';
            calendarSelect.appendChild(allOption);
            
            // 구분선 추가
            const dividerOption = document.createElement('option');
            dividerOption.disabled = true;
            dividerOption.textContent = '─────────────────';
            calendarSelect.appendChild(dividerOption);
            
            // 기존 캘린더들 추가 (아이콘과 함께)
            calendars.forEach(calendar => {
                const option = document.createElement('option');
                option.value = calendar.calendarId;
                
                // 🎨 일관된 아이콘 사용
                const icon = getCalendarIcon(calendar.calendarName);
                option.textContent = `${icon} ${calendar.calendarName}`;
                calendarSelect.appendChild(option);
            });
            
            // 기본값을 전체 일정 보기로 설정
            calendarSelect.value = 'ALL_CALENDARS';
            
            // 전체 일정 로드
            await loadAllSchedules();
        }
    } catch (error) {
        console.error('캘린더 로드 오류:', error);
        showMessage('캘린더 로드 중 오류가 발생했습니다.', 'error');
    }
}

// 전체 일정 로드 함수 + 디버깅 강화
async function loadAllSchedules() {
    try {
        showCalendarLoading(true);
        
        const token = authToken || localStorage.getItem('token');
        
        if (!token) {
            console.log('❌ 토큰이 없습니다.');
            return;
        }
        
        // 캘린더가 없으면 다시 로드
        if (!calendars || calendars.length === 0) {
            const calendarResponse = await fetch('/api/calendars', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            const calendarData = await calendarResponse.json();
            if (!calendarData.success) return;
            
            calendars = calendarData.data.calendars;
        }
        
        console.log('전체 캘린더 목록:', calendars);
        let allSchedules = [];
        
        // 각 캘린더에서 일정 가져오기
        for (const calendar of calendars) {
            try {
                console.log(`캘린더 "${calendar.calendarName}" 일정 로드 중...`);
                
                const scheduleResponse = await fetch(`/api/schedules/${calendar.calendarId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                const scheduleData = await scheduleResponse.json();
                if (scheduleData.success) {
                    // 🎨 일관된 캘린더 정보를 각 일정에 추가 + 디버깅
                    const schedulesWithCalendar = scheduleData.data.schedules.map(schedule => {
                        const colorInfo = {
                            ...schedule,
                            calendarName: calendar.calendarName,
                            calendarIcon: getCalendarIcon(calendar.calendarName),
                            calendarColor: getCalendarColor(calendar.calendarName),
                            calendarBorderColor: getCalendarBorderColor(calendar.calendarName)
                        };
                        
                        console.log(`일정 "${schedule.title}" 색상 정보:`, {
                            calendarName: calendar.calendarName,
                            color: colorInfo.calendarColor,
                            icon: colorInfo.calendarIcon
                        });
                        
                        return colorInfo;
                    });
                    
                    allSchedules = allSchedules.concat(schedulesWithCalendar);
                    console.log(`캘린더 "${calendar.calendarName}"에서 ${schedulesWithCalendar.length}개 일정 로드됨`);
                }
            } catch (error) {
                console.error(`캘린더 ${calendar.calendarId} 일정 로드 오류:`, error);
            }
        }
        
        // 날짜순으로 정렬
        allSchedules.sort((a, b) => new Date(a.startTime || a.start_time) - new Date(b.startTime || b.start_time));
        
        console.log(`전체 일정 로드 완료: ${allSchedules.length}개`);
        console.log('전체 일정 색상 정보:', allSchedules.map(s => ({ title: s.title, color: s.calendarColor, calendar: s.calendarName })));
        
        // 전역변수 업데이트
        schedules = allSchedules;
        
        // 일정 수 업데이트
        document.getElementById('scheduleCount').textContent = allSchedules.length;
        
        // 캘린더에 표시
        renderCalendar();
        loadTodayEvents();
        
    } catch (error) {
        console.error('전체 일정 로드 오류:', error);
        showMessage('일정 로드 중 오류가 발생했습니다.', 'error');
    } finally {
        showCalendarLoading(false);
    }
}

// 캘린더 변경 시 처리
async function onCalendarChange() {
    const calendarSelect = document.getElementById('calendarSelect');
    const selectedCalendar = calendarSelect.value;
    
    console.log('선택된 캘린더:', selectedCalendar);
    
    if (selectedCalendar === 'ALL_CALENDARS') {
        // 전체 일정 보기
        await loadAllSchedules();
    } else if (selectedCalendar) {
        // 특정 캘린더 일정 보기
        currentCalendarId = selectedCalendar;
        await loadSchedules();
    }
}

// 로딩 상태 표시 함수
function showCalendarLoading(show) {
    const calendarGrid = document.querySelector('.calendar-grid');
    if (!calendarGrid) return;
    
    const loadingDiv = document.querySelector('.calendar-loading');
    
    if (show) {
        if (!loadingDiv) {
            const loading = document.createElement('div');
            loading.className = 'calendar-loading';
            loading.textContent = '일정을 불러오는 중...';
            calendarGrid.parentNode.insertBefore(loading, calendarGrid);
        }
        calendarGrid.style.opacity = '0.5';
    } else {
        if (loadingDiv) {
            loadingDiv.remove();
        }
        calendarGrid.style.opacity = '1';
    }
}

// 시간 포맷 헬퍼 함수
function formatTime(timeString) {
    const date = new Date(timeString);
    return date.toLocaleTimeString('ko-KR', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
    });
}

// 🎨 수정된 개별 캘린더 일정 로드 - 색상 정보 포함 + 디버깅
async function loadSchedules() {
    const selectElement = document.getElementById('calendarSelect');
    currentCalendarId = selectElement.value;
    
    console.log('=== 일정 로드 시작 ===');
    console.log('선택된 캘린더 ID:', currentCalendarId);
    console.log('인증 토큰:', authToken);
    
    if (!currentCalendarId || currentCalendarId === 'ALL_CALENDARS') {
        await loadAllSchedules();
        return;
    }
    
    const token = authToken || localStorage.getItem('token');
    if (!token) {
        console.log('❌ 인증 토큰이 없음');
        return;
    }
    
    try {
        const url = `${API_BASE}/schedules/${currentCalendarId}`;
        console.log('일정 API 호출 URL:', url);
        
        const response = await fetch(url, {
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('일정 API 응답 상태:', response.status);
        
        const result = await response.json();
        console.log('일정 API 응답:', result);
        
        if (result.success) {
            // 🎨 개별 캘린더 일정에도 일관된 색상 정보 추가 + 디버깅
            const currentCalendar = calendars.find(cal => cal.calendarId === currentCalendarId);
            const calendarName = currentCalendar ? currentCalendar.calendarName : '';
            
            console.log('현재 캘린더 정보:', currentCalendar);
            console.log('캘린더 이름:', calendarName);
            
            const schedulesWithColor = result.data.schedules.map(schedule => {
                const colorInfo = {
                    ...schedule,
                    calendarName: calendarName,
                    calendarIcon: getCalendarIcon(calendarName),
                    calendarColor: getCalendarColor(calendarName),
                    calendarBorderColor: getCalendarBorderColor(calendarName)
                };
                
                console.log('일정 색상 정보:', {
                    title: schedule.title,
                    calendarName: calendarName,
                    color: colorInfo.calendarColor,
                    icon: colorInfo.calendarIcon
                });
                
                return colorInfo;
            });
            
            schedules = schedulesWithColor;
            console.log('✅ 로드된 일정 개수:', schedules.length);
            console.log('색상이 적용된 일정 목록:', schedules);
            
            document.getElementById('scheduleCount').textContent = schedules.length;
            renderCalendar();
            loadTodayEvents();
        } else {
            console.log('❌ 일정 로드 실패:', result.message);
            showMessage(`일정 로드 실패: ${result.message}`, 'error');
        }
    } catch (error) {
        console.error('일정 로드 오류:', error);
        showMessage('일정 로드 중 네트워크 오류가 발생했습니다.', 'error');
    }
}

// 새 캘린더 생성
async function createCalendar() {
    const name = prompt('캘린더 이름을 입력하세요:');
    if (!name) return;
    
    const token = authToken || localStorage.getItem('token');
    
    try {
        const response = await fetch(`${API_BASE}/calendars`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                calendarName: name,
                description: '새로 생성된 캘린더'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('✅ 캘린더가 생성되었습니다! (Flask MySQL)', 'success');
            await loadCalendars();
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        showMessage('캘린더 생성 중 오류가 발생했습니다.', 'error');
    }
}

// 🎨 완전히 수정된 캘린더 렌더링 - 모든 캘린더에서 일관된 색상 적용
function renderCalendar() {
    console.log('=== 캘린더 렌더링 시작 ===');
    console.log('현재 일정 개수:', schedules.length);
    
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    document.getElementById('currentMonth').textContent = `${year}년 ${month + 1}월`;
    
    const firstDay = new Date(year, month, 1);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const calendarGrid = document.getElementById('calendarGrid');
    const headers = calendarGrid.querySelectorAll('.day-header');
    calendarGrid.innerHTML = '';
    headers.forEach(header => calendarGrid.appendChild(header));
    
    const today = new Date();
    let totalEventsAdded = 0;
    
    for (let i = 0; i < 42; i++) {
        const cellDate = new Date(startDate);
        cellDate.setDate(startDate.getDate() + i);
        
        const dayCell = document.createElement('div');
        dayCell.className = 'day-cell';
        
        if (cellDate.getMonth() !== month) {
            dayCell.classList.add('other-month');
        }
        
        if (cellDate.toDateString() === today.toDateString()) {
            dayCell.classList.add('today');
        }
        
        dayCell.innerHTML = `<div class="day-number">${cellDate.getDate()}</div>`;
        
        // 해당 날짜의 일정 표시
        const daySchedules = schedules.filter(schedule => {
            const scheduleDate = new Date(schedule.start_time || schedule.startTime);
            return scheduleDate.toDateString() === cellDate.toDateString();
        });
        
        daySchedules.forEach((schedule, index) => {
            const eventEl = document.createElement('div');
            eventEl.className = 'event-item';
            
            // 🎨 일관된 색상 적용
            const eventColor = schedule.calendarColor || getCalendarColor(schedule.calendarName);
            const borderColor = schedule.calendarBorderColor || getCalendarBorderColor(schedule.calendarName);
            const icon = schedule.calendarIcon || getCalendarIcon(schedule.calendarName);
            
            // 🔧 캘린더 레이아웃 수정 - 일정이 셀 안에 정확히 배치되도록
            eventEl.style.cssText = `
                background-color: ${eventColor};
                border-left: 3px solid ${borderColor};
                font-size: 9px;
                line-height: 11px;
                padding: 2px 4px;
                margin: 1px 0;
                border-radius: 3px;
                cursor: pointer;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 100%;
                box-sizing: border-box;
                position: relative;
                z-index: 1;
            `;
            
            // 일정 제목 표시 - 간소화
            const titleText = schedule.title.length > 8 ? schedule.title.substring(0, 8) + '...' : schedule.title;
            eventEl.innerHTML = `<span style="font-weight: bold; color: white;">${icon} ${titleText}</span>`;
            
            // 툴팁 추가
            const tooltipText = `${schedule.calendarName || '캘린더'}\n${schedule.title}\n${formatTime(schedule.start_time || schedule.startTime)} - ${formatTime(schedule.end_time || schedule.endTime)}`;
            eventEl.title = tooltipText;
            
            eventEl.onclick = () => showEventDetails(schedule);
            dayCell.appendChild(eventEl);
            totalEventsAdded++;
        });
        
        dayCell.onclick = () => selectDate(cellDate);
        calendarGrid.appendChild(dayCell);
    }
    
    console.log(`✅ 캘린더 렌더링 완료 - 총 ${totalEventsAdded}개 일정 표시`);
}

// 🎨 수정된 오늘의 일정 로드 - 일관된 색상 적용
function loadTodayEvents() {
    const today = new Date();
    const todaySchedules = schedules.filter(schedule => {
        const scheduleDate = new Date(schedule.start_time || schedule.startTime);
        return scheduleDate.toDateString() === today.toDateString();
    });
    
    const todayEventsDiv = document.getElementById('todayEvents');
    if (todaySchedules.length === 0) {
        todayEventsDiv.innerHTML = '<p class="no-schedules">📅 오늘 일정이 없습니다.</p>';
    } else {
        todayEventsDiv.innerHTML = todaySchedules.map(schedule => {
            const time = new Date(schedule.start_time || schedule.startTime).toLocaleTimeString('ko-KR', {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            // 🎨 일관된 색상 및 아이콘 적용
            const backgroundColor = schedule.calendarColor || getCalendarColor(schedule.calendarName);
            const borderColor = schedule.calendarBorderColor || getCalendarBorderColor(schedule.calendarName);
            const icon = schedule.calendarIcon || getCalendarIcon(schedule.calendarName);
            const calendarInfo = schedule.calendarName || '기본 캘린더';
            
            return `<div class="schedule-item" style="margin-bottom: 5px; background: ${backgroundColor}; border-left: 3px solid ${borderColor}; cursor: pointer;" onclick="showEventDetails(${JSON.stringify(schedule).replace(/"/g, '&quot;')})">
                <div style="font-size: 11px;">
                    <strong>${icon} ${time} - ${schedule.title}</strong>
                    <div style="font-size: 9px; opacity: 0.8;">${calendarInfo}</div>
                </div>
            </div>`;
        }).join('');
    }
}

// 월 이동
function previousMonth() {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar();
}

function nextMonth() {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar();
}

// 날짜 선택
function selectDate(date) {
    const isoDate = date.toISOString().slice(0, 16);
    document.getElementById('eventStartDate').value = isoDate;
    
    const endDate = new Date(date);
    endDate.setHours(date.getHours() + 1);
    document.getElementById('eventEndDate').value = endDate.toISOString().slice(0, 16);
    
    showAddEventModal();
}

// 모달 관리
function showAddEventModal() {
    if (!currentCalendarId || currentCalendarId === 'ALL_CALENDARS') {
        showMessage('📅 먼저 사이드바에서 특정 캘린더를 선택해주세요!', 'error');
        return;
    }
    document.getElementById('addEventModal').style.display = 'block';
}

// 상세 일정 추가
document.getElementById('addEventForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!currentCalendarId || currentCalendarId === 'ALL_CALENDARS') {
        showMessage('특정 캘린더를 선택해주세요.', 'error');
        return;
    }
    
    const token = authToken || localStorage.getItem('token');
    
    const eventData = {
        title: document.getElementById('eventTitle').value,
        description: document.getElementById('eventDescription').value,
        startTime: document.getElementById('eventStartDate').value,
        endTime: document.getElementById('eventEndDate').value,
        location: document.getElementById('eventLocation').value,
        category: '일반'
    };
    
    console.log('일정 추가 요청:', eventData);
    
    try {
        const response = await fetch(`${API_BASE}/schedules/${currentCalendarId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(eventData)
        });
        
        const result = await response.json();
        console.log('일정 추가 응답:', result);
        
        if (result.success) {
            showMessage('✅ 일정이 추가되었습니다! (Flask MySQL)', 'success');
            closeModal('addEventModal');
            e.target.reset();
            await loadSchedules();
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        console.error('일정 추가 오류:', error);
        showMessage('일정 추가 중 오류가 발생했습니다.', 'error');
    }
});

// 빠른 일정 추가
document.getElementById('quickEventForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!currentCalendarId || currentCalendarId === 'ALL_CALENDARS') {
        showMessage('📅 먼저 사이드바에서 특정 캘린더를 선택해주세요!', 'error');
        return;
    }
    
    const token = authToken || localStorage.getItem('token');
    const title = document.getElementById('quickTitle').value;
    const date = document.getElementById('quickDate').value;
    const time = document.getElementById('quickTime').value;
    
    const startDateTime = `${date}T${time}`;
    const endDate = new Date(`${date}T${time}`);
    endDate.setHours(endDate.getHours() + 1);
    
    const eventData = {
        title: title,
        description: '빠른 일정 추가 (Flask MySQL)',
        startTime: startDateTime,
        endTime: endDate.toISOString().slice(0, 16),
        location: '',
        category: '일반'
    };
    
    console.log('빠른 일정 추가:', eventData);
    
    try {
        const response = await fetch(`${API_BASE}/schedules/${currentCalendarId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(eventData)
        });
        
        const result = await response.json();
        console.log('빠른 일정 추가 응답:', result);
        
        if (result.success) {
            showMessage('✅ 일정이 추가되었습니다! (Flask MySQL)', 'success');
            e.target.reset();
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('quickDate').value = today;
            await loadSchedules();
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        console.error('빠른 일정 추가 오류:', error);
        showMessage('일정 추가 중 오류가 발생했습니다.', 'error');
    }
});

// 🎨 수정된 일정 세부정보 모달 표시 - 일관된 색상 적용
function showEventDetails(schedule) {
    const startDate = new Date(schedule.start_time || schedule.startTime).toLocaleString('ko-KR');
    const endDate = new Date(schedule.end_time || schedule.endTime).toLocaleString('ko-KR');
    
    // 🎨 일관된 색상 및 정보 설정
    const eventColor = schedule.calendarColor || getCalendarColor(schedule.calendarName);
    const icon = schedule.calendarIcon || getCalendarIcon(schedule.calendarName);
    const calendarInfo = schedule.calendarName || schedule.calendar_name || '기본 캘린더';
    
    // 삭제 버튼은 내 일정일 때만 표시
    const deleteButton = schedule.is_my_schedule !== false ? 
        `<button onclick="deleteScheduleFromModal('${schedule.id}')" class="btn" style="background: #dc2626; border-color: #dc2626; color: white; margin-left: 10px;">
            🗑️ 삭제
        </button>` : '';
    
    const modalHtml = `
        <div id="eventDetailModal" class="modal" style="display: block;">
            <div class="modal-content">
                <button class="close-modal" onclick="closeModal('eventDetailModal')">&times;</button>
                
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="width: 20px; height: 20px; background: ${eventColor}; border-radius: 50%; margin-right: 10px;"></div>
                    <h3 style="margin: 0;">${icon} ${schedule.title}</h3>
                </div>
                
                <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        
                        <div style="display: flex; align-items: center;">
                            <span style="width: 80px; font-weight: bold; color: #374151;">📅 캘린더:</span>
                            <span>${calendarInfo}</span>
                        </div>
                        
                        <div style="display: flex; align-items: center;">
                            <span style="width: 80px; font-weight: bold; color: #374151;">🕐 시작:</span>
                            <span>${startDate}</span>
                        </div>
                        
                        <div style="display: flex; align-items: center;">
                            <span style="width: 80px; font-weight: bold; color: #374151;">🕐 종료:</span>
                            <span>${endDate}</span>
                        </div>
                        
                        ${schedule.location ? `
                        <div style="display: flex; align-items: center;">
                            <span style="width: 80px; font-weight: bold; color: #374151;">📍 장소:</span>
                            <span>${schedule.location}</span>
                        </div>
                        ` : ''}
                        
                        ${schedule.description ? `
                        <div style="display: flex; align-items: flex-start;">
                            <span style="width: 80px; font-weight: bold; color: #374151;">📝 설명:</span>
                            <span style="line-height: 1.4;">${schedule.description}</span>
                        </div>
                        ` : ''}
                        
                        ${schedule.participants ? `
                        <div style="display: flex; align-items: center;">
                            <span style="width: 80px; font-weight: bold; color: #374151;">👥 참석자:</span>
                            <span>${schedule.participants}</span>
                        </div>
                        ` : ''}
                        
                        ${schedule.importance ? `
                        <div style="display: flex; align-items: center;">
                            <span style="width: 80px; font-weight: bold; color: #374151;">⭐ 중요도:</span>
                            <span>${'★'.repeat(Math.min(schedule.importance, 10))}</span>
                        </div>
                        ` : ''}
                        
                        ${schedule.notes ? `
                        <div style="display: flex; align-items: flex-start;">
                            <span style="width: 80px; font-weight: bold; color: #374151;">📌 메모:</span>
                            <span style="line-height: 1.4;">${schedule.notes}</span>
                        </div>
                        ` : ''}
                        
                    </div>
                </div>
                
                <div style="text-align: center; font-size: 12px; color: #6b7280; margin-bottom: 20px;">
                    💾 Flask MySQL에서 로드됨
                </div>
                
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('eventDetailModal')">
                        확인
                    </button>
                    ${deleteButton}
                </div>
            </div>
        </div>
    `;
    
    // 기존 모달이 있다면 제거
    const existingModal = document.getElementById('eventDetailModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 새 모달 추가
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

// 일정 삭제 함수 (모달에서 호출)
async function deleteScheduleFromModal(scheduleId) {
    const confirmed = confirm('⚠️ 이 일정을 삭제하시겠습니까?\n\n삭제된 일정은 복구할 수 없습니다.');
    
    if (!confirmed) {
        return;
    }
    
    try {
        console.log(`일정 삭제 시도: ${scheduleId}`);
        showMessage('🗑️ 일정을 삭제하는 중...', 'info');
        
        const token = authToken || localStorage.getItem('token');
        
        // 일정 삭제 API 호출 (DELETE 방식)
        const response = await fetch(`${API_BASE}/schedules/${scheduleId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        console.log('일정 삭제 응답:', result);
        
        if (result.success || response.ok) {
            showMessage('✅ 일정이 삭제되었습니다!', 'success');
            
            // 모달 닫기
            closeModal('eventDetailModal');
            
            // 일정 목록 새로고침
            const calendarSelect = document.getElementById('calendarSelect');
            if (calendarSelect.value === 'ALL_CALENDARS') {
                await loadAllSchedules();
            } else {
                await loadSchedules();
            }
            
        } else {
            showMessage(`❌ ${result.message || '일정 삭제에 실패했습니다.'}`, 'error');
        }
        
    } catch (error) {
        console.error('일정 삭제 오류:', error);
        showMessage('🚫 일정 삭제 중 오류가 발생했습니다.', 'error');
    }
}

// 데이터 새로고침
async function refreshData() {
    const token = authToken || localStorage.getItem('token');
    if (!token) return;
    
    try {
        showMessage('🔄 Flask MySQL에서 데이터를 새로고침 중...', 'info');
        await loadCalendars();
        
        const calendarSelect = document.getElementById('calendarSelect');
        if (calendarSelect.value === 'ALL_CALENDARS') {
            await loadAllSchedules();
        } else if (currentCalendarId) {
            await loadSchedules();
        }
        
        showMessage('✅ 데이터가 새로고침되었습니다! (Flask MySQL)', 'success');
    } catch (error) {
        showMessage('🚫 데이터 새로고침 중 오류가 발생했습니다.', 'error');
    }
}

// 모달 외부 클릭 시 닫기
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}