import random
from utils.question_loader import load_questions


class ExamService:

    @staticmethod
    def get_path(level, test_type, exam_set):
        if test_type == "Pre-test":
            return f"questions/{level}_pretest_{exam_set}.json"
        elif test_type == "Post-test":
            return f"questions/{level}_posttest_{exam_set}.json"
        elif test_type == "prelearn":
            return f"questions/{level}_prelearn_{exam_set}.json"

    @staticmethod
    def load(level, test_type, exam_set, student_name):
        path = ExamService.get_path(level, test_type, exam_set)
        questions = load_questions(path)

        rnd = random.Random(hash(student_name))
        rnd.shuffle(questions)

        return questions, path

    @staticmethod
    def score(user_answers):
        score = 0
        detail = []

        for q, ans in user_answers:
            correct = str(q["answer"]).strip()
            user = str(ans).strip() if ans else ""

            is_correct = user == correct
            if is_correct:
                score += 1

            detail.append({
                "no": q["no"],
                "user_answer": user,
                "correct_answer": correct,
                "topic": q.get("topic", "N/A"),
                "result": "ถูก" if is_correct else "ผิด"
            })

        return score, detail
