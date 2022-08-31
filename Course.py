import requests
from .Quiz import Quiz

class Assignment:
    def __init__(self,course,assignment):
        '''Stores the connection to the course object and the assignment dict

        Keyword arguments:
        course -- a Course object that this assignment belongs to
        assignment -- an assignment dict (Assignment object) as in https://canvas.instructure.com/doc/api/assignments.html
        '''
        self.course = course
        self.attributes = assignment

class Course:

    def __init__(self, API_URL, API_KEY, COURSE_ID):
        '''Creates a course object that you can use to interface with the physical course on Studium
        it basically only holds the assignments.

        Keyword Arguments:
        API_URL -- This is the api url for Studium, most likely not going to change, but for Uppsala its
        https://uppsala.instructure.com
        API_KEY -- This is your access token, see https://canvas.instructure.com/courses/785215/pages/getting-started-with-the-api
        COURSE_ID -- This is the ID number of the course, if you go into the course on studium you will find the ID
        as the number https://uppsala.instructure.com/courses/23503, in this case 23503 is the course ID
        '''
        self.API_URL = API_URL
        self.API_KEY = API_KEY
        self.COURSE_ID = COURSE_ID
        self.base_req_str = self.API_URL + "/api/v1/courses/" + str(self.COURSE_ID) # The version number here might change later, perhaps?
        self.attributes = None
        self.quizzes = []
        self.assignments = []

        if (COURSE_ID == None):
            print("We should not create courses")
        else:
            self._get_course()
            self._get_assignments()
            self._get_quizzes()

    def _get_course(self):
        '''Downloads the course attributes from Studium,
        see https://canvas.instructure.com/doc/api/courses.html
        '''
        req_str = self.base_req_str + "?access_token=" + self.API_KEY
        response = requests.get(req_str).json()

        self.attributes = dict(response)

    def _get_quizzes(self):
        '''Not used ATM'''

        req_str = self.base_req_str + "/quizzes?access_token=" + self.API_KEY
        response = requests.get(req_str).json()

        for quizz in response:
            self.quizzes.append(Quiz(API_URL=self.API_URL,API_KEY=self.API_KEY,COURSE_ID=self.COURSE_ID,QUIZ_ID=quizz['id']))

    def _get_assignments(self):
        '''Downloads all assignments and not the submissions, these are different things.
        Also, note that in Studium the graded quizzes are also assignments, but we dont want these.
        '''

        req_str = self.base_req_str + "/assignments?access_token=" + self.API_KEY
        response = requests.get(req_str).json()

        for assignment in response:
            if ("quiz_id" not in assignment):
                self.assignments.append(Assignment(self,dict(assignment)))
                # See https://canvas.instructure.com/doc/api/assignments.html

    def getAssignmentSubmissions(self,assignment_id):
        '''
            Downloads all submissions for the assignment_id
        '''
        req_str = self.base_req_str + "/assignments/" + str(assignment_id) + "?access_token=" + self.API_KEY
        response = requests.get(req_str).json()

        name = response['name'].replace(' ','_')
        print("Fetching assignment %s" % name)
        req_str_ass = self.base_req_str + "/assignments/" + str(assignment_id) + "/submissions?per_page=1000&access_token=" + self.API_KEY
        submissions = requests.get(req_str_ass).json()
        print("Assignments Fetched!")

        return submissions

    def getQuizzSubmissions(self,assignment_id):
        '''
            Downloads all submissions for the quiz_id
        '''
        req_str = self.base_req_str + "/quizzes/" + str(assignment_id) + "?access_token=" + self.API_KEY
        response = requests.get(req_str).json()

        #print(response)
        name = response['title'].replace(' ','_')
        print("Fetching assignment %s" % name)
        req_str_ass = self.base_req_str + "/quizzes/" + str(assignment_id) + "/submissions?per_page=1000&access_token=" + self.API_KEY
        submissions = requests.get(req_str_ass).json()
        print("Assignments Fetched!")

        return submissions

    def getGroupCategories(self):
        #/api/v1/courses/:course_id/group_categories
        req_str = self.base_req_str + "/group_categories?access_token=" + self.API_KEY
        response = requests.get(req_str).json()
        return response

    def createGroup(self,group_category_id,group_name):
        #/api/v1/group_categories/:group_category_id/groups
        #name		string
        #The name of the group

        #description		string
        #A description of the group

        #is_public		boolean
        #whether the group is public (applies only to community groups)

        #join_level		string
        options = ['name='+group_name,
                  'join_level='+'invitation_only']
        base_req_str = self.API_URL + "/api/v1"
        req_str = base_req_str + "/group_categories/" + str(group_category_id)+"/groups?" + '&'.join(options) + "&access_token=" + self.API_KEY
        response = requests.post(req_str).json()
        return response

    def addStudentToGroup(self,group_id,user_id):
        #user_ids is a list of user ids
        #/api/v1/groups/:group_id
        options = ['user_id='+str(user_id)]
        base_req_str = self.API_URL + "/api/v1"
        req_str = base_req_str + "/groups/"+str(group_id)+"/memberships?" + '&'.join(options) + "&access_token=" + self.API_KEY
        response = requests.post(req_str).json()
        return response

    def create_quiz(self,title='Empty',description='Empty',quiz_type='assignment'):
        '''Not used ATM'''
        self.quizzes.append(Quiz(API_URL=self.API_URL,
                                 API_KEY=self.API_KEY,
                                 COURSE_ID=self.COURSE_ID,
                                 title=title,
                                 description=description,
                                 quiz_type=quiz_type))
    def get_user(self,user_id):
        '''Takes the user_id and downloads the user dict from Studium, this includes basically
        most personal data about the user stored in the platform. Basically only used to get the name
        of each user. But you can also use this to get the email.

        Returns:
        response -- A dictionary of the type https://canvas.instructure.com/doc/api/users.html (User object)
        '''

        base_req_str = self.API_URL + "/api/v1"
        req_str = base_req_str + "/users/"+str(user_id)+"/profile?access_token=" + self.API_KEY
        response = requests.get(req_str).json()
        return response

    def getStudents(self):
        '''
            Retrieves a list of all students currently in the course
        '''
        base_req_str = self.API_URL + "/api/v1"
        req_str = base_req_str + "/courses/" + str(self.COURSE_ID) + "/students" +"?access_token=" + self.API_KEY
        response = requests.get(req_str).json()
        return response

    def getAssignmentGroup(self):
        '''
            Gets a list of all assignment groups, like Uppgifter / Exams
        '''
        #GET /api/v1/courses/:course_id/assignment_groups
        base_req_str = self.API_URL + "/api/v1"
        req_str = base_req_str + "/courses/" + str(self.COURSE_ID) + "/assignment_groups" +"?access_token=" + self.API_KEY
        response = requests.get(req_str).json()
        return response


    def createAssignment(self,
                        assignmentName = "Test",
                        dueDate = None,
                        description="",
                        extension="",
                        points_possible=40,
                        exam_group_id=0, publish = False):
        '''
        Creates an assignment with assignmentname
        '''
        ass = "/courses/" + str(self.COURSE_ID) + "/assignments?"
        options = ['assignment[name]='+assignmentName,
                  'assignment[published]=' + str(publish),
                  'assignment[description]=' + description,
                  'assignment[only_visible_to_overrides]=True',
                  'assignment[allowed_extensions][]='+extension,
                  'assignment[submission_types][]=online_upload',
                  'assignment[points_possible]='+str(points_possible),
                  'assignment[assignment_group_id]='+str(exam_group_id)
                  ]
        if dueDate != None:
            options.append('assignment[due_at]='+dueDate)

        base_req_str = self.API_URL + "/api/v1"
        req_str = base_req_str + ass + '&'.join(options) + "&access_token=" + self.API_KEY
        print(req_str)
        response = requests.post(req_str)
        print(response)
        respdict = response.json()
        return respdict

    def createAssignmentOverride(self,assignment_id,student_ids,group_name,startDate,dueDate):
        '''
        Creates an override for this assignment so that it only applies
        to students in the student_ids list
        '''
        assert type(student_ids) == list
        ass = "/courses/%s/assignments/%s/overrides?" % (str(self.COURSE_ID),str(assignment_id))
        base_req_str = self.API_URL + "/api/v1"
        options = ['assignment_override[title]=' + group_name,
                   'assignment_override[unlock_at]=' + startDate,
                   'assignment_override[lock_at]=' + dueDate,
                   'assignment_override[due_at]=' + dueDate,
                  ]
        options += ["assignment_override[student_ids][]=%s"%(id) for index,id in enumerate(student_ids)]
        req_str = base_req_str + ass + '&'.join(options) + "&access_token=" + self.API_KEY
        print(req_str)
        response = requests.post(req_str)
        print(response)
        respdict = response.json()
        return respdict

    def deleteAssignmentOverride(self,assignment_id,override_id):
        ass = "/courses/%s/assignments/%s/overrides/%s" % (str(self.COURSE_ID),str(assignment_id),str(override_id))
        base_req_str = self.API_URL + "/api/v1"
        req_str = base_req_str + ass + "?access_token=" + self.API_KEY
        print(req_str)
        response = requests.delete(req_str)
        print(response)
        respdict = response.json()
        return respdict
