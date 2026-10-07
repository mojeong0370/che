import streamlit as st
import chess
import random

# 페이지 기본 설정
st.set_page_config(
    page_title="특수 능력 체스 게임",
    page_icon="♟️",
    layout="wide"
)

# 세션 상태 초기화
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

# 비숍 점프 이동 계산
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

# 룩 관통 직선 판별
def is_rook_laser_move(from_sq, to_sq):
    f_file, f_rank = chess.square_file(from_sq), chess.square_rank(from_sq)
    t_file, t_rank = chess.square_file(to_sq), chess.square_rank(to_sq)
    return (f_file == t_file and f_rank != t_rank) or (f_rank == t_rank and f_file != t_file)

# 이동 가능 위치 계산
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

# 실제 이동 실행
def make_move(from_sq, to_sq):
    attacker = board.piece_at(from_sq)
    target = board.piece_at(to_sq)

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

    if attacker and attacker.piece_type == chess.BISHOP and is_valid_bishop_jump(from_sq, to_sq):
        board.remove_piece_at(from_sq)
        board.set_piece_at(to_sq, attacker)
        board.turn = not current_turn
        st.session_state.selected_square = None
        return

    move = chess.Move(from_sq, to_sq, promotion=chess.QUEEN)
    if move in board.legal_moves:
        knight_splash = False
        if attacker and attacker.piece_type == chess.KNIGHT and target:
            if target.piece_type in [chess.PAWN, chess.BISHOP]:
                knight_splash = True

        board.push(move)

        if knight_splash:
            t_f, t_r = chess.square_file(to_sq), chess.square_rank(to_sq)
            dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for df, dr in dirs:
                nf, nr = t_f + df, t_r + dr
                if 0 <= nf < 8 and 0 <= nr < 8:
                    adj_sq = chess.square(nf, nr)
                    adj_p = board.piece_at(adj_sq)
                    if adj_p and adj_p.piece_type not in [chess.KING, chess.QUEEN, chess.ROOK]:
                        board.remove_piece_at(adj_sq)
            st.toast("💥 나이트 스플래시 폭발! 주변 기물이 파괴되었습니다.")

        st.session_state.selected_square = None

# 클릭 핸들러
def handle_sq_click(sq):
    selected = st.session_state.selected_square
    
    if selected is None:
        p = board.piece_at(sq)
        if p and p.color == current_turn:
            st.session_state.selected_square = sq
    else:
        if selected == sq:
            st.session_state.selected_square = None
        else:
            legal_moves = get_legal_destinations(selected)
            if sq in legal_moves:
                make_move(selected, sq)
            else:
                p = board.piece_at(sq)
                if p and p.color == current_turn:
                    st.session_state.selected_square = sq
                else:
                    st.session_state.selected_square = None

# UI 구성
st.title("♟️ 특수 능력 체스 게임")

if current_turn == chess.WHITE:
    st.subheader("⚪ 백(White) 차례")
else:
    st.subheader("⚫ 흑(Black) 차례")

col_board, col_info = st.columns([1.3, 1])

with col_board:
    selected = st.session_state.selected_square
    legal_moves = get_legal_destinations(selected)

    for rank in range(7, -1, -1):
        cols = st.columns(8)
        for file in range(8):
            sq = chess.square(file, rank)
            p = board.piece_at(sq)
            
            p_str = p.unicode_symbol() if p else ""
            
            if sq == selected:
                btn_text = "🟡 " + p_str
            elif sq in legal_moves:
                btn_text = "🟢 " + p_str if p_str else "🟢"
            else:
                btn_text = p_str if p_str else " "

            if cols[file].button(btn_text, key="sq_" + str(sq)):
                handle_sq_click(sq)
                st.rerun()

with col_info:
    st.markdown("### 🔮 액티브 스킬")
    
    selected = st.session_state.selected_square
    if selected is not None:
        p = board.piece_at(selected)
        if p:
            st.info("선택한 기물: " + p.unicode_symbol() + " (" + chess.square_name(selected).upper() + ")")
            
            if p.piece_type == chess.PAWN and p.color == current_turn:
                if st.button("🌀 폰: 랜덤 아군 기물과 위치 교환", use_container_width=True):
                    targets = [s for s in chess.SQUARES if board.piece_at(s) and board.piece_at(s).color == current_turn and s != selected]
                    if targets:
                        target_sq = random.choice(targets)
                        target_p = board.piece_at(target_sq)
                        board.set_piece_at(selected, target_p)
                        board.set_piece_at(target_sq, p)
                        board.turn = not current_turn
                        st.session_state.selected_square = None
                        st.toast("🌀 위치가 교환되었습니다!")
                        st.rerun()
    else:
        st.write("체스판에서 이동할 내 기물을 마우스로 클릭하세요.")

    st.markdown("---")
    st.markdown("### 🛡️ 실드 및 정보")
    
    w_k = "✅" if st.session_state.shields[chess.WHITE]["king"] else "❌"
    w_q = "✅" if st.session_state.shields[chess.WHITE]["queen"] else "❌"
    b_k = "✅" if st.session_state.shields[chess.BLACK]["king"] else "❌"
    b_q = "✅" if st.session_state.shields[chess.BLACK]["queen"] else "❌"

    st.write("- 백 킹/퀸 실드: " + w_k + " / " + w_q)
    st.write("- 흑 킹/퀸 실드: " + b_k + " / " + b_q)
    
    rook_w = chess.square_name(st.session_state.rook_ability[chess.WHITE]["target_sq"]).upper()
    rook_b = chess.square_name(st.session_state.rook_ability[chess.BLACK]["target_sq"]).upper()
    st.write("- 백 레이저 룩 위치: " + rook_w)
    st.write("- 흑 레이저 룩 위치: " + rook_b)

    st.markdown("---")
    if st.button("🔄 게임 초기화", use_container_width=True):
        init_game()
        st.rerun()
