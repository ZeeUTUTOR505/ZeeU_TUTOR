from utils.common import generate_password_exam, generate_password_pretest


class AuthService:

    @staticmethod
    def validate(input_password, password_type):
        if password_type == "prelearn":
            expected = generate_password_pretest()
        else:
            expected = generate_password_exam()

        return input_password == expected
