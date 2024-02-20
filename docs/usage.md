# RAISE Enclave Usage

This documentation is intended for researchers that want to use enclaves to analyze RAISE data. It assumes some basic familiarity with [Docker](https://www.docker.com/).

## Operational model

RAISE enclaves allow users to write their analysis code with the programming language and framework of their choice with the following constraints:

* The code and all dependencies must be packaged into a Docker image
* The code must not rely on any network access during runtime (network connectivity is blocked during execution of an enclave and attempts to access external endpoints will result in runtime failures)

The contract between the runtime and any container is fairly straight forward:

* Input data is staged at a path exposed via the `DATA_INPUT_DIR` environment variable. Users can read the environment variable and append the relative path for any input files necessary for analysis.

* Analysis outputs should be written to the path exposed via the `RESULT_OUTPUT_DIR` environment variable. Any files written outside of this path will be lost at the end of the execution. Any files written to this path will also be subject to review. Only the following file types are currently allowed / supported (files of any other type will be redacted from the output as part of review):
    * CSV
    * PNG / JPG
    * PDF

A relatively trivial example of an analysis can be found in this repo [here](../examples/quiz-analyzer).

## Data model

:warning: :construction: The RAISE enclave data model is still in early stages and breaking changes could be introduced as things evolve. :construction: :warning:

Enclave containers can access data serialized in CSV format. Data files are populated in subdirectories dedicated for specific academic years / semesters:

| Path | Academic year / semester |
| - | - |
| `{DATA_INPUT_DIR}/ay2022` | Academic year spanning Fall 2022 through Spring 2023 |
| `{DATA_INPUT_DIR}/ay2023` | Academic year spanning Fall 2023 through Spring 2024 |

Each path above includes the following data files:

| CSV | Description |
| - | - |
| [assessments.csv](#assessmentscsv) | The set of assessments (Moodle quizzes) in the course associating name to a unique ID |
| [content_loads.csv](#content_loadscsv) | Events that occur whenever users load a specific piece of content in `course_contents.csv` |
| [courses.csv](#coursescsv) | A list of courses associating name to a unique ID |
| [course_contents.csv](#course_contentscsv) | Information about what part of the course a specific content ID can be associated with |
| [enrollments.csv](#enrollmentscsv) | Enrollment information mapping users to specific courses and their corresponding role in that course |
| [grades.csv](#gradescsv) | Gradebook data for a student based upon from assessments (these are the maximum of all attempts on the assessment when multiple exist) |
| [ib_input_instances.csv](#ib_input_instancescsv) | Details on instances of open input interactives in the course |
| [ib_input_submissions.csv](#ib_input_submissionscsv) | Events that occur when a user submits to an open input interactive |
| [ib_pset_problem_attempts.csv](#ib_pset_problem_attemptscsv) | Events that occur when a user submits to a pset problem interactive |
| [ib_pset_problems.csv](#ib_pset_problemscsv) | Details on instances of pset problem interactives in the course |
| [quiz_attempts.csv](#quiz_attemptscsv) | Attempt details for Moodle quizzes |
| [quiz_attempt_multichoice_responses.csv](#quiz_attempt_multichoice_responsescsv) | Question level responses on a quiz attempt |
| [quiz_questions.csv](#quiz_questionscsv) | Details on the contents of each assessment mapping questions to each assessment |
| [quiz_question_contents.csv](#quiz_question_contentscsv) | Details on the content of each quiz question by ID |
| [quiz_multichoice_answers.csv](#quiz_multichoice_answerscsv) | Details on option choices for `multichoice` quiz questions |
| [users.csv](#userscsv) | User information |

In addition, prejoined view tables are available for easy data query:
| CSV | Description | Source data
| - | - | - |
| [view_enrollment.csv](#view_enrollmentcsv) | Enhanced enrollment information with course ID, course name, user ID and user role | `enrollments.csv`, `courses.csv`
| [view_ib_input.csv](#view_ib_inputcsv) | Event data for open input interactive, with additional information of the question and relevant content | `ib_input_submissions.csv`, `ib_input_instances.csv`, `course_contents.csv`
| [view_ib_pset.csv](#view_ib_psetcsv) | Event data for pset problem interactive, with additional information of the question and relevant content | `ib_pset_problem_attempts.csv`, `ib_pset_problems.csv`, `course_contents.csv`
| [view_quiz.csv](#view_quizcsv) | User responses to quizzes, with additional information of item, assessment, and quiz attempt | `quiz_attempts.csv`, `assessments.csv`, `quiz_question_contents.csv`, `quiz_attempt_multichoice_responses.csv`, `quiz_multichoice_answers.csv` 

Sample files that can be used as illustrative references can be found in this repo [here](../examples/data). Details on columns and types for each CSV file are documented below.

## `assessments.csv`

| Column | Type | Notes |
| - | - | - |
| id | int | A unique assessment ID |
| name | str | The user friendly name associated with this assessment in course content |

## `content_loads.csv`

| Column | Type | Notes |
| - | - | - |
| user_uuid | UUID | User UUID that can be joined against `users.csv` |
| course_id | int | Course ID that can be joined against `courses.csv` |
| impression_id | UUID | A unique identifier that can be used to associate events in a single user impression |
| timestamp | int | A Unix timestamp value that reflects when the grade was created (milliseconds that have elapsed since 00:00:00 UTC on January 1, 1970) |
| content_id | UUID | Content ID that can be joined against `course_contents.csv` |
| variant | str | Variant name |

## `courses.csv`

| Column | Type | Notes |
| - | - | - |
| id | int | Unique course ID |
| name | str | User friendly course name |

## `course_contents.csv`

| Column | Type | Notes |
| - | - | - |
| section | str | Section name |
| activity_name | str | Activity name |
| lesson_page | str | Lesson page name |
| content_id | UUID | Content page UUID |

## `enrollments.csv`

| Column | Type | Notes |
| - | - | - |
| user_uuid | UUID | User UUID that can be joined against `users.csv` |
| course_id | int | Course ID that can be joined against `courses.csv` |
| role | str | Value of either `student` or `teacher` to indicate a user's role in a course |

## `grades.csv`

| Column | Type | Notes |
| - | - | - |
| assessment_id | int | Assessment ID that can be joined against `assessments.csv` |
| user_uuid | UUID | User UUID that can be joined against `users.csv` |
| course_id | int | Course ID that can be joined against `courses.csv` |
| grade_percentage | float | A value between 0 and 100 that reflects in the course gradebook |
| time_submitted | int | A Unix timestamp value that reflects when the grade was created (seconds that have elapsed since 00:00:00 UTC on January 1, 1970) |

## `ib_input_instances.csv`

| Column | Type | Notes |
| - | - | - |
| id | UUID | A unique UUID value that is assigned to the input interactive |
| content_id | UUID | Content page UUID |
| variant | str | Variant name |
| content | str | Input content |
| prompt | str | Prompt content |

## `ib_input_submissions.csv`

| Column | Type | Notes |
| - | - | - |
| id | UUID | A unique UUID value that is assigned to an input interactive attempt |
| user_uuid | UUID | User UUID that can be joined against `users.csv` |
| course_id | int | Course ID that can be joined against `courses.csv` |
| impression_id | UUID | A unique identifier that can be used to associate events in a single user impression |
| timestamp | int | A Unix timestamp value that reflects when the grade was created (milliseconds that have elapsed since 00:00:00 UTC on January 1, 1970) |
| content_id | UUID | Content ID that can be joined against `course_contents.csv` |
| input_content_id | UUID | Input content ID that can be joined against `ib_input_instances.csv` via its `id` column |
| variant | str | Variant name |
| response | str | User input to the interactive |

## `ib_pset_problem_attempts.csv`

| Column | Type | Notes |
| - | - | - |
| id | UUID | A unique UUID value that is assigned to a pset problem interactive attempt |
| user_uuid | UUID | User UUID that can be joined against `users.csv` |
| course_id | int | Course ID that can be joined against `courses.csv` |
| impression_id | UUID | A unique identifier that can be used to associate events in a single user impression |
| timestamp | int | A Unix timestamp value that reflects when the grade was created (milliseconds that have elapsed since 00:00:00 UTC on January 1, 1970) |
| content_id | UUID | Content ID that can be joined against `course_contents.csv` |
| pset_content_id | UUID | Problem set ID that can be joined against `ib_pset_problems.csv` via its `pset_id` column |
| pset_problem_content_id | UUID | Problem ID that can be joined against `ib_pset_problems.csv` via its `id` column|
| variant | str | Variant name |
| problem_type | str | The type of problem (one of 'input', 'dropdown', 'multiselect', or 'multiplechoice') |
| response | str or str[] when `problem_type` is `multiselect` | User response to the problem |
| correct | bool | Whether the response was correct |
| attempt | int | Attempt count for the problem |
| final_attempt | bool | Whether the attempt was the final allowed attempt for the problem |

## `ib_pset_problems.csv`

| Column | Type | Notes |
| - | - | - |
| id | UUID | A unique UUID value that is assigned to the problem interactive |
| content_id | UUID |  Content page UUID |
| variant | str | Variant name |
| pset_id | UUID | A unique UUID value of the problem set|
| content | str | Problem content |
| problem_type | str | Problem type (one of 'input', 'dropdown', 'multiselect', or 'multiplechoice')|
| solution | str | Solution string for problem |
| solution_options | str | Solution options for problem |

## `quiz_attempts.csv`

| Column | Type | Notes |
| - | - | - |
| id | int | A unique quiz attempt ID |
| assessment_id | int |  Assessment ID that can be joined against assessments.csv |
| user_uuid | UUID | User UUID that can be joined against users.csv |
| course_id | int | Course ID that can be joined against courses.csv|
| attempt_number | int | The attempt number for the user in this course assessment |
| grade_percentage | float | A value between 0 and 100 that reflects the attempt grade|
| time_started | int | A Unix timestamp value that reflects when the attempt was started (seconds that have elapsed since 00:00:00 UTC on January 1, 1970) |
| time_finished | int | A Unix timestamp value that reflects when the attempt was finished (seconds that have elapsed since 00:00:00 UTC on January 1, 1970) |

## `quiz_attempt_multichoice_responses.csv`

| Column | Type | Notes |
| - | - | - |
| id | UUID | A unique UUID value that is assigned to an attempt at a quiz question |
| quiz_attempt_id | int | Quiz attempt ID that can be joined against quiz_attempts.csv |
| question_number | int |  The relative order number of the question in the quiz |
| question_id | UUID | Question ID that can be joined against quiz_question_contents.csv |
| answer_id | int | Question choice ID that can be joined against quiz_multichoice_answers.csv |

Key notes:
* There may be 0 or more matches for a given `attempt_id` and `question_number` in this table
* A row for a given `attempt_id` and `question_number` will not be present if a student does not answer the question
* At least one row will be present for a given `attempt_id` and `question_number` if a student answers the question
* More than one row will be present for a given `attempt_id` and `question_number` if a student selects multiple choices where the question is configured as multi-select

## `quiz_questions.csv`

| Column | Type | Notes |
| - | - | - |
| assessment_id | int | Assessment ID that can be joined against `assessments.csv` |
| question_number | int | The relative order number of the question  |
| question_id | UUID | Question ID that can be joined against `quiz_question_contents.csv` (multiple quizzes can reference the same question) |

## `quiz_question_contents.csv`

| Column | Type | Notes |
| - | - | - |
| id | UUID | A unique identifier for the question |
| text | str | The question's text |
| type | str | The type of question (can be ['multichoice', 'multianswer', 'numerical', 'essay']) |

## `quiz_multichoice_answers.csv`

| Column | Type | Notes |
| - | - | - |
| id | int | A unique question answer id |
| question_id | UUID | Question ID that can be joined against `quiz_question_contents.csv` |
| text | str | The answer text |
| grade | float | The percentage of the question's total points received for this answer |
| feedback | str | The feedback that gets delivered when this answer is chosen |

## `users.csv`

| Column | Type | Notes |
| - | - | - |
| uuid | UUID | A unique UUID value that is assigned to a user |
| first_name | str | User's first name |
| last_name | str | User's last name |
| email | str | User's email |

## `view_enrollment.csv`
| Column | Type | Notes |
| - | - | - |
| user_uuid | UUID | User UUID |
| course_id | int | Course ID, same as `id` in `courses.csv` and `course_id` in `enrollments.csv` |
| course_name | str | User friendly course name |
| role | str | Value of either `student` or `teacher` to indicate a user's role in a course |

## `view_ib_input.csv`
| Column | Type | Notes |
| - | - | - |
| id | UUID | A unique UUID value that is assigned to an input interactive attempt |
| impression_id | UUID | A unique identifier that can be used to associate events in a single user impression, same as `impression_id` in `content_loads.csv` and `ib_input_submissions.csv` |
| user_uuid | UUID | User UUID |
| course_id | int | Course ID |
| content_page_id | UUID | Content page UUID, same as `content_id` in `course_contents.csv` and `ib_input_submissions.csv` |
| section | str | Section name of the associated content page |
| activity | str | Activity name of the associated content page |
| lesson_page | str | Lesson page name of the associated content page |
| timestamp | int | A Unix timestamp value that reflects when the grade was created for this input (milliseconds that have elapsed since 00:00:00 UTC on January 1, 1970) |
| input_question_id | UUID | A unique identifier of an input question, same as `input_content_id` in `ib_input_submissions.csv` and `id` in `ib_input_instances.csv` |
| input_question_content | str | Content of the input question, same as `content` in `ib_input_instances.csv` |
| input_question_prompt | str | Prompt of the input question, same as `prompt` in `ib_input_instances.csv` |
| variant | str | Variant name |
| response | str | User input to the interactive |

## `view_ib_pset.csv`

| Column | Type | Notes |
| - | - | - |
| id | UUID | A unique UUID value that is assigned to an attempt at a question in a pset interactive, same as `id` in `ib_pset_problem_attempts.csv` |
| impression_id | UUID | A unique identifier that can be used to associate events in a single user impression, same as `impression_id` in `content_loads.csv` and `ib_pset_problem_attempts.csv` |
| user_uuid | UUID | User UUID |
| course_id | int | Course ID |
| content_page_id | UUID | Content page UUID, same as `content_id` in `course_contents.csv` and `ib_pset_problem_attempts.csv` |
| section | str | Section name of the associated content page |
| activity | str | Activity name of the associated content page |
| lesson_page | str | Lesson page name of the associated content page |
| pset_id | UUID | Problem set ID, same as `pset_content_id` in `ib_pset_problem_attempts.csv` and `pset_id` in `ib_pset_problems.csv` |
| pset_problem_id | UUID | Problem ID, same as `pset_problem_content_id` in `ib_pset_problem_attempts.csv` and `id` in `ib_pset_problems.csv` |
| timestamp | int | A Unix timestamp value that reflects when the grade was created for this problem attempt (milliseconds that have elapsed since 00:00:00 UTC on January 1, 1970) |
| variant | str | Variant name |
| problem_type | str | The type of problem (one of 'input', 'dropdown', 'multiselect', or 'multiplechoice') |
| problem_content | str | Problem content, same as `content` in `ib_pset_problems.csv` |
| problem_solution | str | Correct solution for problem, same as `solution` in `ib_pset_problems.csv`|
| solution_options | str | Solution options for problem, same as `solution_options` in `ib_pset_problems.csv` |
| problem_response | str or str[] when `problem_type` is `multiselect` | User response to the problem, same as `response` in `ib_pset_problem_attempts.csv` |
| is_correct | bool | Whether the response was correct, same as `correct` in `ib_pset_problem_attempts.csv` |
| attempt_number | int | Attempt count for the problem, same as `attempt` in `ib_pset_problem_attempts.csv` |
| is_final_attempt | bool | Whether the attempt was the final allowed attempt for the problem, same as `final_attempt` in `ib_pset_problem_attempts.csv` |

## `view_quiz.csv`

| Column | Type | Notes |
| - | - | - |
| id | UUID | A unique UUID value that is assigned to an attempt at a question in a quiz, same as `id` in `quiz_attempt_multichoice_responses.csv` |
| attempt_id | int | Attempt ID of a quiz, same as `id` in `quiz_attempts.csv` and `attempt_id` in `quiz_attempt_multichoice_responses.csv` |
| quiz_id | int | Quiz ID, same as `assessment_id` in `quiz_attempts.csv` and `id` in `assessments.csv` |
| quiz_name | str | The user friendly name associated with this quiz, same as `assessment_name` in `assessments.csv`|
| user_uuid | UUID | User UUID |
| course_id | int | Course ID |
| quiz_attempt_number | int | The attempt number for the user in this quiz, same as `attempt_number` in `quiz_attempts.csv` |
| quiz_grade_percentage | float | A value between 0 and 100 that reflects the attempt grade, same as `grade_percentage` in `quiz_attempts.csv`|
| quiz_start_time | int | A Unix timestamp value that reflects when the quiz attempt was started (seconds that have elapsed since 00:00:00 UTC on January 1, 1970), same as `time_started` in `quiz_attempts.csv` |
| quiz_end_time | int | A Unix timestamp value that reflects when the quiz attempt was finished (seconds that have elapsed since 00:00:00 UTC on January 1, 1970), same as `time_finished` in `quiz_attempts.csv` |
| question_id | UUID | Unique identifier of a quiz question, same as `id` in `quiz_question_contents.csv`, and `question_id` in `quiz_attempt_multichoice_responses.csv` and `quiz_multichoice_answers.csv`|
| question_number | int |  The relative order number of the question in the quiz |
| question_text | str | The question text, same as `text` in `quiz_question_contents.csv` |
| question_type | str | The type of question (can be ['multichoice', 'multianswer', 'numerical', 'essay']), same as `type` in `quiz_question_contents.csv` |
| answer_id | int | Question choice ID, same as `id` in `quiz_multichoice_answers.csv` and `answer_id` in `quiz_attempt_multichoice_responses.csv` |
| answer_text | str | The answer text, same as `text` in `quiz_multichoice_answers.csv`|
| answer_grade | float | The percentage of the question's total points received for this answer, same as `grade` in `quiz_multichoice_answers.csv` |
| answer_feedback | str | The feedback that gets delivered when this answer is chosen, same as `feedback` in `quiz_multichoice_answers.csv`|


## Development and testing

Users can easily test their code / Docker images locally with fake datasets. The following example steps assume test data has been populated at `$PWD/enclave-input`:

```bash
$ docker image build -t enclave_container .
$ docker run --rm -e DATA_INPUT_DIR=/input -e RESULT_OUTPUT_DIR=/output -v $PWD/enclave-input:/input -v $PWD/enclave-output:/output enclave_container
```

Expected outputs can be found at `$PWD/enclave-output` in the development environment.
