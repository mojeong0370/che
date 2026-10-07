import streamlit as st
import chess
import chess.svg
import streamlit.components.v1 as components
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

# --- UI 레이아웃 ---
st.title("♟️ 특수 능력 체스 게임")

turn_text = "⚪ 백(White) 차례" if current_turn == chess.WHITE else "⚫ 흑(Black) 차례"
st.subheader(f"현재 순서: {turn_text}")

col_left, col_right = st.columns([1.2, 1])

with col_left:
    selected = st.session_state.selected_square
    legal_moves = get_legal_destinations(selected)
    
    # SVG 생성 및 HTML 컴포넌트로 렌더링 (에러 원인 해결)
    svg_data = chess.svg.board(
        board,
        fill=dict.fromkeys(legal_moves, "#76ff0388"),
        size=400
    )
    
    # HTML 컴포넌트를 사용해 안정적으로 출력
    components.html(
        f'<div style="display:flex;justify-content:center;">{svg_data}</div>',
        height=420
    )

    # 내 기물 선택 목록
    my_pieces = [sq for sq in chess.SQUARES if board.piece_at(sq) and board.piece_at(sq).color == current_turn]
    
    piece_options = {"선택 안 함": None}
    for sq in my_pieces:
        p = board.piece_at(sq)
        name = f"{p.unicode_symbol()} ({chess.square_name(sq).upper()})"
        piece_options[name] = sq

    selected_piece_name = st.selectbox("1️⃣ 이동할 내 기물 선택:", list(piece_options.keys()))
    chosen_sq = piece_options[selected_piece_name]

    if chosen_sq is not None:
        st.session_state.selected_square = chosen_sq
        destinations = get_legal_destinations(chosen_sq)
        
        if destinations:
            dest_options = {f"{chess.square_name(d).upper()}" + (" (상대 기물)" if board.piece_at(d) else ""): d for d in destinations}
            target_dest_name = st.selectbox("2️⃣ 이동할 목적지 선택:", list(dest_options.keys()))
            
            if st.button("🚀 기물 이동 실행", use_container_width=True):
                make_move(chosen_sq, dest_options[target_dest_name])
                st.rerun()
        else:
            st.warning("이 기물은 이동할 수 있는 칸이 없습니다.")

with col_right:
    st.markdown("### 🔮 스킬 & 게임 상태")
    
    if chosen_sq is not None:
        p = board.piece_at(chosen_sq)
        if p and p.piece_type == chess.PAWN:
            if st.button("🌀 폰 스킬: 위치 교환", use_container_width=True):
                targets = [s for s in chess.SQUARES if board.piece_at(s) and board.piece_at(s).color == current_turn and s != chosen_sq]
                if targets:
                    target_sq = random.choice(targets)
                    p1, p2 = board.piece_at(chosen_sq), board.piece_at(target_sq)
                    board.set_piece_at(chosen_sq, p2)
                    board.set_piece_at(target_sq, p1)
                    board.turn = not current_turn
                    st.session_state.selected_square = None
                    st.toast("🌀 위치가 교환되었습니다!")
                    st.rerun()

    st.markdown("---")
    st.write("🛡️ **실드 현황**")
    st.write(f"- 백 킹/퀸: {'✅' if st.session_state.shields[chess.WHITE]['king'] else '❌'} / {'✅' if st.session_state.shields[chess.WHITE]['queen'] else '❌'}")
    st.write(f"- 흑 킹/퀸: {'✅' if st.session_state.shields[chess.BLACK]['king'] else '❌'} / {'✅' if st.session_state.shields[chess.BLACK]['queen'] else '❌'}")

    st.markdown("---")
    if st.button("🔄 게임 초기화", use_container_width=True):
        reset_game()
        st.rerun()
