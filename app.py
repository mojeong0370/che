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

# --- 세션 상태 초기화 ---
def init_game():
    st.session_state.board = chess.Board()
    st.session_state.selected_square = None
    
    # 실드 상태 (True: 실드 보유, False: 실드 소멸)
    st.session_state.shields = {
        chess.WHITE: {"king": True, "queen": True},
        chess.BLACK: {"king": True, "queen": True}
    }
    
    # 룩 특수능력 부여 (각 진영별 1개의 룩에 랜덤 부여 및 사용 여부)
    # a1(0), h1(7) / a8(56), h8(63)
    st.session_state.rook_ability = {
        chess.WHITE: {"target_sq": random.choice([chess.A1, chess.H1]), "used": False},
        chess.BLACK: {"target_sq": random.choice([chess.A8, chess.H8]), "used": False}
    }

if "board" not in st.session_state:
    init_game()

board = st.session_state.board
current_turn = board.turn

# --- Helper 함수들 ---
def get_piece_at(sq):
    return board.piece_at(sq)

def is_rook_laser_move(from_sq, to_sq):
    """룩의 1자 레이저 관통 이동 여부 검사"""
    f_file, f_rank = chess.square_file(from_sq), chess.square_rank(from_sq)
    t_file, t_rank = chess.square_file(to_sq), chess.square_rank(to_sq)
    
    # 가로 또는 세로 직선 이동인지 확인
    if f_file == t_file and f_rank != t_rank:
        return True
    if f_rank == t_rank and f_file != t_file:
        return True
    return False

def execute_rook_laser(from_sq, to_sq):
    """룩 레이저 스킬: 경로상의 모든 기물 제거 후 이동"""
    f_file, f_rank = chess.square_file(from_sq), chess.square_rank(from_sq)
    t_file, t_rank = chess.square_file(to_sq), chess.square_rank(to_sq)
    
    step_file = 0 if f_file == t_file else (1 if t_file > f_file else -1)
    step_rank = 0 if f_rank == t_rank else (1 if t_rank > f_rank else -1)
    
    curr_f, curr_r = f_file + step_file, f_rank + step_rank
    rook_piece = board.piece_at(from_sq)
    
    # 경로 및 목적지의 모든 기물 제거
    while True:
        sq = chess.square(curr_f, curr_r)
        board.remove_piece_at(sq)
        if curr_f == t_file and curr_r == t_rank:
            break
        curr_f += step_file
        curr_r += step_rank
        
    board.remove_piece_at(from_sq)
    board.set_piece_at(to_sq, rook_piece)
    
    # 사용 처리 및 턴 교체
    st.session_state.rook_ability[current_turn]["used"] = True
    board.turn = not current_turn

def execute_pawn_swap(pawn_sq):
    """폰 스킬: 내 비숍, 나이트, 킹, 퀸, 룩 중 무작위 1개와 위치 교환"""
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
    """비숍 아군 통과 이동 검사"""
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
        # 경로 상에 적군 기물이 있으면 통과 불가 (아군만 통과 가능)
        if p and p.color != current_turn:
            return False
        curr_f += step_f
        curr_r += step_r
        
    # 도착지 검사
    dest_p = board.piece_at(to_sq)
    if dest_p and dest_p.color == current_turn:
        return False
    return True

def process_move(from_sq, to_sq):
    """일반 및 특수 능력 이동 통합 처리"""
    attacker = board.piece_at(from_sq)
    target = board.piece_at(to_sq)
    
    # 1. [룩 스킬] 사용 확인
    rook_info = st.session_state.rook_ability[current_turn]
    if attacker and attacker.piece_type == chess.ROOK and from_sq == rook_info["target_sq"] and not rook_info["used"]:
        if is_rook_laser_move(from_sq, to_sq):
            execute_rook_laser(from_sq, to_sq)
            st.session_state.selected_square = None
            st.rerun()
            return

    # 2. [비숍 통과 스킬] 검사
    is_bishop_jump = False
    if attacker and attacker.piece_type == chess.BISHOP:
        if is_valid_bishop_jump(from_sq, to_sq):
            is_bishop_jump = True

    move = chess.Move(from_sq, to_sq, promotion=chess.QUEEN)
    
    if move in board.legal_moves or is_bishop_jump:
        # 3. [킹/퀸 실드 패시브] 공격 시 차단 검사
        if target and target.color != current_turn:
            enemy_color = target.color
            if target.piece_type == chess.KING and st.session_state.shields[enemy_color]["king"]:
                st.session_state.shields[enemy_color]["king"] = False
                st.toast("🛡️ 상대 킹의 실드가 공격을 흡수했습니다! (공격 위치 유지)")
                board.turn = not current_turn
                st.session_state.selected_square = None
                st.rerun()
                return
            elif target.piece_type == chess.QUEEN and st.session_state.shields[enemy_color]["queen"]:
                st.session_state.shields[enemy_color]["queen"] = False
                st.toast("🛡️ 상대 퀸의 실드가 공격을 흡수했습니다! (공격 위치 유지)")
                board.turn = not current_turn
                st.session_state.selected_square = None
                st.rerun()
                return

        # 4. [나이트 패시브] 폰/비숍 잡을 때 스플래시 폭발
        knight_splash = False
        if attacker and attacker.piece_type == chess.KNIGHT and target:
            if target.piece_type in [chess.PAWN, chess.BISHOP]:
                knight_splash = True

        # 이동 실행 (비숍 통과 시 수동 이동)
        if is_bishop_jump:
            board.remove_piece_at(from_sq)
            board.set_piece_at(to_sq, attacker)
            board.turn = not current_turn
        else:
            board.push(move)

        # 나이트 스플래시 처리 (동서남북 1칸, 킹/퀸/룩 제외)
        if knight_splash:
            t_f, t_r = chess.square_file(to_sq), chess.square_rank(to_sq)
            dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # 북, 남, 동, 서
            for df, dr in dirs:
                nf, nr = t_f + df, t_r + dr
                if 0 <= nf < 8 and 0 <= nr < 8:
                    adj_sq = chess.square(nf, nr)
                    adj_p = board.piece_at(adj_sq)
                    if adj_p and adj_p.piece_type not in [chess.KING, chess.QUEEN, chess.ROOK]:
                        board.remove_piece_at(adj_sq)
            st.toast("💥 나이트의 폭발 패시브 발동! 주변 기물이 파괴되었습니다.")

        st.session_state.selected_square = None
        st.rerun()

# 클릭 이벤트 핸들러
def handle_click(sq):
    if st.session_state.selected_square is not None:
        from_sq = st.session_state.selected_square
        if from_sq == sq:
            st.session_state.selected_square = None
        else:
            p = board.piece_at(sq)
            if p and p.color == current_turn:
                st.session_state.selected_square = sq
            else:
                process_move(from_sq, sq)
    else:
        p = board.piece_at(sq)
        if p and p.color == current_turn:
            st.session_state.selected_square = sq
    st.rerun()

# --- UI 레이아웃 ---
st.title("⚡ 특수 능력 체스 게임")

col_left, col_board, col_right = st.columns([1.2, 2, 1.2])

# [왼쪽 UI]: 특수 능력 상태 및 사용 버튼
with col_left:
    st.subheader("🔮 특수 스킬 컨트롤")
    
    turn_text = "⚪ 백(White)" if current_turn == chess.WHITE else "⚫ 흑(Black)"
    st.markdown(f"#### 현재 턴: **{turn_text}**")
    
    sel_sq = st.session_state.selected_square
    if sel_sq is not None:
        p = board.piece_at(sel_sq)
        sq_name = chess.square_name(sel_sq).upper()
        st.info(f"선택된 기물: **{p.symbol().upper()}** ({sq_name})")
        
        # 폰 액티브 능력 버튼
        if p and p.piece_type == chess.PAWN:
            if st.button("🌀 [폰 스킬] 랜덤 위치 교환", use_container_width=True):
                execute_pawn_swap(sel_sq)
                
        # 룩 액티브 스킬 안내
        rook_info = st.session_state.rook_ability[current_turn]
        if p and p.piece_type == chess.ROOK and sel_sq == rook_info["target_sq"]:
            if not rook_info["used"]:
                st.success("⚡ [특수 룩 선택됨] 직선상의 어떤 위치든 지정하면 관통 레이저 공격을 수행합니다!")
            else:
                st.caption("❌ 이 룩의 특수 능력은 이미 사용되었습니다.")
    else:
        st.write("보드상의 기물을 선택하면 사용할 수 있는 능력이 표시됩니다.")

    st.markdown("---")
    st.markdown("### 🛡️ 실드 현황")
    st.write(f"- 백 👑 킹 실드: {'✅ 보유' if st.session_state.shields[chess.WHITE]['king'] else '❌ 소멸'}")
    st.write(f"- 백 ♕ 퀸 실드: {'✅ 보유' if st.session_state.shields[chess.WHITE]['queen'] else '❌ 소멸'}")
    st.write(f"- 흑 👑 킹 실드: {'✅ 보유' if st.session_state.shields[chess.BLACK]['king'] else '❌ 소멸'}")
    st.write(f"- 흑 ♕ 퀸 실드: {'✅ 보유' if st.session_state.shields[chess.BLACK]['queen'] else '❌ 소멸'}")

    st.markdown("---")
    st.markdown("### ⚡ 능력 룩 위치")
    w_rook_sq = chess.square_name(st.session_state.rook_ability[chess.WHITE]["target_sq"]).upper()
    b_rook_sq = chess.square_name(st.session_state.rook_ability[chess.BLACK]["target_sq"]).upper()
    st.write(f"- ⚪ 백 능력 룩: **{w_rook_sq}** ({'사용 가능' if not st.session_state.rook_ability[chess.WHITE]['used'] else '사용 완료'})")
    st.write(f"- ⚫ 흑 능력 룩: **{b_rook_sq}** ({'사용 가능' if not st.session_state.rook_ability[chess.BLACK]['used'] else '사용 완료'})")

# [중앙 UI]: 체스판 SVG
with col_board:
    last_move = board.peek() if board.move_stack else None
    fill_dict = {}
    if sel_sq is not None:
        fill_dict[sel_sq] = "#ffeb3b88"  # 선택된 기물 강조
        
    board_svg = chess.svg.board(
        board=board,
        lastmove=last_move,
        fill=fill_dict,
        size=480
    )
    st.image(board_svg, use_container_width=True)

# [오른쪽 UI]: 상태 및 리셋
with col_right:
    st.subheader("🎮 게임 상태")
    if board.is_checkmate():
        st.error("🏆 체크메이트! 승리했습니다.")
    elif board.is_stalemate():
        st.warning("🤝 무승부 (스테일메이트)")
    elif board.is_check():
        st.warning("⚠️ 체크!")
        
    if st.button("🔄 게임 초기화", use_container_width=True):
        init_game()
        st.rerun()

st.markdown("---")
st.subheader("🎯 보드 조작 (클릭용)")

# 8x8 버튼 인터페이스
for rank in range(7, -1, -1):
    cols = st.columns(8)
    for file in range(8):
        sq = chess.square(file, rank)
        p = board.piece_at(sq)
        p_symbol = p.unicode_symbol() if p else " "
        sq_name = chess.square_name(sq)
        
        btn_label = f"{p_symbol}\n({sq_name})"
        if cols[file].button(btn_label, key=f"btn_{sq}"):
            handle_click(sq)
