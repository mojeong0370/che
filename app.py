import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="특수 능력 체스 게임", page_icon="♟️", layout="wide")

# 체스 엔진 및 UI 전체가 완벽하게 동작하는 독립 HTML/JS
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
    </style>
</head>
<body>

    <h2>♟️ 특수 능력 체스 게임</h2>
    <div id="status">⚪ 백(White) 차례입니다.</div>

    <div class="main-container">
        <div id="board" class="board-container"></div>

        <div class="info-panel">
            <h3>🔮 액티브 스킬</h3>
            <div id="skill-info">기물을 클릭하면 사용할 수 있는 특수 스킬이 표시됩니다.</div>
            <button id="pawn-skill-btn" class="btn skill-btn" style="display:none;" onclick="usePawnSkill()">🌀 폰: 위치 위치 랜덤 교환</button>

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
                    sqEl.className = 'square ' + (isWhiteSq ? 'white-sq' : 'black-sq');
                    sqEl.dataset.square = squareName;

                    if (selectedSquare === squareName) {
                        sqEl.classList.add('selected');
                    } else if (legalDestinations.includes(squareName)) {
                        sqEl.classList.add('highlight');
                    }

                    var piece = game.get(squareName);
                    if (piece) {
                        var pieceSymbol = (piece.color === 'w') ? piece.type.toUpperCase() : piece.type;
                        sqEl.innerText = PIECES[pieceSymbol] || '';
                    }

                    sqEl.onclick = (function(sq) {
                        return function() { onSquareClick(sq); };
                    })(squareName);

                    boardEl.appendChild(sqEl);
                }
            }

            updateUI();
        }

        function onSquareClick(sq) {
            var turn = game.turn();
            var piece = game.get(sq);

            if (selectedSquare === null) {
                // 내 차례의 기물을 클릭했을 때 선택
                if (piece && piece.color === turn) {
                    selectedSquare = sq;
                }
            } else {
                if (selectedSquare === sq) {
                    selectedSquare = null; // 같은 칸 다시 누르면 취소
                } else {
                    // 이동 시도
                    var move = game.move({
                        from: selectedSquare,
                        to: sq,
                        promotion: 'q'
                    });

                    if (move !== null) {
                        // 실드 능력 체크
                        if (move.captured) {
                            var enemyColor = (turn === 'w') ? 'b' : 'w';
                            if (move.captured === 'k' && shields[enemyColor].king) {
                                shields[enemyColor].king = false;
                                game.undo(); // 이동 취소 및 차례 넘김
                                switchTurn();
                            } else if (move.captured === 'q' && shields[enemyColor].queen) {
                                shields[enemyColor].queen = false;
                                game.undo(); // 이동 취소 및 차례 넘김
                                switchTurn();
                            }
                        }
                        selectedSquare = null;
                    } else {
                        // 다른 내 기물을 누르면 선택 변경
                        if (piece && piece.color === turn) {
                            selectedSquare = sq;
                        } else {
                            selectedSquare = null;
                        }
                    }
                }
            }
            renderBoard();
        }

        function switchTurn() {
            var tokens = game.fen().split(' ');
            tokens[1] = (tokens[1] === 'w') ? 'b' : 'w';
            game.load(tokens.join(' '));
        }

        function usePawnSkill() {
            if (!selectedSquare) return;
            var piece = game.get(selectedSquare);
            if (!piece || piece.type !== 'p') return;

            var turn = game.turn();
            var boardState = game.board();
            var allies = [];

            for (var r = 0; r < 8; r++) {
                for (var f = 0; f < 8; f++) {
                    var p = boardState[r][f];
                    var sqName = String.fromCharCode(97 + f) + (8 - r);
                    if (p && p.color === turn && sqName !== selectedSquare) {
                        allies.push(sqName);
                    }
                }
            }

            if (allies.length > 0) {
                var targetSq = allies[Math.floor(Math.random() * allies.length)];
                var targetPiece = game.get(targetSq);

                game.put({ type: targetPiece.type, color: targetPiece.color }, selectedSquare);
                game.put({ type: piece.type, color: piece.color }, targetSq);

                switchTurn();
                selectedSquare = null;
                renderBoard();
            }
        }

        function updateUI() {
            var turnText = (game.turn() === 'w') ? '⚪ 백(White) 차례입니다.' : '⚫ 흑(Black) 차례입니다.';
            if (game.in_checkmate()) turnText = '게임 종료! 외통수(Checkmate)';
            document.getElementById('status').innerText = turnText;

            // 실드 표기
            document.getElementById('w-shield').innerText = (shields['w'].king ? '✅' : '❌') + ' / ' + (shields['w'].queen ? '✅' : '❌');
            document.getElementById('b-shield').innerText = (shields['b'].king ? '✅' : '❌') + ' / ' + (shields['b'].queen ? '✅' : '❌');

            // 스킬 버튼 UI
            var pawnBtn = document.getElementById('pawn-skill-btn');
            var skillInfo = document.getElementById('skill-info');

            if (selectedSquare) {
                var piece = game.get(selectedSquare);
                if (piece && piece.type === 'p' && piece.color === game.turn()) {
                    skillInfo.innerText = '선택한 폰(' + selectedSquare.toUpperCase() + ')의 특수 스킬 사용 가능:';
                    pawnBtn.style.display = 'block';
                } else {
                    skillInfo.innerText = '선택한 기물: ' + selectedSquare.toUpperCase();
                    pawnBtn.style.display = 'none';
                }
            } else {
                skillInfo.innerText = '체스판에서 내 기물을 클릭하세요.';
                pawnBtn.style.display = 'none';
            }
        }

        function initGame() {
            game.reset();
            selectedSquare = null;
            shields = {
                'w': { king: true, queen: true },
                'b': { king: true, queen: true }
            };
            renderBoard();
        }

        // 게임 시작
        initGame();
    </script>
</body>
</html>
"""

components.html(html_code, height=650)
