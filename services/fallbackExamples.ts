import { Creation } from '../components/CreationHistory';

export const FALLBACK_EXAMPLES: Creation[] = [
  {
    id: 'fallback-crm-hub',
    name: 'NimbusIQ Dynamics Dashboard',
    timestamp: new Date(),
    originalImages: [],
    html: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NimbusIQ Dynamics CRM V4</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #030712;
            color: #f3f4f6;
        }
    </style>
</head>
<body class="min-h-screen flex flex-col">
    <!-- Navbar -->
    <header class="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/20">
                N
            </div>
            <div>
                <h1 class="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-gray-100 to-gray-400 bg-clip-text text-transparent">NimbusIQ Hub</h1>
                <p class="text-[10px] text-gray-500 uppercase tracking-widest font-semibold">Enterprise Dynamics V4</p>
            </div>
        </div>
        <div class="flex items-center space-x-4 text-sm text-gray-400">
            <span class="flex items-center space-x-1.5 bg-green-500/10 text-green-400 border border-green-500/20 px-2.5 py-1 rounded-full text-xs font-mono font-semibold">
                <span class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
                <span>SYSTEM ONLINE</span>
            </span>
        </div>
    </header>

    <main class="flex-1 p-6 max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Dashboard Left: Stats and Charts -->
        <div class="lg:col-span-2 space-y-6">
            <!-- Widgets Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div class="bg-gray-900/40 border border-gray-800 rounded-2xl p-5 hover:border-gray-700 transition">
                    <p class="text-xs text-gray-400 font-medium">Active Leads</p>
                    <p class="text-2xl font-bold mt-2" id="stat-leads">1,429</p>
                    <p class="text-xs text-green-500 font-medium mt-1">↑ +12.4% this week</p>
                </div>
                <div class="bg-gray-900/40 border border-gray-800 rounded-2xl p-5 hover:border-gray-700 transition">
                    <p class="text-xs text-gray-400 font-medium">Conversion Rate</p>
                    <p class="text-2xl font-bold mt-2">18.42%</p>
                    <p class="text-xs text-indigo-400 font-medium mt-1">↑ +2.1% benchmark</p>
                </div>
                <div class="bg-gray-900/40 border border-gray-800 rounded-2xl p-5 hover:border-gray-700 transition">
                    <p class="text-xs text-gray-400 font-medium">Pipeline Value</p>
                    <p class="text-2xl font-bold mt-2">$2.4M</p>
                    <p class="text-xs text-green-500 font-medium mt-1">↑ +$450K project</p>
                </div>
            </div>

            <!-- Main Interactive Lead List -->
            <div class="bg-gray-900/30 border border-gray-800 rounded-2xl p-6">
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h2 class="text-base font-bold text-white">Lead Management Matrix</h2>
                        <p class="text-xs text-gray-500">Real-time pipeline routing and scoring metrics</p>
                    </div>
                    <button onclick="addRandomLead()" class="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white rounded-lg text-xs font-semibold transition shadow-lg shadow-blue-500/20">
                        + Deploy New Lead
                    </button>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm text-gray-300">
                        <thead>
                            <tr class="border-b border-gray-800 text-gray-500 text-xs uppercase font-mono">
                                <th class="py-3 px-4">Contact</th>
                                <th class="py-3 px-4">Status</th>
                                <th class="py-3 px-4">Lead Score</th>
                                <th class="py-3 px-4">Action</th>
                            </tr>
                        </thead>
                        <tbody id="lead-table-body">
                            <!-- Dynamic Rows -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Dashboard Right: Engagement & Sandbox Creator -->
        <div class="space-y-6">
            <!-- Heatmap / Dynamic Score Distribution Chart -->
            <div class="bg-gray-900/30 border border-gray-800 rounded-2xl p-6 flex flex-col justify-between">
                <div>
                    <h2 class="text-sm font-bold text-white mb-2">CRM Conversion Trajectory</h2>
                    <p class="text-xs text-gray-500 mb-4">Volume scaling performance indexes</p>
                </div>
                <div class="relative w-full h-[220px]">
                    <canvas id="crmStatsChart"></canvas>
                </div>
            </div>

            <!-- Operational Activity Metrics -->
            <div class="bg-gray-900/30 border border-gray-800 rounded-2xl p-6">
                <h2 class="text-sm font-bold text-white mb-4">Live System Operations</h2>
                <div class="space-y-4" id="operational-logs">
                    <!-- Dynamic Log feed -->
                </div>
            </div>
        </div>
    </main>

    <footer class="border-t border-gray-800 py-4 text-center text-xs text-gray-600 bg-gray-950 font-mono mt-auto">
        &copy; 2026 NimbusIQ Engineering. Generated seamlessly via Gemini.
    </footer>

    <script>
        // Initial CRM Leads Data
        let leads = [
            { id: 1, name: "Alpha Systems", email: "procurement@alphasys.com", status: "In Pipeline", score: 94 },
            { id: 2, name: "OmniCorp Ltd.", email: "biz-dev@omnicorp.org", status: "Contacted", score: 81 },
            { id: 3, name: "Nova Logistics", email: "operations@nova.io", status: "Closing", score: 98 },
            { id: 4, name: "Prism Global", email: "tech@prismglobal.co", status: "Qualified", score: 73 }
        ];

        function renderLeads() {
            const tableBody = document.getElementById('lead-table-body');
            tableBody.innerHTML = '';
            
            leads.forEach(lead => {
                const row = document.createElement('tr');
                row.className = 'border-b border-gray-800/50 hover:bg-white/[0.02] transition';
                
                let badgeColor = 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
                if (lead.status === 'Closing') badgeColor = 'bg-green-500/10 text-green-400 border-green-500/20';
                if (lead.status === 'In Pipeline') badgeColor = 'bg-blue-500/10 text-blue-400 border-blue-500/20';

                row.innerHTML = \`
                    <td class="py-3.5 px-4">
                        <div class="font-semibold text-white">\${lead.name}</div>
                        <div class="text-xs text-gray-500">\${lead.email}</div>
                    </td>
                    <td class="py-3.5 px-4">
                        <span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold border \${badgeColor}">
                            \${lead.status}
                        </span>
                    </td>
                    <td class="py-3.5 px-4 font-mono font-bold text-right pr-8">
                        <span class="\${lead.score >= 90 ? 'text-green-400' : 'text-indigo-400'}">\${lead.score} pts</span>
                    </td>
                    <td class="py-3.5 px-4">
                        <button onclick="upgradeLead(\${lead.id})" class="text-xs text-blue-400 hover:text-blue-300 font-semibold underline">Fast Track</button>
                    </td>
                \`;
                tableBody.appendChild(row);
            });
            document.getElementById('stat-leads').innerText = leads.length + 1425;
        }

        const leadNames = ["Zephyr Mobile", "Horizon Energy", "Sovereign Labs", "Quantum Capital", "Vanguard Web", "Genesis Biotech"];
        const statuses = ["In Pipeline", "Contacted", "Qualified", "Closing"];

        function addRandomLead() {
            const randomName = leadNames[Math.floor(Math.random() * leadNames.length)];
            const randomEmail = randomName.toLowerCase().replace(' ', '') + '@vcompany.com';
            const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
            const randomScore = Math.floor(Math.random() * 40) + 60;
            
            const newLead = {
                id: Date.now(),
                name: randomName,
                email: randomEmail,
                status: randomStatus,
                score: randomScore
            };
            
            leads.unshift(newLead);
            renderLeads();
            addLog(\`Added/Deployed Lead: \${randomName} (Score: \${randomScore})\`);
        }

        function upgradeLead(id) {
            const lead = leads.find(l => l.id === id);
            if (lead) {
                lead.status = "Closing";
                lead.score = Math.min(lead.score + 10, 100);
                renderLeads();
                addLog(\`Escalated \${lead.name} to Closing Matrix with high score!\`);
            }
        }

        function addLog(message) {
            const logContainer = document.getElementById('operational-logs');
            const logItem = document.createElement('div');
            logItem.className = 'p-3 bg-gray-950 rounded-xl border border-gray-850 flex justify-between items-center text-xs text-gray-400';
            logItem.innerHTML = \`
                <span>\${message}</span>
                <span class="text-[10px] text-gray-600 font-mono">Just Now</span>
            \`;
            logContainer.insertBefore(logItem, logContainer.firstChild);
            if (logContainer.children.length > 4) {
                logContainer.removeChild(logContainer.lastChild);
            }
        }

        // Initialize Operational Activity Logs
        function initLogs() {
            const logs = [
                "Connection established with Dynamic Leads Router",
                "Successfully authorized Vertex Enterprise APIs",
                "Realtime Analytics sync matching baseline trends"
            ];
            logs.forEach(log => addLog(log));
        }

        // Initialize Chart
        function initChart() {
            const ctx = document.getElementById('crmStatsChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Q1', 'Q2', 'Q3', 'Q4', 'Current Hub'],
                    datasets: [{
                        label: 'CRM Conversion Index',
                        data: [12, 19, 15, 27, 34],
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: { grid: { display: false }, ticks: { color: '#6b7280' } },
                        y: { grid: { color: 'rgba(75, 85, 99, 0.1)' }, ticks: { color: '#6b7280' } }
                    }
                }
            });
        }

        renderLeads();
        initLogs();
        initChart();
    </script>
</body>
</html>`
  },
  {
    id: 'placeholder-builder-sandbox',
    name: 'Interactive Minimal Alignment Simulator',
    timestamp: new Date(),
    originalImages: [],
    html: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Builder V4</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-white min-h-screen flex flex-col justify-center items-center p-8">
    <div class="max-w-md bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-xl text-center">
        <h1 class="text-xl font-bold mb-4">NimbusIQ Interface Optimizer</h1>
        <p class="text-sm text-slate-400 mb-6">This interactive alignment tool evaluates user interface layout weights. Feel free to drag or slide parameters to experiment.</p>
        
        <div class="space-y-4">
            <div>
                <label class="block text-xs font-mono text-slate-500 mb-2">Simulated Operational Traffic</label>
                <input type="range" class="w-full" min="10" max="100" value="75" oninput="document.getElementById('val-track').innerText = this.value">
                <span id="val-track" class="text-xs font-semibold text-blue-400">75</span>% efficiency
            </div>
        </div>
    </div>
</body>
</html>`
  }
];
