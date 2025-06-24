#!/usr/bin/env python3
"""
MLX Study Assistant - Advanced Research and Learning Tool
Designed for students and researchers using Apple Silicon MLX
"""

import os
import json
import warnings
import urllib3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

# Suppress warnings for cleaner output
urllib3.disable_warnings()
warnings.filterwarnings('ignore')

from backend.mlx_controller import MLXController, GenerationParams

class StudyAssistant:
    """Advanced AI-powered study assistant for research and learning"""
    
    def __init__(self, subject="General Studies", model="mlx-community/Qwen2.5-1.5B-Instruct-4bit"):
        print(f"🎓 Initializing Study Assistant for {subject}")
        print("Loading MLX model... (this may take a moment)")
        
        self.controller = MLXController()
        self.subject = subject
        self.model_name = model
        
        # Load model with error handling
        try:
            success = self.controller.load_model(model)
            if success:
                print(f"✅ Model loaded: {model}")
            else:
                print(f"❌ Failed to load {model}, trying backup model...")
                self.controller.load_model("mlx-community/Qwen2.5-0.5B-Instruct-4bit")
        except Exception as e:
            print(f"⚠️  Model loading error: {e}")
            print("Please ensure you have models downloaded or run the download script")
        
        # Initialize study session tracking
        self.study_session = {
            "start_time": datetime.now(),
            "subject": subject,
            "model_used": model,
            "topics_covered": [],
            "questions_asked": [],
            "key_concepts": [],
            "documents_analyzed": [],
            "session_notes": []
        }
        
        # Create study directory
        self.study_dir = Path("study_sessions")
        self.study_dir.mkdir(exist_ok=True)
        
        print(f"📚 Study Assistant ready for {subject}!")
        print("=" * 50)
    
    def research_topic(self, topic: str, depth: str = "detailed", max_tokens: int = 2048) -> str:
        """
        Deep research on any topic with customizable depth
        
        Args:
            topic: The topic to research
            depth: 'overview', 'detailed', 'advanced', or 'research'
            max_tokens: Maximum response length
        """
        print(f"🔬 Researching: {topic} ({depth} level)")
        
        depth_prompts = {
            "overview": "Provide a clear, structured overview of",
            "detailed": "Provide a comprehensive, detailed analysis of", 
            "advanced": "Provide an advanced, technical deep-dive into",
            "research": "Provide a research-level analysis with latest developments, methodologies, and implications for"
        }
        
        # Adjust parameters based on depth
        temp_settings = {
            "overview": 0.3,     # More factual
            "detailed": 0.4,     # Balanced
            "advanced": 0.5,     # More creative connections
            "research": 0.6      # Most creative for insights
        }
        
        params = GenerationParams(
            max_length=max_tokens,
            temperature=temp_settings.get(depth, 0.4),
            top_p=0.85,
            top_k=50
        )
        
        messages = [
            {"role": "system", "content": f"You are an expert research assistant and educator specializing in {self.subject}. Provide accurate, well-structured, and insightful information. Use examples, break down complex concepts, and highlight key relationships."},
            {"role": "user", "content": f"{depth_prompts[depth]} {topic}. Include:\n- Key concepts and definitions\n- Important examples and applications\n- Current relevance and significance\n- Connections to related topics"}
        ]
        
        start_time = time.time()
        result = self.controller.generate_text(messages, params)
        generation_time = time.time() - start_time
        
        # Track the research
        self.study_session["topics_covered"].append({
            "topic": topic,
            "depth": depth,
            "timestamp": datetime.now(),
            "generation_time": generation_time
        })
        
        print(f"✅ Research complete ({generation_time:.1f}s)")
        return result['text']
    
    def analyze_document(self, document_text: str, analysis_type: str = "summary") -> str:
        """
        Analyze research papers, textbooks, articles, or any document
        
        Args:
            document_text: The text to analyze
            analysis_type: 'summary', 'critique', 'methodology', 'implications', 'questions'
        """
        print(f"📄 Analyzing document ({analysis_type})")
        
        analysis_prompts = {
            "summary": "Summarize the key points, main arguments, and conclusions",
            "critique": "Provide a critical analysis examining strengths, weaknesses, and limitations",
            "methodology": "Analyze the methodology, approach, and techniques used",
            "implications": "Discuss the implications, applications, and significance",
            "questions": "Generate thoughtful study questions and discussion points based on this content",
            "key_points": "Extract and organize the most important concepts and information"
        }
        
        # Handle long documents by chunking
        if len(document_text.split()) > 3000:
            print("📚 Long document detected, using advanced chunking analysis...")
            return self._analyze_long_document(document_text, analysis_type)
        
        params = GenerationParams(
            max_length=1536,
            temperature=0.4,
            top_p=0.9,
            top_k=40
        )
        
        messages = [
            {"role": "system", "content": f"You are analyzing academic content in {self.subject}. Provide structured, insightful analysis that helps with learning and understanding."},
            {"role": "user", "content": f"{analysis_prompts[analysis_type]} of this text:\n\n{document_text}"}
        ]
        
        result = self.controller.generate_text(messages, params)
        
        # Track document analysis
        self.study_session["documents_analyzed"].append({
            "analysis_type": analysis_type,
            "timestamp": datetime.now(),
            "word_count": len(document_text.split())
        })
        
        return result['text']
    
    def generate_study_questions(self, topic_or_content: str, difficulty: str = "mixed", count: int = 10) -> str:
        """
        Generate custom study questions for any topic or content
        
        Args:
            topic_or_content: Topic name or actual content to generate questions from
            difficulty: 'basic', 'intermediate', 'advanced', or 'mixed'
            count: Number of questions to generate
        """
        print(f"❓ Generating {count} {difficulty} study questions")
        
        difficulty_levels = {
            "basic": "fundamental understanding, recall, and basic comprehension",
            "intermediate": "application, analysis, and connecting concepts", 
            "advanced": "synthesis, evaluation, critical thinking, and complex problem-solving",
            "mixed": "a balanced mix of basic recall, intermediate application, and advanced analysis"
        }
        
        params = GenerationParams(
            max_length=1024,
            temperature=0.6,
            top_p=0.9,
            top_k=60
        )
        
        messages = [
            {"role": "system", "content": f"You are creating educational study materials for {self.subject}. Generate clear, thought-provoking questions that promote deep learning."},
            {"role": "user", "content": f"Generate {count} study questions focusing on {difficulty_levels[difficulty]} about: {topic_or_content}\n\nFormat as a numbered list with varied question types (multiple choice, short answer, essay, problem-solving)."}
        ]
        
        result = self.controller.generate_text(messages, params)
        
        # Track questions
        self.study_session["questions_asked"].append({
            "topic": topic_or_content,
            "difficulty": difficulty,
            "count": count,
            "timestamp": datetime.now()
        })
        
        return result['text']
    
    def explain_concept(self, concept: str, level: str = "undergraduate", with_examples: bool = True) -> str:
        """
        Explain complex concepts at appropriate academic level
        
        Args:
            concept: The concept to explain
            level: 'high_school', 'undergraduate', 'graduate', or 'expert'
            with_examples: Whether to include examples and analogies
        """
        print(f"💡 Explaining: {concept} ({level} level)")
        
        level_prompts = {
            "high_school": "Explain in clear, simple terms suitable for high school students",
            "undergraduate": "Provide a clear undergraduate-level explanation with appropriate depth",
            "graduate": "Give a graduate-level technical explanation with advanced concepts",
            "expert": "Provide an expert-level analysis with cutting-edge insights"
        }
        
        example_text = "Include concrete examples, analogies, and practical applications." if with_examples else "Focus on core principles and theoretical foundations."
        
        params = GenerationParams(
            max_length=1280,
            temperature=0.4,
            top_p=0.85,
            top_k=45
        )
        
        messages = [
            {"role": "system", "content": f"You are an expert educator in {self.subject}. Make complex topics accessible and engaging while maintaining academic rigor."},
            {"role": "user", "content": f"{level_prompts[level]} of {concept}. {example_text}\n\nStructure your explanation with:\n- Clear definition\n- Key components or principles\n- How it works or applies\n- Why it matters\n- Common misconceptions (if any)"}
        ]
        
        result = self.controller.generate_text(messages, params)
        
        # Track concept explanations
        self.study_session["key_concepts"].append({
            "concept": concept,
            "level": level,
            "with_examples": with_examples,
            "timestamp": datetime.now()
        })
        
        return result['text']
    
    def compare_concepts(self, concept1: str, concept2: str, focus: str = "comprehensive") -> str:
        """
        Compare and contrast concepts for deeper understanding
        
        Args:
            concept1: First concept to compare
            concept2: Second concept to compare
            focus: 'differences', 'similarities', 'applications', or 'comprehensive'
        """
        print(f"🔍 Comparing: {concept1} vs {concept2} ({focus})")
        
        focus_prompts = {
            "differences": "highlighting the key differences and distinctions",
            "similarities": "focusing on similarities, connections, and shared principles", 
            "applications": "comparing their practical applications and use cases",
            "comprehensive": "providing a comprehensive comparison covering similarities, differences, and applications"
        }
        
        params = GenerationParams(
            max_length=1536,
            temperature=0.35,
            top_p=0.9,
            top_k=50
        )
        
        messages = [
            {"role": "system", "content": f"You are analyzing and comparing concepts in {self.subject}. Provide clear, structured comparisons that enhance understanding."},
            {"role": "user", "content": f"Compare and contrast {concept1} and {concept2}, {focus_prompts[focus]}.\n\nOrganize your comparison with:\n- Overview of each concept\n- Key similarities (if focusing on differences, briefly mention)\n- Key differences (if focusing on similarities, briefly mention)\n- Practical examples\n- When to use each\n- Significance of understanding both"}
        ]
        
        result = self.controller.generate_text(messages, params)
        return result['text']
    
    def solve_problem(self, problem_statement: str, show_steps: bool = True) -> str:
        """
        Help solve academic problems with step-by-step reasoning
        
        Args:
            problem_statement: The problem to solve
            show_steps: Whether to show detailed steps
        """
        print(f"🧮 Solving problem: {problem_statement[:50]}...")
        
        step_instruction = "Show detailed step-by-step reasoning and explain each step." if show_steps else "Provide the solution with brief explanations."
        
        params = GenerationParams(
            max_length=1536,
            temperature=0.2,  # Low temperature for accuracy
            top_p=0.8,
            top_k=30
        )
        
        messages = [
            {"role": "system", "content": f"You are an expert problem solver in {self.subject}. Provide accurate, methodical solutions with clear reasoning."},
            {"role": "user", "content": f"Solve this problem: {problem_statement}\n\n{step_instruction}\n\nFormat your response with:\n- Problem analysis\n- Solution approach\n- Step-by-step solution\n- Final answer\n- Verification (if applicable)"}
        ]
        
        result = self.controller.generate_text(messages, params)
        return result['text']
    
    def create_study_plan(self, topics: List[str], duration_days: int = 7, difficulty_progression: bool = True) -> str:
        """
        Create a structured study plan for multiple topics
        
        Args:
            topics: List of topics to cover
            duration_days: Number of days for the study plan
            difficulty_progression: Whether to progress from basic to advanced
        """
        print(f"📅 Creating {duration_days}-day study plan for {len(topics)} topics")
        
        progression_note = "Progress from basic understanding to advanced concepts." if difficulty_progression else "Maintain consistent difficulty level throughout."
        
        params = GenerationParams(
            max_length=2048,
            temperature=0.5,
            top_p=0.9,
            top_k=50
        )
        
        topics_list = "\n".join([f"- {topic}" for topic in topics])
        
        messages = [
            {"role": "system", "content": f"You are an educational planner specializing in {self.subject}. Create effective, realistic study schedules."},
            {"role": "user", "content": f"Create a {duration_days}-day study plan for these topics:\n{topics_list}\n\n{progression_note}\n\nInclude:\n- Daily schedule with time estimates\n- Learning objectives for each day\n- Recommended study methods\n- Assessment/review points\n- Tips for retention and understanding"}
        ]
        
        result = self.controller.generate_text(messages, params)
        return result['text']
    
    def _analyze_long_document(self, document: str, analysis_type: str) -> str:
        """Handle documents longer than context window with intelligent chunking"""
        words = document.split()
        chunk_size = 2500  # Safe chunk size for context window
        chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        
        print(f"📖 Processing {len(chunks)} document chunks...")
        
        # Analyze each chunk
        chunk_analyses = []
        for i, chunk in enumerate(chunks):
            print(f"  Processing chunk {i+1}/{len(chunks)}")
            
            params = GenerationParams(max_length=512, temperature=0.3, top_p=0.85)
            messages = [
                {"role": "system", "content": f"Analyze this section of a larger document for {analysis_type}."},
                {"role": "user", "content": f"Section {i+1} of {len(chunks)}: {chunk}"}
            ]
            
            result = self.controller.generate_text(messages, params)
            chunk_analyses.append(f"Section {i+1}: {result['text']}")
        
        # Synthesize final analysis
        print("🔄 Synthesizing complete analysis...")
        combined_analysis = "\n\n".join(chunk_analyses)
        
        params = GenerationParams(max_length=1024, temperature=0.4, top_p=0.9)
        messages = [
            {"role": "system", "content": f"Synthesize these section analyses into a comprehensive {analysis_type} of the complete document."},
            {"role": "user", "content": f"Combine these section analyses:\n\n{combined_analysis}"}
        ]
        
        result = self.controller.generate_text(messages, params)
        return result['text']
    
    def add_note(self, note: str):
        """Add a note to the current study session"""
        self.study_session["session_notes"].append({
            "note": note,
            "timestamp": datetime.now()
        })
        print(f"📝 Note added: {note[:50]}...")
    
    def get_session_summary(self) -> str:
        """Get a summary of the current study session"""
        duration = datetime.now() - self.study_session["start_time"]
        
        summary = f"""
📊 Study Session Summary
{'='*50}
Subject: {self.subject}
Duration: {duration}
Model: {self.model_name}

📚 Topics Researched: {len(self.study_session['topics_covered'])}
📄 Documents Analyzed: {len(self.study_session['documents_analyzed'])}
❓ Question Sets Generated: {len(self.study_session['questions_asked'])}
💡 Concepts Explained: {len(self.study_session['key_concepts'])}
📝 Notes Added: {len(self.study_session['session_notes'])}

Recent Topics: {', '.join([t['topic'] for t in self.study_session['topics_covered'][-3:]])}
"""
        return summary
    
    def save_study_session(self, filename: Optional[str] = None) -> str:
        """Save the study session for later review"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_subject = "".join(c for c in self.subject if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"study_session_{safe_subject}_{timestamp}.json"
        
        filepath = self.study_dir / filename
        
        # Prepare session data for saving
        session_data = self.study_session.copy()
        session_data["end_time"] = datetime.now()
        session_data["duration"] = str(datetime.now() - self.study_session["start_time"])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"💾 Study session saved: {filepath}")
        return str(filepath)
    
    def load_study_session(self, filepath: str):
        """Load a previous study session"""
        with open(filepath, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        print(f"📂 Loaded study session: {session_data['subject']}")
        print(f"   Original date: {session_data['start_time']}")
        print(f"   Topics covered: {len(session_data['topics_covered'])}")
        
        return session_data
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up study session...")
        if hasattr(self, 'controller') and self.controller.model_loaded:
            self.controller.unload_model()
        print("✅ Cleanup complete")

class ResearchAnalyzer:
    """Specialized tool for analyzing research papers and academic documents"""
    
    def __init__(self, study_assistant: StudyAssistant):
        self.assistant = study_assistant
    
    def analyze_paper_structure(self, paper_text: str) -> Dict[str, str]:
        """Analyze academic paper structure and extract key sections"""
        print("📋 Analyzing paper structure...")
        
        sections = {}
        
        # Abstract/Summary
        if len(paper_text) > 1000:
            abstract_section = paper_text[:1000]
            sections["abstract_analysis"] = self.assistant.analyze_document(abstract_section, "summary")
        
        # Full paper analysis
        sections["methodology"] = self.assistant.analyze_document(paper_text, "methodology")
        sections["key_findings"] = self.assistant.analyze_document(paper_text, "implications")
        sections["critical_analysis"] = self.assistant.analyze_document(paper_text, "critique")
        sections["study_questions"] = self.assistant.analyze_document(paper_text, "questions")
        
        return sections
    
    def extract_citations_context(self, paper_text: str, research_question: str) -> str:
        """Extract relevant information for specific research questions"""
        print(f"🔍 Extracting information relevant to: {research_question}")
        
        params = GenerationParams(max_length=1024, temperature=0.2, top_p=0.8)
        messages = [
            {"role": "system", "content": "Extract and synthesize key information relevant to the research question. Focus on methods, findings, data, and implications."},
            {"role": "user", "content": f"Research Question: {research_question}\n\nPaper Content: {paper_text}\n\nExtract and organize relevant information including:\n- Relevant findings or data\n- Methodological approaches\n- Supporting evidence\n- Implications for the research question"}
        ]
        
        result = self.assistant.controller.generate_text(messages, params)
        return result['text']
    
    def generate_literature_summary(self, papers_data: List[Dict[str, str]]) -> str:
        """Generate a literature review summary from multiple papers"""
        print(f"📚 Generating literature summary from {len(papers_data)} papers...")
        
        # Combine paper summaries
        paper_summaries = []
        for i, paper in enumerate(papers_data):
            title = paper.get('title', f'Paper {i+1}')
            content = paper.get('content', paper.get('abstract', ''))
            summary = self.assistant.analyze_document(content, "key_points")
            paper_summaries.append(f"**{title}**:\n{summary}")
        
        combined_summaries = "\n\n".join(paper_summaries)
        
        params = GenerationParams(max_length=2048, temperature=0.4, top_p=0.9)
        messages = [
            {"role": "system", "content": f"Synthesize these paper summaries into a comprehensive literature review for {self.assistant.subject}."},
            {"role": "user", "content": f"Create a literature review summary from these papers:\n\n{combined_summaries}\n\nInclude:\n- Key themes and trends\n- Methodological approaches\n- Major findings\n- Gaps and future directions\n- Synthesis of different perspectives"}
        ]
        
        result = self.assistant.controller.generate_text(messages, params)
        return result['text']

# Convenience functions for quick use
def quick_research(topic: str, subject: str = "General Studies") -> str:
    """Quick research function for immediate use"""
    assistant = StudyAssistant(subject)
    try:
        result = assistant.research_topic(topic, depth="detailed")
        return result
    finally:
        assistant.cleanup()

def quick_explain(concept: str, level: str = "undergraduate", subject: str = "General Studies") -> str:
    """Quick explanation function for immediate use"""
    assistant = StudyAssistant(subject)
    try:
        result = assistant.explain_concept(concept, level=level)
        return result
    finally:
        assistant.cleanup()

def analyze_text(text: str, analysis_type: str = "summary", subject: str = "General Studies") -> str:
    """Quick text analysis function"""
    assistant = StudyAssistant(subject)
    try:
        result = assistant.analyze_document(text, analysis_type)
        return result
    finally:
        assistant.cleanup()

if __name__ == "__main__":
    # Example usage and demonstration
    print("🎓 MLX Study Assistant Demo")
    print("=" * 50)
    
    # Example 1: Quick research
    print("\n📚 Quick Research Example:")
    result = quick_research("machine learning algorithms", "Computer Science")
    print(result[:300] + "...")
    
    # Example 2: Create study assistant for extended session
    print("\n🔬 Extended Study Session Example:")
    cs_assistant = StudyAssistant("Computer Science")
    
    try:
        # Research a topic
        print("\n1. Researching neural networks...")
        neural_nets = cs_assistant.research_topic("neural networks", depth="detailed", max_tokens=1024)
        print(f"✅ Research complete: {len(neural_nets)} characters")
        
        # Generate questions
        print("\n2. Generating study questions...")
        questions = cs_assistant.generate_study_questions("neural networks", difficulty="intermediate", count=5)
        print(f"✅ Questions generated: {len(questions)} characters")
        
        # Explain a concept
        print("\n3. Explaining backpropagation...")
        explanation = cs_assistant.explain_concept("backpropagation", level="undergraduate")
        print(f"✅ Explanation complete: {len(explanation)} characters")
        
        # Show session summary
        print(cs_assistant.get_session_summary())
        
        # Save session
        saved_file = cs_assistant.save_study_session()
        print(f"📁 Session saved to: {saved_file}")
        
    finally:
        cs_assistant.cleanup()
    
    print("\n🎉 Demo complete! Study Assistant is ready for your research needs.")