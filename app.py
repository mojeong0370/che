import streamlit as st
import chess
import random

# 페이지 기본 설정
st.set_page_config(
    page_title="특수 능력 체스 게임",
    page_icon="♟️",
    layout="wide"
)

# --- 체스판 스타일 CSS (격자 모양 고정) ---
st.markdown("""
<style>
    /* 체스판 버튼을 정사각형 격자 형태로 고정 */
    div[data-testid="column"] {
        padding: 1px !important;
    }
    div[data-testid="column"] > div > div > div > button {
        width: 100% !important;
        height: 60px !important;
        font-size: 24px !important;
        padding: 0px !important;
        margin: 0px !important;
        border-radius: 4px !important;
        border: 1px solid #ccc !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 세션 상태 초기화 ---
def init_game():
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

if "board" not in st.session_state:
    init_game()

board = st.session_state.board
current_turn = board.turn

# --- 비숍 점프 계산 ---
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
        if p and p.color != current_turn: # 상대 기물이 막고 있으면 불가
            return False
        curr_f += step_f
        curr_r += step_r
        
    dest_p = board.piece_at(to_sq)
    if dest_p and dest_p.color == current_turn: # 도착지에 아군이 있으면 불가
        return False
    return True

# --- 룩 관통 이동 계산 ---
def is_rook_laser_move(from_sq, to_sq):
    f_file, f_rank = chess.square_file(from_sq), chess.square_rank(from_sq)
    t_file, t_rank = chess.square_file(to_sq), chess.square_rank(to_sq)
    return (f_file == t_file and f_rank != t_rank) or (f_rank == t_rank and f_file != t_file)

# --- 이동 가능한 칸 계산 ---
def get_legal_moves(sq):
    legal_destinations = set()
    if sq is None:
        return legal_destinations
        
    p = board.piece_at(sq)
    if not p or p.color != current_turn:
        return legal_destinations

    # 1. 일반 규칙 이동
    for move in board.legal_moves:
        if move.from_square == sq:
            legal_destinations.add(move.to_square)

    # 2. 비숍 특수 능력 (아군 점프)
    if p.piece_type == chess.BISHOP:
        for dest in chess.SQUARES:
            if is_valid_bishop_jump(sq, dest):
                legal_destinations.add(dest)

    # 3. 룩 관통 레이저
    rook_info = st.session_state.rook_ability[current_turn]
    if p.piece_type == chess.ROOK and sq == rook_info["target_sq"] and not rook_info["used"]:
        for dest in chess.SQUARES:
            if is_rook_laser_move(sq, dest) and dest != sq:
                legal_destinations.add(dest)

    return legal_destinations

# --- 기물 이동 처리 ---
def make_move(from_sq, to_sq):
    attacker = board.piece_at(from_sq)
    target = board.piece_at(to_sq)
    
    # 1. 룩 관통 레이저 실행
    rook_info = st.session_state.rook_ability[current_turn]
    if attacker and attacker.piece_type == chess.ROOK and from_sq == rook_info["target_sq"] and not rook_info["used"]:
        if is_rook_laser_move(from_sq, to_sq):
            f_f, f_r = chess.square_file(from_sq), chess.square_rank(from_sq)
            t_f, t_r = chess.square_file(to_sq), chess.square_rank(to_sq)
            step_f = 0 if f_f == t_f else (1 if t_f > f_f else -1)
            step_r = 0 if f_r == t_r else (1 if t_r > f_r else -1)
            
            curr_f, curr_r = f_f + step_f, f_r + step_r
            while True:
                sq = chess.square(curr_f, curr_r)
                board.remove_piece_at(sq)
                if curr_f == t_f and curr_r == t_r:
                    break
                curr_f += step_f
                curr_r += step_r
                
            board.remove_piece_at(from_sq)
            board.set_piece_at(to_sq, attacker)
            st.session_state.rook_ability[current_turn]["used"] = True
            board.turn = not current_turn
            st.session_state.selected_square = None
            return

    # 2. 실드 검사
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

    # 3. 비숍 점프 이동 실행
    if attacker and attacker.piece_type == chess.BISHOP and is_valid_bishop_jump(from_sq, to_sq):
        board.remove_piece_at(from_sq)
        board.set_piece_at(to_sq, attacker)
        board.turn = not current_turn
        st.session_state.selected_square = None
        return

    # 4. 일반 이동 (프로모션 퀸 자동 처리)
    move = chess.Move(from_sq, to_sq, promotion=chess.QUEEN)
    if move in board.legal_moves:
        # 나이트 스플래시 판정
        knight_splash = False
        if attacker and attacker.piece_type == chess.KNIGHT and target:
            if target.piece_type in [chess.PAWN, chess.BISHOP]:
                knight_splash = True

        board.push(move)

        if knight
