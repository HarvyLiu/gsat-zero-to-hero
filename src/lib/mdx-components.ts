/**
 * The components every lesson can use without imports, passed as <Content components={mdxComponents} />
 * by src/views/Chapter.astro. remark-dialogue also emits <Term> and <DialogueTurn> into dialogues,
 * so those two must always be here.
 *
 * Islands are wrapped in Astro components that hydrate them (PredictIsland, Quiz): client:*
 * directives only work on components imported inside the MDX file itself.
 * Each component reads the page's locale (Astro.currentLocale) and chapter id (from the URL),
 * so authors never pass either.
 */
import CodeBadge from '../components/exam/CodeBadge.astro';
import ExamCountdown from '../components/exam/ExamCountdown.astro';
import Fact from '../components/exam/Fact.astro';
import FormulaSheet from '../components/exam/FormulaSheet.astro';
import OnTheExam from '../components/exam/OnTheExam.astro';
import Quiz from '../components/exam/Quiz.astro';
import DialogueTurn from '../components/learning/DialogueTurn.astro';
import Misconception from '../components/learning/Misconception.astro';
import Predict from '../components/learning/PredictIsland.astro';
import StudentAsks from '../components/learning/StudentAsks.astro';
import Term from '../components/learning/Term.astro';
import TryIt from '../components/learning/TryIt.astro';
import Zh from '../components/learning/Zh.astro';
import Perspective from '../components/learning/Perspective.astro';
import Graph from '../components/widgets/GraphIsland.astro';
import NumberLine from '../components/widgets/NumberLine.astro';
import Space3D from '../components/widgets/Space3D.astro';

export const mdxComponents = {
  // teaching
  Term,
  DialogueTurn,
  StudentAsks,
  TryIt,
  Predict,
  Misconception,
  Zh,
  Perspective,
  // visuals (owner requirement: always visualize)
  Graph,
  NumberLine,
  Space3D,
  // exam
  Quiz,
  OnTheExam,
  CodeBadge,
  Fact,
  FormulaSheet,
  ExamCountdown,
};

export type MdxComponentName = keyof typeof mdxComponents;
