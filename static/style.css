@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ---------------- CSS VARIABLES ---------------- */
:root {
    --bg-color: #f8fafc;
    --sidebar-bg: #0f172a;
    --sidebar-text: #94a3b8;
    --sidebar-hover: #1e293b;
    --sidebar-active: #ffffff;
    --primary-color: #4f46e5;
    --primary-hover: #4338ca;
    --danger-color: #ef4444;
    --danger-hover: #dc2626;
    --text-main: #1e293b;
    --text-muted: #64748b;
    --card-bg: #ffffff;
    --border-color: #e2e8f0;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --radius-md: 8px;
    --radius-lg: 12px;
}

/* ---------------- BODY & GLOBAL ---------------- */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-color);
    color: var(--text-main);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--text-main);
    font-weight: 600;
}

a {
    text-decoration: none;
    color: var(--primary-color);
    transition: all 0.2s ease;
}

a:hover {
    color: var(--primary-hover);
}

/* ---------------- BUTTONS ---------------- */
button, .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
    border-radius: var(--radius-md);
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    background-color: var(--primary-color);
    color: white;
    box-shadow: var(--shadow-sm);
}

button:hover, .btn:hover {
    background-color: var(--primary-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

button:active, .btn:active {
    transform: translateY(0);
}

.btn.edit { background-color: var(--primary-color); }
.btn.edit:hover { background-color: var(--primary-hover); }

.btn.delete { background-color: var(--danger-color); }
.btn.delete:hover { background-color: var(--danger-hover); }

/* ---------------- LOGIN PAGE ---------------- */
.login-container {
    width: 100%;
    height: 100vh;
    background: radial-gradient(circle at top left, #3b82f6, #4f46e5);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.login-card {
    background: rgba(255, 255, 255, 0.95);
    padding: 40px;
    border-radius: var(--radius-lg);
    width: 100%;
    max-width: 400px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    text-align: center;
    color: var(--text-main);
}

.login-card h2 {
    font-size: 24px;
    margin-bottom: 8px;
    color: var(--sidebar-bg);
}

.login-card .subtitle {
    font-size: 14px;
    color: var(--text-muted);
    margin-bottom: 30px;
}

.login-card .input-group {
    position: relative;
    margin-bottom: 24px;
    text-align: left;
}

.login-card input {
    width: 100%;
    padding: 12px 16px;
    background: #f1f5f9;
    border: 1px solid transparent;
    border-radius: var(--radius-md);
    font-size: 14px;
    color: var(--text-main);
    transition: all 0.3s;
    outline: none;
}

.login-card input:focus {
    background: white;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
}

.login-card label {
    position: absolute;
    top: -10px;
    left: 12px;
    background: white;
    padding: 0 4px;
    font-size: 12px;
    color: var(--primary-color);
    border-radius: 4px;
    font-weight: 500;
}

.login-card button {
    width: 100%;
    padding: 12px;
    font-size: 15px;
    margin-top: 10px;
}

.login-card .error {
    color: var(--danger-color);
    font-size: 13px;
    margin-top: 15px;
    background: #fef2f2;
    padding: 10px;
    border-radius: var(--radius-md);
}

/* ---------------- LAYOUT ---------------- */
.container {
    display: flex;
    min-height: 100vh;
}

/* SIDEBAR */
.sidebar {
    width: 260px;
    background-color: var(--sidebar-bg);
    color: var(--sidebar-text);
    padding: 24px 20px;
    flex-shrink: 0;
    box-shadow: 4px 0 10px rgba(0,0,0,0.05);
    display: flex;
    flex-direction: column;
}

.sidebar h2 {
    color: white;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 40px;
    text-align: center;
}

.sidebar ul {
    list-style: none;
}

.sidebar ul li {
    margin-bottom: 4px;
}

.sidebar ul li a {
    color: var(--sidebar-text);
    display: flex;
    align-items: center;
    padding: 10px 14px;
    border-radius: var(--radius-md);
    font-size: 14px;
    font-weight: 500;
}

.sidebar ul li a:hover {
    background-color: var(--sidebar-hover);
    color: var(--sidebar-active);
}

.sidebar ul li.menu-title {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #64748b;
    margin-top: 30px;
    margin-bottom: 10px;
    font-weight: 600;
    padding-left: 14px;
}

/* MAIN CONTENT */
.main {
    flex: 1;
    padding: 30px 40px;
    overflow-y: auto;
}

.main h1 {
    font-size: 24px;
    margin-bottom: 24px;
    color: var(--sidebar-bg);
}

/* ---------------- DASHBOARD CARDS ---------------- */
.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 24px;
    margin-bottom: 30px;
}

.card {
    background: var(--card-bg);
    padding: 24px;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
    transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.card h3 {
    font-size: 14px;
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.card p {
    font-size: 28px;
    font-weight: 700;
    color: var(--sidebar-bg);
}

/* ---------------- FORMS & INPUTS ---------------- */
.form-card {
    background: var(--card-bg);
    padding: 30px;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
    width: 100%;
    max-width: 800px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-main);
    margin-bottom: 8px;
}

input[type="text"], input[type="number"], input[type="date"], select {
    width: 100%;
    padding: 10px 14px;
    background: #fff;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    font-size: 14px;
    color: var(--text-main);
    transition: all 0.2s;
    outline: none;
    font-family: inherit;
}

input:focus, select:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

/* Form Grid */
.grid-2-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

/* ---------------- FILTER BOX (overall programs) ---------------- */
.filter-box {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    background: var(--card-bg);
    padding: 16px 20px;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
    margin-bottom: 24px;
}

.filter-box input, .filter-box select {
    flex: 1;
    min-width: 140px;
}

/* ---------------- TABLES ---------------- */
.table-responsive {
    overflow-x: auto;
    background: var(--card-bg);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
}

.data-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    text-align: left;
}

.data-table th, .data-table td {
    padding: 14px 16px;
    border-bottom: 1px solid var(--border-color);
    white-space: nowrap;
}

.data-table th {
    background-color: #f8fafc;
    font-size: 12px;
    text-transform: uppercase;
    color: var(--text-muted);
    font-weight: 600;
    letter-spacing: 0.5px;
}

.data-table tbody tr {
    transition: background-color 0.15s;
}

.data-table tbody tr:hover {
    background-color: #f1f5f9;
}

.data-table tbody tr:last-child td {
    border-bottom: none;
}

.data-table td {
    font-size: 14px;
    color: var(--text-main);
}

/* Status Pills */
.status-pill {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}

.s-pending { background: #fef3c7; color: #d97706; }
.s-wip { background: #dbeafe; color: #2563eb; }
.s-completed { background: #d1fae5; color: #059669; }

/* ---------------- ACTION MENU ---------------- */
.action-wrap {
    position: relative;
    display: inline-block;
}

.action-btn {
    background: white;
    color: var(--text-main);
    border: 1px solid var(--border-color);
    box-shadow: none;
}

.action-btn:hover {
    background: #f8fafc;
    color: var(--primary-color);
    box-shadow: none;
}

.action-menu {
    display: none;
    position: absolute;
    right: 0;
    top: calc(100% + 5px);
    background: white;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    z-index: 50;
    min-width: 180px;
    overflow: hidden;
}

.action-menu a {
    display: block;
    padding: 10px 16px;
    color: var(--text-main) !important;
    font-size: 13px;
}

.action-menu a:hover {
    background: #f1f5f9;
    color: var(--primary-color) !important;
}

.action-menu hr {
    border: none;
    border-top: 1px solid var(--border-color);
    margin: 0;
}

/* ---------------- PRINT MEDIA ---------------- */
@media print {
    .sidebar, button, .action-wrap, a.btn {
        display: none !important;
    }
    .main {
        padding: 0;
    }
    .container {
        display: block;
    }
    .data-table, .form-card {
        box-shadow: none;
        border: none;
    }
    .data-table th, .data-table td {
        border: 1px solid #000;
    }
}
