from utils.common import send_email, send_exam_result_email


class EmailService:

    @staticmethod
    def send_register(name, grade, phone):
        return send_email(name, grade, phone)

    @staticmethod
    def send_exam(**kwargs):
        return send_exam_result_email(**kwargs)
