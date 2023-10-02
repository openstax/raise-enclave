from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing import List, Union
from uuid import UUID
from typing import Literal
from math import isnan


class Assessment(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(extra='forbid')


class Course(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(extra='forbid')


class Enrollment(BaseModel):
    user_uuid: UUID
    course_id: int
    role: Literal['student', 'teacher']

    model_config = ConfigDict(extra='forbid')


class Grade(BaseModel):
    assessment_id: int
    user_uuid: UUID
    course_id: int
    grade_percentage: float
    time_submitted: int

    model_config = ConfigDict(extra='forbid')

    @field_validator('grade_percentage')
    @classmethod
    def grade_value(cls, v):
        if isnan(v):
            raise ValueError('Grade value is nan')
        if v < 0.0 or v > 100.0:
            raise ValueError(f'Grade value {v} is out of expected range')
        return v


class User(BaseModel):
    uuid: UUID
    first_name: str
    last_name: str
    email: str

    model_config = ConfigDict(extra='forbid')


class QuizQuestion(BaseModel):
    assessment_id: int
    question_number: int
    question_id: UUID

    model_config = ConfigDict(extra='forbid')


class QuizQuestionContents(BaseModel):
    id: UUID
    text: str
    type: Literal['multichoice', 'multianswer', 'numerical', 'essay']

    model_config = ConfigDict(extra='forbid')


class QuizMultichoiceAnswer(BaseModel):
    id: int
    question_id: UUID
    text: str
    grade: float
    feedback: str

    model_config = ConfigDict(extra='forbid')


class InputInteractiveBlock(BaseModel):
    id: UUID
    content_id: UUID
    variant: str
    content: str
    prompt: str

    model_config = ConfigDict(extra='forbid')


class ProblemSetProblem(BaseModel):
    id: UUID
    content_id: UUID
    variant: str
    pset_id: UUID
    content: str
    problem_type: Literal['input', 'dropdown', 'multiselect', 'multiplechoice']
    solution: str
    solution_options: str

    model_config = ConfigDict(extra='forbid')


class CourseContents(BaseModel):
    section: str
    activity_name: str
    lesson_page: str
    content_id: UUID

    model_config = ConfigDict(extra='forbid')


class QuizAttempts(BaseModel):
    id: int
    assessment_id: int
    user_uuid: UUID
    course_id: int
    attempt_number: int
    grade_percentage: float
    time_started: int
    time_finished: int

    model_config = ConfigDict(extra='forbid')


class QuizAttemptMultichoiceResponses(BaseModel):
    attempt_id: int
    question_number: int
    question_id: UUID
    answer_id: int

    model_config = ConfigDict(extra='forbid')


class ContentLoads(BaseModel):
    user_uuid: UUID
    course_id: int
    impression_id: UUID
    timestamp: int
    content_id: UUID
    variant: str

    model_config = ConfigDict(extra='forbid')


class IBProblemAttempts(BaseModel):
    user_uuid: UUID
    course_id: int
    impression_id: UUID
    timestamp: int
    content_id: UUID
    pset_content_id: UUID
    pset_problem_content_id: UUID
    variant: str
    problem_type: str
    response: Union[str, List[str]]
    correct: bool
    attempt: int
    final_attempt: bool

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def response_type(self):
        if self.problem_type == 'multiselect' and type(self.response) is str:
            raise ValueError('Response must be a list')
        if self.problem_type != 'multiselect' and \
           type(self.response) is not str:
            raise ValueError('Response must be a string')
        return self


class IBInputSubmissions(BaseModel):
    user_uuid: UUID
    course_id: int
    impression_id: UUID
    timestamp: int
    content_id: UUID
    input_content_id: UUID
    variant: str
    response: str

    model_config = ConfigDict(extra='forbid')
