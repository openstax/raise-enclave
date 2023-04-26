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

Enclave containers can access the following data CSV files:

* [assessments.csv](#assessmentscsv)
* [courses.csv](#coursescsv)
* [course_contents.csv](#course_contentscsv)
* [enrollments.csv](#enrollmentscsv)
* [grades.csv](#gradescsv)
* [ib_content_loads.csv](#ib_content_loadscsv)
* [ib_input_instances.csv](#ib_input_instancescsv)
* [ib_input_submissions.csv](#ib_input_submissionscsv)
* [ib_problem_attempts.csv](#ib_problem_attemptscsv)
* [ib_pset_problems.csv](#ib_pset_problemscsv)
* [quiz_attempts.csv](#quiz_attemptscsv)
* [quiz_attempt_multichoice_responses.csv](#quiz_attempt_multichoice_responsescsv)
* [quiz_questions.csv](#quiz_questionscsv)
* [quiz_question_contents.csv](#quiz_question_contentscsv)
* [quiz_multichoice_answers.csv](#quiz_multichoice_answerscsv)
* [users.csv](#userscsv)


Sample files that can be used as illustrative references can be found in this repo [here](../examples/data). Details on columns and types for each CSV file are documented below.

## `assessments.csv`

| Column | Type | Notes |
| - | - | - |
| id | int | A unique assessment ID |
| name | str | The user friendly name associated with this assessment in course content |

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

## `ib_content_loads.csv`

| Column | Type | Notes |
| - | - | - |
| user_uuid | UUID | User UUID that can be joined against `users.csv` |
| course_id | int | Course ID that can be joined against `courses.csv` |
| impression_id | UUID | A unique identifier that can be used to associate events in a single user impression |
| timestamp | int | A Unix timestamp value that reflects when the grade was created (milliseconds that have elapsed since 00:00:00 UTC on January 1, 1970) |
| content_id | UUID | Content ID that can be joined against `course_contents.csv` |
| variant | str | Variant name |


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
| user_uuid | UUID | User UUID that can be joined against `users.csv` |
| course_id | int | Course ID that can be joined against `courses.csv` |
| impression_id | UUID | A unique identifier that can be used to associate events in a single user impression |
| timestamp | int | A Unix timestamp value that reflects when the grade was created (milliseconds that have elapsed since 00:00:00 UTC on January 1, 1970) |
| content_id | UUID | Content ID that can be joined against `course_contents.csv` |
| input_content_id | UUID | Input content ID that can be joined against `ib_input_instances.csv` via its `id` column |
| variant | str | Variant name |
| response | str | User input to the interactive |

## `ib_problem_attempts.csv`

| Column | Type | Notes |
| - | - | - |
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
| attempt_id | int | Attempt ID that can be joined against quiz_attempts.csv |
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


## Development and testing

Users can easily test their code / Docker images locally with fake datasets. The following example steps assume test data has been populated at `$PWD/enclave-input`:

```bash
$ docker image build -t enclave_container .
$ docker run --rm -e DATA_INPUT_DIR=/input -e RESULT_OUTPUT_DIR=/output -v $PWD/enclave-input:/input -v $PWD/enclave-output:/output enclave_container
```

Expected outputs can be found at `$PWD/enclave-output` in the development environment.
