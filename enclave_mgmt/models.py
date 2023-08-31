from pydantic import BaseModel, Extra, validator
from typing import List, Union
from uuid import UUID
from datetime import datetime
from typing import Literal
from math import isnan


class Demographic(BaseModel):
    user_uuid: UUID
    birth_date: str
    sex: Literal['male', 'female']
    american_indian_or_alaska_native: Literal['true', 'false']
    asian: Literal['true', 'false']
    black_or_african_american: Literal['true', 'false']
    native_hawaiian_or_other_pacific_islander: Literal['true', 'false']
    white: Literal['true', 'false']
    demographic_race_two_or_more_races: Literal['true', 'false']
    hispanic_or_latino_ethnicity: Literal['true', 'false']

    class Config:
        extra = Extra.forbid

    @validator('birth_date')
    def birthdate_format(cls, v):
        datetime.strptime(v, "%Y-%m-%d")
        return v


class Assessment(BaseModel):
    id: int
    name: str

    class Config:
        extra = Extra.forbid


class Course(BaseModel):
    id: int
    name: str

    class Config:
        extra = Extra.forbid


class Enrollment(BaseModel):
    user_uuid: UUID
    course_id: int
    role: Literal['student', 'teacher']

    class Config:
        extra = Extra.forbid


class Grade(BaseModel):
    assessment_id: int
    user_uuid: UUID
    course_id: int
    grade_percentage: float
    time_submitted: int

    class Config:
        extra = Extra.forbid

    @validator('grade_percentage')
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

    class Config:
        extra = Extra.forbid


class QuizQuestion(BaseModel):
    assessment_id: int
    question_number: int
    question_id: UUID

    class Config:
        extra = Extra.forbid


class QuizQuestionContents(BaseModel):
    id: UUID
    text: str
    type: Literal['multichoice', 'multianswer', 'numerical', 'essay']

    class Config:
        extra = Extra.forbid


class QuizMultichoiceAnswer(BaseModel):
    id: int
    question_id: UUID
    text: str
    grade: float
    feedback: str

    class Config:
        extra = Extra.forbid


class InputInteractiveBlock(BaseModel):
    id: UUID
    content_id: UUID
    variant: str
    content: str
    prompt: str

    class Config:
        extra = Extra.forbid


class ProblemSetProblem(BaseModel):
    id: UUID
    content_id: UUID
    variant: str
    pset_id: UUID
    content: str
    problem_type: Literal['input', 'dropdown', 'multiselect', 'multiplechoice']
    solution: str
    solution_options: str

    class Config:
        extra = Extra.forbid


class CourseContents(BaseModel):
    section: str
    activity_name: str
    lesson_page: str
    content_id: UUID
    visible: str

    class Config:
        extra = Extra.forbid


class QuizAttempts(BaseModel):
    id: int
    assessment_id: int
    user_uuid: UUID
    course_id: int
    attempt_number: int
    grade_percentage: float
    time_started: int
    time_finished: int

    class Config:
        extra = Extra.forbid


class QuizAttemptMultichoiceResponses(BaseModel):
    attempt_id: int
    question_number: int
    question_id: UUID
    answer_id: int

    class Config:
        extra = Extra.forbid


class ContentLoads(BaseModel):
    user_uuid: UUID
    course_id: int
    impression_id: UUID
    timestamp: int
    content_id: UUID
    variant: str

    class Config:
        extra = Extra.forbid


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

    class Config:
        extra = Extra.forbid

    @validator('response')
    def response_type(cls, value, values):
        if values['problem_type'] == 'multiselect' and type(value) is str:
            raise ValueError('Response must be a list')  # pragma: no cover
        if values['problem_type'] != 'multiselect' and type(value) is not str:
            raise ValueError('Response must be a string')  # pragma: no cover
        return value


class IBInputSubmissions(BaseModel):
    user_uuid: UUID
    course_id: int
    impression_id: UUID
    timestamp: int
    content_id: UUID
    input_content_id: UUID
    variant: str
    response: str

    class Config:
        extra = Extra.forbid
