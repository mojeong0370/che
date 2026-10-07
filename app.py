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
    
    # 실드 상태
    st.session_state.shields = {
        chess.WHITE: {"king": True, "queen": True},
        chess.BLACK: {"king": True, "queen": True}
    }
    
    # 룩 특수능력 부여
    st.session_state.rook_ability = {
        chess.WHITE: {"target_sq": random.choice([chess.A1, chess.H1]), "used": False},
        chess.BLACK: {"target_sq": random.choice([chess.A8, chess.H8]), "used": False}
    }

if "board" not in st.session_state:
    init_game()

board = st.session_state.board
current_turn = board.turn

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
    
    rook_info = st.session_state.rook_ability[current_turn]
    if attacker and attacker.piece_type == chess.ROOK and from_sq == rook_info["target_sq"] and not rook_info["used"]:
        if is_rook_laser_move(from_sq, to_sq):
            execute_rook_laser(from_sq, to_sq)
            st.session_state.selected_square = None
            st.rerun()
            return

    is_bishop_jump = False
    if attacker and attacker.piece_type == chess.BISHOP:
        if is_valid_bishop_jump(from_sq, to_sq):
            is_bishop_jump = True

    move = chess.Move(from_sq, to_sq, promotion=chess.QUEEN)
    
    if move in board.legal_moves or is_bishop_jump:
        if target and target.color != current_turn:
            enemy_color = target.color
            if target.piece_type == chess.KING and st.session_state.shields[enemy_color]["king"]:
                st.session_state.shields[enemy_color]["king"] = False
                st.toast("🛡️ 상대 킹의 실드가 공격을 막아냈습니다!")
                board.turn = not current_turn
                st.session_state.selected_square = None
                st.rerun()
                return
            elif target.piece_type == chess.QUEEN and st.session_state.shields[enemy_color]["queen"]:
                st.session_state.shields[enemy_color]["queen"] = False
                st.toast("🛡️ 상대 퀸의 실드가 공격을 막아냈습니다!")
                board.turn = not current_turn
                st.session_state.selected_square = None
                st.rerun()
                return

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
            st.toast("💥 나이트의 폭발 패시브 발동! 동서남북 기물 파괴!")

        st.session_state.selected_square = None
        st.rerun()

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

# 📢 누구 턴인지 알 수 있는 커다란 상단 안내 바
if current_turn == chess.WHITE:
    st.markdown("## ⚪ **[ 백(White)의 차례입니다 ]** (아래쪽 백색 기물 표시 칸 이용)", unsafe_allow_html=True)
else:
    st.markdown("## ⚫ **[ 흑(Black)의 차례입니다 ]** (위쪽 흑색 기물 표시 칸 이용)", unsafe_allow_html=True)

col_left, col_board, col_right = st.columns([1.2, 2, 1.2])

with col_left:
    st.subheader("🔮 스킬 컨트롤")
    sel_sq = st.session_state.selected_square
    if sel_sq is not None:
        p = board.piece_at(sel_sq)
        sq_name = chess.square_name(sel_sq).upper()
        st.info(f"현재 선택된 기물: **{p.symbol().upper()}** ({sq_name})")
        
        if p and p.piece_type == chess.PAWN:
            if st.button("🌀 [폰 스킬] 랜덤 위치 교환", use_container_width=True):
                execute_pawn_swap(sel_sq)
                
        rook_info = st.session_state.rook_ability[current_turn]
        if p and p.piece_type == chess.ROOK and sel_sq == rook_info["target_sq"]:
            if not rook_info["used"]:
                st.success("⚡ [특수 룩 선택됨] 직선 칸 클릭 시 관통 레이저!")
            else:
                st.caption("❌ 이미 능력을 사용한 룩입니다.")
    else:
        st.write("아래 버튼에서 현재 순서의 기물을 클릭하세요.")

    st.markdown("---")
    st.markdown("### 🛡️ 실드 현황")
    st.write(f"- 백 👑 킹: {'✅ 실드보유' if st.session_state.shields[chess.WHITE]['king'] else '❌ 소멸'}")
    st.write(f"- 백 ♕ 퀸: {'✅ 실드보유' if st.session_state.shields[chess.WHITE]['queen'] else '❌ 소멸'}")
    st.write(f"- 흑 👑 킹: {'✅ 실드보유' if st.session_state.shields[chess.BLACK]['king'] else '❌ 소멸'}")
    st.write(f"- 흑 ♕ 퀸: {'✅ 실드보유' if st.session_state.shields[chess.BLACK]['queen'] else '❌ 소멸'}")

with col_board:
    last_move = board.peek() if board.move_stack else None
    fill_dict = {}
    
    # 🌟 현재 차례인 팀의 모든 기물 칸에 살구색/하늘색 배경 테두리 하이라이트
    turn_color = "#ffeb3baa" if current_turn == chess.WHITE else "#90caf9aa"
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if p and p.color == current_turn:
            fill_dict[sq] = turn_color

    # 선택된 기물은 더욱 진한 노란색으로 강조
    if sel_sq is not None:
        fill_dict[sel_sq] = "#ff9800"

    board_svg = chess.svg.board(
        board=board,
        lastmove=last_move,
        fill=fill_dict,
        size=480
    )
    st.image(board_svg, use_container_width=True)

with col_right:
    st.subheader("🎮 대국 상태")
    if board.is_checkmate():
        st.error("🏆 체크메이트! 게임 종료")
    elif board.is_stalemate():
        st.warning("🤝 무승부")
    elif board.is_check():
        st.warning("⚠️ 체크!")
        
    if st.button("🔄 게임 다시 시작", use_container_width=True):
        init_game()
        st.rerun()

st.markdown("---")
st.subheader("🎯 체스판 조작 버튼 (아래 버튼을 눌러 이동하세요)")

# 8x8 버튼 인터페이스
for rank in range(7, -1, -1):
    cols = st.columns(8)
    for file in range(8):
        sq = chess.square(file, rank)
        p = board.piece_at(sq)
        p_symbol = p.unicode_symbol() if p else " "
        sq_name = chess.square_name(sq)
        
        # 버튼 스타일 강조
        btn_label = f"{p_symbol}\n({sq_name})"
        if cols[file].button(btn_label, key=f"btn_{sq}"):
            handle_click(sq)
