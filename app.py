import streamlit as st
import chess
import chess.svg
import base64
import random

st.set_page_config(page_title="특수 능력 체스 게임", page_icon="♟️", layout="wide")

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

# SVG 보드를 생성하여 HTML로 표시하는 함수
def get_board_svg():
    selected = st.session_state.selected_sq
    fill_dict = {}
    
    if selected is not None:
        fill_dict[selected] = "#ffeb3b" # 선택한 칸 노란색
        for move in board.legal_moves:
            if move.from_square == selected:
                fill_dict[move.to_square] = "#81c784" # 이동 가능 칸 초록색

    svg_data = chess.svg.board(
        board=board,
        fill=fill_dict,
        size=450
    )
    return svg_data

# 클릭 및 이동 로직 처리
def process_square_select(sq):
    selected = st.session_state.selected_sq
    
    if selected is None:
        p = board.piece_at(sq)
        if p and p.color == current_turn:
            st.session_state.selected_sq = sq
    else:
        if selected == sq:
            st.session_state.selected_sq = None
        else:
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

st.title("♟️ 특수 능력 체스 게임")

turn_label = "⚪ 백(White) 차례" if current_turn == chess.WHITE else "⚫ 흑(Black) 차례"
st.subheader(turn_label)

col1, col2 = st.columns([1.2, 1])

with col1:
    # 체스판 SVG 출력
    svg_board = get_board_svg()
    st.image(svg_board, use_column_width=False, width=450)
    
    # 클릭 대신 간편하게 칸을 선택할 수 있는 드롭다운 메뉴 방식 제공
    selected = st.session_state.selected_sq
    
    square_names = [chess.square_name(s).upper() for s in chess.SQUARES]
    
    st.markdown("#### 🎯 기물 이동 조작")
    col_a, col_b = st.columns(2)
    
    with col_a:
        from_choice = st.selectbox(
            "선택할 기물 칸", 
            options=["선택 안함"] + square_names,
            index=0 if selected is None else square_names.index(chess.square_name(selected).upper()) + 1,
            key="from_sq_select"
        )
    
    with col_b:
        to_choice = st.selectbox("이동할 목적지 칸", options=["목적지 선택"] + square_names, key="to_sq_select")
    
    if st.button("이동 실행 🚀", use_container_width=True):
        if from_choice != "선택 안함" and to_choice != "목적지 선택":
            f_sq = chess.parse_square(from_choice.lower())
            t_sq = chess.parse_square(to_choice.lower())
            st.session_state.selected_sq = f_sq
            process_square_select(t_sq)
            st.rerun()

with col2:
    st.markdown("### 🔮 액티브 스킬")
    selected = st.session_state.selected_sq
    
    if selected is not None:
        p = board.piece_at(selected)
        if p:
            sq_name = chess.square_name(selected).upper()
            st.info(f"현재 선택된 위치: **{sq_name}**")
            
            if p.piece_type == chess.PAWN and p.color == current_turn:
                if st.button("🌀 폰 스킬: 랜덤 아군과 위치 교환", use_container_width=True):
                    pawn_swap_skill(selected)
                    st.rerun()
    else:
        st.write("왼쪽에서 이동할 **내 기물 칸**과 **목적지 칸**을 선택해 주세요.")

    st.markdown("---")
    st.markdown("### 🛡️ 실드 현황")
    w_k = "✅" if st.session_state.shields[chess.WHITE]["king"] else "❌"
    w_q = "✅" if st.session_state.shields[chess.WHITE]["queen"] else "❌"
    b_k = "✅" if st.session_state.shields[chess.BLACK]["king"] else "❌"
    b_q = "✅" if st.session_state.shields[chess.BLACK]["queen"] else "❌"

    st.write(f"- 백(White) 킹/퀸: {w_k} / {w_q}")
    st.write(f"- 흑(Black) 킹/퀸: {b_k} / {b_q}")

    st.markdown("---")
    if st.button("🔄 게임 초기화", use_container_width=True):
        reset_game()
        st.rerun()
