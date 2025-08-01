from crewai import Agent, Task, Crew, LLM
from warnings import filterwarnings
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AgentWorkflow:
    def __init__(self):
        # Initialize OpenAI client with Hugging Face's inference provider
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=os.environ["HF_TOKEN"],
        )
        
        # Initialize LLM with the OpenAI client configuration
        self.llm = LLM(
            model="huggingface/meta-llama/Llama-3.2-3B-Instruct:novita",
            base_url="https://router.huggingface.co/v1",
            api_key=os.environ["HF_TOKEN"],
        )
        self.planner = None
        self.writer = None
        self.editor = None

        self.plan = None
        self.write = None
        self.edit = None
        
        filterwarnings("ignore")

    def create_agents(self):
        # Note Structure Planner
        self.planner = Agent(
            role="Note Structure Planner",
            goal="Plan a structured and educational note on {topic}, tailored to the student’s level, with clear explanations and examples",
            backstory="You’re an experienced educator who excels at breaking down complex topics into simple, digestible parts for students. "
                     "You know students learn best with clear explanations and relevant examples, just like how answers were written in college "
                     "with bullet points and examples for each point. Your task is to create a detailed outline for a note on {topic}, ensuring "
                     "it covers all key concepts and includes examples appropriate for the specified student level (e.g., high school, college).",
            allow_delegation=False,
            verbose=True,
            llm=self.llm
        )

        # Educational Content Writer
        self.writer = Agent(
            role="Educational Content Writer",
            goal="Write clear, concise, and example-rich educational notes on {topic} based on the planner’s outline, suitable for students",
            backstory="You’re a skilled writer with a talent for explaining difficult concepts in a way students can easily understand. "
                     "You use the outline from the Note Structure Planner to craft notes on {topic} that are simple, engaging, and tailored "
                     "to the student’s level. You write in bullet points where appropriate and include at least one example for each key point, "
                     "mimicking a college-style answer format that’s student-friendly and free of unnecessary complexity.",
            allow_delegation=False,
            verbose=True,
            llm=self.llm
        )

        # Educational Content Editor
        self.editor = Agent(
            role="Educational Content Editor",
            goal="Refine the educational note on {topic} to ensure it’s student-friendly, grammatically correct, and well-structured",
            backstory="You’re an editor with a background in education. Your role is to review the notes written by the Educational Content Writer "
                     "on {topic}, ensuring they are easy to understand, error-free, and formatted to aid learning. You focus on clarity, proper use "
                     "of bullet points, and relevance of examples, making sure the note aligns with the needs of students at the specified level.",
            allow_delegation=False,
            verbose=True,
            markdown=True,
            llm=self.llm
        )

    def create_tasks(self):
        # Plan Task for Note Structure Planner
        self.plan = Task(
            description=(
                "1. Based on the topic '{topic}' and the specified student level (e.g., high school, college), identify the key concepts and subtopics.\n"
                "2. Create a detailed outline that includes:\n"
                "   - An introduction to the topic.\n"
                "   - Key points or subtopics, each with a brief description.\n"
                "   - At least one example for each key point, appropriate for the student’s level.\n"
                "   - A conclusion or summary.\n"
                "3. Ensure the outline is logical, flows well, and is engaging for students.\n"
                "4. Include relevant references or sources for further reading."
            ),
            expected_output="A structured outline document with sections, key points, example placeholders, and a list of references or sources.",
            agent=self.planner,
        )

        # Write Task for Educational Content Writer
        self.write = Task(
            description=(
                "1. Using the outline, write the note on '{topic}' with the following guidelines:\n"
                "   - Use bullet points to list key points or steps.\n"
                "   - Provide at least one example for each major concept.\n"
                "   - Explain concepts in simple terms, avoiding unnecessary technical jargon.\n"
                "   - For college-level topics, include more detailed explanations and advanced examples if appropriate.\n"
                "2. Ensure the introduction explains why the topic is important or interesting.\n"
                "3. In the conclusion, summarize the key takeaways and include references from the planner for further reading."
            ),
            expected_output="A draft of the educational note in markdown format, with clear sections, bullet points, explanations, and examples.",
            agent=self.writer,
        )

        # Edit Task for Educational Content Editor
        self.edit = Task(
            description=(
                "1. Review the draft note on '{topic}' to ensure:\n"
                "   - The language is appropriate for the specified student level.\n"
                "   - Examples are clear, relevant, and enhance understanding.\n"
                "   - Bullet points are used effectively to break down information.\n"
                "   - There are no factual errors or misleading statements.\n"
                "   - The note must be properly formatted in markdown.\n"
                "   - The note must be accurate and proper to score high marks as per the question's weightage.\n"
                "2. Correct any grammatical errors and ensure consistent formatting (e.g., headings, lists).\n"
                "3. Make sure the note is concise yet comprehensive, avoiding unnecessary complexity."
            ),
            expected_output="A polished version of the educational note in markdown format, ready for students to use.",
            agent=self.editor,
            markdown=True
        )

    def setup_crew(self):
        self.crew = Crew(
            agents=[self.planner, self.writer, self.editor],
            tasks=[self.plan, self.write, self.edit],
            verbose=True
        )

    def kickoff_crew(self, topic):
        result = self.crew.kickoff(inputs={"topic": topic})
        return result
