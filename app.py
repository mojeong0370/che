import streamlit as st
import chess
import chess.svg
import random

# 페이지 기본 설정
st.set_page_config(
    page_title="특수 능력 체스 게임",
    page_icon="♟️",
    layout="wide"
)

# --- 커스텀 CSS (체스판 버튼 스타일링) ---
st.markdown("""
<style>
    div[data-testid="stColumn"] > div > div > div > button {
        width: 100% !important;
        height: 65px !important;
        font-size: 26px !important;
        padding: 0px !important;
        margin: 0px !important;
        border-radius: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 세션 상태 초기화 ---
def init_game():
    st.session_state.board = chess.Board()
    st.session_state.selected_square = None
    
    # 실드 상태
    st.session_state.shields = {
        chess.WHITE: {"king": True, "queen": True},
        chess.BLACK: {"king": True, "queen": True}
    }
    
    # 룩 특수능력 부여 (a1, h1 / a8, h8 중 랜덤)
    st.session_state.rook_ability = {
        chess.WHITE: {"target_sq": random.choice([chess.A1, chess.H1]), "used": False},
        chess.BLACK: {"target_sq": random.choice([chess.A8, chess.H8]), "used": False}
    }

if "board" not in st.session_state:
    init_game()

board = st.session_state.board
current_turn = board.turn

# --- 이동 가능 경로 계산 함수 ---
def get_legal_moves_for_square(sq):
    legal_destinations = set()
    
    # 1. 일반 규칙상 가능한 이동
    for move in board.legal_moves:
        if move.from_square == sq:
            legal_destinations.add(move.to_square)
            
    # 2. 비숍 특수 능력 (아군 통과 가능)
    piece = board.piece_at(sq)
    if piece and piece.piece_type == chess.BISHOP and piece.color == current_turn:
        for dest in chess.SQUARES:
            if is_valid_bishop_jump(sq, dest):
                legal_destinations.add(dest)
                
    # 3. 룩 특수 능력 (관통 레이저)
    rook_info = st.session_state.rook_ability[current_turn]
    if piece and piece.piece_type == chess.ROOK and sq == rook_info["target_sq"] and not rook_info["used"]:
        for dest in chess.SQUARES:
            if is_rook_laser_move(sq, dest) and dest != sq:
                legal_destinations.add(dest)
                
    return legal_destinations

# --- Helper 함수들 ---
def is_rook_laser_move(from_sq, to_sq):
    f_file, f_rank = chess.square_file(from_sq), chess.square_rank(from_sq)
    t_file, t_rank = chess.square_file(to_sq), chess.square_rank(to_sq)
    return (f_file == t_file and f_rank != t_rank) or (f_rank == t_rank and f_file != t_file)

def execute_rook_laser(from_sq, to_sq):
    f_file, f_rank = chess.square_file(from_sq), chess.square_rank(from_sq)
    t_file, t_rank = chess.square_file(to_sq), chess.square_rank(to_sq)
    
    step_file = 0 if f_file == t_file else (1 if t_file > f_file else -1)
    step_rank = 0 if f_rank == t_rank else (1 if t_rank > f_rank else -1)
    
    curr_f, curr_r = f_file + step_file, f_rank + step_rank
    rook_piece = board.piece_at(from_sq)
    
    while True:
        sq = chess.square(curr_f, curr_r)
        board.remove_piece_at(sq)
        if curr_f == t_file and curr_r == t_rank:
            break
        curr_f += step_file
        curr_r += step_rank
        
    board.remove_piece_at(from_sq)
    board.set_piece_at(to_sq, rook_piece)
    
    st.session_state.rook_ability[current_turn]["used"] = True
    board.turn = not current_turn

def execute_pawn_swap(pawn_sq):
    my_targets = []
    target_types = [chess.BISHOP, chess.KNIGHT, chess.KING, chess.QUEEN, chess.ROOK]
    
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if p and p.color == current_turn and p.piece_type in target_types:
            my_targets.append(sq)
            
    if my_targets:
        swap_sq = random.choice(my_targets)
        pawn_p = board.piece_at(pawn_sq)
        target_p = board.piece_at(swap_sq)
        
        board.set_piece_at(pawn_sq, target_p)
        board.set_piece_at(swap_sq, pawn_p)
        
        board.turn = not current_turn
        st.session_state.selected_square = None
        st.rerun()

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

def process_move(from_sq, to_sq):
    attacker = board.piece_at(from_sq)
    target = board.piece_at(to_sq)
    
    # 룩 특수 능력
    rook_info = st.session_state.rook_ability[current_turn]
    if attacker and attacker.piece_type == chess.ROOK and from_sq == rook_info["target_sq"] and not rook_info["used"]:
        if is_rook_laser_move(from_sq, to_sq):
            execute_rook_laser(from_sq, to_sq)
            st.session_state.selected_square = None
            st.rerun()
            return

    # 비숍 특수 능력
    is_bishop_jump = False
    if attacker and attacker.piece_type == chess.BISHOP:
        if is_valid_bishop_jump(from_sq, to_sq):
            is_bishop_jump = True

    move = chess.Move(from_sq, to_sq, promotion=chess.QUEEN)
    
    if move in board.legal_moves or is_bishop_jump:
        # 실드 검사
        if target and target.color != current_turn:
            enemy_color = target.color
            if target.piece_type == chess.KING and st.session_state.shields[enemy_color]["king"]:
                st.session_state.shields[enemy_color]["king"] = False
                st.toast("🛡️ 상대 킹의 실드가 공격을 흡수했습니다!")
                board.turn = not current_turn
                st.session_state.selected_square = None
                st.rerun()
                return
            elif target.piece_type == chess.QUEEN and st.session_state.shields[enemy_color]["queen"]:
                st.session_state.shields[enemy_color]["queen"] = False
                st.toast("🛡️ 상대 퀸의 실드가 공격을 흡수했습니다!")
                board.turn = not current_turn
                st.session_state.selected_square = None
                st.rerun()
                return

        # 나이트 스플래시 검사
        knight_splash = False
        if attacker and attacker.piece_type == chess.KNIGHT and target:
            if target.piece_type in [chess.PAWN, chess.BISHOP]:
                knight_splash = True

        if is_bishop_jump:
            board.remove_piece_at(from_sq)
            board.set_piece_at(to_sq, attacker)
            board.turn = not current_turn
        else:
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
            st.toast("💥 나이트의 스플래시 폭발! 주변 기물이 제거되었습니다.")

        st.session_state.selected_square = None
        st.rerun()

def handle_click(sq):
    selected = st.session_state.selected_square
    if selected is not None:
        if selected == sq:
            st.session_state.selected_square = None
        else:
            legal_moves = get_legal_moves_for_square(selected)
            if sq in legal_moves:
                process_move(selected, sq)
            else:
                p = board.piece_at(sq)
                if p and p.color == current_turn:
                    st.session_state.selected_square = sq
                else:
                    st.session_state.selected_square = None
    else:
        p = board.piece_at(sq)
        if p and p.color == current_turn:
            st.session_state.selected_square = sq
    st.rerun()

# --- UI 화면 배치 ---
st.title("⚡ 특수 능력 체스 게임")

# 상단 턴 안내 표시
turn_str = "⚪ 백(White)" if current_turn == chess.WHITE else "⚫ 흑(Black)"
st.markdown(f"### 현재 차례: **{turn_str}**")

col_board, col_info = st.columns([2.2, 1])

# [메인 인터페이스]: 통합 체스 보드
with col_board:
    selected = st.session_state.selected_square
    legal_destinations = get_legal_moves_for_square(selected) if selected is not None else set()

    # 8x8 대국판 버튼 구성
    for rank in range(7, -1, -1):
        cols = st.columns(8)
        for file in range(8):
            sq = chess.square(file, rank)
            p = board.piece_at(sq)
            
            p_symbol = p.unicode_symbol() if p else ""
            
            # 버튼 라벨 및 힌트 아이콘
            if sq in legal_destinations:
                # 이동 가능한 위치 표시 (점 및 강조)
                btn_label = f"🟢 {p_symbol}" if p else "🟢"
            else:
                btn_label = p_symbol if p else " "
                
            # 선택된 칸 표시
            if selected == sq:
                btn_label = f"🟡 {p_symbol}"

            if cols[file].button(btn_label, key=f"board_btn_{sq}"):
                handle_click(sq)

# [우측 컨트롤 패널]: 능력 스킬 & 정보
with col_info:
    st.subheader("🔮 특수 스킬")
    
    if selected is not None:
        p = board.piece_at(selected)
        sq_name = chess.square_name(selected).upper()
        st.info(f"선택된 기물: **{p.symbol().upper()}** ({sq_name})")
        
        # 폰 위치 교환 스킬
        if p and p.piece_type == chess.PAWN:
            if st.button("🌀 [폰 스킬] 랜덤 위치 교환", use_container_width=True):
                execute_pawn_swap(selected)
                
        # 룩 관통 레이저 스킬 안내
        rook_info = st.session_state.rook_ability[current_turn]
        if p and p.piece_type == chess.ROOK and selected == rook_info["target_sq"]:
            if not rook_info["used"]:
                st.success("⚡ [특수 룩 선택됨] 초록색(🟢)으로 표시된 모든 칸을 다 관통하여 파괴합니다!")
            else:
                st.caption("❌ 특수 능력을 이미 사용한 룩입니다.")
    else:
        st.write("체스판에서 기물을 누르면 이동할 수 있는 칸(🟢)이 표시됩니다.")

    st.markdown("---")
    st.markdown("### 🛡️ 실드 상태")
    st.write(f"- 백 👑 킹 실드: {'✅' if st.session_state.shields[chess.WHITE]['king'] else '❌'}")
    st.write(f"- 백 ♕ 퀸 실드: {'✅' if st.session_state.shields[chess.WHITE]['queen'] else '❌'}")
    st.write(f"- 흑 👑 킹 실드: {'✅' if st.session_state.shields[chess.BLACK]['king'] else '❌'}")
    st.write(f"- 흑 ♕ 퀸 실드: {'✅' if st.session_state.shields[chess.BLACK]['queen'] else '❌'}")

    st.markdown("---")
    if st.button("🔄 게임 초기화", use_container_width=True):
        init_game()
        st.rerun()
