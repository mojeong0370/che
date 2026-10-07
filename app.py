import streamlit as st
import chess
import random

st.set_page_config(page_title="특수 능력 체스 게임", page_icon="♟️", layout="wide")

# CSS: 체스판 격자 및 기물 스타일
st.markdown("""
<style>
    div.stButton > button {
        width: 100% !important;
        height: 55px !important;
        font-size: 28px !important;
        padding: 0px !important;
        margin: 0px !important;
        border-radius: 0px !important;
        line-height: 55px !important;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
    st.session_state.selected_sq = None
    st.session_state.shields = {
        chess.WHITE: {"king": True, "queen": True},
        chess.BLACK: {"king": True, "queen": True}
    }

board = st.session_state.board
current_turn = board.turn

def reset_game():
    st.session_state.board = chess.Board()
    st.session_state.selected_sq = None
    st.session_state.shields = {
        chess.WHITE: {"king": True, "queen": True},
        chess.BLACK: {"king": True, "queen": True}
    }

# 클릭 처리 함수
def handle_square_click(sq):
    selected = st.session_state.selected_sq
    
    # 1. 기물이 선택되지 않은 상태
    if selected is None:
        p = board.piece_at(sq)
        if p and p.color == current_turn:
            st.session_state.selected_sq = sq
    # 2. 이미 기물이 선택된 상태
    else:
        if selected == sq:
            st.session_state.selected_sq = None  # 같은 칸 클릭 시 취소
        else:
            # 이동 규칙 확인
            move = chess.Move(selected, sq, promotion=chess.QUEEN)
            
            if move in board.legal_moves:
                target = board.piece_at(sq)
                # 실드 체크
                if target and target.color != current_turn:
                    enemy = target.color
                    if target.piece_type == chess.KING and st.session_state.shields[enemy]["king"]:
                        st.session_state.shields[enemy]["king"] = False
                        board.turn = not current_turn
                        st.session_state.selected_sq = None
                        return
                    elif target.piece_type == chess.QUEEN and st.session_state.shields[enemy]["queen"]:
                        st.session_state.shields[enemy]["queen"] = False
                        board.turn = not current_turn
                        st.session_state.selected_sq = None
                        return
                
                board.push(move)
                st.session_state.selected_sq = None
            else:
                p = board.piece_at(sq)
                if p and p.color == current_turn:
                    st.session_state.selected_sq = sq
                else:
                    st.session_state.selected_sq = None

def pawn_swap_skill(sq):
    p = board.piece_at(sq)
    targets = [s for s in chess.SQUARES if board.piece_at(s) and board.piece_at(s).color == current_turn and s != sq]
    if targets:
        target_sq = random.choice(targets)
        target_p = board.piece_at(target_sq)
        board.set_piece_at(sq, target_p)
        board.set_piece_at(target_sq, p)
        board.turn = not current_turn
        st.session_state.selected_sq = None

# UI 구성
st.title("♟️ 특수 능력 체스 게임")

turn_label = "⚪ 백(White) 차례" if current_turn == chess.WHITE else "⚫ 흑(Black) 차례"
st.subheader(turn_label)

col1, col2 = st.columns([1.2, 1])

# 체스 기물 표기용 딕셔너리
UNICODE_PIECES = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
}

with col1:
    selected = st.session_state.selected_sq
    
    # 이동 가능한 칸 목록 계산
    legal_dests = set()
    if selected is not None:
        for m in board.legal_moves:
            if m.from_square == selected:
                legal_dests.add(m.to_square)

    # 8x8 체스판 출력
    for rank in range(7, -1, -1):
        cols = st.columns(8)
        for file in range(8):
            sq = chess.square(file, rank)
            p = board.piece_at(sq)
            
            symbol = UNICODE_PIECES[p.symbol()] if p else ""
            
            # 칸 색상 강조
            if sq == selected:
                btn_label = f"🟡{symbol}" if symbol else "🟡"
            elif sq in legal_dests:
                btn_label = f"🟢{symbol}" if symbol else "🟢"
            else:
                btn_label = symbol if symbol else " "

            cols[file].button(
                btn_label, 
                key=f"sq_{sq}", 
                on_click=handle_square_click, 
                args=(sq,)
            )

with col2:
    st.markdown("### 🔮 액티브 스킬")
    selected = st.session_state.selected_sq
    
    if selected is not None:
        p = board.piece_at(selected)
        if p:
            sq_name = chess.square_name(selected).upper()
            sym = UNICODE_PIECES[p.symbol()]
            st.info(f"선택한 기물: **{sym} ({sq_name})**")
            
            if p.piece_type == chess.PAWN and p.color == current_turn:
                st.button(
                    "🌀 폰 스킬: 랜덤 아군과 위치 교환", 
                    use_container_width=True, 
                    on_click=pawn_swap_skill, 
                    args=(selected,)
                )
    else:
        st.write("체스판에서 이동할 **내 기물**을 마우스로 클릭하세요.")

    st.markdown("---")
    st.markdown("### 🛡️ 실드 현황")
    w_k = "✅" if st.session_state.shields[chess.WHITE]["king"] else "❌"
    w_q = "✅" if st.session_state.shields[chess.WHITE]["queen"] else "❌"
    b_k = "✅" if st.session_state.shields[chess.BLACK]["king"] else "❌"
    b_q = "✅" if st.session_state.shields[chess.BLACK]["queen"] else "❌"

    st.write(f"- 백(White) 킹/퀸: {w_k} / {w_q}")
    st.write(f"- 흑(Black) 킹/퀸: {b_k} / {b_q}")

    st.markdown("---")
    st.button("🔄 게임 초기화", use_container_width=True, on_click=reset_game)
