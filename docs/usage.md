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
* [enrollments.csv](#enrollmentscsv)
* [grades.csv](#gradescsv)
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



## `quiz_questions.csv`

| Column | Type | Notes |
| - | - | - |
| assessment_id | int | Assessment ID that can be joined against `assessments.csv` |
| question_number | int | The relative order number of the question  |
| question_id | UUID | A unique identifier for the question number |

## `quiz_question_contents.csv`

| Column | Type | Notes |
| - | - | - |
| id | UUID | Question ID that can be joined against `quiz_questions.csv` |
| text | str | The question's text |
| type | str | The type of question (can be ['multichoice', 'multianswer', 'numerical', 'essay']) |

## `quiz_multichoice_answers.csv`

| Column | Type | Notes |
| - | - | - |
| id | int | A unique question answer id |
| question_id | UUID | Question ID that can be joined against `quiz_questions.csv` |
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
