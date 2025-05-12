from profanity_check import predict

def validate_question(question):
    if len(question) < 5:
        return False, "Question too short"
    if predict([question])[0] == 1:
        return False, "Offensive content detected"
    return True, "Valid question"