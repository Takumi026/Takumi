import streamlit as st
import random
import time

# アプリのタイトル
st.title("🔢 マルチ数字当てゲーム")
st.write("コンピューターが選んだすべての数字をピタリと当ててね！")

# 1. 難易度設定の定義
DIFFICULTIES = {
    "簡単 (1つの数字 / 無制限)": (1, None),
    "普通 (2つの数字 / 無制限)": (2, None),
    "難しい (3つの数字 / 無制限)": (3, None),
    "ゲキムズ 🔥 (3つの数字 / 10回制限)": (3, 10)
}

# 💡 難易度ごとの最高スコア（最少回数）を記録するセッション状態の初期化
if "high_scores" not in st.session_state:
    st.session_state.high_scores = {diff: None for diff in DIFFICULTIES.keys()}

# 💡 2. サイドバーの設定エリア
st.sidebar.header("⚙️ ゲームの設定")

# 難易度を選択
selected_diff = st.sidebar.selectbox("難易度を選んでね：", list(DIFFICULTIES.keys()))
required_numbers, max_attempts = DIFFICULTIES[selected_diff]

# 数字の上限を100〜1000の間で選択できるようにする
max_range = st.sidebar.slider(
    "数字の上限を選んでね：", 
    min_value=100, 
    max_value=1000, 
    value=100, # 初期値は100
    step=50    # 50きざみで動かせる
)

# 🏆 3. サイドバーに最高スコアを表示するエリアを追加
st.sidebar.write("---")
st.sidebar.subheader("🏆 難易度ごとの最高スコア")
for diff_name, score in st.session_state.high_scores.items():
    if score is None:
        st.sidebar.write(f"🔹 {diff_name} : -- 回")
    else:
        st.sidebar.write(f"⭐ **{diff_name}** : `{score} 回`")

# 💡 4. ゲームの初期化（難易度、または「上限値」が変わったら強制リセット）
if ("current_diff" not in st.session_state or \
    "current_max" not in st.session_state or \
    st.session_state.current_diff != selected_diff or \
    st.session_state.current_max != max_range):

    st.session_state.current_diff = selected_diff
    st.session_state.current_max = max_range # 現在の上限値を保存

    # 1から設定された上限値（max_range）の間でランダムな数字を作成
    st.session_state.secret_numbers = [random.randint(1, max_range) for _ in range(required_numbers)]
    st.session_state.attempts = 0
    st.session_state.game_over = False
    st.session_state.history = []
    st.session_state.last_status = None 
    st.session_state.last_hints = []

# 5. 残り回数（ライフ）の表示
if max_attempts is not None:
    remaining_lives = max_attempts - st.session_state.attempts
    if remaining_lives > 0 and not st.session_state.game_over:
        st.error(f"❤️ 残りライフ: {remaining_lives} 回 / {max_attempts} 回")
    elif remaining_lives <= 0:
        st.session_state.game_over = True

st.subheader(f"現在のモード: {selected_diff} (範囲: 1 〜 {max_range})")
user_guesses = []

# 難易度に応じた数の入力欄を表示
for i in range(required_numbers):
    guess = st.number_input(
        f"{i+1}つ目の数字（1〜{max_range}）:", 
        min_value=1, 
        max_value=max_range, # 入力の上限も自動で変わる
        value=int(max_range / 2), # 初期値を上限の半分にして入力しやすくする
        step=1,
        key=f"guess_{i}",
        disabled=st.session_state.game_over
    )
    user_guesses.append(guess)

# 6. 判定ボタン
if st.button("すべての予想をチェック！", disabled=st.session_state.game_over):
    with st.spinner("コンピューターが判定中... 🧠"):
        time.sleep(0.6)  # 0.6秒間、画面をぐるぐるさせて操作をロックする    
    st.session_state.attempts += 1

    all_correct = True
    hint_parts = []
    history_parts = []

    # 入力された数字を1つずつ正解と比較
    for i in range(required_numbers):
        g = user_guesses[i]
        s = st.session_state.secret_numbers[i]

        if g < s:
            hint_parts.append(f"{i+1}つ目: もっと大きい ⬆️")
            history_parts.append(f"{g}⬆️")
            all_correct = False
        elif g > s:
            hint_parts.append(f"{i+1}つ目: もっと小さい ⬇️")
            history_parts.append(f"{g}⬇️")
            all_correct = False
        else:
            hint_parts.append(f"{i+1}つ目: ピタリ！ 🎉")
            history_parts.append(f"{g}🎯")

    # 今回の入力を履歴に保存
    round_history = " , \".join(history_parts)"
    st.session_state.history.append(f"回数 {st.session_state.attempts}: [ {round_history} ]")

    # 判定結果と各ヒントをセッション状態に保存する
    st.session_state.last_hints = hint_parts

    if all_correct:
        st.session_state.last_status = "win"
        st.session_state.game_over = True

        # 🏆 最高スコア（最少回答回数）の更新処理
        current_score = st.session_state.attempts
        best_score = st.session_state.high_scores[selected_diff]

        # 初クリア、または今までの記録より回数が少ない場合に更新
        if best_score is None or current_score < best_score:
            st.session_state.high_scores[selected_diff] = current_score
            st.session_state.new_high_score_triggered = True  # 新記録フラグ
        else:
            st.session_state.new_high_score_triggered = False
    else:
        if max_attempts is not None and st.session_state.attempts >= max_attempts:
            st.session_state.last_status = "lose"
            st.session_state.game_over = True
        else:
            st.session_state.last_status = "continue"

    st.rerun()

# 7. 判定結果とヒントを画面に表示
if st.session_state.last_status == "win":
    secrets_str = ", ".join(map(str, st.session_state.secret_numbers))
    st.success(f"🎉 おめでとう！すべて大正解！ 正解は [ {secrets_str} ] でした！")

    # 🏆 新記録達成時の特別お祝いメッセージ
    if st.session_state.get("new_high_score_triggered", False):
        st.write(f"👑 **難易度「{selected_diff}」で最高スコア（最少回数）を更新しました！**")

    st.info(f"合計 {st.session_state.attempts} 回で当てられました。")
    st.balloons()

elif st.session_state.last_status == "lose":
    # 💥 ゲキムズ終了時の「画面シェイク＆一時的なダークノイズ」演出
    st.markdown("""
        <style>
        @keyframes screenShake {
            0% { transform: translate(0, 0) rotate(0deg); }
            10% { transform: translate(-5px, 2px) rotate(-1deg); }
            20% { transform: translate(3px, -1px) rotate(1deg); }
            30% { transform: translate(-3px, -2px) rotate(0deg); }
            40% { transform: translate(2px, 3px) rotate(1deg); }
            50% { transform: translate(-1px, 1px) rotate(-1deg); }
            60% { transform: translate(3px, 2px) rotate(0deg); }
            70% { transform: translate(-2px, -1px) rotate(1deg); }
            80% { transform: translate(-1px, -3px) rotate(-1deg); }
            90% { transform: translate(2px, 2px) rotate(0deg); }
            100% { transform: translate(0, 0) rotate(0deg); }
        }
        @keyframes darkFadeAndOut {
            0% { background-color: rgba(255, 0, 0, 0.3); }
            40% { background-color: rgba(10, 10, 10, 0.85); }
            60% { background-color: rgba(10, 10, 10, 0.85); }
            100% { background-color: rgba(0, 0, 0, 0); }
        }
        .stApp { animation: screenShake 0.5s linear 1; }
        .lose-overlay {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            pointer-events: none; z-index: 99998;
            animation: darkFadeAndOut 3.0s ease-in-out forwards;
        }
        </style>
        <div class="lose-overlay"></div>
    """, unsafe_allow_html=True)

    secrets_str = ", ".join(map(str, st.session_state.secret_numbers))
    st.error(f"💀 ゲームオーバー！10回以内に当てられませんでした…")
    st.info(f"正解は [ {secrets_str} ] でした。")

elif st.session_state.last_status == "continue":
    att = st.session_state.attempts
    st.markdown(f"""
        <style>
        @keyframes fullScreenFlash_{att} {{
            0% {{ opacity: 0.35; }}
            100% {{ opacity: 0; }}
        }}
        .flash-overlay_{att} {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background-color: #ff4b4b; pointer-events: none; z-index: 99999;
            animation: fullScreenFlash_{att} 0.8s ease-out forwards;
        }}
        </style>
        <div class="flash-overlay_{att}"></div>
    """, unsafe_allow_html=True)

    st.warning("残念！ちがう数字があるよ。下のヒントを見てね！")
    for hint in st.session_state.last_hints:
        st.write(hint)

# 8. これまでの入力履歴を表示
if st.session_state.history:
    st.write("-----")
    st.subheader("📋 これまでの履歴")
    for item in reversed(st.session_state.history):
        st.write(item)

# 9. もう一度遊ぶボタン
if st.session_state.game_over:
    if st.button("もう一度遊ぶ 🔄"):
        st.session_state.secret_numbers = [random.randint(1, max_range) for _ in range(required_numbers)]
        st.session_state.attempts = 0
        st.session_state.history = []
        st.session_state.last_status = None
        st.session_state.last_hints = []
        st.session_state.game_over = False
        st.session_state.new_high_score_triggered = False
        st.rerun()
