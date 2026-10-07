import streamlit as st
import chess
from streamlit_chessboard import chessboard
import random

# 페이지 설정
st.set_page_config(page_title="특수 능력 체스 게임", page_icon="♟️", layout="wide")

# 세션 상태 초기화
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
    st.session_state.shields = {
        chess.WHITE: {"king": True, "queen": True},
        chess.BLACK: {"king": True, "queen": True}
    }

board = st.session_state.board
current_turn = board.turn

st.title("♟️ 특수 능력 체스 게임")

turn_label = "⚪ 백(White) 차례" if current_turn == chess.WHITE else "⚫ 흑(Black) 차례"
st.subheader(f"현재 순서: {turn_label}")

col1, col2 = st.columns([1.2, 1])

with col1:
    # 안정적인 HTML5 드래그 앤 드롭 체스판 컴포넌트
    move = chessboard(
        fen=board.fen(),
        key="chess_board"
    )

    # 체스판에서 기물을 움직였을 때 처리
    if move:
        from_sq = chess.parse_square(move["from"])
        to_sq = chess.parse_square(move["to"])
        
        # 이동하려는 기물과 목적지 기물 확인
        attacker = board.piece_at(from_sq)
        target = board.piece_at(to_sq)

        # 실드 능력 체크
        move_cancelled = False
        if target and target.color != current_turn:
            enemy = target.color
            if target.piece_type == chess.KING and st.session_state.shields[enemy]["king"]:
                st.session_state.shields[enemy]["king"] = False
                st.toast("🛡️ 상대 킹의 실드가 공격을 흡수했습니다!")
                board.turn = not current_turn
                move_cancelled = True
            elif target.piece_type == chess.QUEEN and st.session_state.shields[enemy]["queen"]:
                st.session_state.shields[enemy]["queen"] = False
                st.toast("🛡️ 상대 퀸의 실드가 공격을 흡수했습니다!")
                board.turn = not current_turn
                move_cancelled = True

        if not move_cancelled:
            chess_move = chess.Move(from_sq, to_sq, promotion=chess.QUEEN)
            if chess_move in board.legal_moves:
                board.push(chess_move)
                st.rerun()

with col2:
    st.markdown("### 🛡️ 게임 및 실드 현황")
    
    w_k = "✅" if st.session_state.shields[chess.WHITE]["king"] else "❌"
    w_q = "✅" if st.session_state.shields[chess.WHITE]["queen"] else "❌"
    b_k = "✅" if st.session_state.shields[chess.BLACK]["king"] else "❌"
    b_q = "✅" if st.session_state.shields[chess.BLACK]["queen"] else "❌"

    st.write(f"- **백(White)** 킹 실드: {w_k} | 퀸 실드: {w_q}")
    st.write(f"- **흑(Black)** 킹 실드: {b_k} | 퀸 실드: {b_q}")

    st.markdown("---")
    
    if st.button("🔄 게임 초기화", use_container_width=True):
        st.session_state.board = chess.Board()
        st.session_state.shields = {
            chess.WHITE: {"king": True, "queen": True},
            chess.BLACK: {"king": True, "queen": True}
        }
        st.rerun()
