async function updateModelStatus(modelName, data) {
    const indicator = document.getElementById(`${modelName}-indicator`);
    const responseTime = document.getElementById(`${modelName}-response-time`);
    const response = document.getElementById(`${modelName}-response`);
    const error = document.getElementById(`${modelName}-error`);
    const card = document.getElementById(`${modelName}-card`);
    const header = card.querySelector('.card-header');
    
    // 상태 표시기 업데이트
    const statusDot = indicator.querySelector('.status-dot');
    const statusText = indicator.querySelector('.status-text');
    
    // 기존 클래스 제거
    statusDot.className = 'status-dot';
    statusText.className = 'status-text';
    header.className = 'card-header d-flex justify-content-between align-items-center';
    
    // 내용 초기화
    response.textContent = '';
    error.textContent = '';
    responseTime.textContent = '';
    
    if (data.status === 'success') {
        statusDot.classList.add('success');
        statusText.classList.add('success');
        statusText.textContent = '정상';
        header.classList.add('success');
        
        responseTime.textContent = `응답 시간: ${data.response_time}ms`;
        response.textContent = data.response;
        response.style.display = 'block';
        error.style.display = 'none';
        
    } else if (data.status === 'error') {
        statusDot.classList.add('error');
        statusText.classList.add('error');
        statusText.textContent = '오류';
        header.classList.add('error');
        
        error.textContent = data.error;
        response.style.display = 'none';
        error.style.display = 'block';
        
    } else if (data.status === 'checking') {
        statusDot.classList.add('checking');
        statusText.classList.add('checking');
        statusText.textContent = '확인 중...';
        header.classList.add('checking');
        
        response.style.display = 'none';
        error.style.display = 'none';
    }
}

async function checkStatus() {
    try {
        // 확인 중 상태로 설정
        await updateModelStatus('openai', { status: 'checking' });
        await updateModelStatus('huggingface', { status: 'checking' });
        
        const response = await fetch('/api/status');
        const data = await response.json();
        
        await updateModelStatus('openai', data.openai);
        await updateModelStatus('huggingface', data.huggingface);
        
        // 마지막 확인 시간 업데이트
        const lastCheck = new Date().toLocaleString('ko-KR');
        document.getElementById('last-check').textContent = lastCheck;
        
    } catch (error) {
        console.error('상태 확인 실패:', error);
        
        // 네트워크 오류 처리
        await updateModelStatus('openai', { 
            status: 'error', 
            error: '서버에 연결할 수 없습니다' 
        });
        await updateModelStatus('huggingface', { 
            status: 'error', 
            error: '서버에 연결할 수 없습니다' 
        });
    }
}

// 페이지 로드 시 자동으로 상태 확인
document.addEventListener('DOMContentLoaded', function() {
    checkStatus();
    
    // 30초마다 자동 새로고침
    setInterval(checkStatus, 30000);
});