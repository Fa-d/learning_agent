import json
from typing import Union
from ..models.learning import Course, Exam, Chapter, Section, Paragraph
from ..llm_provider import get_llm_provider

class LearningService:
    def generate_course(self, topic: str, llm_provider_name: str = "llama") -> Course:
        llm_provider = get_llm_provider(llm_provider_name)
        prompt = f"""Generate a comprehensive yet concise course on the topic '{topic}' in the following JSON structure:

{{
  "title": "Title of the Course",
  "id": 1,
  "chapters": [
    {{
      "title": "Chapter 1 Title",
      "id": 1,
      "sections": [
        {{
          "title": "Section Title",
          "id": 1,
          "paragraphs": [
            {{
              "content": "Paragraph 1 text.",
              "id": 1
            }},
            {{
              "content": "Paragraph 2 text.",
              "id": 2
            }}
          ]
        }}
      ]
    }},
    {{
      "title": "Chapter 2 Title",
      "id": 2,
      "sections": [
        {{
          "title": "Section Title",
          "id": 1,
          "paragraphs": [
            {{
              "content": "Paragraph 1 text.",
              "id": 1
            }}
          ]
        }}
      ]
    }}
  ]
}}

Each chapter should have sections, and each section should have paragraphs as a list of objects, each with a 'content' and 'id' field. The response must be valid JSON and follow this structure strictly. Return only the raw JSON. Do not include any markdown, code block formatting, or extra text. Now, generate the course on '{topic}'."""
        
        response = llm_provider.generate_completion(
            prompt=prompt,
            max_tokens=4096,
            temperature=0.7,
            top_p=0.9,
            stop=[""]
        )
        
        course_json = json.loads(response['choices'][0]['text'].strip())
        return Course(**course_json)

    def generate_exam(self, paragraph: str, llm_provider_name: str = "llama") -> Exam:
        llm_provider = get_llm_provider(llm_provider_name)
        prompt = f"""Generate an exam for the following paragraph. Include a mix of question types: multiple-choice (with 4 options), true/false, short answer, and fill-in-the-blank. For fill-in-the-blank, indicate the blank with "___".

Paragraph:
{paragraph}

Return the exam in the following JSON structure. Ensure 'options' and 'correct_answer' are only present for relevant question types.

{{
  "questions": [
    {{
      "question_text": "Multiple-choice question?",
      "question_type": "multiple_choice",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A"
    }},
    {{
      "question_text": "True/False statement?",
      "question_type": "true_false",
      "correct_answer": "True"
    }},
    {{
      "question_text": "Short answer question?",
      "question_type": "short_answer",
      "correct_answer": "Expected short answer"
    }},
    {{
      "question_text": "Fill in the blank: The capital of France is ___",
      "question_type": "fill_in_the_blank",
      "correct_answer": "Paris"
    }}
  ]
}}

The response must be valid JSON and follow this structure strictly. Return only the raw JSON. Do not include any markdown, code block formatting, or extra text."""

        response = llm_provider.generate_completion(
            prompt=prompt,
            max_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            stop=[""]
        )

        exam_json = json.loads(response['choices'][0]['text'].strip())
        return Exam(**exam_json)

    def get_course_part(self, course: Course, chapter_id: int, section_id: int = 0, paragraph_id: int = 0) -> Union[Chapter, Section, Paragraph, None]:
        for chapter in course.chapters:
            if chapter.id == chapter_id:
                if section_id is None:
                    return chapter
                for section in chapter.sections:
                    if section.id == section_id:
                        if paragraph_id is None:
                            return section
                        for paragraph in section.paragraphs:
                            if paragraph.id == paragraph_id:
                                return paragraph
        return None

