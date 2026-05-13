import streamlit as st
import pytz
from datetime import datetime
import itertools
import operator
import random
from collections import Counter
import hashlib
from fractions import Fraction


class GamePage:

    def __init__(self, state):
        self.state = state

        self.ops = [
            ('+', operator.add),
            ('-', operator.sub),
            ('*', operator.mul),
            ('/', operator.truediv)
        ]

    def get_daily_seed(self, name, today_str):
        raw = f"{name}-{today_str}"
        return int(hashlib.md5(raw.encode()).hexdigest(), 16)

    def is_valid_set(self, s):
        count = Counter(s)
        return all(v <= 2 for v in count.values())

    def generate_expressions(self, a, b, c, d, op1, op2, op3):
        op1_sym, _ = op1
        op2_sym, _ = op2
        op3_sym, _ = op3

        return [
            f"(({a}{op1_sym}{b}){op2_sym}{c}){op3_sym}{d}",
            f"({a}{op1_sym}({b}{op2_sym}{c})){op3_sym}{d}",
            f"{a}{op1_sym}(({b}{op2_sym}{c}){op3_sym}{d})",
            f"{a}{op1_sym}({b}{op2_sym}({c}{op3_sym}{d}))",
            f"({a}{op1_sym}{b}){op2_sym}({c}{op3_sym}{d})"
        ]

    # def solve_num(self, nums, ans):
    #     for perm in itertools.permutations(nums):
    #         a, b, c, d = perm
    #         for op1 in self.ops:
    #             for op2 in self.ops:
    #                 for op3 in self.ops:
    #                     expressions = self.generate_expressions(
    #                         a, b, c, d, op1, op2, op3)
    #                     for expr in expressions:
    #                         try:
    #                             if abs(eval(expr) - ans) < 1e-6:
    #                                 return expr
    #                         except ZeroDivisionError:
    #                             continue
    #     return None

    def solve_num(self, nums, ans):

        ans = Fraction(ans)

        for perm in set(itertools.permutations(nums)):

            a, b, c, d = map(Fraction, perm)

            for op1 in self.ops:
                for op2 in self.ops:
                    for op3 in self.ops:

                        expressions = self.generate_expressions(
                            a, b, c, d,
                            op1, op2, op3
                        )

                        for expr in expressions:
                            try:
                                result = eval(expr)

                                if result == ans:
                                    return expr

                            except ZeroDivisionError:
                                continue

        return None

    def generate_solvable_sets(self, n, ans, seed):
        digits = list(range(1, 10))
        all_sets = list(itertools.combinations_with_replacement(digits, 4))

        rng = random.Random(seed)
        rng.shuffle(all_sets)

        results = []
        for s in all_sets:
            if not self.is_valid_set(s):
                continue

            solution = self.solve_num(s, ans)
            if solution:
                results.append({
                    "digits": list(s),
                    "solution": solution
                })

            if len(results) >= n:
                break

        return results

    def render(self):
        st.markdown("""
<style>

@keyframes float {
    0% {transform: translateY(0px);}
    50% {transform: translateY(-6px);}
    100% {transform: translateY(0px);}
}

.game-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 16px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 8px 20px rgba(0,0,0,0.35);
    animation: float 3s ease-in-out infinite;
}

.game-number {
    font-size: 32px;
    font-weight: bold;
    color: #f8fafc;
    letter-spacing: 2px;
}

.target-box {
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    padding: 14px;
    border-radius: 16px;
    text-align: center;
    color: white;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 25px;
}

.player-box {
    background: rgba(255,255,255,0.05);
    padding: 10px 18px;
    border-radius: 14px;
    margin-bottom: 10px;
    color: white;
}

.stButton>button {
    width: 100%;
    border-radius: 14px;
    border: none;
    background: linear-gradient(90deg,#ec4899,#8b5cf6);
    color: white;
    font-weight: bold;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(168,85,247,0.7);
}

html, body, [data-testid="stAppViewContainer"] {
    background: #020617;
    color: white;
}

</style>
""", unsafe_allow_html=True)

        if st.button("⬅ กลับ"):
            self.state.go("home")
            return

        bkk_tz = pytz.timezone('Asia/Bangkok')
        now = datetime.now(bkk_tz)
        today_str = now.strftime("%Y-%m-%d")
        target = now.day

        if "player_name" not in st.session_state:
            st.session_state.player_name = None

        if st.session_state.player_name is None:
            st.title("🎮 เกม 24")
            name = st.text_input("👤 ใส่ชื่อ")

            if st.button("เริ่มเกม"):
                if name.strip():
                    st.session_state.player_name = name.strip()
                    st.rerun()
                else:
                    st.warning("กรุณาใส่ชื่อ")

            return

        name = st.session_state.player_name

        st.title("🎮 เกม 24")
        st.write(f"👤 ผู้เล่น: **{name}**")
        st.write(f"🎯 เป้าหมายวันนี้: **{target}**")

        seed = self.get_daily_seed(name, today_str)
        cache_key = f"game_sets_{name}_{today_str}"

        if cache_key not in st.session_state:
            st.session_state[cache_key] = self.generate_solvable_sets(
                10, target, seed
            )

        sets = st.session_state[cache_key]

        for i, item in enumerate(sets, 1):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"{i}. {item['digits']}")

            with col2:

                if st.button(f"เฉลย {i}"):

                    pwd_key = f"pwd_open_{i}"

                    st.session_state[pwd_key] = True

                pwd_key = f"pwd_open_{i}"

                if st.session_state.get(pwd_key, False):

                    password = st.text_input(
                        "รหัสผ่าน",
                        type="password",
                        key=f"pwd_input_{i}"
                    )

                    if password == "game24":
                        st.success(item["solution"])

                    elif password:
                        st.error("รหัสผ่านไม่ถูกต้อง")
