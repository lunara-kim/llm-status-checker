let responseTimeChart = null;
let uptimeChart = null;

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
        
    } else if (data.status === 'disabled') {
        statusDot.classList.add('disabled');
        statusText.classList.add('disabled');
        statusText.textContent = '비활성화';
        header.classList.add('disabled');
        
        response.style.display = 'none';
        error.style.display = 'none';
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
        await updateModelStatus('claude', { status: 'checking' });
        await updateModelStatus('gemini', { status: 'checking' });
        
        const response = await fetch('/api/status');
        const data = await response.json();
        
        await updateModelStatus('openai', data.openai);
        await updateModelStatus('huggingface', data.huggingface);
        await updateModelStatus('claude', data.claude);
        await updateModelStatus('gemini', data.gemini);
        
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
        await updateModelStatus('claude', {
            status: 'error',
            error: '서버에 연결할 수 없습니다'
        });
        await updateModelStatus('gemini', {
            status: 'error',
            error: '서버에 연결할 수 없습니다'
        });
    }
}

async function loadHistory() {
    try {
        // 히스토리 데이터 로드
        const historyResponse = await fetch('/api/history?hours=24');
        const historyData = await historyResponse.json();
        
        // 통계 데이터 로드
        const statsResponse = await fetch('/api/stats?hours=24');
        const statsData = await statsResponse.json();
        
        // 통계 카드 업데이트
        updateStatsCards(statsData.stats);
        
        // 차트 업데이트
        updateResponseTimeChart(historyData.history);
        updateUptimeChart(statsData.stats);
        
    } catch (error) {
        console.error('히스토리 로드 실패:', error);
    }
}

function updateStatsCards(stats) {
    const container = document.getElementById('stats-cards');
    container.innerHTML = '';
    
    const modelNames = {
        'openai': 'OpenAI GPT-4o',
        'huggingface': 'HuggingFace GLM-4.7',
        'claude': 'Anthropic Claude',
        'gemini': 'Google Gemini'
    };
    
    for (const [model, data] of Object.entries(stats)) {
        const card = document.createElement('div');
        card.className = 'col-md-6 col-lg-3 mb-3';
        
        const uptimeClass = data.uptime_percent >= 95 ? 'text-success' : 
                           data.uptime_percent >= 80 ? 'text-warning' : 'text-danger';
        
        card.innerHTML = `
            <div class="card stats-card">
                <div class="card-body">
                    <h6 class="card-subtitle mb-2 text-muted">${modelNames[model] || model}</h6>
                    <h2 class="card-title ${uptimeClass}">${data.uptime_percent}%</h2>
                    <p class="card-text mb-1">
                        <small>가동률 (24시간)</small>
                    </p>
                    <p class="card-text mb-1">
                        <small>평균 응답: ${data.avg_response_time ? data.avg_response_time + 'ms' : 'N/A'}</small>
                    </p>
                    <p class="card-text">
                        <small class="text-muted">${data.success_count}/${data.total_checks} 성공</small>
                    </p>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    }
}

function updateResponseTimeChart(history) {
    const ctx = document.getElementById('responseTimeChart');
    
    if (responseTimeChart) {
        responseTimeChart.destroy();
    }
    
    // 데이터셋 준비
    const datasets = [];
    const colors = {
        'openai': 'rgb(16, 185, 129)',
        'huggingface': 'rgb(245, 158, 11)',
        'claude': 'rgb(139, 92, 246)',
        'gemini': 'rgb(59, 130, 246)'
    };
    
    const modelNames = {
        'openai': 'OpenAI',
        'huggingface': 'HuggingFace',
        'claude': 'Claude',
        'gemini': 'Gemini'
    };
    
    for (const [model, data] of Object.entries(history)) {
        const points = data
            .filter(d => d.status === 'success' && d.response_time)
            .map(d => ({
                x: new Date(d.timestamp),
                y: d.response_time
            }));
        
        if (points.length > 0) {
            datasets.push({
                label: modelNames[model] || model,
                data: points,
                borderColor: colors[model] || 'rgb(107, 114, 128)',
                backgroundColor: (colors[model] || 'rgb(107, 114, 128)') + '20',
                tension: 0.4,
                fill: false
            });
        }
    }
    
    responseTimeChart = new Chart(ctx, {
        type: 'line',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'hour',
                        displayFormats: {
                            hour: 'HH:mm'
                        }
                    },
                    title: {
                        display: true,
                        text: '시간'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: '응답시간 (ms)'
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

function updateUptimeChart(stats) {
    const ctx = document.getElementById('uptimeChart');
    
    if (uptimeChart) {
        uptimeChart.destroy();
    }
    
    const labels = [];
    const data = [];
    const backgroundColors = [];
    
    const modelNames = {
        'openai': 'OpenAI',
        'huggingface': 'HuggingFace',
        'claude': 'Claude',
        'gemini': 'Gemini'
    };
    
    for (const [model, modelData] of Object.entries(stats)) {
        labels.push(modelNames[model] || model);
        data.push(modelData.uptime_percent);
        
        // 가동률에 따라 색상 결정
        if (modelData.uptime_percent >= 95) {
            backgroundColors.push('rgb(16, 185, 129)');
        } else if (modelData.uptime_percent >= 80) {
            backgroundColors.push('rgb(245, 158, 11)');
        } else {
            backgroundColors.push('rgb(239, 68, 68)');
        }
    }
    
    uptimeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: '가동률 (%)',
                data,
                backgroundColor: backgroundColors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: '가동률 (%)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// 페이지 로드 시 자동으로 상태 확인
document.addEventListener('DOMContentLoaded', function() {
    checkStatus();
    
    // 30초마다 자동 새로고침
    setInterval(checkStatus, 30000);
});
