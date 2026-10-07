import streamlit as st
import chess
import chess.svg
import random

# 페이지 설정
st.set_page_config(
    page_title="특수 능력 체스 게임",
    page_icon="♟️",
    layout="wide"
)

# 세션 상태 초기화
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
    st.session_state.selected_square = None
    st.session_state.shields = {
        chess.WHITE: {"king": True, "queen": True},
        chess.BLACK: {"king": True, "queen": True}
    }
    st.session_state.rook_ability = {
        chess.WHITE: {"target_sq": random.choice([chess.A1, chess.H1]), "used": False},
        chess.BLACK: {"target_sq": random.choice([chess.A8, chess.H8]), "used": False}
    }

board = st.session_state.board
current_turn = board.turn

def reset_game():
    st.session_state.board = chess.Board()
    st.session_state.selected_square = None
    st.session_state.shields = {
        chess.WHITE: {"king": True, "queen": True},
        chess.BLACK: {"king": True, "queen": True}
    }
    st.session_state.rook_ability = {
        chess.WHITE: {"target_sq": random.choice([chess.A1, chess.H1]), "used": False},
        chess.BLACK: {"target_sq": random.choice([chess.A8, chess.H8]), "used": False}
    }

# --- 로직 함수들 ---
def get_legal_destinations(sq):
    legal_destinations = set()
    if sq is None:
        return legal_destinations
    p = board.piece_at(sq)
    if not p or p.color != current_turn:
        return legal_destinations

    for move in board.legal_moves:
        if move.from_square == sq:
            legal_destinations.add(move.to_square)
    return legal_destinations

def make_move(from_sq, to_sq):
    attacker = board.piece_at(from_sq)
    target = board.piece_at(to_sq)

    # 실드 처리
    if target and target.color != current_turn:
        enemy_color = target.color
        if target.piece_type == chess.KING and st.session_state.shields[enemy_color]["king"]:
            st.session_state.shields[enemy_color]["king"] = False
            st.toast("🛡️ 상대 킹의 실드가 공격을 흡수했습니다!")
            board.turn = not current_turn
            st.session_state.selected_square = None
            return
        elif target.piece_type == chess.QUEEN and st.session_state.shields[enemy_color]["queen"]:
            st.session_state.shields[enemy_color]["queen"] = False
            st.toast("🛡️ 상대 퀸의 실드가 공격을 흡수했습니다!")
            board.turn = not current_turn
            st.session_state.selected_square = None
            return

    move = chess.Move(from_sq, to_sq, promotion=chess.QUEEN)
    if move in board.legal_moves:
        board.push(move)
        st.session_state.selected_square = None

# --- 메인 화면 ---
st.title("♟️ 특수 능력 체스 게임")

turn_text = "⚪ 백(White) 차례" if current_turn == chess.WHITE else "⚫ 흑(Black) 차례"
st.subheader(f"현재 순서: {turn_text}")

col_left, col_right = st.columns([1.5, 1])

with col_left:
    # 체스판 SVG 시각화
    selected = st.session_state.selected_square
    legal_moves = get_legal_destinations(selected)
