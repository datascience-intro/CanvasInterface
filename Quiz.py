import requests

class Quiz:

    def __init__(self, API_URL, API_KEY, COURSE_ID, QUIZ_ID = None,
                title='Empty',description='Empty',quiz_type='assignment'):
        self.API_URL = API_URL
        self.API_KEY = API_KEY
        self.COURSE_ID = COURSE_ID
        self.base_req_str = self.API_URL + "/api/v1/courses/" + str(self.COURSE_ID)
        self.attributes = None
        self.questions = []

        if (QUIZ_ID == None):
            self._create_quiz(title,description,quiz_type)
        else:
            self._get_quiz(QUIZ_ID)
            self._get_questions()

    def _create_quiz(self,title,description,quiz_type):


        options = ['quiz[title]='+title,
                  'quiz[description]=' + description,
                  'quiz[quiz_type]='+quiz_type]

        req_str = self.base_req_str + "/quizzes?" + '&'.join(options) + "&access_token=" + self.API_KEY
        response = requests.post(req_str).json()
        self.attributes = dict(response)
        self.quizjson = response

    def _get_quiz(self,QUIZ_ID):

        req_str = self.base_req_str + "/quizzes/" + str(QUIZ_ID) + "?access_token=" + self.API_KEY
        response = requests.get(req_str).json()

        self.attributes = dict(response)

    def _get_questions(self):

        req_str = self.base_req_str + "/quizzes/" + str(self.attributes['id']) + "/questions?access_token=" + self.API_KEY
        response = requests.get(req_str).json()

        self.questions = [dict(json) for json in response]


    def add_question(self,question_name='Empty',
                          question_type='essay_question',
                          question_text='Empty',
                          answers=[''],
                          points_possible=1):

        base_req_str = self.base_req_str

        options = ['question[question_name]='+question_name,
              'question[question_text]=' + question_text,
              'question[question_type]='+question_type,
              'question[points_possible]=' + str(points_possible)]
        if (question_type == "multiple_choice_question"):
            options = options + ['question[answers][%d][answer_text]=%s' % (question_num,answer) for (question_num,answer) in enumerate(answers)]

        req_str = self.base_req_str + "/quizzes/" + str(self.attributes['id']) + "/questions?" +'&'.join(options)+ "&access_token=" + self.API_KEY
        response = requests.post(req_str)

        if (response.status_code == 200):
            self.questions.append(dict(response.json()))
        else:
            print(response.json())

        return self

    def _set_publish(self,state):


        options = ['quiz[published]='+str(state)]

        req_str = self.base_req_str + "/quizzes/" + str(self.attributes['id']) + "?" + '&'.join(options) + "&access_token=" + self.API_KEY
        response = requests.put(req_str).json()

        self.attributes = response

        return response

    def publish(self):
        return self._set_publish(True)

    def unpublish(self):
        return self._set_publish(False)


    def delete_quiz(self):


        req_str = self.base_req_str + "/quizzes/" + str(self.attributes['id']) + "?access_token=" + self.API_KEY
        response = requests.delete(req_str).json()

        return response
