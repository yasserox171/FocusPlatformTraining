export type Role = "admin" | "learner";

export interface User {
  id: string;
  email: string;
  role: Role;
  full_name_ar: string;
  full_name_fr: string;
  is_active: boolean;
}

export interface ContentSummary {
  id: string;
  type: "lesson" | "course" | "exercise" | "quiz";
  title_ar: string;
  title_fr: string;
  category_id: string | null;
  status?: "draft" | "published";
  is_ai_generated?: boolean;
  published_at: string | null;
  progress?: number | null;
}

export interface QuizOption {
  id: string;
  text: string;
}

export interface QuizQuestion {
  id: string;
  question_text: string;
  question_type: "mcq" | "yes_no";
  options: QuizOption[];
  hint: string | null;
  is_final_quiz: boolean;
}

export interface ExerciseData {
  id: string;
  description: string;
  hint: string | null;
}

export interface Paragraph {
  id: string;
  type: "text" | "video" | "quiz" | "exercise";
  order: number;
  lang_hint: "ar" | "fr" | "auto";
  content_html: string | null;
  video_url: string | null;
  video_type: "youtube" | "direct" | null;
  completed: boolean;
  quiz_questions: QuizQuestion[];
  exercises: ExerciseData[];
}

export interface Lesson {
  id: string;
  title_ar: string;
  title_fr: string;
  order: number;
  paragraphs: Paragraph[];
}

export interface Unit {
  id: string;
  title_ar: string;
  title_fr: string;
  order: number;
  prerequisite_unit_id: string | null;
  accessible: boolean;
  completed: boolean;
  lessons: Lesson[];
}

export interface CourseDetail extends ContentSummary {
  pass_threshold: number;
  units: Unit[];
  lessons: Lesson[];
}

export interface Certificate {
  id: string;
  type: "attendance" | "competency";
  serial_number: string;
  qr_code_url: string;
  issued_at: string;
  course: { id: string; title_ar: string; title_fr: string };
  linkedin_url: string;
}

export interface PipelineJob {
  id: string;
  prompt: string;
  status:
    | "pending"
    | "validating"
    | "searching"
    | "analyzing"
    | "awaiting_user"
    | "generating"
    | "uploading"
    | "done"
    | "failed";
  user_request: {
    possible_contents: {
      type: string;
      title_ar: string;
      title_fr: string;
      description: string;
    }[];
    duplicate_warnings: {
      topic: string;
      existing_title: string;
      similarity: number;
    }[];
  } | null;
  generated_content_ids: string[] | null;
  error_message: string | null;
  created_at: string;
}
