import streamlit as st
import chess
import random

# 페이지 설정
st.set_page_config(
    page_title="특수 능력 체스 게임",
    page_icon="♟️",
    layout="wide"
)

# --- 체스판 격자 CSS (버튼 클릭 이동용) ---
st.markdown("""
<style>
    .chess-grid {
        display: grid;
        grid-template-columns: repeat(8, 55px);
        grid-template-rows: repeat(8, 55px);
        gap: 0px;
        width: 440px;
        margin: 0 auto;
        border: 3px solid #333;
    }
    div.stButton > button {
        width: 55px !important;
        height: 55px !important;
        font-size: 26px !important;
        padding: 0px !important;
        margin: 0px !important;
        border-radius: 0px !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        line-height: 55px !important;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
def init_game():
    st.session_state.board = chess.Board()
    st.session_state.selected_square = None
    st.session_state.shields = {
        chess.WHITE: {"king": True, "queen": True},
        chess.BLACK: {"king": True, "queen": True}
    }

if "board" not in st.session_state:
    init_game()

board = st.session_state.board
current_turn = board.turn

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
    return legal_destinations

# 실제 기물 이동 함수
def make_move(from_sq, to_sq):
    target = board.piece_at(to_sq)

    # 실드 검사
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

    # 일반 이동 및 프로모션
    move = chess.Move(int(from_sq), int(to_sq), promotion=chess.QUEEN)
    if move in board.legal_moves:
        board.push(move)
        st.session_state.selected_square = None
    else:
        # 혹시 모를 승진 등의 다른 기물 대응
        for legal in board.legal_moves:
            if legal.from_square == from_sq and legal.to_square == to_sq:
                board.push(legal)
                st.session_state.selected_square = None
                break

# 칸 클릭 처리
def handle_click(sq):
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

turn_text = "⚪ 백(White) 차례" if current_turn == chess.WHITE else "⚫ 흑(Black) 차례"
st.subheader(f"현재 순서: {turn_text}")

col_board, col_info = st.columns([1.2, 1])

with col_board:
    selected = st.session_state.selected_square
    legal_moves = get_legal_destinations(selected)

    # 8x8 체스판 그리드 생성
    for rank in range(7, -1, -1):
        cols = st.columns(8)
        for file in range(8):
            sq = chess.square(file, rank)
            p = board.piece_at(sq)
            
            p_str = p.unicode_symbol() if p else ""
            
            # 체스판 배경 색상 지정
            if sq == selected:
                bg = "🟡"
            elif sq in legal_moves:
                bg = "🟢"
            else:
                bg = ""

            btn_label = f"{bg}{p_str}" if bg else (p_str if p_str else " ")

            if cols[file].button(btn_label, key=f"sq_{sq}"):
                handle_click(sq)
                st.rerun()

with col_info:
    st.markdown("### 🔮 액티브 스킬 & 선택 정보")
    
    selected = st.session_state.selected_square
    if selected is not None:
        p = board.piece_at(selected)
        if p:
            sq_name = chess.square_name(selected).upper()
            st.info(f"선택한 기물: **{p.unicode_symbol()} ({sq_name})**")
            
            if p.piece_type == chess.PAWN and p.color == current_turn:
                if st.button("🌀 폰 스킬: 아군 위치 교환", use_container_width=True):
                    targets = [s for s in chess.SQUARES if board.piece_at(s) and board.piece_at(s).color == current_turn and s != selected]
                    if targets:
                        target_sq = random.choice(targets)
                        p1 = board.piece_at(selected)
                        p2 = board.piece_at(target_sq)
                        board.set_piece_at(selected, p2)
                        board.set_piece_at(target_sq, p1)
                        board.turn = not current_turn
                        st.session_state.selected_square = None
                        st.toast("🌀 위치가 교환되었습니다!")
                        st.rerun()
    else:
        st.write("체스판에서 이동하고 싶은 **내 기물**을 마우스로 클릭해 주세요.")

    st.markdown("---")
    st.write("🛡️ **실드 현황**")
    st.write(f"- 백 킹/퀸: {'✅' if st
