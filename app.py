import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="특수 능력 체스 게임", page_icon="♟️", layout="wide")

st.title("♟️ 특수 능력 체스 게임")

# HTML + JS 드래그 앤 드롭 체스판 엔진 (외부 라이브러리 설치 필요 없음)
html_code = """
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>
    <style>
        body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; background-color: #f0f2f6; margin: 0; padding: 10px; }
        #board { width: 450px; margin-bottom: 10px; }
        .status-container { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="status-container" id="status">백(White) 차례입니다.</div>
    <div id="board"></div>

    <script>
        var board = null
        var game = new Chess()
        var $status = $('#status')

        function onDragStart (source, piece, board, orientation) {
            // 게임이 끝났거나 내 차례가 아닌 기물은 선택 안됨
            if (game.game_over()) return false
            if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
                (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
                return false
            }
        }

        function onDrop (source, target) {
            // 이동 규칙 검증
            var move = game.move({
                from: source,
                to: target,
                promotion: 'q'
            })

            // 올바르지 않은 이동일 경우 제자리로 복귀
            if (move === null) return 'snapback'

            updateStatus()
        }

        function onSnapEnd () {
            board.position(game.fen())
        }

        function updateStatus () {
            var status = ''
            var moveColor = (game.turn() === 'b') ? '흑(Black)' : '백(White)'

            if (game.in_checkmate()) {
                status = '게임 종료! ' + moveColor + '가 외통수(Checkmate)당했습니다.'
            } else if (game.in_draw()) {
                status = '게임 종료! 무승부입니다.'
            } else {
                status = moveColor + ' 차례입니다.'
                if (game.in_check()) {
                    status += ' (체크 상태!)'
                }
            }
            $status.html(status)
        }

        var config = {
            draggable: true,
            position: 'start',
            onDragStart: onDragStart,
            onDrop: onDrop,
            onSnapEnd: onSnapEnd
        }
        board = Chessboard('board', config)
        updateStatus()
    </script>
</body>
</html>
"""

components.html(html_code, height=580)
