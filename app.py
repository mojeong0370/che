import streamlit as st
import chess
import random

# 페이지 기본 설정
st.set_page_config(
    page_title="특수 능력 체스 게임",
    page_icon="♟️",
    layout="wide"
)

# CSS 스타일 적용
st.markdown("""
<style>
    div.stButton > button {
        width: 100% !important;
        height: 52px !important;
        font-size: 22px !important;
        padding: 0px !important;
        margin: 0px !important;
        border-radius: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. 세션 상태 초기화
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

# 2. 이동 규칙 관련 함수들
def is_valid_bishop_jump(from_sq, to_sq):
    f_f, f_r = chess.square_file(from_sq), chess.square_rank(from_sq)
    t_f, t_r = chess.square_file(to_sq), chess.square_rank(to_sq)
    
    if abs(f_f - t_f) != abs(f_r - t_r) or from_sq == to_sq:
        return False
        
    step_f = 1 if t_f > f_f else -1
    step_r = 1 if t_r > f_r else -1
    
    curr_f, curr_r = f_f + step_f, f_r + step_r
    while curr_f != t_f and curr_r != t_r:
        sq = chess.square(curr_f, curr_r)
        p = board.piece_at(sq)
        if p and p.color != current_turn:
            return False
        curr_f += step_f
        curr_r += step_r
        
    dest_p = board.piece_at(to_sq)
    if dest_p and dest_p.color == current_turn:
        return False
    return True

def is_rook_laser_move(from_sq, to_sq):
    f_file, f_rank = chess.square_file(from_sq), chess.square_rank(from_sq)
    t_file, t_rank = chess.square_file(to_sq), chess.square_rank(to_sq)
    return (f_file == t_file and f_rank != t_rank) or (f_rank == t_rank and f_file != t_file)

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

    if p.piece_type == chess.BISHOP:
        for dest in chess.SQUARES:
            if is_valid_bishop_jump(sq, dest):
                legal_destinations.add(dest)

    rook_info = st.session_state.rook_ability[current_turn]
    if p.piece_type == chess.ROOK and sq == rook_info["target_sq"] and not rook_info["used"]:
        for dest in chess.SQUARES:
            if is_rook_laser_move(sq, dest) and dest != sq:
                legal_destinations.add(dest)

    return legal_destinations

# 3. 콜백 함수: 실제 이동 수행
def execute_move(from_sq, to_sq):
    attacker = board.piece_at(from_sq)
    target = board.piece_at(to_sq)

    rook_info = st.session_state.rook_ability[current_turn]
    if attacker and attacker.piece_type == chess.ROOK and from_sq == rook_info["target_sq"] and not rook_info["used"]:
        if is_rook_laser_move(from_sq, to_sq):
            f_f, f_r = chess.square_file(from_sq), chess.square_rank(from_sq)
            t_f, t_r = chess.square_file(to_sq), chess.square_rank(to_sq)
            step_f = 0 if f_f == t_f else (1 if t_f > f_f else -1)
            step_r = 0 if f_r == t_r else (1 if t_r > f_r else -1)
            
            curr_f, curr_r = f_f + step_f, f_
