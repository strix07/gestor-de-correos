document.addEventListener('DOMContentLoaded', () => {
    const loginView = document.getElementById('login-view');
    const dashboardView = document.getElementById('dashboard-view');
    const loginBtn = document.getElementById('login-btn');
    const searchBtn = document.getElementById('search-btn');
    const resultTable = document.getElementById('results-body');
    const detailPanel = document.getElementById('detail-panel');
    const detailContent = document.getElementById('detail-content');
    const closeDetail = document.getElementById('close-detail');
    const overlay = document.getElementById('overlay');
    const copyMsgBtn = document.getElementById('copy-msg-btn');
    const copyAllBtn = document.getElementById('copy-all-btn');
    const logoutBtn = document.getElementById('logout-btn');

    // Global state
    let allResults = [];
    let currentMessageBody = '';

    // Check Auth Status
    fetch('/api/auth_status')
        .then(res => res.json())
        .then(data => {
            if (data.authenticated) {
                showDashboard();
            } else {
                showLogin();
            }
        });

    function showLogin() {
        loginView.classList.add('active');
        dashboardView.classList.remove('active');
    }

    function showDashboard() {
        loginView.classList.remove('active');
        dashboardView.classList.add('active');
    }

    loginBtn.addEventListener('click', () => {
        fetch('/api/login', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showDashboard();
                } else {
                    alert('Login failed or was cancelled.');
                }
            });
    });

    searchBtn.addEventListener('click', () => {
        const recipient = document.getElementById('recipient-input').value;
        const keyword = document.getElementById('keyword-input').value;

        if (!recipient) {
            alert('Please enter a recipient email.');
            return;
        }

        resultTable.innerHTML = '<tr><td colspan="3" style="text-align:center;">Searching...</td></tr>';

        const params = new URLSearchParams({ recipient, keyword });
        fetch(`/api/search?${params}`)
            .then(res => res.json())
            .then(data => {
                allResults = data;
                renderTable(data);
            })
            .catch(err => {
                console.error(err);
                resultTable.innerHTML = '<tr><td colspan="3" style="text-align:center;">Error fetching results.</td></tr>';
            });
    });

    function renderTable(rows) {
        resultTable.innerHTML = '';
        if (rows.length === 0) {
            resultTable.innerHTML = '<tr><td colspan="3" style="text-align:center;">No conversation found.</td></tr>';
            return;
        }

        rows.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.date}</td>
                <td>${row.subject}</td>
                <td style="color: #666; font-size: 13px;">${row.snippet}</td>
            `;
            tr.addEventListener('click', () => openDetail(row.id));
            resultTable.appendChild(tr);
        });
    }

    function openDetail(msgId) {
        detailContent.innerHTML = 'Loading...';
        detailPanel.classList.add('open');
        overlay.classList.add('visible');

        fetch(`/api/message/${msgId}`)
            .then(res => res.json())
            .then(data => {
                currentMessageBody = data.content;
                // Create a shadow root or iframe to isolate email styles
                const frame = document.createElement('iframe');
                frame.style.width = '100%';
                frame.style.height = '100%';
                frame.style.border = 'none';
                detailContent.innerHTML = '';
                detailContent.appendChild(frame);

                // Write content
                frame.contentWindow.document.open();
                frame.contentWindow.document.write(currentMessageBody);
                frame.contentWindow.document.close();
            });
    }

    closeDetail.addEventListener('click', closePanel);
    overlay.addEventListener('click', closePanel);

    function closePanel() {
        detailPanel.classList.remove('open');
        overlay.classList.remove('visible');
    }

    copyMsgBtn.addEventListener('click', () => {
        if (!currentMessageBody) return;

        const htmlBlob = new Blob([currentMessageBody], { type: 'text/html' });
        // Create a plain text version as fallback
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = currentMessageBody;
        const text = tempDiv.innerText || tempDiv.textContent;
        const textBlob = new Blob([text], { type: 'text/plain' });

        const data = [new ClipboardItem({
            'text/html': htmlBlob,
            'text/plain': textBlob
        })];

        navigator.clipboard.write(data).then(() => {
            alert('Message content copied! You can now paste it into Word with formatting.');
        }).catch(err => {
            console.error('Copy failed', err);
            alert('Copy failed: ' + err);
        });
    });

    copyAllBtn.addEventListener('click', () => {
        if (!allResults.length) return;

        const originalText = copyAllBtn.innerHTML;
        copyAllBtn.innerHTML = '<span class="material-icons">hourglass_empty</span> Fetching...';
        copyAllBtn.disabled = true;

        const ids = allResults.map(r => r.id);

        fetch('/api/batch_content', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids })
        })
            .then(res => res.json())
            .then(data => {
                const contents = data.contents;
                // Join all emails with a separator
                const fullHtml = contents.join('<br><hr><br>');

                const htmlBlob = new Blob([fullHtml], { type: 'text/html' });
                const textBlob = new Blob([fullHtml.replace(/<[^>]*>?/gm, '')], { type: 'text/plain' }); // Simple strip tags for text fallback

                const clipboardData = [new ClipboardItem({
                    'text/html': htmlBlob,
                    'text/plain': textBlob
                })];

                navigator.clipboard.write(clipboardData).then(() => {
                    alert('Full history (all emails) copied to clipboard!');
                }).catch(err => {
                    console.error(err);
                    alert('Copy failed: ' + err);
                });
            })
            .catch(err => {
                console.error(err);
                alert('Error fetching full history.');
            })
            .finally(() => {
                copyAllBtn.innerHTML = originalText;
                copyAllBtn.disabled = false;
            });
    });

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to logout?')) {
                fetch('/api/logout', { method: 'POST' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            showLogin();
                            // Optional: clear table
                            resultTable.innerHTML = '';
                            document.getElementById('recipient-input').value = '';
                        }
                    });
            }
        });
    }
});
