```python
from flask import Flask, render_template_string

app = Flask(__name__)

# ==========================================
# 釣りゲームのHTML/JS/CSSすべてを含むテンプレート
# ==========================================
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>魔釣お魚釣りゲーム - Python版</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Kiwi+Maru:wght@500;700&display=swap');
        body {
            font-family: 'Kiwi Maru', sans-serif;
            touch-action: none;
            -webkit-user-select: none;
            user-select: none;
            overflow: hidden;
            background-color: #020617;
        }
        canvas {
            image-rendering: pixelated;
        }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        @keyframes pulse-fast {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.05); opacity: 0.9; }
        }
        .fever-text { animation: pulse-fast 0.5s infinite; }
    </style>
</head>
<body class="m-0 p-0 w-full h-[100dvh]">

    <div id="gameUI" class="relative w-full h-full bg-slate-900 overflow-hidden flex flex-col">
        
        <!-- Canvas (海と魚の描画レイヤー) -->
        <canvas id="gameCanvas" class="absolute inset-0 z-0 block w-full h-full"></canvas>

        <!-- ================= ヘッダーUIレイヤー ================= -->
        <div class="absolute top-0 inset-x-0 p-3 md:p-4 flex justify-between items-center z-10 pointer-events-none">
            <div class="flex items-center space-x-2 bg-slate-900/80 px-4 py-2 rounded-full border border-cyan-500/50 shadow-lg pointer-events-auto backdrop-blur-sm">
                <span class="text-xl text-yellow-400">🏆</span>
                <span id="scoreText" class="font-bold text-sm text-white tracking-wider">SCORE: 0</span>
            </div>
            
            <div class="flex items-center space-x-2 bg-slate-900/80 px-4 py-2 rounded-full border border-cyan-500/50 shadow-lg pointer-events-auto backdrop-blur-sm">
                <span id="timeIcon" class="text-xl text-cyan-400 animate-pulse">⏱️</span>
                <span id="timeText" class="font-bold text-sm text-white tracking-wider">TIME: 60</span>
            </div>

            <button id="soundBtn" class="w-10 h-10 flex items-center justify-center bg-slate-900/80 rounded-full hover:bg-slate-800 text-cyan-300 border border-cyan-500/50 active:scale-90 transition-all pointer-events-auto shadow-lg backdrop-blur-sm">
                <i id="soundIcon" class="fas fa-volume-up text-lg"></i>
            </button>
        </div>

        <!-- ================= 演出オーバーレイレイヤー ================= -->
        <div id="feverOverlay" class="absolute top-20 inset-x-0 mx-auto w-11/12 max-w-[320px] z-10 bg-gradient-to-r from-cyan-600/95 via-blue-600/95 to-cyan-600/95 border-2 border-yellow-400 rounded-xl py-2 px-3 text-center text-white hidden shadow-[0_0_20px_rgba(6,182,212,0.8)] animate-pulse pointer-events-none">
            <div class="fever-text flex items-center justify-center gap-2">
                <span class="text-2xl">👹</span>
                <span class="font-black text-sm tracking-wider text-yellow-300">魔釣発動！ポイント2倍！</span>
                <span class="text-2xl">👹</span>
            </div>
            <div class="w-full bg-slate-950/60 h-2 rounded-full mt-2 overflow-hidden">
                <div id="feverBar" class="bg-yellow-400 h-full w-full transition-all duration-100 ease-linear"></div>
            </div>
        </div>

        <div id="mazumeOverlay" class="absolute bottom-10 inset-x-0 mx-auto w-11/12 max-w-[320px] z-10 bg-gradient-to-r from-amber-500/95 to-orange-600/95 border-2 border-yellow-300 rounded-xl py-3 px-3 text-center text-white hidden shadow-[0_0_20px_rgba(249,115,22,0.8)] animate-bounce pointer-events-none">
            <div class="flex items-center justify-center gap-2">
                <span class="text-2xl">🌅</span>
                <span class="font-black text-sm tracking-wider text-white drop-shadow-md">マズメタイム！お魚大増殖！</span>
                <span class="text-2xl">🌅</span>
            </div>
        </div>

        <div id="tapHint" class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none text-white text-center font-bold text-base bg-cyan-950/90 border-2 border-cyan-400 px-6 py-4 rounded-full animate-pulse transition-opacity duration-500 shadow-lg shadow-cyan-500/50 hidden z-10">
            🌊 タップして釣り針を落とそう！
        </div>

        <!-- ================= START SCREEN ================= -->
        <div id="startScreen" class="absolute inset-0 z-30 bg-gradient-to-b from-slate-950/95 via-blue-950/95 to-cyan-950/95 backdrop-blur-sm overflow-y-auto no-scrollbar flex flex-col items-center pt-8 pb-12 px-4 transition-opacity duration-300">
            <div class="w-full max-w-md flex flex-col items-center">
                <div class="w-full text-center shrink-0 mb-4">
                    <span class="inline-block text-[10px] bg-cyan-500 text-slate-950 font-black px-3 py-1 rounded-full uppercase tracking-wider animate-pulse shadow-md shadow-cyan-500/50">
                        ラスト10秒：お魚2倍「マズメタイム」！
                    </span>
                    <h1 class="text-[32px] font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-300 to-yellow-300 mt-2 drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)] leading-tight flex flex-col items-center justify-center">
                        <span>魔釣</span>
                        <span class="text-[40px] text-cyan-400 font-black tracking-tighter mt-1">お魚釣りゲーム</span>
                    </h1>
                </div>

                <div class="w-full bg-slate-900/80 border border-yellow-500/50 rounded-2xl p-4 my-2 text-center shadow-[0_0_20px_rgba(234,179,8,0.2)] shrink-0">
                    <p class="text-xs text-yellow-400 font-black tracking-wider flex items-center justify-center gap-1">
                        <i class="fas fa-trophy"></i> あなたの最高記録 (MY BEST)
                    </p>
                    <p class="text-4xl font-black text-yellow-400 tracking-wider mt-2">
                        <span id="startHighScore">0</span> <span class="text-lg">点</span>
                    </p>
                </div>

                <div class="w-full my-6 shrink-0">
                    <button id="startBtn" class="w-full py-5 px-6 bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-400 hover:to-blue-500 text-white font-black text-2xl rounded-2xl shadow-[0_0_25px_rgba(6,182,212,0.6)] border-b-4 border-blue-800 active:border-b-0 active:translate-y-1 transition-all duration-150 transform flex items-center justify-center gap-3">
                        <i class="fas fa-ship text-3xl"></i> 出航する！
                    </button>
                </div>

                <div class="w-full bg-slate-950/80 border border-cyan-500/30 rounded-2xl p-4 mb-4 text-xs text-left shadow-lg shrink-0">
                    <p class="font-bold text-center text-cyan-400 mb-2 border-b border-cyan-500/20 pb-1.5 flex items-center justify-center gap-1 text-sm">
                        <i class="fas fa-info-circle"></i> ゲームの極意
                    </p>
                    <ul class="space-y-2 text-slate-300 font-semibold leading-relaxed">
                        <li class="flex items-start gap-1.5">
                            <span class="text-cyan-400">●</span>
                            <span>「魔釣（👹）」を釣ると、<b>10秒間すべての得点が2倍</b>！</span>
                        </li>
                        <li class="flex items-start gap-1.5">
                            <span class="text-yellow-400">●</span>
                            <span>残り10秒は<b>マズメタイム</b>！お魚の出現数が<b>2倍（24匹）</b>に増殖！</span>
                        </li>
                        <li class="flex items-start gap-1.5">
                            <span class="text-purple-400">●</span>
                            <span>クラゲ（🪼）はビリビリ減点！避けて釣ろう！</span>
                        </li>
                    </ul>
                </div>

                <div class="w-full bg-slate-900/60 border border-cyan-500/20 rounded-2xl p-3 mb-6 text-center shadow-md shrink-0">
                    <p class="text-[10px] text-cyan-400 font-black tracking-wider mb-2 flex items-center justify-center gap-1">
                        <i class="fas fa-fish"></i> 獲物の得点一覧
                    </p>
                    <div class="grid grid-cols-4 gap-1.5 text-[10px] font-bold text-slate-300">
                        <div class="bg-slate-900/80 py-2 rounded-lg border border-cyan-500/10 flex flex-col items-center gap-0.5"><span class="text-2xl">🐟</span><span class="text-cyan-400">+10</span></div>
                        <div class="bg-slate-900/80 py-2 rounded-lg border border-cyan-500/10 flex flex-col items-center gap-0.5"><span class="text-2xl">🐠</span><span class="text-cyan-400">+30</span></div>
                        <div class="bg-slate-900/80 py-2 rounded-lg border border-cyan-500/10 flex flex-col items-center gap-0.5"><span class="text-2xl">🐡</span><span class="text-cyan-400">+50</span></div>
                        <div class="bg-slate-900/80 py-2 rounded-lg border border-cyan-500/10 flex flex-col items-center gap-0.5"><span class="text-2xl">🦑</span><span class="text-cyan-400">+40</span></div>
                        <div class="bg-slate-900/80 py-2 rounded-lg border border-cyan-500/10 flex flex-col items-center gap-0.5"><span class="text-2xl">🦈</span><span class="text-cyan-400">+120</span></div>
                        <div class="bg-slate-900/80 py-2 rounded-lg border border-cyan-500/10 flex flex-col items-center gap-0.5"><span class="text-2xl">💎</span><span class="text-yellow-400">+200</span></div>
                        <div class="bg-slate-900/80 py-2 rounded-lg border border-cyan-500/30 flex flex-col items-center gap-0.5"><span class="text-2xl">👹</span><span class="text-cyan-300 text-[8px]">得点2倍</span></div>
                        <div class="bg-slate-900/80 py-2 rounded-lg border border-red-500/30 flex flex-col items-center gap-0.5"><span class="text-2xl">🪼</span><span class="text-purple-400">-30</span></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ================= GAMEOVER SCREEN ================= -->
        <div id="gameOverScreen" class="absolute inset-0 z-30 bg-slate-950/95 backdrop-blur-md flex flex-col items-center justify-center p-4 text-white text-center hidden overflow-y-auto no-scrollbar pb-16">
            <div class="bg-slate-900 text-white rounded-3xl p-6 w-full max-w-sm shadow-2xl border-4 border-cyan-500 my-4 shadow-[0_0_30px_rgba(6,182,212,0.3)]">
                <h2 class="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 mb-2">漁が終了しました！</h2>
                <div class="my-6 py-4 border-y border-slate-800">
                    <p class="text-sm text-slate-400 font-bold">今回の獲得スコア</p>
                    <p id="finalScore" class="text-6xl font-extrabold text-yellow-400 tracking-wider my-3 drop-shadow-md">0</p>
                    <div class="mt-4 bg-slate-950/80 rounded-xl p-3 border border-slate-800 flex flex-col items-center">
                        <p class="text-xs text-slate-400 font-semibold mb-1">
                            <i class="fas fa-crown text-yellow-500"></i> これまでの最高記録
                        </p>
                        <p id="highScoreText" class="text-2xl text-cyan-300 font-bold block">0</p>
                    </div>
                </div>
                <div id="newRecordMsg" class="mb-6 text-sm font-bold py-3 px-3 rounded-xl bg-gradient-to-r from-yellow-500 to-orange-500 text-white shadow-lg animate-bounce hidden">
                    🎉 新記録達成！おめでとうございます！ 🎉
                </div>
                <div class="space-y-3 mt-4">
                    <button id="retryBtn" class="w-full py-4 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-xl rounded-xl shadow-[0_0_15px_rgba(6,182,212,0.4)] active:translate-y-1 transition-all border-b-4 border-blue-800 flex justify-center items-center gap-2">
                        <i class="fas fa-redo"></i> もう一度挑戦！
                    </button>
                    <button id="backToTitleBtn" class="w-full py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold rounded-xl text-sm transition-all border border-slate-700">
                        タイトルに戻る
                    </button>
                </div>
            </div>
        </div>

    </div>

    <!-- ================= JAVASCRIPT LOGIC ================= -->
    <script>
        let canvas = document.getElementById('gameCanvas');
        let ctx = canvas.getContext('2d', { alpha: false });
        let CANVAS_WIDTH = window.innerWidth;
        let CANVAS_HEIGHT = window.innerHeight;

        const safeStorage = {
            getItem(key) { try { return localStorage.getItem(key); } catch (e) { return this[key] || null; } },
            setItem(key, value) { try { localStorage.setItem(key, value); } catch (e) { this[key] = value; } }
        };

        let scoreText, timeText, timeIcon, startScreen, gameOverScreen, tapHint, finalScore, highScoreText, startHighScore, newRecordMsg;
        let feverOverlay, feverBar, mazumeOverlay, soundIcon, soundBtn;

        let soundEnabled = true;
        let state = 'start'; 
        let score = 0;
        let timeLeft = 60;
        let timerInterval = null;
        let highScore = parseInt(safeStorage.getItem('fishing_high_score')) || 0;
        let feverTimeLeft = 0;
        const feverDuration = 10000; 

        // --- ★釣り番組風 BGMシステム (ファミコン風8-bit) ---
        let bgmStep = 0;
        let bgmTimeoutId = null;

        const MUSIC_NOTES = {
            'F2': 87.31, 'G2': 98.00, 'A2': 110.00, 'B2': 123.47,
            'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
            'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
            'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00, 'B5': 987.77, 
            'C6': 1046.50, 'D6': 1174.66, 'E6': 1318.51
        };

        const melodyPattern = [
            'C5', '-', 'E5', '-', 'G5', '-', 'E5', '-',  'C6', '-', '-', '-', 'G5', '-', '-', '-',
            'A5', '-', '-', '-', 'G5', '-', '-', '-',  'E5', '-', 'C5', '-', 'D5', '-', 'E5', '-',
            'D5', '-', 'F5', '-', 'A5', '-', 'F5', '-',  'D6', '-', '-', '-', 'A5', '-', '-', '-',
            'G5', '-', '-', '-', 'F5', '-', '-', '-',  'D5', '-', 'B4', '-', 'G4', '-', '-', '-',
            'C5', '-', 'E5', '-', 'G5', '-', 'E5', '-',  'C6', '-', '-', '-', 'G5', '-', '-', '-',
            'A5', '-', '-', '-', 'G5', '-', '-', '-',  'E5', '-', 'C5', '-', 'A4', '-', '-', '-',
            'F5', '-', 'E5', '-', 'D5', '-', 'C5', '-',  'B4', '-', 'C5', '-', 'D5', '-', 'E5', '-',
            'C5', '-', '-', '-', 'C5', '-', 'G4', '-',  'C5', '-', '-', '-', '-', '-', '-', '-'
        ];

        const bassPattern = [
            'C3', '-', '-', '-', 'G3', '-', '-', '-',  'C4', '-', '-', '-', 'G3', '-', '-', '-',
            'C3', '-', '-', '-', 'G3', '-', '-', '-',  'C4', '-', '-', '-', 'G3', '-', '-', '-',
            'D3', '-', '-', '-', 'A3', '-', '-', '-',  'D4', '-', '-', '-', 'A3', '-', '-', '-',
            'G3', '-', '-', '-', 'D4', '-', '-', '-',  'B3', '-', '-', '-', 'G3', '-', '-', '-',
            'C3', '-', '-', '-', 'G3', '-', '-', '-',  'C4', '-', '-', '-', 'G3', '-', '-', '-',
            'A3', '-', '-', '-', 'E3', '-', '-', '-',  'A3', '-', '-', '-', 'E3', '-', '-', '-',
            'F3', '-', '-', '-', 'G3', '-', '-', '-',  'A3', '-', '-', '-', 'B3', '-', '-', '-',
            'C3', '-', 'G3', '-', 'C4', '-', 'G3', '-',  'C3', '-', '-', '-', '-', '-', '-', '-'
        ];

        let audioCtx = null;
        function initAudio() {
            try { if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { audioCtx = null; }
        }

        const unlockAudio = () => {
            try {
                initAudio();
                if (audioCtx && audioCtx.state === 'suspended') {
                    audioCtx.resume().then(() => {
                        window.removeEventListener('click', unlockAudio);
                        window.removeEventListener('touchstart', unlockAudio);
                    }).catch(e => {});
                }
            } catch (e) {}
        };
        window.addEventListener('click', unlockAudio);
        window.addEventListener('touchstart', unlockAudio, { passive: true });

        function playDrumTone(time, type) {
            try {
                if (!audioCtx) return;
                if (type === 'kick') {
                    const osc = audioCtx.createOscillator();
                    const gain = audioCtx.createGain();
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(120, time);
                    osc.frequency.exponentialRampToValueAtTime(20, time + 0.1); 
                    gain.gain.setValueAtTime(0.2, time);
                    gain.gain.exponentialRampToValueAtTime(0.01, time + 0.1);
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    osc.start(time);
                    osc.stop(time + 0.15);
                } else if (type === 'snare') {
                    const bufferSize = audioCtx.sampleRate * 0.1;
                    const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
                    const data = buffer.getChannelData(0);
                    for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;
                    const noise = audioCtx.createBufferSource();
                    noise.buffer = buffer;
                    const filter = audioCtx.createBiquadFilter();
                    filter.type = 'highpass';
                    filter.frequency.value = 800;
                    const gain = audioCtx.createGain();
                    gain.gain.setValueAtTime(0.15, time);
                    gain.gain.exponentialRampToValueAtTime(0.01, time + 0.1);
                    noise.connect(filter);
                    filter.connect(gain);
                    gain.connect(audioCtx.destination);
                    noise.start(time);
                    noise.stop(time + 0.15);
                } else if (type === 'hihat') {
                    const bufferSize = audioCtx.sampleRate * 0.05;
                    const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
                    const data = buffer.getChannelData(0);
                    for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;
                    const noise = audioCtx.createBufferSource();
                    noise.buffer = buffer;
                    const filter = audioCtx.createBiquadFilter();
                    filter.type = 'highpass';
                    filter.frequency.value = 5000;
                    const gain = audioCtx.createGain();
                    gain.gain.setValueAtTime(0.03, time);
                    gain.gain.exponentialRampToValueAtTime(0.01, time + 0.05);
                    noise.connect(filter);
                    filter.connect(gain);
                    gain.connect(audioCtx.destination);
                    noise.start(time);
                    noise.stop(time + 0.1);
                }
            } catch (e) {}
        }

        function playBGMStep() {
            if (state !== 'playing' || !soundEnabled) return;
            initAudio();

            try {
                if (audioCtx && audioCtx.state === 'running') {
                    const now = audioCtx.currentTime;
                    const mNote = melodyPattern[bgmStep];
                    const bNote = bassPattern[bgmStep];
                    
                    const bpm = (timeLeft <= 10) ? 175 : 130; 
                    const stepDurationSec = 60 / bpm / 4; 

                    if (mNote && mNote !== '-') {
                        const oscMel = audioCtx.createOscillator();
                        const gainMel = audioCtx.createGain();
                        oscMel.type = 'square';
                        oscMel.frequency.setValueAtTime(MUSIC_NOTES[mNote], now);
                        
                        let sustainCount = 0;
                        for(let i = bgmStep + 1; i < melodyPattern.length; i++) {
                            if(melodyPattern[i] === '-') sustainCount++;
                            else break;
                        }
                        const holdTime = (sustainCount + 1) * stepDurationSec;
                        
                        gainMel.gain.setValueAtTime(0.025, now);
                        gainMel.gain.setValueAtTime(0.025, now + holdTime * 0.7);
                        gainMel.gain.linearRampToValueAtTime(0.0001, now + holdTime * 0.95);
                        
                        oscMel.connect(gainMel);
                        gainMel.connect(audioCtx.destination);
                        oscMel.start(now);
                        oscMel.stop(now + holdTime);
                    }

                    if (bNote && bNote !== '-') {
                        const oscBass = audioCtx.createOscillator();
                        const gainBass = audioCtx.createGain();
                        oscBass.type = 'triangle';
                        oscBass.frequency.setValueAtTime(MUSIC_NOTES[bNote], now);
                        
                        let sustainCount = 0;
                        for(let i = bgmStep + 1; i < bassPattern.length; i++) {
                            if(bassPattern[i] === '-') sustainCount++;
                            else break;
                        }
                        const holdTime = (sustainCount + 1) * stepDurationSec;
                        
                        gainBass.gain.setValueAtTime(0.07, now);
                        gainBass.gain.setValueAtTime(0.07, now + holdTime * 0.8);
                        gainBass.gain.linearRampToValueAtTime(0.0001, now + holdTime * 0.95);
                        
                        oscBass.connect(gainBass);
                        gainBass.connect(audioCtx.destination);
                        oscBass.start(now);
                        oscBass.stop(now + holdTime);
                    }

                    const beatIdx = bgmStep % 16;
                    if (beatIdx === 0 || beatIdx === 8) playDrumTone(now, 'kick');
                    if (beatIdx === 4 || beatIdx === 12) playDrumTone(now, 'snare');
                    if (beatIdx % 2 === 0) playDrumTone(now, 'hihat'); 
                    
                } else if (audioCtx && audioCtx.state === 'suspended') {
                    audioCtx.resume().catch(e => {});
                }
            } catch (e) {}

            bgmStep = (bgmStep + 1) % melodyPattern.length;
            const bpm = (timeLeft <= 10) ? 175 : 130;
            const stepDurationMs = (60 / bpm / 4) * 1000;
            bgmTimeoutId = setTimeout(playBGMStep, stepDurationMs);
        }

        function stopBGM() {
            if (bgmTimeoutId) {
                clearTimeout(bgmTimeoutId);
                bgmTimeoutId = null;
            }
        }

        function playSound(type) {
            if (!soundEnabled) return;
            try {
                initAudio();
                if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume().catch(e => {});
                if (audioCtx && audioCtx.state === 'running') {
                    const osc = audioCtx.createOscillator();
                    const gainNode = audioCtx.createGain();
                    osc.connect(gainNode);
                    gainNode.connect(audioCtx.destination);
                    const now = audioCtx.currentTime;

                    if (type === 'click') {
                        osc.type = 'triangle';
                        osc.frequency.setValueAtTime(150, now);
                        osc.frequency.exponentialRampToValueAtTime(300, now + 0.1);
                        gainNode.gain.setValueAtTime(0.15, now);
                        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
                        osc.start(now);
                        osc.stop(now + 0.1);
                    } else if (type === 'cast') {
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(600, now);
                        osc.frequency.exponentialRampToValueAtTime(150, now + 0.4);
                        gainNode.gain.setValueAtTime(0.1, now);
                        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
                        osc.start(now);
                        osc.stop(now + 0.4);
                    } else if (type === 'catch') {
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(300, now);
                        osc.frequency.setValueAtTime(450, now + 0.08);
                        osc.frequency.setValueAtTime(700, now + 0.16);
                        gainNode.gain.setValueAtTime(0.15, now);
                        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                        osc.start(now);
                        osc.stop(now + 0.3);
                    } else if (type === 'fever_trigger') {
                        osc.type = 'sawtooth';
                        osc.frequency.setValueAtTime(200, now);
                        osc.frequency.setValueAtTime(400, now + 0.1);
                        osc.frequency.setValueAtTime(300, now + 0.2);
                        osc.frequency.setValueAtTime(600, now + 0.3);
                        osc.frequency.linearRampToValueAtTime(800, now + 0.6);
                        gainNode.gain.setValueAtTime(0.2, now);
                        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.7);
                        osc.start(now);
                        osc.stop(now + 0.7);
                    } else if (type === 'mazume_trigger') {
                        osc.type = 'triangle';
                        osc.frequency.setValueAtTime(293.7, now); 
                        osc.frequency.setValueAtTime(349.2, now + 0.1); 
                        osc.frequency.setValueAtTime(440.0, now + 0.2); 
                        osc.frequency.setValueAtTime(587.3, now + 0.3); 
                        gainNode.gain.setValueAtTime(0.15, now);
                        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.8);
                        osc.start(now);
                        osc.stop(now + 0.8);
                    } else if (type === 'jellyfish') {
                        osc.type = 'sawtooth';
                        osc.frequency.setValueAtTime(120, now);
                        osc.frequency.setValueAtTime(90, now + 0.08);
                        osc.frequency.setValueAtTime(100, now + 0.16);
                        gainNode.gain.setValueAtTime(0.25, now);
                        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
                        osc.start(now);
                        osc.stop(now + 0.4);
                    } else if (type === 'treasure') {
                        osc.type = 'triangle';
                        osc.frequency.setValueAtTime(350, now);
                        osc.frequency.setValueAtTime(440, now + 0.1);
                        osc.frequency.setValueAtTime(554, now + 0.2);
                        osc.frequency.setValueAtTime(659, now + 0.3);
                        osc.frequency.setValueAtTime(880, now + 0.4);
                        gainNode.gain.setValueAtTime(0.2, now);
                        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.8);
                        osc.start(now);
                        osc.stop(now + 0.8);
                    } else if (type === 'gameover') {
                        osc.type = 'square';
                        osc.frequency.setValueAtTime(250, now);
                        osc.frequency.linearRampToValueAtTime(80, now + 0.9);
                        gainNode.gain.setValueAtTime(0.15, now);
                        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.9);
                        osc.start(now);
                        osc.stop(now + 0.9);
                    }
                }
            } catch (e) {}
        }


        // --- ゲームオブジェクト ---
        class Boat {
            constructor() {
                this.x = CANVAS_WIDTH / 2;
                this.y = 120;
                this.targetX = CANVAS_WIDTH / 2;
                this.width = 60;
                this.height = 30;
                this.speed = 5.5;
            }
            update() {
                const diff = this.targetX - this.x;
                if (Math.abs(diff) > 2) this.x += Math.sign(diff) * this.speed;
            }
            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);

                if (feverTimeLeft > 0) {
                    ctx.fillStyle = `rgba(6, 182, 212, ${0.15 + Math.sin(Date.now() / 100) * 0.05})`;
                    ctx.beginPath();
                    ctx.arc(0, -10, 45, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.font = '16px sans-serif';
                    ctx.fillText('✨', -25, -30 + Math.sin(Date.now() / 100) * 3);
                    ctx.fillText('✨', 20, -25 + Math.cos(Date.now() / 110) * 3);
                } else {
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
                    ctx.beginPath();
                    ctx.ellipse(0, 5, 30 + Math.sin(Date.now() / 200) * 3, 5, 0, 0, Math.PI * 2);
                    ctx.fill();
                }

                ctx.fillStyle = feverTimeLeft > 0 ? '#083344' : '#1e3a8a';
                ctx.beginPath();
                ctx.moveTo(-30, -5);
                ctx.lineTo(25, -5);
                ctx.lineTo(15, 10);
                ctx.lineTo(-20, 10);
                ctx.closePath();
                ctx.fill();

                ctx.fillStyle = feverTimeLeft > 0 ? '#22d3ee' : '#3b82f6';
                ctx.fillRect(-28, -8, 52, 3);

                ctx.font = '28px sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(feverTimeLeft > 0 ? '🧜' : '👨‍🌾', -5, -18);

                ctx.strokeStyle = feverTimeLeft > 0 ? '#22d3ee' : '#94a3b8';
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.moveTo(8, -15);
                ctx.lineTo(38, -28);
                ctx.stroke();

                ctx.restore();
            }
        }

        class Hook {
            constructor(boat) {
                this.boat = boat;
                this.x = boat.x + 35;
                this.y = boat.y - 25;
                this.state = 'idle';
                this.targetY = 0;
                this.speed = 10.0;
                this.caughtFish = null;
            }
            update() {
                this.x = this.boat.x + 35;
                const currentSpeed = feverTimeLeft > 0 ? this.speed * 1.3 : this.speed;

                if (this.state === 'idle') {
                    this.y = this.boat.y - 10;
                } else if (this.state === 'dropping') {
                    this.y += currentSpeed;
                    if (this.y >= this.targetY || this.y >= CANVAS_HEIGHT - 20) {
                        this.state = 'retracting';
                    }
                } else if (this.state === 'retracting') {
                    this.y -= currentSpeed;
                    if (this.caughtFish) {
                        this.caughtFish.x = this.x;
                        this.caughtFish.y = this.y + 15;
                    }

                    if (this.y <= this.boat.y - 10) {
                        this.y = this.boat.y - 10;
                        this.state = 'idle';

                        if (this.caughtFish) {
                            const isMazuri = this.caughtFish.type === 'mazuri';
                            let earned = this.caughtFish.score;
                            const wasFever = feverTimeLeft > 0;
                            
                            if (wasFever) earned *= 2; 
                            score += earned;

                            if (isMazuri) {
                                feverTimeLeft = feverDuration;
                                playSound('fever_trigger');
                                createCatchParticles(this.x, this.y, '#06b6d4'); 
                            } else if (earned < 0) {
                                playSound('jellyfish');
                                createCatchParticles(this.x, this.y, '#a855f7'); 
                            } else if (this.caughtFish.type === 'treasure') {
                                playSound('treasure');
                                createCatchParticles(this.x, this.y, '#facc15'); 
                            } else {
                                playSound('catch');
                                createCatchParticles(this.x, this.y, wasFever ? '#22d3ee' : '#38bdf8');
                            }
                            if(scoreText) scoreText.innerText = `SCORE: ${score}`;
                            this.caughtFish = null;
                        }
                    }
                }
            }
            draw() {
                ctx.strokeStyle = feverTimeLeft > 0 ? '#22d3ee' : '#cbd5e1';
                ctx.lineWidth = feverTimeLeft > 0 ? 2.5 : 1.5;
                ctx.beginPath();
                ctx.moveTo(this.boat.x + 38, this.boat.y - 25);
                ctx.lineTo(this.x, this.y);
                ctx.stroke();

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.strokeStyle = feverTimeLeft > 0 ? '#facc15' : '#e2e8f0';
                ctx.lineWidth = 2.5;
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.arc(0, 5, 5, 0, Math.PI, false);
                ctx.moveTo(0, -3);
                ctx.lineTo(0, 5);
                ctx.moveTo(-5, 5);
                ctx.lineTo(-5, 1);
                ctx.stroke();

                ctx.fillStyle = feverTimeLeft > 0 ? '#06b6d4' : '#ff85a2';
                ctx.beginPath();
                ctx.arc(2, 2, 2.5, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            }
            cast(targetY, targetX) {
                if (this.state !== 'idle') return;
                this.targetY = targetY;
                this.boat.targetX = targetX - 35;
                this.state = 'dropping';
                playSound('cast');
            }
        }

        const FISH_TYPES = [
            { id: 'fish1', name: '小魚', emoji: '🐟', score: 10, speed: 1.8, size: 34, depthMin: 0.25, depthMax: 0.4 },
            { id: 'fish2', name: 'クマノミ', emoji: '🐠', score: 30, speed: 2.5, size: 36, depthMin: 0.35, depthMax: 0.55 },
            { id: 'fish3', name: 'フグ', emoji: '🐡', score: 50, speed: 1.2, size: 40, depthMin: 0.45, depthMax: 0.65 },
            { id: 'squid', name: 'イカ', emoji: '🦑', score: 40, speed: 1.5, size: 38, depthMin: 0.55, depthMax: 0.75 },
            { id: 'shark', name: 'サメ', emoji: '🦈', score: 120, speed: 4.0, size: 65, depthMin: 0.65, depthMax: 0.9 },
            { id: 'jellyfish', name: 'クラゲ', emoji: '🪼', score: -30, speed: 0.8, size: 38, depthMin: 0.3, depthMax: 0.8, harmful: true },
            { id: 'treasure', name: '宝箱', emoji: '💎', score: 200, speed: 0, size: 42, depthMin: 0.85, depthMax: 0.95, static: true },
            { id: 'mazuri', name: '魔釣', emoji: '👹', score: 50, speed: 3.2, size: 48, depthMin: 0.5, depthMax: 0.85 }
        ];

        class Fish {
            constructor() {
                this.reset();
                this.x = Math.random() * CANVAS_WIDTH;
            }
            reset() {
                const roll = Math.random() * 100;
                let chosenType = FISH_TYPES[0];

                if (roll < 30) chosenType = FISH_TYPES[0]; 
                else if (roll < 48) chosenType = FISH_TYPES[1]; 
                else if (roll < 62) chosenType = FISH_TYPES[2]; 
                else if (roll < 72) chosenType = FISH_TYPES[3]; 
                else if (roll < 82) chosenType = FISH_TYPES[5]; 
                else if (roll < 89) chosenType = FISH_TYPES[7]; 
                else if (roll < 95) chosenType = FISH_TYPES[4]; 
                else chosenType = FISH_TYPES[6]; 

                this.type = chosenType.id;
                this.emoji = chosenType.emoji;
                this.score = chosenType.score;
                this.speed = chosenType.speed * (0.8 + Math.random() * 0.4);
                
                if (timeLeft <= 10) this.speed *= 1.3;

                this.size = chosenType.size;
                this.harmful = chosenType.harmful || false;
                this.static = chosenType.static || false;

                const minH = CANVAS_HEIGHT * chosenType.depthMin;
                const maxH = CANVAS_HEIGHT * chosenType.depthMax;
                this.y = minH + Math.random() * (maxH - minH);

                this.direction = Math.random() > 0.5 ? 1 : -1;
                this.x = this.direction === 1 ? -60 : CANVAS_WIDTH + 60;
                this.angle = Math.random() * Math.PI * 2;
                this.bobSpeed = 0.02 + Math.random() * 0.03;
            }
            update() {
                if (this.static) {
                    this.angle += 0.01;
                    this.x += Math.sin(this.angle) * 0.1;
                    return;
                }
                this.x += this.speed * this.direction;

                if (this.type === 'squid' || this.type === 'jellyfish' || this.type === 'mazuri') {
                    this.angle += this.bobSpeed;
                    this.y += Math.sin(this.angle) * 0.8;
                } else {
                    this.angle += this.bobSpeed;
                    this.y += Math.sin(this.angle) * 0.3;
                }

                if (this.direction === 1 && this.x > CANVAS_WIDTH + 80) this.reset();
                else if (this.direction === -1 && this.x < -80) this.reset();
            }
            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                if (this.direction === 1 && !this.static) ctx.scale(-1, 1);

                if (this.type === 'mazuri') {
                    ctx.fillStyle = 'rgba(6, 182, 212, 0.25)';
                    ctx.beginPath();
                    ctx.arc(0, 0, this.size * 0.7, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = 'rgba(6, 182, 212, 0.5)';
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                }

                ctx.font = `${this.size}px sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(this.emoji, 0, 0);
                ctx.restore();
            }
        }

        class Particle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.color = color;
                this.size = 2 + Math.random() * 4;
                this.vx = (Math.random() - 0.5) * 6;
                this.vy = (Math.random() - 0.5) * 6 - 2;
                this.alpha = 1;
                this.decay = 0.02 + Math.random() * 0.02;
                this.isBubble = color === 'bubble';
                this.isFire = color === 'fire';
            }
            update() {
                this.x += this.vx;
                this.y += this.vy;
                if (this.isBubble) {
                    this.vy = -0.5 - Math.random() * 1;
                    this.vx += (Math.random() - 0.5) * 0.2;
                } else if (this.isFire) {
                    this.vy -= 0.1; 
                    this.vx += (Math.random() - 0.5) * 0.3;
                }
                this.alpha -= this.decay;
            }
            draw() {
                ctx.save();
                ctx.globalAlpha = this.alpha;
                if (this.isBubble) {
                    ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                    ctx.stroke();
                } else if (this.isFire) {
                    const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size);
                    grad.addColorStop(0, '#22d3ee'); 
                    grad.addColorStop(0.5, '#06b6d4'); 
                    grad.addColorStop(1, 'rgba(6, 182, 212, 0)');
                    ctx.fillStyle = grad;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                    ctx.fill();
                } else {
                    ctx.fillStyle = this.color;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                    ctx.fill();
                }
                ctx.restore();
            }
        }

        let boat = new Boat();
        let hook = new Hook(boat);
        let fishes = [];
        let particles = [];
        const normalMaxFishes = 12;
        let currentMaxFishes = normalMaxFishes;
        let isMazumeTriggered = false; 
        let lastTime = Date.now();

        function createCatchParticles(x, y, color) {
            try {
                const scorePopup = document.createElement('div');
                scorePopup.className = `absolute text-2xl font-extrabold select-none pointer-events-none transition-all duration-1000 transform -translate-x-1/2 -translate-y-1/2 z-10`;
                scorePopup.style.left = `${(x / CANVAS_WIDTH) * 100}%`;
                scorePopup.style.top = `${(y / CANVAS_HEIGHT) * 100}%`;
                
                const caught = hook.caughtFish;
                const isFeverNow = feverTimeLeft > 0;

                if (caught) {
                    if (caught.type === 'mazuri') {
                        scorePopup.innerHTML = `<span class="text-cyan-400 font-black">魔釣発動!! 👹</span><br><span class="text-yellow-300 text-sm">10秒間 ポイント2倍！</span>`;
                        scorePopup.style.textAlign = 'center';
                    } else if (caught.score < 0) {
                        scorePopup.innerText = isFeverNow ? `-60!! ⚡` : `-30!! ⚡`;
                        scorePopup.style.color = '#c084fc';
                    } else {
                        const scoreVal = isFeverNow ? caught.score * 2 : caught.score;
                        scorePopup.innerText = isFeverNow ? `+${scoreVal} 🔥2倍!!🔥` : `+${scoreVal}`;
                        scorePopup.style.color = isFeverNow ? '#facc15' : '#38bdf8';
                        if (isFeverNow) scorePopup.style.fontSize = '1.75rem';
                    }
                }

                if(canvas && canvas.parentElement) canvas.parentElement.appendChild(scorePopup);

                setTimeout(() => {
                    scorePopup.style.opacity = '0';
                    scorePopup.style.transform = 'translate(-50%, -120px) scale(1.3)';
                }, 50);

                setTimeout(() => { scorePopup.remove(); }, 1000);
            } catch (e) {}

            const count = hook.caughtFish?.type === 'mazuri' ? 30 : 15;
            for (let i = 0; i < count; i++) particles.push(new Particle(x, y, color));
        }

        function spawnBubble() {
            if (state !== 'playing') return;
            if (Math.random() < 0.1) particles.push(new Particle(Math.random() * CANVAS_WIDTH, CANVAS_HEIGHT, 'bubble'));
            if (feverTimeLeft > 0 && Math.random() < 0.2) particles.push(new Particle(Math.random() * CANVAS_WIDTH, CANVAS_HEIGHT - 20, 'fire'));
        }

        function handleTap(clientX, clientY) {
            if (state !== 'playing') return;
            try { if(tapHint) tapHint.style.opacity = '0'; } catch (e) {}

            if(!canvas) return;
            const rect = canvas.getBoundingClientRect();
            const scaleX = CANVAS_WIDTH / rect.width;
            const scaleY = CANVAS_HEIGHT / rect.height;

            const tapX = (clientX - rect.left) * scaleX;
            const tapY = (clientY - rect.top) * scaleY;

            if (tapY > 130) hook.cast(tapY, tapX);
        }

        function updateGame() {
            const now = Date.now();
            const dt = now - lastTime;
            lastTime = now;

            if (state === 'start' || state === 'gameover') {
                fishes.forEach(fish => fish.update());
            }

            if (state !== 'playing') return;

            if (feverTimeLeft > 0) {
                feverTimeLeft -= dt;
                if (feverTimeLeft < 0) feverTimeLeft = 0;
                if(feverOverlay) feverOverlay.classList.remove('hidden');
                if(feverBar) feverBar.style.width = `${(feverTimeLeft / feverDuration) * 100}%`;
            } else {
                if(feverOverlay) feverOverlay.classList.add('hidden');
            }

            if (timeLeft <= 10) {
                currentMaxFishes = normalMaxFishes * 2; 
                if (!isMazumeTriggered) {
                    isMazumeTriggered = true;
                    playSound('mazume_trigger');
                    if(mazumeOverlay) mazumeOverlay.classList.remove('hidden');

                    const fishToSpawn = currentMaxFishes - fishes.length;
                    for (let i = 0; i < fishToSpawn; i++) fishes.push(new Fish());
                    if(timeIcon) timeIcon.className = "text-xl text-orange-400 animate-ping";
                    if(timeText) timeText.className = "font-black text-sm text-orange-400";
                }
                if (Math.random() < 0.2) particles.push(new Particle(Math.random() * CANVAS_WIDTH, CANVAS_HEIGHT, 'bubble'));
            } else {
                currentMaxFishes = normalMaxFishes;
                if(mazumeOverlay) mazumeOverlay.classList.add('hidden');
            }

            boat.update();
            hook.update();

            fishes.forEach(fish => {
                fish.update();

                if ((hook.state === 'dropping' || hook.state === 'retracting') && !hook.caughtFish) {
                    const dx = hook.x - fish.x;
                    const dy = hook.y + 10 - fish.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    const hitRange = (fish.size / 2) + 16;

                    if (distance < hitRange) {
                        hook.caughtFish = fish;
                        hook.state = 'retracting';
                        fishes = fishes.filter(f => f !== fish);
                        
                        const respawnDelay = timeLeft <= 10 ? 500 : 2000;
                        setTimeout(() => {
                            if (state === 'playing' && fishes.length < currentMaxFishes) {
                                fishes.push(new Fish());
                            }
                        }, respawnDelay);
                    }
                }
            });

            particles.forEach((p, index) => {
                p.update();
                if (p.alpha <= 0 || p.y < 50) particles.splice(index, 1);
            });

            spawnBubble();
        }

        function drawGame() {
            ctx.fillStyle = '#020617';
            ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

            const oceanGrad = ctx.createLinearGradient(0, 0, 0, CANVAS_HEIGHT);
            
            if (timeLeft <= 10 && state === 'playing') {
                oceanGrad.addColorStop(0, '#f97316'); 
                oceanGrad.addColorStop(0.25, '#7c2d12'); 
                oceanGrad.addColorStop(0.6, '#1e1b4b'); 
                oceanGrad.addColorStop(1, '#020617');
            } else if (feverTimeLeft > 0 && state === 'playing') {
                oceanGrad.addColorStop(0, '#06b6d4'); 
                oceanGrad.addColorStop(0.2, '#1e3a8a'); 
                oceanGrad.addColorStop(0.5, '#0f172a'); 
                oceanGrad.addColorStop(1, '#020617'); 
            } else {
                oceanGrad.addColorStop(0, '#38bdf8'); 
                oceanGrad.addColorStop(0.2, '#0284c7'); 
                oceanGrad.addColorStop(0.6, '#0f172a'); 
                oceanGrad.addColorStop(1, '#020617');
            }
            
            ctx.fillStyle = oceanGrad;
            ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

            ctx.fillStyle = (timeLeft <= 10 && state === 'playing') ? 'rgba(251, 146, 60, 0.15)' : 'rgba(255, 255, 255, 0.07)';
            ctx.beginPath();
            ctx.moveTo(CANVAS_WIDTH * 0.2, 110);
            ctx.lineTo(CANVAS_WIDTH * 0.5, CANVAS_HEIGHT);
            ctx.lineTo(CANVAS_WIDTH * 0.35, CANVAS_HEIGHT);
            ctx.lineTo(CANVAS_WIDTH * 0.1, 110);
            ctx.closePath();
            ctx.fill();

            ctx.beginPath();
            ctx.moveTo(CANVAS_WIDTH * 0.6, 110);
            ctx.lineTo(CANVAS_WIDTH * 0.9, CANVAS_HEIGHT);
            ctx.lineTo(CANVAS_WIDTH * 0.75, CANVAS_HEIGHT);
            ctx.lineTo(CANVAS_WIDTH * 0.5, 110);
            ctx.closePath();
            ctx.fill();

            fishes.forEach(fish => fish.draw());
            particles.forEach(p => p.draw());
            
            if (state === 'playing') {
                hook.draw();
                boat.draw();

                if (hook.caughtFish) {
                    ctx.save();
                    ctx.translate(hook.x, hook.y + 12);
                    ctx.rotate(Math.sin(Date.now() / 50) * 0.3 + Math.PI / 2);
                    ctx.font = `${hook.caughtFish.size}px sans-serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(hook.caughtFish.emoji, 0, 0);
                    ctx.restore();
                }
            }

            ctx.fillStyle = (timeLeft <= 10 && state === 'playing') ? 'rgba(251, 146, 60, 0.3)' : 'rgba(255, 255, 255, 0.25)';
            ctx.beginPath();
            for (let i = 0; i <= CANVAS_WIDTH; i += 20) {
                const waveY = 120 + Math.sin((i + Date.now() / 15) * 0.05) * 3;
                if (i === 0) ctx.moveTo(i, waveY);
                else ctx.lineTo(i, waveY);
            }
            ctx.lineTo(CANVAS_WIDTH, CANVAS_HEIGHT);
            ctx.lineTo(0, CANVAS_HEIGHT);
            ctx.closePath();
            ctx.strokeStyle = (timeLeft <= 10 && state === 'playing') ? 'rgba(251, 146, 60, 0.6)' : 'rgba(255, 255, 255, 0.4)';
            ctx.lineWidth = 2;
            ctx.stroke();
        }

        function gameLoop() {
            try { updateGame(); drawGame(); } catch (e) {}
            requestAnimationFrame(gameLoop);
        }

        // --- ゲームフロー制御 ---
        function initGame() {
            try {
                score = 0;
                timeLeft = 60;
                feverTimeLeft = 0;
                isMazumeTriggered = false;
                currentMaxFishes = normalMaxFishes;
                lastTime = Date.now();
                if(scoreText) scoreText.innerText = `SCORE: ${score}`;
                if(timeText) {
                    timeText.innerText = `TIME: ${timeLeft}`;
                    timeText.className = "font-bold text-sm text-white tracking-wider";
                }
                if(timeIcon) timeIcon.className = "text-xl text-cyan-400";
                hook.state = 'idle';
                hook.caughtFish = null;
                boat.x = CANVAS_WIDTH / 2;
                boat.targetX = CANVAS_WIDTH / 2;

                fishes = [];
                for (let i = 0; i < currentMaxFishes; i++) fishes.push(new Fish());
                particles = [];
                
                if(tapHint) tapHint.style.opacity = '1';
                if(feverOverlay) feverOverlay.classList.add('hidden');
                if(mazumeOverlay) mazumeOverlay.classList.add('hidden');
                if(newRecordMsg) newRecordMsg.classList.add('hidden');

                bgmStep = 0;
            } catch (err) {}
        }

        function startGame() {
            try {
                initAudio();
                if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume().catch(e => {});
            } catch (e) {}

            try {
                playSound('click');
                initGame();
                state = 'playing';
                if(startScreen) startScreen.classList.add('hidden');
                if(document.getElementById('startBtn')) document.getElementById('startBtn').style.display = 'none';
                if(gameOverScreen) gameOverScreen.classList.add('hidden');

                stopBGM();
                playBGMStep();

                if (timerInterval) clearInterval(timerInterval);
                timerInterval = setInterval(() => {
                    timeLeft--;
                    if(timeText) timeText.innerText = `TIME: ${timeLeft}`;

                    if (timeLeft <= 5 && timeLeft > 0) playSound('click');

                    if (timeLeft <= 0) endGame();
                }, 1000);
            } catch (err) {
                state = 'playing';
                if(startScreen) startScreen.classList.add('hidden');
                if(document.getElementById('startBtn')) document.getElementById('startBtn').style.display = 'none';
                if(gameOverScreen) gameOverScreen.classList.add('hidden');
            }
        }

        function endGame() {
            state = 'gameover';
            clearInterval(timerInterval);
            stopBGM(); 
            playSound('gameover');

            let isNewRecord = false;
            if (score > highScore) {
                highScore = score;
                safeStorage.setItem('fishing_high_score', highScore);
                isNewRecord = true;
            }

            if(finalScore) finalScore.innerText = score;
            if(highScoreText) highScoreText.innerText = highScore;
            if(startHighScore) startHighScore.innerText = highScore;

            if (isNewRecord && newRecordMsg) newRecordMsg.classList.remove('hidden');
            else if (newRecordMsg) newRecordMsg.classList.add('hidden');

            if(gameOverScreen) gameOverScreen.classList.remove('hidden');
        }

        function bindSafeButton(buttonId, actionFn) {
            const btn = document.getElementById(buttonId);
            if (!btn) return;
            let isTriggered = false;
            const safeAction = (e) => {
                try { e.preventDefault(); } catch(err) {}
                if (isTriggered) return;
                isTriggered = true;
                setTimeout(() => { isTriggered = false; }, 800); 
                try { actionFn(); } catch (err) {}
            };
            btn.addEventListener('click', safeAction);
            btn.addEventListener('touchstart', safeAction, { passive: false });
        }

        function bootGame() {
            if (window.gameBooted) return; 
            window.gameBooted = true;
            setupCanvas();
            setupDOM();
            gameLoop();
        }

        function setupCanvas() {
            canvas = document.getElementById('gameCanvas');
            if(canvas) {
                ctx = canvas.getContext('2d', { alpha: false });
                let w = window.innerWidth;
                let h = window.innerHeight;
                if (!w || w < 100) w = 400;
                if (!h || h < 100) h = 640;
                CANVAS_WIDTH = w;
                CANVAS_HEIGHT = h;
                canvas.width = CANVAS_WIDTH;
                canvas.height = CANVAS_HEIGHT;
                if (boat) {
                    boat.x = CANVAS_WIDTH / 2;
                    boat.targetX = CANVAS_WIDTH / 2;
                }
            }
            fishes = [];
            for (let i = 0; i < 8; i++) fishes.push(new Fish());
            state = 'start';
        }

        window.addEventListener('resize', setupCanvas);

        function setupDOM() {
            scoreText = document.getElementById('scoreText');
            timeText = document.getElementById('timeText');
            timeIcon = document.getElementById('timeIcon');
            startScreen = document.getElementById('startScreen');
            gameOverScreen = document.getElementById('gameOverScreen');
            tapHint = document.getElementById('tapHint');
            finalScore = document.getElementById('finalScore');
            highScoreText = document.getElementById('highScoreText');
            startHighScore = document.getElementById('startHighScore');
            newRecordMsg = document.getElementById('newRecordMsg');
            feverOverlay = document.getElementById('feverOverlay');
            feverBar = document.getElementById('feverBar');
            mazumeOverlay = document.getElementById('mazumeOverlay');
            soundIcon = document.getElementById('soundIcon');
            soundBtn = document.getElementById('soundBtn');

            if(startHighScore) startHighScore.innerText = highScore;
            if(highScoreText) highScoreText.innerText = highScore;

            bindSafeButton('startBtn', startGame);
            bindSafeButton('retryBtn', startGame);
            bindSafeButton('backToTitleBtn', () => {
                playSound('click');
                state = 'start';
                if(startScreen) startScreen.classList.remove('hidden');
                if(document.getElementById('startBtn')) document.getElementById('startBtn').style.display = 'flex';
                if(gameOverScreen) gameOverScreen.classList.add('hidden');
            });

            if(soundBtn && soundIcon) {
                soundBtn.addEventListener('click', () => {
                    soundEnabled = !soundEnabled;
                    if (soundEnabled) {
                        soundIcon.className = "fas fa-volume-up text-sm";
                        initAudio();
                        if (state === 'playing' && !bgmTimeoutId) playBGMStep();
                    } else {
                        soundIcon.className = "fas fa-volume-mute text-red-500 text-sm";
                        stopBGM();
                    }
                    playSound('click');
                });
            }

            if(canvas) {
                canvas.addEventListener('mousedown', (e) => handleTap(e.clientX, e.clientY));
                canvas.addEventListener('touchstart', (e) => {
                    if (e.touches.length > 0) handleTap(e.touches[0].clientX, e.touches[0].clientY);
                }, { passive: true });
            }
        }

        if (document.readyState === 'complete' || document.readyState === 'interactive') setTimeout(bootGame, 50);
        else {
            window.addEventListener('DOMContentLoaded', () => setTimeout(bootGame, 50));
            window.addEventListener('load', () => setTimeout(bootGame, 50));
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

if __name__ == '__main__':
    # Renderなどのクラウド環境に対応できるように設定
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

```
