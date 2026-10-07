import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="특수 능력 체스 게임", page_icon="♟️", layout="wide")

html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #0e1117;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }
        h2 { margin-bottom: 10px; color: #f0f2f6; }
        #status {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #ffbd45;
        }
        .main-container {
            display: flex;
            gap: 30px;
            align-items: flex-start;
        }
        .board-container {
            display: grid;
            grid-template-columns: repeat(8, 65px);
            grid-template-rows: repeat(8, 65px);
            border: 4px solid #444;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5);
            user-select: none;
        }
        .square {
            width: 65px;
            height: 65px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 45px;
            cursor: pointer;
            position: relative;
        }
        .white-sq { background-color: #eeeed2; color: #000; }
        .black-sq { background-color: #769656; color: #000; }
        .selected { background-color: #f6f669 !important; }
        .highlight {
            position: relative;
        }
        .highlight::after {
            content: '';
            position: absolute;
            width: 22px;
            height: 22px;
            background-color: rgba(20, 85, 30, 0.5);
            border-radius: 50%;
        }
        .info-panel {
            width: 280px;
            background: #262730;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        .btn {
            width: 100%;
            padding: 12px;
            margin-top: 15px;
            background-color: #ff4b4b;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        .btn:hover { background-color: #ff3333; }
        .skill-btn {
            background-color: #0068c9;
            margin-top: 10px;
        }
        .skill-btn:hover { background-color: #0051a3; }
        .skill-btn:disabled {
            background-color: #555555;
            cursor: not-allowed;
        }
    </style>
</head>
<body>

    <h2>♟️ 특수 능력 체스 게임</h2>
    <div id="status">⚪ 백(White) 차례입니다.</div>

    <div class="main-container">
        <div id="board" class="board-container"></div>

        <div class="info-panel">
            <h3>🔮 액티브 스킬 현황</h3>
            <div id="skill-info">기물을 클릭하면 사용할 수 있는 특수 스킬이 표시됩니다.</div>
            <button id="pawn-skill-btn" class="btn skill-btn" style="display:none;" onclick="usePawnSkill()">🌀 폰: 위치 랜덤 교환 (1회용)</button>
            
            <div style="margin-top:10px; font-size: 14px;">
                - 백(White) 폰 스킬 남은 횟수: <span id="w-skill-count">1 / 1</span><br>
                - 흑(Black) 폰 스킬 남은 횟수: <span id="b-skill-count">1 / 1</span>
            </div>

            <hr style="border: 0.5px solid #444; margin: 20px 0;">

            <h3>🛡️ 실드 현황</h3>
            <div>- 백(White) 킹/퀸: <span id="w-shield">✅ / ✅</span></div>
            <div>- 흑(Black) 킹/퀸: <span id="b-shield">✅ / ✅</span></div>

            <button class="btn" onclick="initGame()">🔄 게임 초기화</button>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>
    <script>
        var game = new Chess();
        var selectedSquare = null;
        var shields = {
            'w': { king: true, queen: true },
            'b': { king: true, queen: true }
        };
        
        // 폰 스킬 잔여 횟수 (각 팀당 1회)
        var pawnSkillCount = {
            'w': 1,
            'b': 1
        };

        var PIECES = {
            'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
            'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔'
        };

        function renderBoard() {
            var boardEl = document.getElementById('board');
            boardEl.innerHTML = '';

            var legalMoves = selectedSquare ? game.moves({ square: selectedSquare, verbose: true }) : [];
            var legalDestinations = legalMoves.map(m => m.to);

            for (var rank = 7; rank >= 0; rank--) {
                for (var file = 0; file < 8; file++) {
                    var squareName = String.fromCharCode(97 + file) + (rank + 1);
                    var sqEl = document.createElement('div');
                    
                    var isWhiteSq = (rank + file) % 2 !== 0;
                    sqEl.className = 'square ' + (isWhiteSq ? 'white-sq' : '
